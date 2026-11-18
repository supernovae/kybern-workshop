# Amendment A3.1: non-adaptive completion retry

Frozen 2026-11-18 15:26 UTC, before the authorized completion retry and
before any A3 capture, proxy, or permutation outcome was observed.

The first A3 attempt passed archive authentication and completed the only
required mature forward, then stopped before SVD, capture, or control analysis
with TypeError: 'str' object is not callable. A reused A1 prefix used the name
sha for a digest string, shadowing a helper in the A3 wrapper. No result was
produced. The first attempt used 9.91 seconds outer wall and 851,124 KiB peak
RSS, on four CPU affinity slots with no optimizer update or GPU use. The
failed wrapper SHA-256 is
3d2adf99f9877d9c373ff8cf99e40099d0b0fab05b799c225972fb7fd80d2617.
The empty receipt and launcher accounting are retained. No results or
thresholds were changed or selected based on that attempt.

Make only one source correction: rename the wrapper helper sha, and its
calls, to a3_sha256_bytes. Leave the pinned A1 prefix, the A3 mature checkpoint
pair, sample, model, inference, metrics, controls, seeds, thresholds and
decision rule unchanged. Statically confirm the generated retry differs
from the failed wrapper only by that name, and that the name is not bound
by the reused prefix or analysis body.

One completion retry only, with at most four CPUs and a hard 4 GiB address
space limit, 160-second soft and 170-second hard wall cap. Including earlier
work (16.84s for A1/A2/preflight and 9.91s for the stopped A3 attempt), the
combined maximum is 196.75 seconds. Keep all attempts and actual resource
use in the record. No training, GPU, archive writes, or held-out scoring.
