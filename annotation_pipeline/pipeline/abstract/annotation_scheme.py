from abc import ABC
from typing import List

from pipeline.abstract.annotation import Annotation, IntervalAnnotation


# TODO Maybe do validation of annotations


class AnnotationScheme(ABC):
    """
    Abstract class that represents a set of annotations within an Audio that
    follow the same semantic scheme (e.g. for breath detection there are
    only interval segments with the text 'sp', 'b' or 'sil')
    """

    def __init__(self, annotations: List[Annotation]):
        self._annotations = annotations

    @property
    def annotations(self):
        return self._annotations

    def transform_embed(self, start_sec: float, end_sec: float) -> "AnnotationScheme":
        """
        Transform the annotations and create an equivalent annotation scheme
        whose temoral annotations are transformed when the audio is embeded
        to another audio starting at start_sec and ending at end_sec
        """
        new_annotations = []
        for annotation in self._annotations:
            new_annotations.append(annotation.transform_embed(start_sec, end_sec))
        return AnnotationScheme(new_annotations)

    @classmethod
    def from_textgrid(cls, textgrid):
        intervals = textgrid.tierDict["annot"].entryList
        annotations = [
            IntervalAnnotation(x.start * 1000, x.end * 1000, x.label) for x in intervals
        ]
        return AnnotationScheme(annotations)


class BreathDetectionScheme(AnnotationScheme):
    """
    Interval Annotations with only texts in 'sp', 'b' and 'sil'
    """
