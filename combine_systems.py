__author__ = "Georgios-Ioannis Brokos"
__copyright__ = "Copyright (c) 2016, " + __author__
__license__ = "3-clause BSD"
__email__ = "g.brokos@gmail.com"

import json, sys, os
from tools.Question import *

def combine_systems(sys1_file, sys2_file):
    # Combines results of IR systems sys1 and sys2 as follows:
    #     for each question:
    #         if sys1 retrieved at least one document,
    #             use sys1 retrieved documents
    #         else
    #             use sys2 retrieved documents

    f = open(sys1_file, 'r')
    data_sys1 = json.load(f)
    f.close()

    f = open(sys2_file, 'r')
    data_sys2 = json.load(f)
    f.close()

    sys1_q_array = []
    for i in range(len(data_sys1["questions"])):
        sys1_q_array.append((data_sys1["questions"][i]["body"], data_sys1["questions"][i]["id"], data_sys1["questions"][i]["retrieved"]))

    sys2_q_array = []
    for i in range(len(data_sys2["questions"])):
        sys2_q_array.append((data_sys2["questions"][i]["body"], data_sys2["questions"][i]["id"],data_sys2["questions"][i]["retrieved"]))

    q_array = []
    for i in range(len(sys1_q_array)):

        if len(sys1_q_array[i][2]) == 0:
            q = Question(sys1_q_array[i][0], sys1_q_array[i][1], sys2_q_array[i][2])
        else:
            q = Question(sys1_q_array[i][0], sys1_q_array[i][1], sys1_q_array[i][2])
        q_array.append(q)

    directory = 'system_results/'
    if not os.path.exists(directory):
            os.makedirs(directory)
    with open(directory + 'hybrid_' + '.'.join(sys1_file.split('/')[-1].split('.')[:-1]) + '.'
                      + '.'.join(sys2_file.split('/')[-1].split('.')[:-1])
                      + '.json', 'w+') as outfile:
        outfile.write(json.dumps({"questions":[ob.__dict__ for ob in q_array]}, indent=2))


if __name__ == '__main__':
    combine_systems(sys.argv[1], sys.argv[2])
