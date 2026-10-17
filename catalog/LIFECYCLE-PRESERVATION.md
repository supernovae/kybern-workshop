# Historical lifecycle evidence supplement

The [preserved portable Engram guide](../provenance/lab/docs/portable-engram.md)
was a tracked source referenced by the historical lifecycle registry but missing
from the earlier preservation manifests. Its original bytes are now retained;
[the scoped manifest](../provenance/lab-lifecycle-supplement.json) records the exact
Lab source revision, Git blob, byte count and SHA-256.

This guide describes historical behavior and claims, not current Lab guarantees
or an executable compatibility target. Commands and absolute paths remain
original provenance. Current reproduction uses supported interfaces and new
identities under [the contribution policy](../CONTRIBUTING.md).

Five lifecycle-linked references were already unavailable in the checked Lab
tracked tree and the corresponding Workshop provenance paths. Their exact names
and pinned checks are recorded in the scoped manifest. No payload hashes are
invented for absent files. Nothing was reconstructed, downloaded or recovered;
absence from these Git trees is not a search of every host or external store.
Those references do not establish verified evidence, runnable artifacts or
lifecycle clearance. The original populated registry remains byte-preserved.

Validation checked the guide's bytes, SHA-256, size and Git blob against the pinned
source; checked all five paths for absence in both pinned tracked trees; and
checked these authored links and diff whitespace. This preservation PR does not
delete the Lab guide, change native behavior, run workloads or authorize recovery.
