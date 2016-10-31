"""
A module to help with mutating strings.  Provides a class with methods that
mutate input strings,

1) insert - insert a character
2) delete - delete a character
3) replace - replace the character at a given index with another
4) transpose - transpose two characters at a given index

In addition, a call to set_random_seed will seed the local random instance
for reproducibility.
"""

import string
import random


DEFAULT_INSERT_ALPHABET = string.ascii_lowercase
DEFAULT_REPLACE_ALPHABET = string.ascii_lowercase


class Mutator():
    """A class to handle string mutations."""

    def __init__(self, insert_alphabet=None, replace_alphabet=None):

        if insert_alphabet is None:
            self.set_insert_alphabet(DEFAULT_INSERT_ALPHABET)
        else:
            self.set_insert_alphabet(insert_alphabet)

        if replace_alphabet is None:
            self.set_replace_alphabet(DEFAULT_REPLACE_ALPHABET)
        else:
            self.set_replace_alphabet(replace_alphabet)

        self.random = random.Random()


    def set_random_seed(self, seed):
        """set the seed for the local random instance"""
        self.random.seed(seed)


    def set_insert_alphabet(self, alphabet):
        """set possible character insertions when `insert_char` is `None`"""
        self.insert_alphabet = alphabet


    def set_replace_alphabet(self, alphabet):
        """set possible character replacements when `replace_char` is `None`"""
        self.replace_alphabet = alphabet


    def insert(self, input_string, insert_char=None, indx=None):
        """insert character `insert_char` into string `input_string`
        at index `indx`.  a random character and index are chosen if
        not passed in."""
        if insert_char is None:
            insert_char = self.random.choice(self.insert_alphabet)
        ll = len(input_string)
        if indx is None:
            indx = self.random.randint(0, ll)
        if indx < 0:
            raise ValueError('index must be >= 0')
        if indx > ll:
            raise ValueError('index must be <= len(input_string)')
        return input_string[:indx] + insert_char + input_string[indx:]


    def delete(self, input_string, indx=None):
        """delete character at index `indx` from string `input_string`.
        a random index is chosen if not passed in."""
        ll = len(input_string)
        if indx is None:
            indx = self.random.randint(0, ll-1)
        if indx < 0:
            raise ValueError('index must be >= 0')
        if indx > ll-1:
            raise ValueError('index must be <= len(input_string)-1')
        return input_string[:indx] + input_string[(indx+1):]


    def replace(self, input_string, replace_char=None, indx=None):
        """replace character at index `indx` in string `input_string` with
        character `replace_char`.  a random character and index are chosen if
        not passed in."""
        if replace_char is None:
            replace_char = self.random.choice(self.replace_alphabet)
        ll = len(input_string)
        if indx is None:
            indx = self.random.randint(0, ll-1)
        if indx < 0:
            raise ValueError('index must be >= 0')
        if indx > ll-1:
            raise ValueError('index must be <= len(input_string)-1')
        return input_string[:indx] + replace_char + input_string[(indx+1):]


    def transpose(self, input_string, indx=None):
        """transpose the characters with indices `indx` and `indx`+1 in string
        `input_string`.  a random index is chosen if not passed in."""
        ll = len(input_string)
        if indx is None:
            indx = self.random.randint(0, ll-2)
        if indx < 0:
            raise ValueError('index must be >= 0')
        if indx > ll-2:
            raise ValueError('index must be <= len(input_string)-2')
        ii = indx
        ff = indx+2
        swapped = input_string[ii:ff][::-1]
        return input_string[:ii] + swapped + input_string[(indx+2):]
