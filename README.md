The task:
---------

Write a python script that takes as an argument a filename of a text file to process.
The python script needs to load this file and parse it's contents.
It needs to print out to standard output a report of word frequencies, with the most frequent word at the top of the output, followed by the second most frequent word and so on.

Features:

- Configuration to have a minimum count of words so we can exclude say all words not occurring more than 100 times from the script output.
- The ability to use a list (either hardcoded or preferable loaded from another file) of "stop words" (i.e. "a","the","then","them") to exclude from the analysis and report.
- Error handling if the file is not present, or cannot be opened, showing a sensible error message back to the user.

Usage:
```
python count_words.py --help

python count_words.py input.txt --minimum=4 --exclude=a,the,an --order=asc
```

