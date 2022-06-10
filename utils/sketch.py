from typing import List

class TranscriptionDataset:
    """
    Dataset mapping input audio samples to transcriptions

    Also has some precalculated transcriptions (Google)
    """
    def __init__(self, audio_filenames: List[str],
                 transcriptions: List[str],
                 precalculated_transcriptions: List[str]):
        self.audio_filenames = audio_filenames
        self.transcriptions = transcriptions
        self.precalculated_transcriptions

    @staticmethod
    def from_speakers_folder_kb(speaker_names : List[str]):
        """
        TMH format

        z21/
            file_01.wav
            file_02.wav
            z21.googleasr
            z21.correct

        z22/
            etc
        """

# List of filenames mapped to transcriptions


class Transcriber:
    pass

class PrecalculatedTranscriber:
    # This one has calculated outptus
    pass