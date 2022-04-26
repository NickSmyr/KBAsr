import os
from functools import reduce

from google_kb_z_speaker.main import fix_lines
from utils.loadfile import get_fname_lines, transcriptions
from utils.phonemes import get_swedish_phonemes
from utils.preprocess import preprocess_text


def singular_phonemes(txt: str):
    """
    Creates a list of singular phonemes from the
    output of get_swedish_phonemes
    """
    return txt.replace("_", " ").split()


def singular_phonemes_preprocess(bunches):
    return {
        k: [" ".join(singular_phonemes(s)) for s in v]
        for k, v in bunches.items()
    }


def get_swedish_phonemes_z(bunches, phonemizer, stress_marks=True):
    # Phonemizer creates a dict of words2phonemes for each line, so it
    # so all phonemes should be created with a single call for consistency
    # Impose an order to models
    models = list(bunches.keys())
    num_lines = len(bunches["google"])
    concatenated = reduce(lambda x, y: x + y, [bunches[x] for x in models])
    phoneme_lines = get_swedish_phonemes(
        concatenated,
        phonemizer,
        "./models/stress_lex_mtm.txt",
        include_stress_marks=True,
    )
    return {
        model: phoneme_lines[num_lines * i : num_lines * (i + 1)]
        for model, i in zip(models, range(0, len(models)))
    }


# Speaker


def get_bunches(transcriptions_path, speechType="dialogue"):
    """
    Parses directory of kb-google-z data and generates the bunches object. The bunches object is
    Dict[str,List[str]] where the keys are the models ("google", "correct", "kb") and the values are
    the transcriptions in the file order.

    The transcriptions are preprocessed, removing punctation and  lowercasing on both ground_truth ("correct")
    and the model predicted outputs

    :return: The bunches object
    """
    if speechType == "maggan_dialogue":
        speakers = ["z21", "z20", "z28", "z29"]
    elif speechType == "maggan_read":
        speakers = set(
            [
                x.split(".")[0]
                for x in os.listdir(os.path.join("transcriptions", speechType))
            ]
        )
    else:
        raise Exception(
            "Speech type must be one of [maggan_dialogue, maggan_read]"
        )

    print("====Loading data====")
    print(f"Speech type : {speechType} detected speakers {speakers}")

    models = ["google", "correct", "kb"]
    models2fnameendings = {
        "google": "googleasr",
        "correct": "correct",
        "kb": "kb",
    }
    # Create filenames model -> List[List[str]] (List[str] are the lines from one filename
    fnames = {
        model: [
            f"{transcriptions_path}/{speechType}/{sp}.{models2fnameendings[model]}"
            for sp in speakers
        ]
        for model in models
    }
    bunches = {
        model: [get_fname_lines(fname) for fname in fnames]
        for model, fnames in fnames.items()
    }
    # Create a list [Dict[model,speakerlines] for speaker]
    list_of_model2speaker_lines = [
        {model: bunch[i] for model, bunch in bunches.items()}
        for i in range(len(speakers))
    ]
    [fix_lines(x) for x in list_of_model2speaker_lines]
    # recreate bunches Dict[model, List[speakerLines]]
    bunches = {
        x: [list_of_model2speaker_lines[i][x] for i in range(len(speakers))]
        for x in models
    }
    # Reduce bunches to bunches_reduced Dict[model, speakerLines_aggr]
    bunches = {k: reduce(lambda x, y: x + y, v) for k, v in bunches.items()}
    # Extract the transcriptions
    bunches = {k: transcriptions(v) for k, v in bunches.items()}
    # Preprocess  each transcription
    bunches = {k: [preprocess_text(x) for x in v] for k, v in bunches.items()}
    return bunches
