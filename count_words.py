#!/usr/bin/env python

import click
import re


word_pattern = re.compile(r"[\w']+")

def words_in_text(s):        
    return word_pattern.findall(s)


class Word():
    def __init__(self, content, frequency):
        self.content = content
        self.frequency = frequency


class Words():
    def __init__(self):
        self.words = []
        self.min = None
        self.exclude = None
        self.condition = None

    def from_file(self,filename):
        pass

    def min(self):
        pass

    def exclude(self):
        pass

    def fetch(self):
        pass

    def display_report(self, format='table'):
        pass


def validate_minimum(ctx, param, value):
    # import ipdb;ipdb.set_trace()
    if value is None:
        return
    if value <= 0:
        raise click.BadParameter('Should be a positive integer value.')
    return value

def validate_exclude_list(ctx, param, value):
    # import ipdb;ipdb.set_trace()
    if value is None:
        return
    excludes = [i.strip() for i in value.strip().split(',')]
    excludes = [i for i in excludes if i != ''] # forgive empty values, extra commas, etc
    if not all(len(words_in_text(exclude)) == 1 for exclude in excludes):
        raise click.BadParameter('Should be a Comma-separated list of words only.')            
    return excludes


@click.command()
@click.argument('filename')
@click.option('--minimum', default=None, type=int, callback=validate_minimum, help='minimum count of words.')
@click.option('--exclude', default=None, type=str, callback=validate_exclude_list, help='Comma-separated list of words to be excluded from the report.')
def count_words(filename, minimum, exclude):
    """ Main click command for counting words in a file. """
    words = Words().from_file(filename)
    if minimum:
        words.min(minimum)
    if exclude:
        words.exclude(exclude)
    words.fetch().display_report()


if __name__ == '__main__':
    count_words()