import sys, time, random

from sklearn.neighbors import NearestNeighbors

from tools.get_centroid import *
from tools.load_files import *
from tools.split_seq import split_seq
from tools.Question import *
from tools.read_npy_chunk import *
from tools.progress import *


class NearestNeighborsRetrieval:

    def __init__(self, emb, centroids_file, test_file, n_neighbors, n_chunks, idmap, stopwords, idf=None):
        self.dim = len(emb[random.sample(emb, 1)[0]])
        self.centroids_file = centroids_file
        self.test_file = test_file
        self.n_neighbors = n_neighbors
        self.n_chunks = n_chunks
        self.idmap = idmap
        self.emb = emb
        self.stopwords = stopwords
        if idf is not None:self.idf = idf

    def load_questions_matrix(self):
        with open(self.test_file, 'r') as data_file:
            data = json.load(data_file)
            question_details = []
            for i in range(len(data["questions"])):
                question_body = data["questions"][i]["body"]
                question_id = data["questions"][i]["id"]
                q_centroid = np.transpose(np.array(get_centroid_idf(question_body, self.emb, self.idf, self.stopwords, self.dim)))
                q_centroid = q_centroid.reshape(1, -1)
                if i > 0:
                    q_centroids = np.concatenate((q_centroids, q_centroid), axis=0)
                else:
                    q_centroids = q_centroid.reshape(1, -1)
                question_details.append((question_body, question_id))
            return q_centroids, question_details

    def get_chunk_nns(self, X, q_centroids, question_details, chunk):
        nbrs = NearestNeighbors(algorithm='brute', metric='cosine', n_neighbors=1000).fit(X)
        dist, nns = nbrs.kneighbors(q_centroids, return_distance=True)
        q_array = []
        for q_point in range(nns.shape[0]):
            doc_nns = []
            for n_point in range(nns.shape[1]):
                doc_nns.append(self.idmap[chunk[0] + nns[q_point, n_point]])
            q = Question(question_details[q_point][0], question_details[q_point][1], doc_nns, list(dist[q_point, :]))
            q_array.append(q)
        return q_array

    # Dataset indeces are splitted in N chucks. Nearest top-(N*k) neighbors are extracted from each chunk, and then
    # the final top-k neighbors are extracted from those.

    def main(self):

        chunks = split_seq(range(len(self.idmap)), self.n_chunks)
        q_centroids, question_details = self.load_questions_matrix()
        q_arrays = []

        c = 0  # Number of current chunk
        for chunk in chunks:
            start_row = chunk[0]
            n_rows = len(chunk)
            corpus_centroids = read_npy_chunk(centroids_file, start_row, n_rows)
            q_arrays.append(self.get_chunk_nns(corpus_centroids, q_centroids, question_details, chunk))

            c += 1
            progress(c, len(chunks), 'chunks')
        self.reorder(q_arrays)
        return

    def reorder(self, q_arrays):
        final_q_array = []
        with open(self.test_file, 'r') as data_file:
            data = json.load(data_file)
            question_details = []
            for i in range(len(data["questions"])):
                q_body = data["questions"][i]["body"]
                q_id = data["questions"][i]["id"]
                top_nk = []
                for c in q_arrays:
                    top_nk += zip(c[i].retrieved, c[i].distances)
                top_k = sorted(top_nk, key=lambda tup: tup[1])[:self.n_neighbors]
                q = Question(q_body, q_id, [x[0] for x in top_k], [x[1] for x in top_k])
                final_q_array.append(q)

        directory = 'system_results/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(directory + '.'.join(self.centroids_file.split('/')[-1].split('.')[:-1]) + '.json', 'w+') as outfile:
            outfile.write(json.dumps({"questions":[ob.__dict__ for ob in final_q_array]}, indent=2))


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
    # Number of documents to retrieve
    n_neighbors = 1000
    # Numner of chunks to split the dataset. The less the memory of your system, the more the n_chucks you need.
    n_chunks = 8
    centroids_file = sys.argv[1]

    #Loading all necessary data to pass as arguments to NearestNeighborsRetrieval object
    print 'Loading necessary files..'
    stopwords = load_stopwords(stopwords_file)
    emb = load_emb(types_file, emb_file)
    idf = load_idf(idf_file)
    idmap = load_idmap(idmap_file)
    n_docs = len(idmap)

    print 'Nearest Neighbor Retrieval..'
    nnr = NearestNeighborsRetrieval(emb, centroids_file, test_file, n_neighbors, n_chunks, idmap, stopwords, idf)
    start = time.time()
    nnr.main()
    print 'Nearest Neighbor Retrieval finished, after: ', time.time() - start, 'sec'
