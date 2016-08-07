from __future__ import division

__author__ = ("Georgios-Ioannis Brokos, "
              "Natural Language Processing Group, "
              "Department of Informatics, "
              "Athens University of Economics and Business, Greece.")
__copyright__ = "Copyright (c) 2016, " + __author__
__license__ = "3-clause BSD"
__email__ = "g.brokos@gmail.com"

import numpy as np

def pr_rec(rel_docs, retr_docs):
    rel_docs = set(rel_docs)
    total_rel = len(rel_docs)
    total_retr = len(retr_docs)
    n_rel = 0
    avg_precision = 0
    pr_rec = np.zeros((total_retr, 2))
    int_pr_rec = np.zeros((1, 11))
    if total_retr == 0:
        return pr_rec, avg_precision, int_pr_rec

    for i in range(total_retr):
        pos = i + 1
        if retr_docs[i] in rel_docs:
            n_rel += 1
            avg_precision += n_rel/pos
        pr_rec[i, 0] = n_rel / pos
        pr_rec[i, 1] = n_rel / total_rel

    avg_precision = avg_precision/total_rel

    rec_levels = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    for r in range(len(rec_levels)):
        d = np.where(pr_rec[:, 1] >= rec_levels[r])
        if len(d[0]) != 0:
            int_pr_rec[0, r] = np.max(pr_rec[d, 0])
        else:
            int_pr_rec[0, r] = 0
    return pr_rec, avg_precision, int_pr_rec
