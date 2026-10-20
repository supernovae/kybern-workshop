"""Connected native preparation from first32 templates, generated fixtures only.

Explicit substitutions: 2,000 generated parent rows per source, 8/1/1 family
weights, 260 BPE vocabulary, 6,000 fit bytes and 300 target tokens. No real corpus,
network or model execution. Production declarations remain unchanged.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "experiments/devmind/first32"

@unittest.skipUnless(os.environ.get("WORKSHOP_LAB_CHECKOUT"), "requires installed subset-capable Lab")
class ConnectedFirst32(unittest.TestCase):
    def test_native_subset_to_cold_prepared_inputs(self):
        sys.path.insert(0, str(Path(os.environ["WORKSHOP_LAB_CHECKOUT"]) / "src"))
        import yaml
        from sparselab.corpus.acquisition import acquire, _adapter, _digest, declaration_sha256
        from sparselab.corpus.project import SourceDeclaration, load_project, source_declaration_payload
        from sparselab.training.manifest import canonical_json, sha256_file
        from sparselab.corpus.admission_draft import draft_admission_manifest
        from sparselab.corpus.split_inventory import write_split_inventory
        from sparselab.corpus.split_freeze import freeze_splits, finalize_family_inventory
        from sparselab.corpus.pipeline import build
        from sparselab.corpus.release import freeze, verify_release
        from sparselab.corpus.export import export_release, _split_stats, _licenses
        from sparselab.config.loading import load_config, load_tokenizer_config
        from sparselab.config.models import TokenizerSampling, RunConfig
        from sparselab.data.tokenizer import train_tokenizer, verify_tokenizer_artifact
        from sparselab.corpus.mixture import materialize_mixture, verify_mixture
        from sparselab.staging import materialize_prepared_inputs, verify_prepared_inputs

        def write(path, value):
            path.write_text(yaml.safe_dump(value, sort_keys=False))

        with tempfile.TemporaryDirectory() as directory, patch(
            "urllib.request.build_opener", side_effect=AssertionError("fixture attempted network")
        ):
            root = Path(directory)
            recipe = root / "recipe"
            shutil.copytree(PACKAGE, recipe)
            for index, name in enumerate(["000-web", "001-synthetic", "002-code"]):
                target = recipe / "sources" / (name + ".yaml")
                child = yaml.safe_load(target.read_text())
                original = json.loads(json.dumps(child))
                original["revision"] = "f" * 40
                original["notes"] = "Generated offline fixture; not upstream content or evidence."
                acquisition = original["acquisition"]
                acquisition.pop("retained_subset")
                acquisition.update(max_rows=2000, max_bytes=8 * 1024**2)
                rows = []
                for number in range(2000):
                    text = (f"Fixture {index} document {number} explains a distinct useful example. "
                            "A reader follows the clear sequence and checks the stated result. ") * 3
                    if index == 0:
                        row = {"text": text, "metadata": {"url": f"https://example.org/{number}", "language": "en"}}
                    elif index == 1:
                        row = {"text": text, "seed_data": f"fixture-seed-{number}", "prompt": text,
                               "audience": "students", "format": "explanation"}
                    else:
                        row = {"code": f"# {text}\ndef fixture_{number}():\n    return {number}\n",
                               "repo_name": f"fixture/repository-{number}", "path": "example.py",
                               "language": "Python", "license": "mit"}
                    rows.append(row)
                raw = b"".join(canonical_json(row) + b"\n" for row in rows)
                upstream_sha = hashlib.sha256(raw).hexdigest()
                shard = acquisition["bounded_shards"][0]
                shard.update(path="fixture/train.jsonl", expected_sha256=upstream_sha,
                             max_shard_bytes=len(raw), max_scanned_rows=2000)
                source = SourceDeclaration.model_validate(original)
                receipts, rendered = [], []
                for number, row in enumerate(rows):
                    row_sha = hashlib.sha256(canonical_json(row)).hexdigest()
                    receipt = {"source_row_index": number, "source_row_sha256": row_sha}
                    receipts.append(receipt)
                    envelope = {**receipt, "dataset_revision": source.revision,
                                "source_shard_path": shard["path"], "source_shard_sha256": upstream_sha}
                    rendered.append(canonical_json({**row, "_sparselab_source": envelope}) + b"\n")
                body = b"".join(rendered)
                file = {"path": "fixture/train.jsonl.sample.jsonl", "size": len(body),
                        "sha256": hashlib.sha256(body).hexdigest()}
                identity = {"declaration_sha256": declaration_sha256(source),
                            "adapter": _adapter(source), "files": [file]}
                digest = _digest(identity)
                parent = root / "parents" / name / digest
                data = parent / "files" / file["path"]
                data.parent.mkdir(parents=True)
                data.write_bytes(body)
                manifest = {"schema_version": 1, "source_id": source.id,
                            "declaration": source_declaration_payload(source), **identity,
                            "snapshot_sha256": digest, "retrieval": {"shards": [{
                                "output_path": file["path"], "source_shard_path": shard["path"],
                                "source_shard_sha256": upstream_sha, "selected_rows": receipts}]}}
                (parent / "manifest.json").write_bytes(canonical_json(manifest) + b"\n")
                # Restore production selection caps while substituting only fixture ancestry.
                original["acquisition"].update(max_rows=child["acquisition"]["max_rows"],
                    max_bytes=child["acquisition"]["max_bytes"], retained_subset={
                        **child["acquisition"]["retained_subset"], "snapshot_path": str(parent),
                        "snapshot_sha256": digest, "manifest_sha256": sha256_file(parent / "manifest.json")})
                write(target, original)
            project = load_project(recipe / "project-acquire.yaml")
            lock = acquire(project, root)
            self.assertEqual(len(lock["sources"]), 3)
            self.assertEqual(acquire(project, root, offline=True), lock)
            admission = recipe / "admission.json"
            draft_admission_manifest(project, root, recipe / "application-policy.json", recipe / "POLICY.md", admission)
            release_spec = yaml.safe_load((recipe / "release-reviewed.template.yaml").read_text())
            release_spec["record_admission"] = {"path": admission.name, "sha256": sha256_file(admission)}
            write(recipe / "release-reviewed.yaml", release_spec)
            prefreeze = load_project(recipe / "project-pre-freeze.yaml")
            inventory = recipe / "inventory.jsonl"
            write_split_inventory(prefreeze, root, inventory)
            clusters = json.loads((recipe / "family-clusters.template.json").read_text())
            clusters.update(inventory_sha256=sha256_file(inventory), split_weights={"train": 8, "validation": 1, "test": 1},
                            merges=[], reviewer="Generated fixture reviewer", reviewed_on="2026-10-20")
            cluster_path = recipe / "clusters.json"
            cluster_path.write_text(json.dumps(clusters))
            splits = recipe / "splits-reviewed.yaml"
            freeze_splits(prefreeze, root, inventory, cluster_path, splits)
            release = freeze(build(load_project(recipe / "project-build.yaml"), root, offline=True), root)
            self.assertEqual(verify_release(release)["release_id"], release.name)
            family = recipe / "family.jsonl"
            finalize_family_inventory(release, splits, family)
            exported = export_release(release, "lm", recipe / "base-run.yaml", 260, root)
            fit = load_tokenizer_config(exported / "tokenizer.yaml")
            sampling = yaml.safe_load((recipe / "tokenizer-sampling.yaml").read_text())
            sampling.update(max_fit_bytes=6000, audit_documents_per_stratum=1, max_audit_bytes=65536)
            fit = fit.model_copy(update={"sampling": TokenizerSampling.model_validate(sampling)})
            fit_path = recipe / "fit.yaml"
            write(fit_path, fit.model_dump(mode="json"))
            tokenizer = train_tokenizer(fit)
            verified = verify_tokenizer_artifact(tokenizer, source="local_text", revision=fit.dataset.revision,
                                                vocab_size=260, dataset=fit.dataset)
            self.assertTrue(verified["sampling_audit"]["disjoint_from_fit"])
            mixture = yaml.safe_load((recipe / "mixture.template.yaml").read_text())
            mixture.update(release_path=str(release), tokenizer_config=str(fit_path), family_inventory=str(family),
                           tokenizer_origin_release_id=release.name, target_quotas={"web": 180, "synthetic": 60, "code": 60})
            declaration = recipe / "mixture.yaml"
            write(declaration, mixture)
            output = root / "mixture"
            receipt = materialize_mixture(declaration, output)
            self.assertEqual(verify_mixture(declaration, output), receipt)
            self.assertEqual(sum(receipt["actual_target_tokens"].values()), 300)
            # Only data packing: tiny CPU config avoids any accelerator/runtime requirement.
            run = load_config(Path(os.environ["WORKSHOP_LAB_CHECKOUT"]) / "configs/runtime_smoke_cpu.yaml").model_dump(mode="json")
            count, size = _split_stats(release / "lm/validation.jsonl", "lm")
            run["model"]["vocab_size"] = 260
            run["tokenizer"]["path"] = str(tokenizer)
            run["dataset"] = {"source": "local_token_mixture", "revision": release.name,
                "cache_dir": str(root / "cache"), "train_path": str(output / "train.tokens.jsonl"),
                "validation_path": str(release / "lm/validation.jsonl"), "train_max_documents": receipt["records"],
                "validation_max_documents": count, "train_max_tokens": 300, "validation_max_tokens": size + count + 1,
                "license": _licenses(release), "mixture_declaration_path": str(declaration), "mixture_output_path": str(output)}
            config = RunConfig.model_validate(run)
            bundle = root / "prepared"
            materialize_prepared_inputs(config, bundle, tokenizer_batch_source_bytes=1024, verification_mode="cold")
            verify_prepared_inputs(bundle, config, verification_mode="cold")
            self.assertTrue((bundle / "inputs.json").is_file())
            # The GPU handoff must not reopen controller-only parents or recipe paths.
            for name in ("recipe", "parents", "corpora", "mixture", "cache"):
                (root / name).rename(root / (name + "-unavailable"))
            verify_prepared_inputs(bundle, config, verification_mode="cold")
            detached = root / "detached-prepared"
            materialize_prepared_inputs(config, detached, prepared_inputs=bundle,
                                        verification_mode="cold")
            verify_prepared_inputs(detached, config, verification_mode="cold")

if __name__ == "__main__":
    unittest.main()
