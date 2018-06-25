#!/usr/bin/env python

import click
import os
import re
from collections import Counter
from operator import attrgetter
from pathlib import Path
from prettytable import PrettyTable


def validate_order(func):
    def func_wrapper(obj, order):
        if order not in ['desc', 'asc']:
            raise click.BadParameter("Sort order has to be either 'desc' or 'asc'.")
        return func(obj, order)

    return func_wrapper


def validate_filename(func):
    def func_wrapper(obj, filename):
        # try full path
        file = Path(filename)
        if file.is_file():
            return func(obj, filename)
        # try relative path
        file = Path(os.path.join(os.getcwd(), filename))
        if file.is_file():
            return func(obj, filename)
        # both full & relative paths didn't work, so raise an error.
        raise click.BadParameter("filename provided does not exist.")

    return func_wrapper


def validate_minimum(func):
    def func_wrapper(obj, minimum):
        if minimum is None:
            return obj
        if minimum <= 0:
            raise click.BadParameter('Should be a positive integer value.')
        return func(obj, minimum)

    return func_wrapper


def validate_exclude_list(func):
    def func_wrapper(obj, exclude_list):
        if exclude_list is None:
            return obj
        excludes = [i.strip().upper() for i in exclude_list.strip().split(',')]
        excludes = [i for i in excludes if i != '']  # forgive empty values, extra commas, etc
        if len(excludes) == 0:
            return obj
        if not all(len(words_in_text(exclude)) == 1 for exclude in excludes):
            raise click.BadParameter('Should be a Comma-separated list of words only.')
        return func(obj, excludes)

    return func_wrapper


# word_pattern = re.compile(r"[\w']+")
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

    @validate_filename
    def from_file(self, filename):
        with open(filename, 'r') as f:
            content = f.read().replace('\n', '')
        counts = Counter([detected_word.upper() for detected_word in words_in_text(content)])
        self.words = [Word(word, counts[word]) for word in counts]
        return self

    @validate_minimum
    def minimum(self, minimum):
        self.additional_conditions.append('word.frequency >= {minimum}'.format(minimum=minimum))
        return self

    @validate_exclude_list
    def exclude(self, exclude_list):
        self.additional_conditions.append('word.content not in {exclude_list}'.format(exclude_list=exclude_list))
        return self

    @validate_order
    def fetch(self, order='desc'):
        stmt = '[{query} {conditions}]'
        if len(self.additional_conditions) > 0:
            conditions = 'if {}'.format(' and '.join(self.additional_conditions))
            self.additional_conditions = []  # reset
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
    rows = Words().from_file(filename).minimum(minimum).exclude(exclude).fetch(order)
    print_report(rows)


if __name__ == '__main__':
    count_words()
