"""
Python cmd tool to perform breath/silence detection, speaker diarization on large files for conversion into
small utterances for ASR systems. Also provides functionality for creating tasks for crowdworkers and hosting the
tasks locally
"""
import click
import os
from os.path import basename, join
from praatio import tgio
# Disable TF logging for now TODO
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from breath_detection.split_on_breaths_and_silences import split_on_breaths_and_silences
BREATH_DETECTION_MODEL_PATH = "./breath_detection/models/modelMix4.h5"

@click.command()
@click.option('--input-wav', type=click.Path(exists=True), required=True,
              help="The filename to split on breaths and silences")
@click.option('--output-dir', required=True,
              help="The output directory for files")
def split(input_wav, output_dir):
    """
    Split files according to breaths and silences. For each input file
    A directory is created in the form <filename>.d and the splitted
    utterance files are placed inside in the format file_<x>.wav.

    This command is mainly for processing large files with long sound recordings
    and it can process about 1GB of data per 16 minutes. However significant
    improvements can be achieved by multi core processors due to parallelization.
    On large files a progress bar is output showing the progress in MBytes

    Examples:\n
        python -m pipeline --input-wav mywavfile --output-dir mydir
    """
    split_output_dir = join(output_dir, "tmp")
    split_on_breaths_and_silences(input_wav, split_output_dir, BREATH_DETECTION_MODEL_PATH)
    tg = tgio.openTextgrid(join(split_output_dir, "C" + basename(input_wav) + ".TextGrid"))
    intervals = tg.tierDict["annot"].entryList
    print("Number of labels: ", set([x.label for x in intervals]))
    print("Number of speaking intervals ", len([x.label for x in intervals if x.label == "sp"]))
    print("Total number of intervals ", len(intervals))
    utterance_lengths = [x.end - x.start for x in intervals if x.label == "b"]
    import matplotlib.pyplot as plt
    plt.hist(utterance_lengths)




if __name__ == '__main__':
    split()