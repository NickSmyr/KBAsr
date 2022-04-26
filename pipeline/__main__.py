"""Python cmd tool to perform breath/silence detection, speaker diarization
on large files for conversion into small utterances for ASR systems. Also
provides functionality for creating tasks for crowdworkers and hosting the
tasks locally """
import click
import os
from os.path import basename, join
from praatio import tgio
from pydub import AudioSegment

# Disable TF logging for now TODO
from pipeline.speaker_diarization.separate_speakers import (
    create_speaker_files_from_audio_path_old,
)
from pipeline.breath_detection.split_on_breaths_and_silences import (
    split_on_breaths_and_silences,
)

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

BREATH_DETECTION_MODEL_PATH = "./models/modelMix4.h5"


@click.group()
def main():
    pass


@main.command()
@click.option(
    "--input-wav",
    type=click.Path(exists=True),
    required=True,
    help="The filename to split on breaths and silences",
)
@click.option(
    "--output-dir", required=True, help="The output directory for files"
)
@click.option("--model-path", help="The trained model to use")
def split(input_wav, output_dir, model_path):
    """
    Split files according to breaths and silences. For each input file
    A directory is created in the form <filename>.d and the splitted
    utterance files are placed inside in the format file_<x>.wav.

    Utterances are segments of speech that are

    This command is mainly for processing large files with long sound
    recordings and it can process about 1GB of data per 16 minutes. However
    significant improvements can be achieved by multi core processors due to
    parallelization. On large files a progress bar is output showing the
    progress in MBytes

    Examples:\n
        python -m pipeline --input-wav mywavfile --output-dir mydir

    Some files may end up wrongly containing breaths or silences since this
     algorithm
    is based on a statistical model
    """
    if model_path is None:
        model_path = BREATH_DETECTION_MODEL_PATH

    split_output_dir = join(output_dir, "tmp")
    try:
        split_on_breaths_and_silences(input_wav, split_output_dir, model_path)
    except Exception as e:
        raise Exception(
            "Failed to split on breaths. This most likely means no breaths "
            "were detected from the input file"
        ) from e
    tg = tgio.openTextgrid(
        join(split_output_dir, "C" + basename(input_wav) + ".TextGrid")
    )
    intervals = tg.tierDict["annot"].entryList
    speakingIntervals = [x for x in intervals if x.label == "sp"]
    song = AudioSegment.from_wav(input_wav)
    for i, interval in enumerate(speakingIntervals):
        utterance = song[interval.start * 1000 : interval.end * 1000]
        utterance.export(join(output_dir, f"file_{i}.wav"), format="wav")
    print(f"Generated {len(intervals)} utterances in directory {output_dir}")
    # Clean up files generated from breath detection
    # shutil.rmtree(split_output_dir)


@main.command()
@click.option(
    "--input-wav",
    type=click.Path(exists=True),
    required=True,
    help="The filename to split on breaths and silences",
)
@click.option(
    "--output-dir", required=True, help="The output directory for files"
)
def diarize(input_wav, output_dir):
    """
    Split an audio file containing two speakers into two separate audio files
    for each speaker.
    """
    create_speaker_files_from_audio_path_old(input_wav)


if __name__ == "__main__":
    main()
