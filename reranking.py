from __future__ import division
import json, re, sys, gc
import ijson.backends.yajl2 as ijson
import numpy as np
from collections import defaultdict
from scipy.spatial.distance import euclidean
from tools.Question import *
from tools.load_files import *
from tools.progress import *

# clean for BioASQ
bioclean = lambda t: re.sub('[.,?;*!%^&_+():-\[\]{}]', '', t.replace('"', '').replace('/', '').replace('\\', '').replace("'", '').strip().lower()).split()


class reranking:

    emb = None
    stopwords = None
    corpus_file = ""
    ret_file = ""
    corpus_index = {}
    counter = 0

    def __init__(self, emb, stopwords, corpus_file, ret_file):
        self.emb = emb
        self.stopwords = stopwords
        self.corpus_file = corpus_file
        self.ret_file = ret_file
        self.counter = 0

    def initialize(self):
        f = open(self.ret_file, 'r')
        data_q = json.load(f)
        abstracts_needed = set()
        for i in range(len(data_q["questions"])):
            abstracts_needed = abstracts_needed | set(data_q["questions"][i]["retrieved"])
        f.close()

        print "Collecting Abstracts.."
        f = open(self.corpus_file, 'r')
        corpus = ijson.items(f, 'articles.item')
        for article in corpus:
            pmid = article["pmid"]
            if pmid in abstracts_needed:
                self.corpus_index[pmid] = article["title"] + ' ' + article["abstractText"]
                abstracts_needed.remove(pmid)
                if not abstracts_needed:
                    break
        f.close()


        print len(self.corpus_index)
        q_array_q = []
        q_array_d = []
        q_array_max = []
        print "Reranking.."
        n_questions = len(data_q["questions"])
        for i in range(n_questions):
            #print i
            progress(i+1, n_questions, 'questions')
            q_id = data_q["questions"][i]["id"]
            q_body = data_q["questions"][i]["body"]
            q_retrieved = data_q["questions"][i]["retrieved"]

            retr_array_q, retr_array_d, retr_array_max = self.rerank(q_body, q_retrieved)

            q_array_q.append(Question(q_body, q_id, [x[0] for x in retr_array_q], [x[1] for x in retr_array_q]))
            q_array_d.append(Question(q_body, q_id, [x[0] for x in retr_array_d], [x[1] for x in retr_array_d]))
            q_array_max.append(Question(q_body, q_id, [x[0] for x in retr_array_max], [x[1] for x in retr_array_max]))

        with open('.'.join(self.ret_file.split('.')[:-1]) + '_RWMD_Q.json', 'w+') as outfile:
            outfile.write(json.dumps({"questions":[ob.__dict__ for ob in q_array_q]}, indent=2))

        with open('.'.join(self.ret_file.split('.')[:-1]) + '_RWMD_D.json', 'w+') as outfile:
            outfile.write(json.dumps({"questions":[ob.__dict__ for ob in q_array_d]}, indent=2))

        with open('.'.join(self.ret_file.split('.')[:-1]) + '_RWMD_MAX.json', 'w+') as outfile:
            outfile.write(json.dumps({"questions":[ob.__dict__ for ob in q_array_max]}, indent=2))


    def rerank(self, q_body, q_retrieved):
        # {word:frequency} dictionary for the question's words
        q_body_tokens = bioclean(q_body)
        tf_q = defaultdict(int)
        for word in q_body_tokens:
            if word in self.emb and word not in self.stopwords:
                tf_q[word] += 1
        retr_array_q = []
        retr_array_d = []
        retr_array_max = []
        for doc in q_retrieved:
            # if document text is available, calculate rwmd distances
            if doc in self.corpus_index:
                # {word:frequency} dictionary for the document's words
                document_body_tokens = bioclean(self.corpus_index[doc])
                tf_d = defaultdict(int)
                for word in document_body_tokens:
                    if word in self.emb and word not in self.stopwords:
                        tf_d[word] += 1
                # Calculate RWMD-Q
                dist_q = self.rwmd(tf_q, tf_d)
                retr_array_q.append((doc, dist_q))

                # Calculate RWMD-D
                dist_d = self.rwmd(tf_d, tf_q)
                retr_array_d.append((doc, dist_d))

                # Calculate RWMD-MAX
                dist_max = np.max([dist_q, dist_d])
                retr_array_max.append((doc, dist_max))
        retr_array_q.sort(key=lambda tup: tup[1])
        retr_array_d.sort(key=lambda tup: tup[1])
        retr_array_max.sort(key=lambda tup: tup[1])

        return retr_array_q, retr_array_d, retr_array_max


    def rwmd(self, tf_doc1, tf_doc2):
        rwmdistance = 0
        sumtf1 = sum(tf_doc1.values())
        for word1 in tf_doc1:
            dst = []
            for word2 in tf_doc2:
                dst.append(euclidean(self.emb[word1], self.emb[word2]))
            rwmdistance += np.min(dst)*tf_doc1[word1]/sumtf1

        return rwmdistance

if __name__ == '__main__':
    # Load file names from config.json file.
    f = open('config.json', 'r')
    data_cfg = json.load(f)
    f.close()
    types_file = data_cfg["config"]["types_file"]
    emb_file = data_cfg["config"]["vectrors_file"]
    stopwords_file = data_cfg["config"]["stopwords_file"]
    corpus_file = data_cfg["config"]["corpus_file"]

    stopwords = load_stopwords(stopwords_file)
    emb = load_emb(types_file, emb_file)
    ret_file = sys.argv[1]
    r = reranking(emb, stopwords, corpus_file, ret_file)
    r.initialize()
