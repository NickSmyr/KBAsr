import codecs
import os
import shutil

import sys
print(sys.path)
from jiwer import wer
from tqdm import tqdm

from google_kb_z_speaker.experiments import get_ensemble_output, google_kb_wer, \
    ensemble
from google_kb_z_speaker.preprocessing import get_bunches
from utils.main import transcribe_directory_of_wav_files
from utils.phonemes import read_phoneme_dict

# Script params
dataset = "maggan_dialogue" # maggan_read or maggan_dialogue


def convert_iso_to_utf(sourceFileName):
    BLOCKSIZE = 1048576  # or some other, desired size in bytes
    with codecs.open(sourceFileName, "r", "ISO-8859-1") as sourceFile:
        with codecs.open(sourceFileName + ".converted", "w", "utf-8") as targetFile:
            while True:
                contents = sourceFile.read(BLOCKSIZE)
                if not contents:
                    break
                targetFile.write(contents)
    shutil.move(sourceFileName + ".converted", sourceFileName)


if dataset == "maggan_read":
    speech_dir = "data/maggan_read"
else:
    speech_dir = "data/maggan_dialogue"

speech_type = os.path.basename(speech_dir)

# Clean previous output
shutil.rmtree(os.path.join("output", speech_type), ignore_errors=True)
shutil.rmtree(os.path.join("transcriptions", speech_type), ignore_errors=True)
os.makedirs(os.path.join("output", speech_type))
os.makedirs(os.path.join("transcriptions", speech_type))

speaker_paths = [ os.path.join(speech_dir, x)
                 for x in os.listdir(speech_dir) if x.startswith("z")]

# Copy files from /data/ to output dir and convert to UTF8
for sp in speaker_paths:
    for x in os.listdir(sp):
        if "google" in x:
            shutil.copy(os.path.join(sp,x), os.path.join("output",speech_type,x))
            if speech_type == "maggan_dialogue":
                convert_iso_to_utf( os.path.join("output",speech_type,x))
        if "correct" in x:
            shutil.copy(os.path.join(sp,x), os.path.join("output",speech_type,x))
            convert_iso_to_utf( os.path.join("output",speech_type,x))

iso_speakers = ["z16", "z17", "z18", "z22", "z23", "z25", "z26", "z3", "z5", "z6", "z7"]

# Some maggan read files are iso-8859 # Not idempotent
if speech_type == "maggan_read":
    for filename in os.listdir(os.path.join("output", speech_type)):
        for speaker in iso_speakers:
            if speaker in filename and "google" in filename:
                print(f"Converting {speaker} in filename {filename}")
                convert_iso_to_utf( os.path.join("output",speech_type,filename))



models = [
    "KBLab/wav2vec2-large-voxrex-swedish"
        "birgermoell/lm-swedish"
]

for d in tqdm(speaker_paths):
    speaker_name = os.path.basename(d)
    output_path = os.path.join("output",speech_type, speaker_name + ".kb")
    print(f"Transcribing {speaker_name} with output path {output_path}")
    transcribe_directory_of_wav_files(d, output_path, model_type="KBLab/wav2vec2-large-voxrex-swedish")

from distutils.dir_util import copy_tree
copy_tree(f"./output/{speech_type}", f"./transcriptions/{speech_type}")


# Get ensemble wer only on non agreement between kb and google
def ensemble_wer_on_non_agreement(bunches, phonemizer, ratio_threshold, use_phonemizer):
    bunch_list = [{k: bunches[k][i] for k in bunches} for i in
                  range(len([x for x in bunches.values()][0]))]
    # Filter on non agreement
    bunch_list = [x for x in bunch_list if x["google"] != x["kb"]]
    # get ensemble outputs
    ensemble_outputs = [
        get_ensemble_output(bunch, phonemizer, ratio_threshold, use_phonemizer) for
        bunch in bunch_list]
    # Recreate bunches
    bunches = {k: [x[k] for x in bunch_list] for k in bunch_list[0]}

    return {**google_kb_wer(bunches),
            "ensemble_wer": wer(bunches["correct"], ensemble_outputs)}


bunches = get_bunches("transcriptions", speechType=dataset)

res = ensemble_wer_on_non_agreement(bunches, None, 0.6, False)

print(res)
