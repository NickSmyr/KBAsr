from abc import ABC
from typing import List

from pipeline.abstract.annotation import Annotation


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

    def transform_embed(
        self, start_sec: float, end_sec: float
    ) -> "AnnotationScheme":
        new_annotations = []
        for annotation in self._annotations:
            new_annotations.append(
                annotation.transform_embed(start_sec, end_sec)
            )
        return AnnotationScheme(new_annotations)


class BreathDetectionScheme(AnnotationScheme):
    """
    Interval Annotations with only texts in 'sp', 'b' and 'sil'
    """
