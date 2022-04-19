import unittest

import torch

from utils.phonemes import get_swedish_phonemes, init_phonemizer, unravel_phonemes, phonemizer_wrapper, read_phoneme_dict


class TestPhonemes(unittest.TestCase):

    def setUp(self) -> None:
        self.TEST_SENTENCES = [
            "hello trevligt",
            "hello my name is Nikos",
            "hallå jag heter Nikolaos",
            "trevligt att träffas",
            "27"
        ]
        self.STRESS_MARKS = ["\'", "\"", "`"]
        self.PHONEME_DICT = read_phoneme_dict("models/stress_lex_mtm.txt")
        self.PHONEMIZER = init_phonemizer("cpu", "models/deep-phonemizer-se.pt")

        # Assert there exist OOV words and stress marks
        oov_exist = False
        stress_marks_exist = False
        for x in self.TEST_SENTENCES:
            for w in x.split():
                if w not in self.PHONEME_DICT:
                    oov_exist = True
            x = self.PHONEMIZER(x, "se")
            for char in x:
                if char in self.STRESS_MARKS:
                    stress_marks_exist = True

        self.assertTrue(oov_exist and stress_marks_exist)

    def test_phonemization_wrapper(self):
        ph = init_phonemizer("cpu", "../models/deep-phonemizer-se.pt")
        # Phonemizer wrapper that provides no extra functionality
        ph_new = phonemizer_wrapper(ph, None, include_stress_marks=True)
        # Phonemizer wrapper that only translates non OOV words to known phoneme seqs
        ph_new_dict = phonemizer_wrapper(ph, self.PHONEME_DICT ,
                                         include_stress_marks=True)
        # Phonemizer wrapper that provides only removes stress marks
        ph_new_no_stress = phonemizer_wrapper(ph, None, include_stress_marks=False)
        for sent in self.TEST_SENTENCES:
            torch.manual_seed(0)
            output_ph = ph(sent, "se")
            torch.manual_seed(0)
            output_ph_new = ph_new(sent,"se")
            self.assertEqual(output_ph, output_ph_new)
            # Check ph no stress
            output = ph_new_no_stress(sent,"se")
            for x in output:
                self.assertTrue(x not in self.STRESS_MARKS)
            # Check ph non OOV
            output = ph_new_dict(sent, "se")
            for x,w in zip(sent.split(), output.split()):
                if x in self.PHONEME_DICT:
                    self.assertTrue("".join(self.PHONEME_DICT[x]) == w)

    def test_phonemizer_loading(self):
        ph = init_phonemizer("cpu", "../models/deep-phonemizer-se.pt")
        res = ph(self.TEST_SENTENCES[0], "se")
        # This model only supports with stres marks
        # ph = init_phonemizer("cpu", "../models/deep-phonemizer-se.pt", stress_marks=False)
        # res = ph("Hello trevligt", "se")
        ph = init_phonemizer("cpu", "../models/DeepPhon/winhome/Downloads/DeepPhon_to_send/best_model.pt")
        res = ph(self.TEST_SENTENCES[0], "se")
        ph = init_phonemizer("cpu", "../models/DeepPhon/winhome/Downloads/DeepPhon_to_send/model_step_40k.pt")
        res = ph(self.TEST_SENTENCES[0], "se")

    def test_unravel(self):
        text = "Hello my name is Nikos"
        phonemizer = init_phonemizer("cpu", "../models/deep-phonemizer-se.pt", True)
        res = get_swedish_phonemes(text, phonemizer, "../models/stress_lex_mtm.txt")
        self.assertTrue("_" in res and " " in res)
        res = unravel_phonemes(res)
        self.assertFalse("_" in res and " " in res)


if __name__ == '__main__':
    unittest.main()
