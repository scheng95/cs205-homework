from pyspark import SparkContext
from collections import Counter
import numpy as np
import random

# constants
NUM_PHRASES = 10
WORDS_PER_PHRASE = 20

sc = SparkContext("local", "Shakespeare")

shakes = sc.textFile("Shakespeare.txt")

shakes_words = shakes.map(lambda l: l.split(" ")).flatMap(lambda l: l)
shakes_words = shakes_words.filter(lambda w: not w.isdigit())
shakes_words = shakes_words.filter(lambda w: len(w) > 0)
shakes_words = shakes_words.filter(lambda w: not w.isupper())

word_index0 = shakes_words.zipWithIndex().map(lambda (w, i): (i, w))
word_index1 = word_index0.map(lambda (i, w): (i + 1, w))
word_index2 = word_index0.map(lambda (i, w): (i - 1, w))

pair_words = word_index1.join(word_index0)
phrases = pair_words.join(word_index2).map(lambda (k, (w2, w1)): (w2, [w1]))
grouped_phrases = phrases.reduceByKey(lambda x, y: x + y).map(lambda x: x)

def to_dict(words):
    c = Counter(words)
    l = []
    for k in c.keys():
        l.append((k, c[k]))
    return l

counted_phrases = grouped_phrases.map(lambda (p, l): (p, to_dict(l)))

seed = grouped_phrases.takeSample(False, NUM_PHRASES)

# seed_rdd = sc.parallelize(seed)
# seed_rdd = seed_rdd.map(lambda (k, v): [x for x in k])

prose = []
for i in range(0, NUM_PHRASES):
    current = seed[i][0]
    prose.append([current[0], current[1]])
    for j in range(2, WORDS_PER_PHRASE):
        space = grouped_phrases.lookup(current)[0]
        if len(space) == 0:
            break
        prose[i].append(random.choice(space))
        current = (prose[i][j - 1], prose[i][j])

print prose
