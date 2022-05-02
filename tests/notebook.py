import unittest

from annotation_pipeline.pipeline.breath_detection.split_on_breaths_and_silences import (
    split_on_breaths_and_silences,
)

BREATH_DETECTION_MODEL_PATH = "./breath_detection/models/modelMix4.h5"


class MyTestCase(unittest.TestCase):
    def test_something(self):
        input_wav = "./data/dummywavs/medium.wav"
        split_output_dir = "/tmp/medium/"
        split_on_breaths_and_silences(
            input_wav, split_output_dir, BREATH_DETECTION_MODEL_PATH
        )  # add assertion here


if __name__ == "__main__":
    unittest.main()
