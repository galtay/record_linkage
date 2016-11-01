import time
import random
import pandas
from pandas import np

import record_mocker

MUTA_SEED = 193
FAKE_SEED = 73824
REMO_SEED = 998765

n_people = 6
remo = record_mocker.RecordMocker(
    n_people, remo_seed=REMO_SEED, muta_seed=MUTA_SEED, fake_seed=FAKE_SEED)
