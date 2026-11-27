# Software and astronomy gradient alignment

How does local gradient agreement change across the astronomy expansion and
replay arms? Measure the gradients of the same fixed software and astronomy
development panels at five saved checkpoints per seed. Use the terminal
software parent, each of its two astronomy-only additions, and both replay
orders. The [expansion](../README.md) and [replay](../replay/README.md)
studies supply the checkpoints and measured loss changes.

Each measurement uses all 4,480 software and 1,344 astronomy panel targets
and divides by the corresponding target count before comparing gradients.
The sign of the dot product describes the first-order effect of a small step
along one raw descent direction on the other panel. We report the comparison
at each checkpoint. Adam's updates and the intervening trajectory need
separate measurements. All declared panels are development data.

## Reproduce

Set `EXPANSION` and `REPLAY` to the completed run directories from the two
linked recipes. Use Lab with `eval --gradient-against` and an absolute work
directory outside either input. The diagnostic loads one checkpoint per
pair, runs on CPU, and leaves the original runs in place.

```bash
set -euo pipefail
WORK="${WORK:-$HOME/.local/share/klab/relational-panel-gradients}"
mkdir -p "$WORK"
cd "$WORK"
export KLAB_WORK_DIR="$WORK/state" OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1
mkdir -p panels results receipts
for seed in 11 23 37; do
  for stage in parent triples factorized late interleaved; do
    origin="$EXPANSION"
    case "$stage" in
      parent)
        checkpoint=$(jq -er .continuation.checkpoint "$origin/receipts/try-$seed.json")
        run=$(dirname "$(dirname "$checkpoint")")
        sha=$(jq -er .continuation.sha256 "$origin/receipts/try-$seed.json")
        ;;
      *)
        case "$stage" in
          triples) role=baseline ;;
          factorized) role=candidate ;;
          late) origin="$REPLAY"; role=baseline ;;
          interleaved) origin="$REPLAY"; role=candidate ;;
        esac
        record="$origin/receipts/try-$seed.json"
        run=$(jq -er --arg role "$role" '.arms[$role].run_dir' "$record")
        checkpoint="$run/$(jq -er --arg role "$role" '.arms[$role].checkpoint' "$record")"
        sha=$(jq -er --arg role "$role" '.arms[$role].checkpoint_sha256' "$record")
        ;;
    esac
    for domain in software astronomy; do
      jq --arg sha "$sha" '. + {checkpoint_sha256:$sha}' "$EXPANSION/panels/$domain.json" \
        > "panels/$seed-$stage-$domain.json"
    done
    result="results/$seed-$stage.json"
    klab eval "$(basename "$run")" --runs-dir "$(dirname "$run")" --checkpoint "$checkpoint" \
      --panel "panels/$seed-$stage-software.json" \
      --gradient-against "panels/$seed-$stage-astronomy.json" \
      --gradient-max-bytes 1048576 --output "$WORK/$result" \
      > "receipts/$seed-$stage.out" 2> "receipts/$seed-$stage.log"
    jq -es '
      def equivalent($gradient; $prior):
        $gradient.valid_targets == $prior.valid_targets
        and $gradient.data_identity.validation_sha256 == $prior.data_identity.validation_sha256
        and $gradient.protocol_sha256 == $prior.protocol_sha256
        and (($gradient.loss - $prior.loss)|fabs) < 0.000001;
      .[0].evidence_complete
      and equivalent(.[0].panels.left; .[1])
      and equivalent(.[0].panels.right; .[2])
    ' "$result" "$origin/results/$seed-$stage-software.json" \
      "$origin/results/$seed-$stage-astronomy.json" >/dev/null
  done
done
```

## Result

All 15 comparisons completed on the CPU checkpoints. The 30 panel losses
matched the earlier scores within 0.000001 nats. Swapping the panels on
seed 11's parent reproduced the dot product and cosine exactly and swapped
the gradient norms. Both gradients occupied 821,760 bytes.

| Checkpoint | Seed 11 cosine | Seed 23 cosine | Seed 37 cosine | Mean |
| --- | ---: | ---: | ---: | ---: |
| Software parent | 0.213 | 0.213 | 0.189 | 0.205 |
| Astronomy triples | 0.365 | 0.142 | 0.319 | 0.275 |
| Astronomy factorization | 0.080 | 0.207 | 0.280 | 0.189 |
| Late replay | 0.094 | 0.101 | −0.246 | −0.017 |
| Interleaved replay | 0.256 | 0.147 | 0.022 | 0.142 |

All six astronomy-only endpoints had positive cosine despite the rise in
software loss during expansion. Interleaved replay had higher cosine than
late replay in every seed, by 0.159 on average. The same seeds had higher
software loss under interleaving. The checkpoint measurement captures local
agreement on two triple-encoded development panels. The observed retention
differences span the updates leading up to those checkpoints.

The [run record](results/2026-11-27.json) keeps the exact checkpoint and panel
digests, gradient norms, and loss observations.
