#!/usr/bin/env python3

"""BeerTester: produces randomised multiple choice tests, based on BJCP data, to test
    knowledge of the ABVs, IBUs, and SRMs of individual beer styles."""

import argparse
from datetime import datetime
import json
import os
import random
import uuid


class Beer(object):
    beername = ''
    ABV = None
    IBU = None
    SRM = None


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


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--studyaid", help="creates a study aid to accompany the test",
                    action="store_true")
args = parser.parse_args()
test_id = uuid.uuid4().hex
test_time = '{:%Y-%m-%d %H:%M}'.format(datetime.now())
desktop = os.path.join(os.path.expanduser('~'), 'Desktop')

# load beer data into list of objects, should get data for 92 beer styles
data = json.load(open('BJCP2015.json'))
beers = []
for beer in data['beers']:
    if beer['number'] < 27:     # exclude weird categories at the end of the data
        for subcat in beer['subcategories']:
            this_beer = Beer()
            this_beer.beername = subcat['name']
            this_beer.ABV = ['ABV', subcat['guidelines']['vitalStatistics']['abv']]
            this_beer.IBU = ['IBU', subcat['guidelines']['vitalStatistics']['ibu']]
            this_beer.SRM = ['SRM', subcat['guidelines']['vitalStatistics']['srm']]
            beers.append(this_beer)

# now we have the beer data, output to a study aid if requested
if args.studyaid:
    with open(f'{desktop}/{test_id}_study_aid.txt', 'w') as s:
        s.write(f'Test ID {test_id}, {test_time}\n\n')
        for b in beers:
            s.write(f'{b.beername}:\n')
            s.write(f'\t{b.ABV[0]}: {b.ABV[1]}\n')
            s.write(f'\t{b.IBU[0]}: {b.IBU[1]}\n')
            s.write(f'\t{b.SRM[0]}: {b.SRM[1]}\n\n')

# compile questions
questions = []
for x in range(20):
    b = random.choice(beers)
    correct_answer = random.choice([b.ABV, b.IBU, b.SRM])
    answer_options = get_wrong_answer_options(correct_answer, beers)
    answer_options.append(correct_answer[1])
    random.shuffle(answer_options)
    questions.append([b.beername, correct_answer, answer_options])

# output questions and answer key to text files
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
