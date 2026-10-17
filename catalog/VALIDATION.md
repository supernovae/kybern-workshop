# Stage-one preservation validation

Source Lab commit: `eab014ef7ca92de89d37b47c30df2ebf021d9473`.
Workshop base: `c2dd1b9d1e10afd46a4de1f10000c3a839be68ad`.

Bounded metadata checks on 2026-10-17 passed:

- Exactly 1,077 distinct frozen source paths and destinations; 45,454,519 source bytes.
- Every destination matches source Git blob identity, SHA-256 and byte length.
- Source tree entries are regular non-executable blobs; the sole Python fixture is retained as inert `.py.txt`, unchanged.
- Catalog JSON parses, all 31 IDs are unique, all 26 available landing pages and their origin/report pointers exist, and authored local Markdown links resolve.
- Five later example imports are explicitly planned, not available. Shared router/YAML sources remain pending.
- Existing DevMind (148 files) and microlab (11 files) manifests were independently rechecked against original source commits with zero mismatches before this import. Those originals are not copied again.

These checks establish preservation and discoverability, not execution readiness. No native handlers, recipe execution, source acquisition, training, generation, workload tests or website changes were performed. Packaged research resources remain original provenance, so no current native schema/admission claim is made for them. Native adaptation and explicit local resource-root validation are later work.
