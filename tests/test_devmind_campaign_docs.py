"""Offline regression checks for the published historical campaign summary."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / "experiments/devmind/engram-campaign-20261106.md"


class CampaignDocsTests(unittest.TestCase):
    def test_notebook_source_pin_matches_original_and_hub_commit(self):
        text = CAMPAIGN.read_text()
        pin = "ef882ad1ed8274340e8fc9bac087c903f2f75396"
        pins = re.findall(
            r"HuggingFaceTB/issues-kaggle-notebooks(?:\s*\|\s*|\x60 \(\x60)([0-9a-f]+)",
            text.replace("| \x60", "| "),
        )
        self.assertEqual(pins, [pin, pin])
        self.assertIn("/commit/" + pin, text)

    def test_standalone_source_revisions_are_full_sha1(self):
        revisions = re.findall(r"`([0-9a-f]{30,45})`", CAMPAIGN.read_text())
        self.assertTrue(revisions)
        self.assertTrue(all(len(pin) == 40 for pin in revisions))

    def test_final_phase_completed_exposure_uses_declared_reference(self):
        text = CAMPAIGN.read_text()
        self.assertIn("Combined Targets (`+2,080,374,784` ref)", text)
        self.assertEqual(6_766_391_105 + 2_080_374_784, 8_846_765_889)
        self.assertIn("`8,846,765,889`", text)
        self.assertIn("planned endpoints unless explicitly marked completed", text)


if __name__ == "__main__":
    unittest.main()
