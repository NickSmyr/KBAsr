from abc import ABC, abstractmethod
from typing import List

from pipeline.abstract.audio import Audio


class Processor(ABC):
    """
    A processor receives as input an Audio and produces an annotation scheme
    for that audio
    """

    @abstractmethod
    def process(self, audios: List[Audio]) -> None:
        """Apply the processor to a list of audios"""
        pass


class IntervalProcessor(Processor):
    """
    A Processor whose produced annotations are IntervalAnnotations
    """

    @abstractmethod
    def process(self, audios: List[Audio]) -> None:
        pass
