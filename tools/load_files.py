import csv
import os
import numpy as np
import cPickle as pickle
from itertools import izip

def load_types(TYPES_FILE):
    i = 0
    types = {}
    with open(TYPES_FILE, 'r') as types_f:
        for line in types_f:
            types[line.strip('\r\n').decode('UTF-8', 'ignore')] = i
            i += 1
    return types

def load_emb(types_file, emb_file):
    emb = {}
    with open(types_file, 'r') as types_f, open(emb_file, 'r') as emb_f:
            for line1, line2 in izip(types_f, emb_f):
                line2 = line2.strip()
                emb[line1.strip('\r\n').decode('UTF-8', 'ignore')] = np.array(map(float, line2.split(' ')), dtype=np.float32)
    return emb

def load_df2idf(DF_FILE, n_docs=10876004):
    idf = {}
    with open(DF_FILE) as df_file:
        c = csv.reader(df_file, delimiter=" ")
        for line in c:
            # Converting DF to IDF
            # n_docs = 14891717
            #n_docs = 528155
            idf[line[0].decode('UTF-8', 'ignore')] = np.log(n_docs / float(line[1]))
    return idf

def load_idf(DF_FILE):
    idf = {}
    with open(DF_FILE) as df_file:
        c = csv.reader(df_file, delimiter=" ")
        for line in c:
            idf[line[0].decode('UTF-8', 'ignore')] = float(line[1])
    return idf

def load_vectors_to_ram(VECTORS_FILE, NOFTYPES, D):
    i = 0
    v = np.zeros((NOFTYPES, D))
    with open(VECTORS_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            v[i][:] = map(float, line.split(' '))
            i += 1
    return v


def load_stopwords(stopwords_file):
    stopwords = set()
    with open(stopwords_file, 'r') as s:
        for word in s:
            stopwords.add(word.rstrip().decode('UTF-8', 'ignore'))
    return set(stopwords)


def load_vectors_mmaped(VECTORS_FILE, NOFTYPES, D, UPDATE_VECTORS):
    if (not os.path.exists('vectors.mymemmap')) or UPDATE_VECTORS == 1:
        v = np.memmap('vectors.mymemmap', dtype='float', mode='w+', shape=(NOFTYPES, D))
        i = 0

        # Showing percentage to user
        limit = 100000
        with open(VECTORS_FILE, 'r') as f:
            for line in f:
                if i >= limit:
                    print(limit/float(NOFTYPES)*100)
                    limit += 100000
                line = line.strip()
                if len(line) > 0:
                    v[i][:] = map(float, line.split(' '))
                i += 1
    else:
        v = np.memmap('vectors.mymemmap', dtype='float', mode='r', shape = (NOFTYPES, D))
    return v


def load_idmap(idmap_file):
    pkl_file = open(idmap_file, 'rb')
    idmap = pickle.load(pkl_file)
    pkl_file.close()

    return idmap
