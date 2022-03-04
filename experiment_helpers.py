from statistics import mean, stdev
from tqdm.auto import tqdm


class ExperimentResult:
    def __init__(self, mean, std):
        self._mean = mean
        self._std = std

    @property
    def mean(self):
        return self._mean

    @property
    def std(self):
        return self._std

    @mean.setter
    def mean(self, value):
        self._mean = value

    @std.setter
    def std(self, value):
        self._std = value

    def __str__(self):
        return str(self.mean) + "±" + str(self.std)


def experiment_repeats(experiment, count: int, *args, **kwargs):
    """
    Performs an experiment. Experiment can be any function with
    any inputs and return a number of numerical outputs.
    :param experiment:  function with
    any inputs and return a Dict[str,float]
    :param count: number of times to run experiment
    :param args: pos args to give to experiment
    :param kwargs: kwargs to give to experiment
    :return:
    """
    res = []
    for _ in tqdm(range(count)):
        res.append(experiment(*args, **kwargs))
    means = {k: mean([dict[k] for dict in res]) for k in res[0]}
    if count == 1:      
        stds = {k: 0 for k in res[0]}
    else:
        stds = {k: stdev([dict[k] for dict in res]) for k in res[0]}
    return {k: ExperimentResult(means[k], stds[k]) for k in res[0]}

def print_experiment_report(experiment_output):
    for k,v in experiment_output.items():
        print(k + ": " + str(v))