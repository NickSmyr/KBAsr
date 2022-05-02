from abc import abstractmethod, ABC


class Annotation(ABC):
    """
    Abstract class that represents a single on an audio file
    """

    def __init__(self, text):
        self._text = text

    @property
    def text(self):
        return self._text

    @abstractmethod
    def in_range(self, start_sec: float, end_sec: float):
        pass

    @abstractmethod
    def transform_embed(self, start_sec: float, end_sec: float) -> "Annotation":
        """
        Transform the location of the annotation when the new audio is
        embeded into an audio file between start_sec and end_sec
        """
        pass


class PointAnnotation(Annotation):
    """
    Annotation that has a start and an end in an Audio
    """

    def transform_embed(self, start_sec: float, end_sec: float) -> "Annotation":
        return PointAnnotation(self._position + start_sec, self._text)

    def in_range(self, start_sec: float, end_sec: float):
        return start_sec <= self.position < end_sec

    def __init__(self, position, text):
        super(PointAnnotation, self).__init__(text)
        self._position = position

    @property
    def position(self):
        return self._position


class IntervalAnnotation(Annotation):
    """
    Annotation that represents a point in an Audio
    """

    def transform_embed(self, start_sec: float, end_sec: float):
        return IntervalAnnotation(
            self._start_sec + start_sec, self._end_sec + start_sec, self.text
        )

    def __init__(self, start_sec, end_sec, text):
        super(IntervalAnnotation, self).__init__(text)
        self._start_sec = start_sec
        self._end_sec = end_sec

    def in_range(self, start_sec: float, end_sec: float):
        return self._end_sec < end_sec and self.start >= start_sec

    @property
    def start(self):
        return self._start_sec

    @property
    def end(self):
        return self._end_sec
