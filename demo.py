import time
import random
from collections import defaultdict
import pandas
from pandas import np
from faker import Faker
import mutator


MUTE_SEED = 193
FAKE_SEED = 73824
N_PEOPLE = 10
COLS = ['first_name', 'last_name', 'zipcode']


def create_base(n_people=N_PEOPLE):
    """create initial records"""

    # initialize as empty
    df_base = pandas.DataFrame(
        np.empty((n_people, len(COLS))) * np.nan,
        columns=COLS)

    # add unique person ID
    df_base['id'] = np.arange(n_people)

    # generate fake data
    for i in range(n_people):
        df_base.loc[i, 'first_name'] = fake.first_name()
        df_base.loc[i, 'last_name'] = fake.last_name()
        df_base.loc[i, 'zipcode'] = fake.zipcode()

    return df_base


# create DataFrame with mutated records
#=================================================

def add_nan(df_in, columns=None):
    """create missing data for a randomly selected column in each row."""
    df = df_in.copy()
    if columns is None:
        columns = df.columns
    columns = [col for col in columns if col != 'id']
    for ii in df.index:
        col = random.choice(columns)
        df.loc[ii, col] = None
    return df


def swap_columns(df_in, col1, col2):
    """swap values given a pair of columns."""
    df = df_in.copy()
    df[[col1, col2]] = df[[col2, col1]].values
    return df


def single_room_columns(df_in, col1, col2, target_col):
    """combine values from col1 and col2 into target_col (must be either col1
    or col2), null out whichever column is not the target col."""
    if target_col not in [col1, col2]:
        raise ValueError('target col must be either col1 or col2')
    df = df_in.copy()
    df[target_col] = df[col1] + df[col2]
    null_col = col1 if target_col == col2 else col2
    df[null_col] = None
    return df


def sample_base(df_base, indx_min, indx_max, frac):
    """sample rows from df_base and update indices in sampled df"""

    # choose random rows from base
    df = df_base.sample(replace=False, frac=frac)
    n_new_rows = df.shape[0]

    # reindex
    indx_min = indx_max + 1
    indx_max = indx_min + n_new_rows - 1
    df.index = range(indx_min, indx_max + 1)

    return df, indx_min, indx_max



if __name__ == '__main__':

    # initialize
    #====================================================

    # initialize class instances
    muta = mutator.Mutator()
    muta.set_random_seed(MUTE_SEED)
    fake = Faker()
    fake.seed(FAKE_SEED)

    # create base data
    df_base = create_base()

    # this will become the final sample
    df_sample = df_base.copy()

    # initialize index trackers for history
    indx_min = df_base.index.min()
    indx_max = df_base.index.max()

    # keep a record of mutations and alterations for each row
    history = defaultdict(list)


    # do some multi-column mutations
    #====================================================

    # sample base and null some data out
    df_nulls, indx_min, indx_max = sample_base(
        df_base, indx_min, indx_max, frac=0.5)
    df_nulls = add_nan(df_nulls)
    for ii in df_nulls.index:
        history[ii].append(('add_nan', 'random'))
    df_sample = pandas.concat([df_sample, df_nulls])

    # sample base and swap first name and last name
    df_name_swap, indx_min, indx_max = sample_base(
        df_base, indx_min, indx_max, frac=0.5)
    df_name_swap = swap_columns(
        df_name_swap, 'first_name', 'last_name')
    for ii in df_name_swap.index:
        history[ii].append(('swap_cols', ('first_name', 'last_name')))
    df_sample = pandas.concat([df_sample, df_name_swap])

    # sample base and single room first and last name
    df_single_room, indx_min, indx_max = sample_base(
        df_base, indx_min, indx_max, frac=0.5)
    df_single_room = single_room_columns(
        df_single_room, 'first_name', 'last_name', 'last_name')
    for ii in df_single_room.index:
        history[ii].append(('single_room', ('first_name', 'last_name')))
    df_sample = pandas.concat([df_sample, df_single_room])



    # do some single column mutations
    # we will do a number of sweeps. in each sweep, a fraction of the
    # original data is sampled.  the data in each sweep is mutated away
    # from the base data during a number of generations.  during each
    # generation a random column is chosen and a random mutation is added.
    #====================================================

    # the set of possible mutations that will be applied to the columns
    mutation_scheme = {
        'first_name': [muta.transpose, muta.insert, muta.replace, muta.delete],
        'last_name': [muta.transpose, muta.insert, muta.replace, muta.delete],
        'zipcode': [muta.transpose],
    }

    # number of sweeps
    n_sweeps = 2

    # fraction of rows to choose from df_base each sweep
    base_frac = 0.5

    # number of mutation generations in each sweep
    n_generations = 4

    # what fraction of rows mutate in each generation
    gen_frac = 0.3

    # go thourgh sweeps
    for i_sweep in range(n_sweeps):

        # sample from base
        df, indx_min, indx_max = sample_base(
            df_base, indx_min, indx_max, frac=base_frac)

        # for each "generation" do some mutations
        for i_generation in range(n_generations):

            # choose rows to mutate
            df_to_muta = df.sample(replace=False, frac=gen_frac)

            # choose a column at random
            col = random.choice(COLS)

            # choose a function at random
            muta_func = random.choice(mutation_scheme[col])

            # record history
            for ii in df_to_muta.index:
                history[ii].append((muta_func.__name__, col))

            # do the mutation
            muta_col = df_to_muta[col].apply(muta_func)

            # put into df
            df.loc[df_to_muta.index, col] = muta_col

        # add into sample data frame
        df_sample = pandas.concat([df_sample, df])
