__author__ = ("Georgios-Ioannis Brokos, "
              "Natural Language Processing Group, "
              "Department of Informatics, "
              "Athens University of Economics and Business, Greece.")
__copyright__ = "Copyright (c) 2016, " + __author__
__license__ = "3-clause BSD"
__email__ = "g.brokos@gmail.com"

from __future__ import division
import numpy as np
import json, re
from collections import defaultdict


# clean for BioASQ
bioclean = lambda t: re.sub('[.,?;*!%^&_+():-\[\]{}]', '', t.replace('"', '').replace('/', '').replace('\\', '').replace("'", '').strip().lower()).split()


def get_centroid_idf(text, emb, idf, stopwords, D):
    # Computing Terms' Frequency
    tf = defaultdict(int)
    tokens = bioclean(text)
    for word in tokens:
        if word in emb and word not in stopwords:
            tf[word] += 1

    # Computing the centroid
    centroid = np.zeros((1, D))
    div = 0

    for word in tf:
        if word in idf:
            p = tf[word] * idf[word]
            centroid = np.add(centroid, emb[word]*p)
            div += p
    if div != 0:
        centroid = np.divide(centroid, div)
    return centroid



def get_centroid(text, emb, stopwords, D):
    tokens = bioclean(text)
    centroid = np.zeros((1, D))
    div = 0
    for word in tokens:
        if word in emb and word not in stopwords:
            centroid = np.add(centroid, emb[word][:])
            div += 1
    if div != 0:
        centroid = np.divide(centroid, div)
    return centroid
