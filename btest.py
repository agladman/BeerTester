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
    """Holds the name, ABV, IBU and SRM of a beer."""

    def __init__(self, beername, ABV, IBU, SRM):
        self.beername = beername
        self.ABV = ABV
        self.IBU = IBU
        self.SRM = SRM


def load_data():
    """Loads beer data, should get data for 92 beer styles. Returns objects in a list."""
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
    """Gathers three wrong answer options and returns them in a list."""
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
    """Constructs a question. Returns a list containing the beer name, the figure on which
        the question is based (ABV, IBU or SRM), the correct answer and three incorrect
        answer options."""
    correct_answer = random.choice([my_beer.ABV, my_beer.IBU, my_beer.SRM])
    answer_options = get_wrong_answer_options(correct_answer, my_beer_list)
    answer_options.append(correct_answer[1])
    random.shuffle(answer_options)
    return [my_beer.beername, correct_answer, answer_options]


def get_key(question):
    """Indicates which option out of A, B, C or D is the correct answer."""
    keys = 'A B C D'.split()
    for i, o in enumerate(question[2]):
        if o == question[1][1]:
            return keys[i]


def ask(qnum, question):
    """Displays the question in the terminal window, then aptures and evaluates the user's answer."""
    time.sleep(1)
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'\n\n\tQ{qnum + 1}: What is the {question[1][0]} of {question[0]}?\n')
    for i in range(4):
        print(f'\t\t{"ABCD"[i]}: {question[2][i]}')
    while True:
        answer = input('\n\tEnter A, B, C, or D: ')
        if answer.upper() in set('ABCD'):
            break
        else:
            print('\n\tInvalid answer.')
    if answer.upper() == get_key(question):
        time.sleep(0.5)
        print('\n\tCorrect!')
        return True
    else:
        time.sleep(0.5)
        print(f'\n\tUh oh. The answer was {question[1][1]}')
        return False


def set_length():
    """Asks the user for the number of questions to ask in the quiz. This must be between 0 and 30."""
    l = input('Enter number of questions to ask: ')
    while True:
        if l.isdigit() and 0 < int(l) <= 30:
            return int(l)
        else:
            print('invalid answer, please enter a number between 0 and 30.')


def build_queue(my_list):
    """Returns a shuffled copy of a list."""
    result = [x for x in my_list]
    random.shuffle(result)
    return result


def main():
    """Runs the script."""
    # set arguments for argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--studyaid", help="creates a study aid instead of the test",
                        action="store_true")
    parser.add_argument("-t", "--terminal", help="runs the quiz in the terminal",
                        action="store_true")
    parser.add_argument("-l", "--length", help="set number of questions, default is 20, max is 30",
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
        queue = build_queue(beers)
        for _ in range(length):
            b = queue.pop(0)
            q = build_question(b, beers)
            questions.append(q)

        # if terminal otion was given, run the quiz in the terminal window
        if args.terminal:
            my_score = 0
            for i, q in enumerate(questions):
                if ask(i, q):
                    my_score += 1
                time.sleep(0.5)
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f'\n\n\n\n\n\t\t\tThe test is over. You scored {my_score}/{length}.\n')
            time.sleep(3.5)
            os.system('cls' if os.name == 'nt' else 'clear')

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
