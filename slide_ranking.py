# adapted from https://colab.research.google.com/github/UKPLab/sentence-transformers/blob/master/examples/applications/retrieve_rerank/retrieve_rerank_simple_wikipedia.ipynb#scrollTo=UlArb7kqN3Re

from sentence_transformers import SentenceTransformer, CrossEncoder, util

#We use the Bi-Encoder to encode all passages, so that we can use it with sematic search
bi_encoder = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
bi_encoder.max_seq_length = 500

#The bi-encoder will retrieve 100 documents. We use a cross-encoder, to re-rank the results list to improve the quality
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def calculate_embeddings(transcriptions, path = None):
    corpus_embeddings = bi_encoder.encode(transcriptions, convert_to_tensor=True)

    if path:
        import pickle
        pickle.dump(corpus_embeddings, open(path, "wb"))
    return corpus_embeddings

def load_embeddings(path):
    import pickle
    corpus_embeddings = pickle.load(open(path, "rb"))
    return corpus_embeddings

def get_hits(query, corpus_embeddings, transcriptions, top_k = 32):

    ##### Sematic Search #####
    # Encode the query using the bi-encoder and find potentially relevant passages
    question_embedding = bi_encoder.encode(query, convert_to_tensor=True)
    hits = util.semantic_search(question_embedding, corpus_embeddings, top_k=top_k)
    hits = hits[0]  # Get the hits for the first query

    ##### Re-Ranking #####
    # Now, score all retrieved passages with the cross_encoder
    cross_inp = [[query, transcriptions[hit['corpus_id']]] for hit in hits]
    cross_scores = cross_encoder.predict(cross_inp)

    # Sort results by the cross-encoder scores
    for idx in range(len(cross_scores)):
        hits[idx]['cross-score'] = cross_scores[idx]

    hits = sorted(hits, key=lambda x: x['cross-score'], reverse=True)
    return hits