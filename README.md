# BeerTester

A simple tool to produce randomised, multiple-choice tests based on BJCP 2015 guideline data. The test and answer key are output to separate text files by default, but you can run the test entirely in the terminal as well. Tests have 20 questions, each with four answer options.

The study aid option will create a CSV file with all of the data, instead of the tests. You can use this for doing your homework before taking the test.

Optional arguments when running btest.py:

* -s, --studyaid: creates a study aid instead of the test
* -t, --terminal: runs the quiz in the terminal
* -l, --length: set number of questions, default is 20, max is 30


Stats drawn from the data are: ABV, IBU and SRM. This is good to know if you're studying for BCJP certification, or a Beer Sommelier or Cicerone qualification.