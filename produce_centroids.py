__author__ = ("Georgios-Ioannis Brokos, "
              "Natural Language Processing Group, "
              "Department of Informatics, "
              "Athens University of Economics and Business, Greece.")
__copyright__ = "Copyright (c) 2016, " + __author__
__license__ = "3-clause BSD"
__email__ = "g.brokos@gmail.com"

import random, time
from tools.get_centroid import *
from tools.load_files import *

try:
    import ijson.backends.yajl2 as ijson
    print 'Using yajl2 backend for ijson'
except ImportError:
    import ijson
    print 'yajl2 backend for ijson not found. Using standard ijson.'

class doc2cent:

    tpyes = None
    emb = None
    idf = None
    stopwords = None
    corpus_file = ""
    centroids_file = ""
    idmap_file = ""
    idf_cent = True

    def __init__(self, corpus_file, centroids_file, idmap_file, emb, idf=None, stopwords=None, idf_cent=True):
        self.corpus_file = corpus_file
        self.centroids_file = centroids_file
        self.idmap_file = idmap_file
        self.emb = emb
        self.dim = len(self.emb[random.sample(self.emb, 1)[0]])
        if idf_file is not None:self.idf = idf
        if stopwords_file is not None:self.stopwords = stopwords
        self.idf_cent = idf_cent

    def calculate_centroids(self):
        if os.path.exists(self.centroids_file):
            os.remove(self.centroids_file)

        f = open(self.corpus_file, 'r')
        objects = ijson.items(f, 'articles.item')
        i = 0
        idmap = {}
        cent_array = []
        for article in objects:
            abstract_text = article["abstractText"]
            abstract_id = article["pmid"]
            text = article["title"] + " " + abstract_text

            centroid = get_centroid_idf(text, self.emb, self.idf, self.stopwords, self.dim)

            cent_array.append(np.array(centroid, dtype=np.float32))

            idmap[i] = abstract_id
            i += 1
        final_cent_array = np.array(cent_array, dtype=np.float32).reshape((i, self.dim))
        print final_cent_array.shape
        np.save(centroids_file, final_cent_array)


        fout = open(self.idmap_file, 'wb')
        pickle.dump(idmap, fout)
        fout.close()

if __name__ == '__main__':

    # Load file names from config.json file.
    f = open('config.json', 'r')
    data_cfg = json.load(f)
    f.close()
    types_file = data_cfg["config"]["types_file"]
    emb_file = data_cfg["config"]["vectrors_file"]
    corpus_file = data_cfg["config"]["corpus_file"]
    idf_file = data_cfg["config"]["idf_file"]
    stopwords_file = data_cfg["config"]["stopwords_file"]

    centroids_file = 'data/CentIDF.npy'
    idmap_file = 'data/idmap.pkl'

    # Loading all necessary data.
    print 'Loading Embeddings..'
    emb = load_emb(types_file, emb_file)
    print 'Loading IDF..'
    idf = load_idf(idf_file)
    print 'Loading Stopwords..'
    stopwords = load_stopwords(stopwords_file)

    # Create doc2cent object and start computing.
    d2c = doc2cent(corpus_file, centroids_file, idmap_file, emb, idf, stopwords, idf_cent=True)
    print 'Calculating Centroids..'
    start = time.time()
    d2c.calculate_centroids()
    print 'Centroids Calculated in: ', time.time() - start, ' seconds.'
