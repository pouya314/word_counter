#!/usr/bin/env python

import click
import re
from collections import Counter
from operator import attrgetter
from prettytable import PrettyTable


def validate_order(func):
    def func_wrapper(_, value):
        if value not in ['desc', 'asc']:
            raise click.BadParameter("Sort order has to be either 'desc' or 'asc'.")
        return func(_, value)
    return func_wrapper


def validate_minimum(func):
    def func_wrapper(_, value):
        if value is None:
            return
        if value <= 0:
            raise click.BadParameter('Should be a positive integer value.')
        return func(_, value)
    return func_wrapper


def validate_exclude_list(func):
    def func_wrapper(_, value):
        if value is None:
            return
        excludes = [i.strip().upper() for i in value.strip().split(',')]
        excludes = [i for i in excludes if i != ''] # forgive empty values, extra commas, etc
        if not all(len(words_in_text(exclude)) == 1 for exclude in excludes):
            raise click.BadParameter('Should be a Comma-separated list of words only.')
        return func(_, excludes)
    return func_wrapper


#word_pattern = re.compile(r"[\w']+")
word_pattern = re.compile(r"\d*[a-zA-Z'][a-zA-Z'\d]*")
def words_in_text(s):        
    return word_pattern.findall(s)


class Word():
    def __init__(self, content, frequency):
        self.content = content
        self.frequency = frequency


class Words():
    def __init__(self):
        self.words = []
        self.fetch_query = 'word for word in self.words'
        self.additional_conditions = []

    def from_file(self,filename):
        #
        # >> TODO(POUYA) << : make relative paths work as well.
        #
        with open(filename, 'r') as f:
            content = f.read().replace('\n', '')
        counts = Counter([detected_word.upper() for detected_word in words_in_text(content)])
        self.words = [Word(word, counts[word]) for word in counts]

    @validate_minimum
    def min(self, min):
        self.additional_conditions.append('word.frequency >= {min}'.format(min=min))

    @validate_exclude_list
    def exclude(self, exclude_list):
        self.additional_conditions.append('word.content not in {exclude_list}'.format(exclude_list=exclude_list))

    @validate_order
    def fetch(self, order='desc'):
        stmt = '[{query} {conditions}]'
        if len(self.additional_conditions) > 0:
            conditions = 'if {}'.format(' and '.join(self.additional_conditions))
            self.additional_conditions = [] #reset
        else:
            conditions = ''
        stmt = stmt.format(query=self.fetch_query, conditions=conditions)
        reverse = True if order == 'desc' else False
        print('Statement => {}'.format(stmt))
        return sorted(eval(stmt), key=attrgetter('frequency'), reverse=reverse)


def print_report(rows):
    """ Pretty print the words and their frequencies in a table """
    report = PrettyTable()
    report.field_names = ["Word", "Frequency"]
    for row in rows:
        report.add_row([row.content, row.frequency])
    print(report)


@click.command()
@click.argument('filename')
@click.option('--minimum', default=None, type=int, 
    help='minimum count of words.')
@click.option('--exclude', default=None, type=str, 
    help="""Comma-separated list of words to be excluded from the report.
    If keyword contains apostrophe character, please escape it. Example: let\\'s.""")
@click.option('--order', default='desc', type=str, 
    help="Sort order for word frequencies. 'desc' or 'asc'. Defaults to 'desc'.")
def count_words(filename, minimum, exclude, order):
    """ Main click command for counting words in a file. """
    words = Words()
    words.from_file(filename)
    if minimum: words.min(minimum)
    if exclude: words.exclude(exclude)
    rows = words.fetch(order)

    print_report(rows)


if __name__ == '__main__':
    count_words()
