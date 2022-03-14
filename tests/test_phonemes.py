import unittest

from phonemes import get_swedish_phonemes, init_phonemizer, unravel_phonemes


class TestPhonemes(unittest.TestCase):

    def test_phonemizer_loading(self):
        ph = init_phonemizer("cpu", "../models/deep-phonemizer-se.pt")
        res = ph("Hello trevligt", "se")
        # This model only supports with stres marks
        # ph = init_phonemizer("cpu", "../models/deep-phonemizer-se.pt", stress_marks=False)
        # res = ph("Hello trevligt", "se")
        ph = init_phonemizer("cpu", "../models/DeepPhon/winhome/Downloads/DeepPhon_to_send/best_model.pt")
        res = ph("Hello trevligt", "se")
        ph = init_phonemizer("cpu", "../models/DeepPhon/winhome/Downloads/DeepPhon_to_send/model_step_40k.pt")
        res = ph("Hello trevligt", "se")

    def test_unravel(self):
        text = "Hello my name is Nikos"
        phonemizer = init_phonemizer("cpu", "../models/deep-phonemizer-se.pt", True)
        res = get_swedish_phonemes(text, phonemizer, "../models/stress_lex_mtm.txt")
        self.assertTrue("_" in res and " " in res)
        res = unravel_phonemes(res)
        self.assertFalse("_" in res and " " in res)


if __name__ == '__main__':
    unittest.main()
