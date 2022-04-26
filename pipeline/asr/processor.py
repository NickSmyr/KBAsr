# TODO Need to load from pretrained, train this and apply to only sections of
#  an Audio
from abc import abstractmethod
from typing import List

from pipeline.abstract.audio import Audio
from pipeline.abstract.processors import IntervalProcessor


class AbstractASRProcessor(IntervalProcessor):
    @abstractmethod
    def get_max_wave_length(self):
        pass

    @abstractmethod
    def get_sr(self):
        pass


# TODO with the times
class GoogleASRProcessor(AbstractASRProcessor):
    def get_max_wave_length(self):
        pass

    def get_sr(self):
        pass

    def process(self, audios: List[Audio]) -> None:
        pass


class KBASRProcessor(AbstractASRProcessor):
    def get_max_wave_length(self):
        pass

    def get_sr(self):
        pass

    def process(self, audios: List[Audio]) -> None:
        pass
