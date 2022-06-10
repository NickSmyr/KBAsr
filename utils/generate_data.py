import numpy as np
import soundfile


def generate_bogus_wav_file(samplerate, filename, numsamples):
    """
    Generate random noise wav file with the given parameters
    """
    wave = np.random.random((numsamples,))
    with open(filename, "wb") as f:
        soundfile.write(f, wave, samplerate)
