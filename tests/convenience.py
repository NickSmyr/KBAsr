from uuid import uuid4


def generate_unique_tmp_filename() -> str:
    return "/tmp/" + uuid4().hex


def calculate_num_samples_for_seconds(sample_rate_hz: int, seconds: float) -> int:
    """
    Returns the number of samples to create an audio file with the specified
    duration given the sample rate
    """
    return int(sample_rate_hz * seconds)
