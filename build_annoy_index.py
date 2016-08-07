__author__ = "Georgios-Ioannis Brokos"
__copyright__ = "Copyright (c) 2016, " + __author__
__license__ = "3-clause BSD"
__email__ = "g.brokos@gmail.com"

from annoy import AnnoyIndex
import numpy as np
import time, sys


def build_annoy_index(metric, input_filename, output_filename, n_trees):
# Creates an index for Approimate Nearest Neighbors retrieval, using the annoy library.
    print 'Aproximate Nearest Neighbors for: ' + input_filename
    centroids_array = np.load(input_filename)
    n_dimensions = centroids_array.shape[1]
    t = AnnoyIndex(n_dimensions, metric=metric)
    for i in range(centroids_array.shape[0]):
        t.add_item(i, centroids_array[i][:])
    print "Building Index - Number of Trees: ",str(n_trees)
    t.build(n_trees)
    t.save(output_filename)

if __name__ == '__main__':
    metric = 'angular'
    input_filename = sys.argv[1]
    n_trees = 100
    output_filename = input_filename + '.' + str(n_trees) + 'Trees' + '.annoy'
    print 'Input file: ' + input_filename
    print 'Index(output) file: ' + output_filename
    print 'Number of trees: ' + str(n_trees)
    start = time.time()
    build_annoy_index(metric, input_filename, output_filename, n_trees)
    print 'Index of ', n_trees, 'built after ', time.time() - start, ' seconds.'

