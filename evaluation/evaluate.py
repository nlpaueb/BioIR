from __future__ import division
import json
import sys
from pr_rec import pr_rec
from perfect_reranking import perfect_reranking
from ndcg import ndcg
import numpy as np
import csv

# TODO: Add Mean Average Precision (MAP) calculation.


def evaluate(rel_file, retr_file, write_flag='-y'):
    f = open(rel_file, 'r')
    data_rel = json.load(f)
    f.close()

    f = open(retr_file, 'r')
    data_retr = json.load(f)
    f.close()

    total_relevant = 0
    rel_found = 0
    total_retrieved = 0
    macro_precision = 0
    macro_recall = 0
    t_ndcg = np.zeros((1, 3))

    sumAIP = 0
    sumIP = np.zeros((1, 11))

    sum_prfAIP = 0
    sum_prfIP = np.zeros((1, 11))

    n_questions = len(data_retr["questions"])
    np.set_printoptions(threshold=np.nan)
    for i in range(n_questions):
        #print i
        data_rel_id = data_rel["questions"][i]["id"]
        data_retr_id = data_retr["questions"][i]["id"]
        assert data_rel_id == data_retr_id

        rel_docs = []
        relevant_docs = data_rel["questions"][i]["documents"]
        [rel_docs.append(doc.split('/')[4]) for doc in relevant_docs]
        #rel_docs = relevant_docs
        retr_docs = map(str, data_retr["questions"][i]["retrieved"])
        retr_docs = [x.strip() for x in retr_docs]
        n_rel_docs = len(data_rel["questions"][i]["documents"])
        n_retr_docs = len(data_retr["questions"][i]["retrieved"])

        total_relevant += n_rel_docs
        total_retrieved += n_retr_docs
        common = set(rel_docs) & set(retr_docs)
        n_common = len(common)
        rel_found += n_common
        if n_retr_docs != 0:
            macro_precision += (n_common/n_retr_docs)
        if n_rel_docs != 0:
            macro_recall += (n_common/n_rel_docs)

        curve, int_curve = pr_rec(rel_docs, retr_docs)

        perfect_curve, perfect_int_curve = perfect_reranking(rel_docs, retr_docs, n_common)
        t_ndcg = np.add(t_ndcg, ndcg(rel_docs, retr_docs))

        sumAIP += np.sum(int_curve) / 11
        sumIP = np.add(sumIP, int_curve)

        sum_prfAIP += np.sum(perfect_int_curve, 1) / 11
        sum_prfIP = np.add(sum_prfIP, perfect_int_curve)

    mean_ndcg = np.divide(t_ndcg, n_questions)
    micro_precision = rel_found / total_retrieved
    macro_precision = macro_precision / n_questions

    micro_recall = rel_found / total_relevant
    macro_recall = macro_recall / n_questions

    MAIP = sumAIP / n_questions
    MIP = np.divide(sumIP, n_questions)

    prf_MAIP = sum_prfAIP / n_questions
    prf_MIP = np.divide(sum_prfIP, n_questions)

    print '\n'
    print 'Micro-Average Precision: ' + str("{0:.4f}".format(micro_precision))
    print 'Macro-Average Precision: ' + str("{0:.4f}".format(macro_precision))
    print 'Micro-Average Recall:    ' + str("{0:.4f}".format(micro_recall))
    print 'Macro-Average Recall:    ' + str("{0:.4f}".format(macro_recall))
    print 'MAIP:                    ' + str("{0:.4f}".format(MAIP))
    print 'MIP:                     ' + str(map("{0:.4f}".format,MIP[0]))
    print 'nDCG@20:                 ' + str("{0:.4f}".format(mean_ndcg[0][0]))
    print 'nDCG@100:                ' + str("{0:.4f}".format(mean_ndcg[0][1])) + '\n'
    print 'Perfect Reranking: '
    print 'MAIP:                    ' + str("{0:.4f}".format(prf_MAIP[0]))
    print 'MIP:                     ' + str(map("{0:.4f}".format,prf_MIP[0]))


    if write_flag!='-n':
        with open('evaluation.txt', 'a+') as outfile:
            outfile.write(retr_file)
            outfile.write(' %.4f' % (micro_precision))
            outfile.write(' %.4f' % (macro_precision))
            outfile.write(' %.4f' % (micro_recall))
            outfile.write(' %.4f' % (macro_recall))
            outfile.write(' %.4f' % (MAIP))
            outfile.write(' ')
            np.savetxt(outfile, MIP, delimiter=' ', fmt='%.4f', newline=' ')
            outfile.write('%.4f ' % (prf_MAIP[0]))
            np.savetxt(outfile, prf_MIP, delimiter=' ', fmt='%.4f', newline=' ')
            np.savetxt(outfile, mean_ndcg, delimiter=' ', fmt='%.4f')


if __name__ == '__main__':
    if len(sys.argv)==3:
        write_flag = sys.argv[2]
    else:
        write_flag = '-y'
    f = open('../config.json', 'r')
    data_cfg = json.load(f)
    f.close()
    rel_file = data_cfg["config"]["test_file"]
    evaluate(rel_file, sys.argv[1], write_flag)
