import unittest

from utils.loadfile import generate_unique_tmp_filename
from utils.asr_models import transcribe_from_dir_path

from os.path import join

DATA_DIR = "../data"
MODEL_TYPES=[
    "KBLab/wav2vec2-large-voxrex-swedish", # Regular Swe-Wav2Vec no LM
    "birgermoell/lm-swedish", # Birgers Wav2Vec with LM
    "viktor-enzell/wav2vec2-large-voxrex-swedish-4gram" # Wav2Vec with LM
]
class MyTestCase(unittest.TestCase):
    def test_asr_no_lm(self):
        fname = generate_unique_tmp_filename()
        transcribe_from_dir_path(
            dir=join(DATA_DIR, "dummy", "dummywavdir"),
            output_file=fname,
            device="cpu",
            model_id=MODEL_TYPES[0],
            batch_size=2
        )
    def test_asr_with_lm(self):
        fname = generate_unique_tmp_filename()
        transcribe_from_dir_path(
            dir=join(DATA_DIR, "dummy", "dummywavdir"),
            output_file=fname,
            device="cpu",
            model_id=MODEL_TYPES[2],
            batch_size=5
        )
    def test_asr_with_lm2(self):
        fname = generate_unique_tmp_filename()
        transcribe_from_dir_path(
            dir=join(DATA_DIR, "dummy", "dummywavdir"),
            output_file=fname,
            device="cpu",
            model_id=MODEL_TYPES[1],
            batch_size=5
        )


if __name__ == '__main__':
    unittest.main()
