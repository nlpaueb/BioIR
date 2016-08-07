from __future__ import division

__author__ = ("Georgios-Ioannis Brokos, "
              "Natural Language Processing Group, "
              "Department of Informatics, "
              "Athens University of Economics and Business, Greece.")
__copyright__ = "Copyright (c) 2016, " + __author__
__license__ = "3-clause BSD"
__email__ = "g.brokos@gmail.com"

import numpy as np

def ndcg(rel_docs, retr_docs):

    rel_docs = set(rel_docs)

    n_retr_docs = len(retr_docs)
    n_rel_docs = len(rel_docs)

    dcg = np.zeros((1, 1000))
    ndcg = np.zeros((1, 3))
    if n_retr_docs == 0:
        return ndcg
    for i in range(n_retr_docs):
        pos = i + 1
        if retr_docs[i] in rel_docs:
            dcg[0, i] = 1/np.log2(pos + 1)
    idcg = np.zeros((1, 1000))
    for i in range(n_rel_docs):
        pos = i + 1
        idcg[0, i] = 1/np.log2(pos + 1)
    ndcg[0, 0] = np.sum(dcg[0, :20])/np.sum(idcg[0, :20])
    ndcg[0, 1] = np.sum(dcg[0, :100])/np.sum(idcg[0, :100])
    ndcg[0, 2] = np.sum(dcg[0, :1000])/np.sum(idcg[0, :1000])
    return ndcg