# coding:utf-8
import numpy as np
import os
import re
import pandas as pd
from pandas import Series, DataFrame
from sklearn.model_selection import train_test_split
# from src.data_utils import full_to_half

def process_csv(csv_filename):
    df = pd.read_csv(csv_filename, names=['session_id', 'session', 'round_id', 'ner_input', 'id_input', 'ner_label', 'id_label'])

    # fout_test_seq_in = open('test.seq.in', 'w+')
    # fout_test_seq_out = open('test.seq.out', 'w+')
    # print df['id_label'][1:][1:8]
    df['id_label'][1:].to_csv('test.label', header=None, index=None)
    df['ner_label'][1:].to_csv('test.ner.label', header=None, index=None)

def lower_id_label(label_filename):
    lines = []
    with open(label_filename, "r") as f_id_label:
        for line in f_id_label.readlines():
            line = line.lower()
            lines.append(line)
    # lines = set(lines)
    with open(label_filename, "w") as f_id_label:
        f_id_label.write("".join(lines))
'''
def full_to_half(s):
    """
    Convert full-width character to half-width one 
    """
    n = []
    semicolon = "："
    semicolon_half = ":"
    comma = "，"
    comma_half = ","
    try:
        s = s.replace(semicolon, semicolon_half)
        s = s.replace(comma, comma_half)
    except:
        print "did not match comma and semicolon"
    for char in s:
        num = ord(char)
        if num == 0x3000:
            num = 32
        elif 0xFF01 <= num <= 0xFF5E:
            num -= 0xfee0
        char = chr(num)
        n.append(char)
    return ''.join(n)
'''
def parse_ner_sequence(sequence):
    for sentence in sequence.strip().split(u"。"):
        sentence = sentence.lower()
        # sentence = sentence.rstrip().lstrip()
        if sentence == "": continue
        for ne_segment in re.split(r"{|}", sentence):
            if ":" in ne_segment:
                ne_tok = ne_segment.split(":", 1)
                for i, word in enumerate(filter(None, re.split("(\d+|[a-zA-z]+)", ne_tok[-1]))):
                    if re.match(r"\w+", word):
                        tag = "B-%s" % ne_tok[0].upper() if i == 0 else "I-%s" % ne_tok[0].upper()
                        yield (word, tag)
                    else:
                        for k, char in enumerate(word):
                            tag = "B-%s" % ne_tok[0].upper() if i + k == 0 else "I-%s" % ne_tok[0].upper()
                            yield (char, tag)
            else:
                for word in filter(None, re.split("(\d+|[a-zA-z]+)", ne_segment)):
                    if re.match(r"\w+", word):
                        yield (word, "O")
                    else:
                        for char in word:
                            yield (char, "O")

def process_ner_label(ner_filename):
    f_ner_label = open(ner_filename, "r")
    fout_test_seq_in = open("test.seq.in", "w+")
    fout_test_seq_out = open("test.seq.out", "w+")

    for line in f_ner_label.readlines():
        line_seq_in = []
        line_seq_out = []
        for tup in parse_ner_sequence(line.decode('utf-8')):
            # fout.write("%s\t%s\n" % (tup[0].encode("utf-8"), tup[1].encode("utf-8")))
            line_seq_in.append(tup[0].encode("utf-8"))
            line_seq_out.append(tup[1].encode("utf-8"))

        # line_seq_in = [x.strip() for x in line_seq_in]
        # line_seq_out = [x.strip() for x in line_seq_out]

        fout_test_seq_in.write(" ".join(line_seq_in))#@todo check the space problem here.
        fout_test_seq_out.write(" ".join(line_seq_out))
        fout_test_seq_in.write("\n")
        fout_test_seq_out.write("\n")

if __name__ == "__main__":
    csv_filename = "session_round.csv"
    process_csv(csv_filename)
    lower_id_label("test.label")

    ner_filename = "test.ner.label"
    process_ner_label(ner_filename)

    #split dev, test, train dataset
    if not os.path.exists("HER/train"):
        os.makedirs("HER/train")
    if not os.path.exists("HER/test"):
        os.makedirs("HER/test")
    if not os.path.exists("HER/valid"):
        os.makedirs("HER/valid")

    # split label into train, dev, test
    f_lines = open("test.label", 'r').read()[:-2].split('\n')
    for line in f_lines:
        if line == '\n':
            f_lines.remove(line)
    X_train, X_test = train_test_split(f_lines, test_size=0.1, random_state=10)
    X_train, X_dev = train_test_split(X_train, test_size=0.11, random_state=10)

    print "Writing label file..."
    with open('HER/train/train.label', 'w+') as f_train:
        f_train.write('\n'.join(X_train))
        f_train.write('\n')

    with open('HER/test/test.label', 'w+') as f_test:
        f_test.write('\n'.join(X_test))
        f_test.write('\n')

    with open('HER/valid/valid.label', 'w+') as f_dev:
        f_dev.write('\n'.join(X_dev))
        f_dev.write('\n')

    # split seq.in into train, dev, test
    f_lines = open("test.seq.in", 'r').read()[:-2].split('\n')
    X_train, X_test = train_test_split(f_lines, test_size=0.1, random_state=10)
    X_train, X_dev = train_test_split(X_train, test_size=0.11, random_state=10)

    print "Writing seq.in file..."
    with open('HER/train/train.seq.in', 'w+') as f_train:
        f_train.write('\n'.join(X_train))
        f_train.write('\n')

    with open('HER/test/test.seq.in', 'w+') as f_test:
        f_test.write('\n'.join(X_test))
        f_test.write('\n')

    with open('HER/valid/valid.seq.in', 'w+') as f_dev:
        f_dev.write('\n'.join(X_dev))
        f_dev.write('\n')

    # split seq.out into train, dev, test
    f_lines = open("test.seq.out", 'r').read()[:-2].split('\n') #todo line.strip()
    for line in f_lines:
        if line == '\n':
            f_lines.remove(line)
    X_train, X_test = train_test_split(f_lines, test_size=0.1, random_state=10)
    X_train, X_dev = train_test_split(X_train, test_size=0.11, random_state=10)

    print "Writing seq.out file..."
    with open('HER/train/train.seq.out', 'w+') as f_train:
        f_train.write('\n'.join(X_train))
        f_train.write('\n')

    with open('HER/test/test.seq.out', 'w+') as f_test:
        f_test.write('\n'.join(X_test))
        f_test.write('\n')

    with open('HER/valid/valid.seq.out', 'w+') as f_dev:
        f_dev.write('\n'.join(X_dev))
        f_dev.write('\n')
