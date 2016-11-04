"""
A module to help create fake datasets for tranining/testing record linkage
models.
"""

import random
from collections import defaultdict
import pandas
from pandas import np
from faker import Faker
import mutator


DEFAULT_MUTA_SEED = 193
DEFAULT_FAKE_SEED = 73824
DEFAULT_RECO_SEED = 45632
COLS = ['first_name', 'last_name', 'zipcode']

# the set of possible mutations that will be applied to the columns
MUTATION_SCHEME = {
    'first_name': ['transpose', 'insert', 'replace', 'delete'],
    'last_name': ['transpose', 'insert', 'replace', 'delete'],
    'zipcode': ['transpose'],
}


class RecordMocker():
    """A class to generate mock records."""

    def __init__(
            self,
            n_people,
            reco_seed=DEFAULT_RECO_SEED,
            muta_seed=DEFAULT_MUTA_SEED,
            fake_seed=DEFAULT_FAKE_SEED):

        """Initialize with the number of people to put in the base records.
        Provodes variables for random seeds to be passed to,
          1) the random instance used to choose columns in this class
          2) the random instance used in the mutator module
          3) the random instance used in the faker module
        """

        # initialize mutator class
        self.muta = mutator.Mutator(seed=muta_seed)

        # initialize faker
        self.fake = Faker()
        self.fake.seed(fake_seed)

        # initialize local random
        self.random = random.Random()
        self.random.seed(reco_seed)

        # initialize empty DataFrame
        df_base = pandas.DataFrame(
            np.empty((n_people, len(COLS))) * np.nan,
            columns=COLS)

        # add unique person ID
        df_base['id'] = np.arange(n_people)

        # generate fake data
        for i in range(n_people):
            df_base.loc[i, 'first_name'] = self.fake.first_name()
            df_base.loc[i, 'last_name'] = self.fake.last_name()
            df_base.loc[i, 'zipcode'] = self.fake.zipcode()

        self.n_people = n_people
        self.df_base = df_base

        # initialize index trackers
        self.indx_min = self.df_base.index.min()
        self.indx_max = self.df_base.index.max()

        # initialize mutation history tracker
        self.history = defaultdict(list)


    def sample_base(self, frac=1.0, replace=False):
        """Sample rows from the base records. Increments index tracker."""

        # sample from base records
        df = self.df_base.sample(replace=replace, frac=frac)
        n_new_rows = df.shape[0]

        # reindex
        self.indx_min = self.indx_max + 1
        self.indx_max = self.indx_min + n_new_rows - 1
        df.index = range(self.indx_min, self.indx_max + 1)

        return df


    def gen_add_nan(self, df, columns=None):
        """Generate a block of records where each row has a random column
        selected from the list `columns` set to None. Excludes `id` column."""
        if columns is None:
            columns = df.columns
        columns = [col for col in columns if col != 'id']
        for ii in df.index:
            col = self.random.choice(columns)
            df.loc[ii, col] = None
            self.history[ii].append(('add_nan', col))
        return df


    def gen_swap_columns(self, df, col1, col2):
        """Generate a block of records with two column values swapped."""
        df[[col1, col2]] = df[[col2, col1]].values
        for ii in df.index:
            self.history[ii].append(('swap_columns', (col1, col2)))
        return df


    def gen_combine_columns(
            self, df, col1, col2, target_col=None, null_non_target=True):
        """Generate a block of records with two columns combined.
        Combine values from col1 and col2 into target_col (must be either col1
        or col2 and defaults to col2), Optionally null out whichever column is
        not the target col."""
        if target_col is None:
            target_col = col2
        if target_col not in [col1, col2]:
            raise ValueError('target col must be either col1 or col2')
        null_col = col1 if target_col == col2 else col2
        df[target_col] = df[col1] + df[col2]
        if null_non_target:
            df[null_col] = None
        for ii in df.index:
            self.history[ii].append(
                ('combine_columns', (col1, col2, target_col, null_col)))
        return df


    def gen_point_mutations(self, df, n_sweeps=1, columns=None):
        """During each sweep, a single point mutation is performed on
        each row in a random column chosen from `columns`"""
        if columns is None:
            columns = df.columns
        columns = [col for col in columns if col != 'id']
        for i_sweep in range(n_sweeps):
            for ii in df.index:
                col = self.random.choice(columns)
                muta_func_name = self.random.choice(MUTATION_SCHEME[col])
                muta_func = getattr(self.muta, muta_func_name)
                df.loc[ii, col] = muta_func(df.loc[ii, col])
                self.history[ii].append((muta_func_name, col))
        return df

if __name__ == '__main__':

    remo = RecordMocker(5)

    # generate a sample and compose swap columns with add nan
    df1 = remo.sample_base()
    df1 = remo.gen_swap_columns(df1, 'first_name', 'last_name')
    df1 = remo.gen_add_nan(df1)

    # generate a sample and combine columns
    df2 = remo.sample_base()
    df2 = remo.gen_combine_columns(df2, 'first_name', 'last_name')

    # generate a sample and add point mutations
    df3 = remo.sample_base()
    df3 = remo.gen_point_mutations(df3, n_sweeps=2)

    # combine all
    df_sample = pandas.concat([remo.df_base, df1, df2, df3])
