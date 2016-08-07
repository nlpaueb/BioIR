__author__ = ("Georgios-Ioannis Brokos, "
              "Natural Language Processing Group, "
              "Department of Informatics, "
              "Athens University of Economics and Business, Greece.")
__copyright__ = "Copyright (c) 2016, " + __author__
__license__ = "3-clause BSD"
__email__ = "g.brokos@gmail.com"

import math

def split_list(x, n_chunks):
    max_chunk_size = int(math.ceil(float(len(x))/float(n_chunks)))
    chunks = []
    [chunks.append(x[i:i+max_chunk_size]) for i in range(0, len(x), max_chunk_size)]
    return chunks