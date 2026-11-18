# Native 32k ROCm calibration: the first update

Two fresh, completed 40-update native calibration runs used seed 13: ordinary untied C0 (`rocm32k-cal40-c0-s13`) and trainable full-width identity-factor C4 (`rocm32k-cal40-c4-s13`). They used BF16 autocast on an RX 7900 XTX, PyTorch 2.15.0+rocm10.0, ROCm runtime 7.15.26333, FP32 AdamW state, and 2,048-target output chunks. Both manifests bind the same reconstructed TinyStories inputs at revision `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`. Their common native package hash matches clean Model Lab commit `d605f003377173c4019e21c41a843bddeb7291cb`.

## Same start, different head step

The native step-0 checkpoints matched byte-for-byte over all 74 shared trunk tensors and over C4's starting A versus C0's dense W. C4's B was exactly I, so their initial effective W matched exactly. RNG state and stored initial validation values matched; no scores are reported. Manifest-bound packed data and tokenizer digests matched, and both step-1 snapshots had the same data cursor and 131,072 valid targets.

| Realized step-1 change | C0 norm | C4 norm | C4/C0 | Cosine |
| --- | ---: | ---: | ---: | ---: |
| Effective output head | 0.121363547 | 0.134469893 | 1.107992444 | 0.909481664 |
| Common trunk | 0.156117183 | 0.156105974 | 0.999928201 | 0.999999964 |

These are Frobenius norms of endpoint differences computed from the stored parameters in FP64: `W1-W0` for C0 and `A1@B1-A0@B0` for C4. The head deltas differ by 0.055912863 in norm (maximum absolute element difference 0.000208832). C4's B moved by 0.015352611 in Frobenius norm and has saved first moment. The combined trunk difference norm was 0.0000431524 (maximum absolute element difference 0.000000119209). At this shared start, C4 therefore produced a roughly 10.8% larger, visibly rotated effective head step while its realized trunk step stayed very close.

## Clipping explains the common first-moment scale

| First native training update | C0 | C4 |
| --- | ---: | ---: |
| Logged global preclip gradient norm | 4.157756805 | 4.197612762 |
| Declared global clip cap | 1.0 | 1.0 |
| Global norm implied by saved first moments | 0.999999782 | 0.999999761 |
| Implied postclip norm divided by logged preclip norm | 0.240514255 | 0.238230589 |

C4's saved common-trunk and A first moments were both 0.990505084 times their C0 counterparts in norm, with cosines indistinguishable from 1 at the shown precision. The implied clip multipliers have the same ratio. C4's B first-moment norm was 0.013747592. With empty initial state, step 1 and AdamW beta1 = 0.9, the saved FP32 exp_avg divided by 0.1 approximates the postclip gradient seen by the optimizer. The proportional common moments are consistent with equal common derivatives followed by different global clipping; they do not independently recover the raw BF16 gradients. The logged preclip numbers are full-arm scalars, not per-parameter gradients.

[Machine-readable receipt](results/calibration-32k-step-one.json) includes the four checkpoint digests, config/source hashes, and full numerical comparisons. It was computed on CPU using the Lab native checkpoint reader on only the explicit step-0 and step-1 generations; the two matching native `optimizer/grad_norm` rows were the only metric rows queried. Receipt SHA-256: `a9444527ac5a3e953bcedeb38338ffbcefd907590002ad217bc8188406740db4`. [Offline analysis source](compare_step_one.py), SHA-256: `750da252586ff682bbe0a6e097facdd0ac52ff443c39a4f8ade0f6c69d4c2816`.

This is a single-seed mechanism observation. It does not establish native logits or hidden-gradient equality, frozen-control parity, or better learning. The frozen arm and prespecified inline checks were not run here. No later checkpoint or efficacy metric was examined.

Recompute with the same native checkpoint reader, not a training command:

```sh
python compare_step_one.py \
  --c0-initial "$C0/checkpoints/step_00000000_gen_000001" \
  --c0-step-one "$C0/checkpoints/step_00000001_gen_000002" \
  --c4-initial "$C4/checkpoints/step_00000000_gen_000001" \
  --c4-step-one "$C4/checkpoints/step_00000001_gen_000002"
```

C0 and C4 denote local run directories. Their weights are not distributed here.
