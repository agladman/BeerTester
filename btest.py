#!/usr/bin/env python3

"""BeerTester: produces randomised multiple choice tests, based on BJCP data, to test
    knowledge of the ABVs, IBUs, and SRMs of individual beer styles."""

import argparse
import csv
from datetime import datetime
import json
import os
import random
import time
import uuid


class Beer(object):

    def __init__(self, beername, ABV, IBU, SRM):
        self.beername = beername
        self.ABV = ABV
        self.IBU = IBU
        self.SRM = SRM


def load_data():
    # load beer data into list of objects, should get data for 92 beer styles
    data = json.load(open('BJCP2015.json'))
    beer_objects = []
    for beer in data['beers']:
        if beer['number'] < 27:     # exclude weird categories at the end of the data
            for subcat in beer['subcategories']:
                beername = subcat['name']
                abv = ['ABV', subcat['guidelines']['vitalStatistics']['abv']]
                ibu = ['IBU', subcat['guidelines']['vitalStatistics']['ibu']]
                srm = ['SRM', subcat['guidelines']['vitalStatistics']['srm']]
                beer_objects.append(Beer(beername, abv, ibu, srm))
    return beer_objects


def get_wrong_answer_options(my_correct_answer, my_list):
    options = []
    while len(options) < 3:
        c = random.choice(my_list)
        if my_correct_answer[0] == 'ABV':
            o = c.ABV[1]
        elif my_correct_answer[0] == 'IBU':
            o = c.IBU[1]
        else:
            o = c.SRM[1]
        if o != my_correct_answer[1] and o not in options:
            options.append(o)
    return options


def build_question(my_beer, my_beer_list):
    correct_answer = random.choice([my_beer.ABV, my_beer.IBU, my_beer.SRM])
    answer_options = get_wrong_answer_options(correct_answer, my_beer_list)
    answer_options.append(correct_answer[1])
    random.shuffle(answer_options)
    return [my_beer.beername, correct_answer, answer_options]


def show_question(my_list):
    time.sleep(1)
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'\n\nWhat is the {my_list[1][0]} of {my_list[0]}?\n')
    for i in range(4):
        print(f'\t{"ABCD"[i]}: {my_list[2][i]}')


def get_key(question):
    keys = 'A B C D'.split()
    for i, o in enumerate(question[2]):
        if o == question[1][1]:
            return keys[i]


def ask(question):
    show_question(question)
    while True:
        answer = input('\nEnter A, B, C, or D: ')
        if answer.upper() in set('ABCD'):
            break
        else:
            print('\nInvalid answer.')
    if answer.upper() == get_key(question):
        time.sleep(0.5)
        print('\nCorrect!')
        return True
    else:
        time.sleep(0.5)
        print(f'\nUh oh. The answer was {question[1][1]}')
        return False


def score(question, my_score):
    if ask(question):
        my_score += 1
    return my_score


def go():
    """quick n durty checker func."""
    beers = load_data()
    b = random.choice(beers)
    q = build_question(b, beers)
    return beers, b, q


def set_length():
    l = input('Enter number of questions to ask: ')
    while True:
        if l.isdigit() and 0 < int(l) <= 30:
            return int(l)
        else:
            print('invalid answer, please enter a number between 0 and 30.')


def main():
    # set arguments for argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--studyaid", help="creates a study aid instead of the test",
                        action="store_true")
    parser.add_argument("-t", "--terminal", help="runs the quiz in the terminal",
                        action="store_true")
    parser.add_argument("-l", "--length", help="set number of question, default is 20, max is 30",
                        action="store_true")
    args = parser.parse_args()

    # load in the beer data
    beers = load_data()

    # now we have the beer data, output to a study aid if requested
    if args.studyaid:
        """outputs to a CSV file, a bit hacky with the IBU and SRM options
            but it stops excel from automatically turning these columns into dates."""
        with open(f'{desktop}/{test_id}_study_aid.csv', 'w', newline='') as csvfile:
            mywriter = csv.writer(csvfile, dialect='excel')
            mywriter.writerow(['NAME', 'ABV', 'IBU', 'SRM'])
            for b in beers:
                mywriter.writerow([b.beername, b.ABV[1], f'="{b.IBU[1]}"', f'="{b.SRM[1]}"'])

    # if study aid is not requested move on to the test
    else:
        if args.length:
            length = set_length()
        else:
            length = 20

        # compile questions
        questions = []
        for x in range(length):
            b = random.choice(beers)
            q = build_question(b, beers)
            questions.append(q)

        # if terminal otion was given, run the quiz in the terminal window
        if args.terminal:
            my_score = 0
            for q in questions:
                my_score = score(q, my_score)
                time.sleep(0.5)
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f'\n\nThe test is over. Your score is {my_score}')

        # if the terminal option was not given output questions and answer key to text files
        else:
            test_id = uuid.uuid4().hex
            test_time = '{:%Y-%m-%d %H:%M}'.format(datetime.now())
            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
            with open(f'{desktop}/{test_id}.txt', 'w') as f:
                with open(f'{desktop}/{test_id}_answers.txt', 'w') as g:
                    f.write(f'Test ID {test_id}, {test_time}\n\n')
                    g.write(f'Test ID {test_id}, {test_time}\n\n')
                    for i, q in enumerate(questions):
                        f.write(f'{i + 1}: What is the {q[1][0]} of {q[0]}?\n')
                        for j in range(4):
                            f.write(f'{"ABCD"[j]}: {q[2][j]}\n')
                        f.write('\n')
                        g.write(f'{i + 1}: {q[1][1]}\n')
                    f.write('\n--END--')


if __name__ == "__main__":
    main()
