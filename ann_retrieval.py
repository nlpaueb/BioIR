import time, sys, random

from annoy import AnnoyIndex
from tools.get_centroid import *
from tools.load_files import *
from tools.get_centroid import *
from tools.Question import *


class ApproximateNearestNeighborsRetrieval:

    def __init__(self, emb, index_file, test_file, knns, n_trees, multipliers, idmap, stopwords, idf=None):
        self.index_file = index_file
        self.test_file = test_file
        self.knns = knns
        self.n_trees = n_trees
        self.multipliers = multipliers
        self.idmap = idmap
        self.emb = emb
        self.stopwords = stopwords
        if idf is not None:self.idf = idf
        self.dim = len(self.emb[random.sample(emb, 1)[0]])

    def retrieve(self):

        print 'Loading necessary files..'
        u = AnnoyIndex(self.dim, metric='angular')
        u.load(index_file)

        print 'ANN Retrieval..'
        for n_neighbors in knns:
            print 'Number of neighbors: ' + str(n_neighbors)
            for mult in self.multipliers:
                print 'Multiplier: ' + str(mult)
                search_k = self.n_trees * n_neighbors * mult
                filename = '.'.join((self.test_file.split('/')[-1].split('.')[:-1]))
                with open("test/" + str(filename) + ".json", 'r') as data_file:
                    data = json.load(data_file)
                    qArray = []
                    for i in range(len(data["questions"])):
                        question_body = data["questions"][i]["body"]
                        question_id = data["questions"][i]["id"]
                        qcentroid = np.transpose(np.array(get_centroid_idf(question_body, self.emb, self.idf, self.stopwords, self.dim)))

                        anns = u.get_nns_by_vector(qcentroid, n_neighbors, search_k)
                        doc_anns = []
                        for n in anns:
                            doc_anns.append(self.idmap[n])
                        q = Question(question_body, question_id, doc_anns)
                        qArray.append(q)
                    directory = "system_results/"
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    with open(str(directory)+"/"+"CentIDF_annoy_"+str(n_trees)+"_"+str(n_neighbors)+"_"+str(mult)+".json", "w+") as outfile:
                        outfile.write(json.dumps({"questions":[ob.__dict__ for ob in qArray]}, indent=2))

if __name__ =='__main__':
    # Load file names from config.json file.
    f = open('config.json', 'r')
    data_cfg = json.load(f)
    f.close()
    types_file = data_cfg["config"]["types_file"]
    emb_file = data_cfg["config"]["vectrors_file"]
    corpus_file = data_cfg["config"]["corpus_file"]
    idf_file = data_cfg["config"]["idf_file"]
    stopwords_file = data_cfg["config"]["stopwords_file"]
    test_file = data_cfg["config"]["test_file"]

    idmap_file = 'data/idmap.pkl'
    index_file = sys.argv[1]

    # Setting annoy parameters
    knns = [1000]
    multipliers = [10]
    n_trees = 100

    # Loading all necessary data to pass as arguments to NearestNeighborsRetrieval object
    print 'Loading necessary files..'
    stopwords = load_stopwords(stopwords_file)
    emb = load_emb(types_file, emb_file)
    idf = load_idf(idf_file)
    idmap = load_idmap(idmap_file)
    n_docs = len(idmap)

    print 'Approximate Nearest Neighbors Retrieval..'
    annr = ApproximateNearestNeighborsRetrieval(emb, index_file, test_file, knns, n_trees, multipliers, idmap,
                                                stopwords, idf)
    start = time.time()
    annr.retrieve()
    print 'Nearest Neighbor Retrieval finished, after: ', time.time() - start, 'sec'
