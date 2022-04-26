"""
Python cmd tool to perform breath/silence detection, speaker diarization on large files for conversion into
small utterances for ASR systems. Also provides functionality for creating tasks for crowdworkers and hosting the
tasks locally
"""
import click
import soundfile
import numpy as np


@click.command()
@click.option(
    "--samplerate",
    type=click.INT,
    required=True,
    help="The samplerate of the file",
)
@click.option(
    "--filename",
    type=click.Path(exists=False),
    required=True,
    help="The output directory for files",
)
@click.option(
    "--numsamples",
    type=click.INT,
    required=True,
    help="The number of samples (length of array)",
)
def generate_bogus_wav_file(samplerate, filename, numsamples):
    """
    Generate random noise wav file with the given parameters
    """
    wave = np.random.random((numsamples,))
    with open(filename, "wb") as f:
        soundfile.write(f, wave, samplerate)


if __name__ == "__main__":
    generate_bogus_wav_file()
