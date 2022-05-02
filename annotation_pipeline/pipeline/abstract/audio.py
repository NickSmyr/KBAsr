from typing import List

from pydub import AudioSegment

from pipeline.abstract.annotation_scheme import AnnotationScheme


# TODO create test folder and test starter logic
# TODO generate ASRable segments and be able to run them, in another procecss
#  Fault tolerance (resume from stop)
# TODO generate AUDIO from textgrid, lab, json files output to textgrid lab
# json files
# TODO visualize Audio
class Audio:
    """
    An Audio object is the representation of an audio file. The audio file
    can have a number of annotations that are created from the processors
    """

    pass

    def __init__(self, audio_segment):
        """
        :param audio_segment: underlying AudioSegment object
        """
        self._audio_segment = audio_segment
        self._annotation_schemes = []

    @property
    def annotation_schemes(self) -> List[AnnotationScheme]:
        return self._annotation_schemes

    def get_duration_sec(self) -> float:
        """Returns the duration in seconds"""
        return len(self._audio_segment) / 1000

    # TODO add names to annotation schemes
    def add_annotation_scheme(self, annotation_scheme: AnnotationScheme):
        """Registers the given annotation scheme for the given soundfile"""
        self._annotation_schemes.append(annotation_scheme)

    def incorporate_annotations(self, audio: "Audio", start_time_sec: float):
        """Incorporates all the annotations from the given audio in the
        current Audio"""
        end_time_sec = start_time_sec + audio.get_duration_sec()
        if end_time_sec > self.get_duration_sec():
            raise Exception(
                "Cannot incorporate audio annotations, because target audio "
                "is too "
                "long to be incorporated at the given start time"
            )
        for annotation_scheme in audio.annotation_schemes:
            self.add_annotation_scheme(
                annotation_scheme.transform_embed(start_time_sec, end_time_sec)
            )

    def extract(self, start_sec: float, end_sec: float) -> "Audio":
        """
        Extracts an audio file between start and end from the current Audio
        """
        return Audio(self._audio_segment[start_sec:end_sec])

    @classmethod
    def load(cls, filepath):
        segment = AudioSegment.from_file(filepath)
        return Audio(segment)
