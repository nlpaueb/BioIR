# BioIR
This software accompanies the following paper and contains code for reproducing the experiments described in it.
>*Using Centroids of Word Embeddings and Word Mover's Distance for Biomedical Document Retrieval in Question Answering
>G. Brokos, P. Malakasiotis and I. Androutsopoulos, "Using Centroids of Word Embeddings and Word Mover's Distance for Biomedical Document >Retrieval in Question Answering". Proceedings of the 15th Workshop on Biomedical Natural Language Processing (BioNLP 2016), at the 54th >Annual Meeting of the Association for Computational Linguistics (ACL 2016), Berlin, Germany, 2016*



# Detailed Instructions
##Files format
In order to run these experiments, some files in a specific format, are needed:
* WordEmbedding files in the BioASQ format:
 * **Types file** (types.txt)  -  contains a list of the vocabulary.
 * **Vectors file** (vectors.txt)  -  contains the vectors(embeddings), matching the types file line by line.  
   You can download the embeddings provided by BioASQ, in the described format, from the following link:  
   http://participants-area.bioasq.org/tools/BioASQword2vec/
* **IDF file** (IDF.txt)  -  Each line consists of a word and its corresponding IDF score, delimited by space character.  
  https://drive.google.com/open?id=0B62bnH-apTfObmNHX1VvQ3UwX1E
* **Stop-words file** (stopwords.txt)  -  A list of stop-words  
  https://drive.google.com/open?id=0B62bnH-apTfOQmdjNnJ1cG9mek0
* **Dataset file**  (allPubMedAbstracts.json)  -  A json file containing the biomedical articles from PubMed (pmid, title and Abstract), with the following format:
```
{  
  "articles": [  
    {
      "pmid": "7614544",  
      "title": "Safety of coronary ultrasound angioplasty: effects of sonication on in  
       tact canine coronary arteries.",  
      "abstractText": "The purpose of this work was to examine in vivo the safety of s  
       onication in the coronary arteries in a live animal model...Thus, the data sug  
       gest that transluminal coronary sonication exerts no overt adverse effects in vivo."  
    }, ...
  ]
}
```
* **Test file**  (BioASQ-trainingDataset4b.json)  -  A json file containing the biomedical question with a list of their relevant documents (pmids).
  You can download this file from the following link (register required):  
  http://participants-area.bioasq.org/Tasks/4b/trainingDataset/  

The above files should either placed in the data folder with the same naming as above, or you sould configure the config.json file with the new path/filename. 

##Experiments
Software cosists of the following python excecutables:
* **produce_centroids.py**  -  Procuces a numpy array with the centroids of the documents contained in the dataset file and stores in in the data folder.  
Numpy array shape: Number of Documents x Embedding dimensions)  
```python produce_centroids.py```
* **knn_retrieval.py**  -  Given a test file (questions with relevant judgments) and the centroids file previously produced by produce_centroids.py, knn_retrieval.py retrieves top-1000 documents based on cosine similarity between the question centroid and the document centroids and stores the results in the system_results file, in .json format.  
```python knn_retrieval.py [centroids npy filepath]```  
* **build_annoy_index.py**  -  Given the centroids file produced by produce_centroids.py, builds an Approximate Nearest Neighbrors index file, using the annoy library.  
```python build_annoy_index.py [centroids npy filepath] [Number of trees]```  
* **ann_retrieval.py**  -  Given a test file (questions with relevant judgments) and the index file previously built by build_annoy_index.py, ann_retrieval retrieves the approximate top-1000 documents based on cosine similarity between the question centroid and the document centroids and stores the results in the system_results file, in .json format.  
```python ann_retrieval.py [ANN index filepath]```  
* **reranking.py**  -  Reranks the retrieved documents of a system, using a Relaxation of Word Mover's Distance. It produces three new  .json files for RWMD-Q, RWMD-D and RWMD-MAX and stores them in the system_results file, in .json format.  
```python reranking.py [system results filepath]```  
* **combine_systems.py**  - Takes two system results as input and combines them as follows:  
```
for each question:
  if sys1 retrieved at least one document,
    use sys1 retrieved documents
  else
    use sys2 retrieved documents
```  
```python combine_systems.py [sys_1 results filepath] [sys_2 results filepath]```  

##Evaluation  
You can evaluate each system with the following commands:
```
cd evaluation
python evaluate [system results filepath]
```
Evaluation measures will be printed on terminal.
##Execution example  

You can reproduce the experiments described on the paper with the following commands:  

####Retrival
```
python produce_centroids.py 
python knn_retrieval.py data/CentIDF.npy
python build_annoy_index.py data/CentIDF.npy 100
python ann_retrieval.py data/CentIDF.npy.100Trees.annoy
```
####Reranking
```
python reranking.py system_results/CentIDF.json  
python reranking.py system_results/CentIDF_annoy_100_1000_10.json
python reranking.py system_results/PubMed.json  
```
####Hybrid
```
python combine_systems.py system_results/PubMed_RWMD_Q.json system_results/CentIDF_RWMD_Q.json
python combine_systems.py system_results/PubMed_RWMD_Q.json system_results/CentIDF_annoy_100_1000_10_RWMD_Q.json
```
####Evaluation
```
cd evaluation
python evaluate.py system_results/CentIDF.json
python evaluate.py system_results/PubMed.json  
python evaluate.py system_results/CentIDF_RWMD_Q.json
python evaluate.py system_results/CentIDF_RWMD_D.json
python evaluate.py system_results/PubMed_RWMD_Q.json
python evaluate.py system_results/hybrid_PubMed_RWMD_Q.CentIDF_RWMD_Q.json
python evaluate.py system_results/hybrid_PubMed_RWMD_Q.CentIDF_annoy_100_1000_10_RWMD_Q.json
```
