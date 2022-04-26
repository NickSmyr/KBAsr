import unittest

from google_kb_z_speaker.main import (
    bunch_agrees,
    agreement_percentage,
    get_lcs_str,
)


class MyTestCase(unittest.TestCase):
    def test_agreement(self):
        bunch = {
            "google": "Hello one",
            "kb": "Hello one",
            "correct": "Hello one",
        }
        print("Percentage agreement ", agreement_percentage(bunch))
        self.assertTrue(bunch_agrees(bunch, threshold=1))
        print(bunch_agrees(bunch, threshold=1))

        bunch = {
            "google": "one two four",
            "kb": "one two three four",
            "correct": "one three four",
        }
        self.assertTrue(bunch_agrees(bunch, 0.75))

    def test_get_lcs_str(self):
        bunch = {
            "google": "one kaååa two zeta four",
            "kb": "one two three four",
            "correct": "one three four",
        }
        self.assertEqual(get_lcs_str(bunch), "one two four")


if __name__ == "__main__":
    unittest.main()
