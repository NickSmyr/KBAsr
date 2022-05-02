import pickle

from utils.experiment_helpers import grid, experiment_repeats
from google_kb_z_speaker.experiments import ensemble
from google_kb_z_speaker.preprocessing import get_bunches
import numpy as np


kwargs = {
    "bunches": get_bunches("transcriptions"),
}
args = [
    # Experiment Repeats args
    [ensemble],
    [5],
    [
        "./models/DeepPhon/winhome/Downloads/DeepPhon_to_send/best_model.pt",
        "./models/deep-phonemizer-se.pt",
        "./models/DeepPhon/winhome/Downloads/DeepPhon_to_send/model_step_40k.pt",
    ],
    np.linspace(0.5, 0.7, num=50),
]
experiment = experiment_repeats
res = grid(experiment, *args, stub=False, **kwargs)
with open("output/ensemble_eval", "wb") as f:
    pickle.dump(res, f)
