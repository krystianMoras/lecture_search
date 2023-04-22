from nltk import SnowballStemmer
import string
from nltk import word_tokenize
from nltk.corpus import stopwords
from math import log


import numpy as np
import networkx as nx


def count_sublist(search, searched):
    
    all_indices = [i for i, x in enumerate(searched) if x == search[0]]
    count = 0
    for index in all_indices:
        if search == searched[index:index+len(search)]:
            count+=1
    return count


class CandidatePostProcessor:

    def __init__(self, transcriptions):
        #initialize stemmer
        self.STEMMER = SnowballStemmer('porter', ignore_stopwords=False)
        # assuming transcriptions are in chronological order
        self.transcription_list = list(transcriptions.values())
        self.all_words = []
        self.all_distinct_words = dict()
        self.stemmed_transcriptions = []
        self.stemmed_transcriptions_dicts = []
        for transcription in self.transcription_list:
            # remove punctuation and special characters
            words = word_tokenize(transcription)
            # remove punctuation from words
            words = [w for w in words if w not in string.punctuation]
            words_stemmed = [self.STEMMER.stem(w) for w in words]
            stemmed_to_word = {self.STEMMER.stem(w):w for w in words}

            # stem transcription
            self.stemmed_transcriptions.append(words_stemmed)
            self.stemmed_transcriptions_dicts.append(stemmed_to_word)
            self.all_words.extend(words_stemmed)
            
            self.all_distinct_words.update(stemmed_to_word)

    @staticmethod
    def get_possible_spans(words):
        spans = []
        for i in range(len(words)-1):
            for j in range(i+2,len(words)+1):
                spans.append(" ".join(words[i:j]))
        return spans
    
    @staticmethod
    def character_filter(candidate):
         # if there is a number it probably isn't a candidate
        if any(char.isdigit() for char in candidate):
            return False
        # if there are lowercase single letters it probably isn't a candidate
        if any((len(w) == 1 and w.islower()) or w in stopwords.words("english") for w in word_tokenize(candidate)):
            return False
        return True
    
    def count_documents_where_word_appears(self, word):
        count = 0
        for doc in self.stemmed_transcriptions_dicts:
            if word in doc:
                count += 1
        return count
    
    def idf(self,word):
        # number of documents
        N = len(self.stemmed_transcriptions_dicts)
        word_idf = N / self.count_documents_where_word_appears(word)
        return log(1 + word_idf)

    def filter_candidates(self, candidates):
        # merge all candidates into one list
        all_candidates = []
        for doc_id, doc_candidates in candidates.items():
            doc_candidates = [cand for cand in doc_candidates if CandidatePostProcessor.character_filter(cand)]
            all_candidates.extend(doc_candidates)

  #      print(f"all candidates: {len(all_candidates)}")
        # stem all candidates (multiword)
        stemmed_candidates = [[self.STEMMER.stem(word) for word in word_tokenize(cand) if word not in string.punctuation] for cand in all_candidates]
        stemmed_to_full_candidate = {" ".join([self.STEMMER.stem(word) for word in word_tokenize(cand) if word not in string.punctuation]):cand for cand in all_candidates }

  #      print(stemmed_candidates[:10])

        # verify that all candidates are in the transcriptions
        # for stemmed_candidate in stemmed_candidates:
        #     if not sublist(stemmed_candidate, self.all_words):
        #         print(f"candidate not in transcriptions: {stemmed_candidate}")
        
        # filter out multiple word grams

        # sort by length
        sorted_candidates = sorted(stemmed_candidates, key=lambda x: len(x), reverse=True)
#        print(f"sorted candidates: {sorted_candidates[:10]}")

        # filter out candidates that are subsets of other candidates, pick the best one
        superset_candidates = set()
        for candidate in sorted_candidates:
            joined_candidate = " ".join(candidate)
            add = True

            for superset_candidate in superset_candidates:
                if joined_candidate in CandidatePostProcessor.get_possible_spans(superset_candidate.split()):
                    # dont add candidate
                    add = False
                    break
            if add:
                superset_candidates.add(joined_candidate)

  #      print(f"superset candidates: {len(superset_candidates)}")

        filtered = {}
        for superset_candidate in superset_candidates:
            possible_spans = CandidatePostProcessor.get_possible_spans(superset_candidate.split())
            ranked_spans = []
            for span in possible_spans:
                if span.split() in stemmed_candidates:
                    support = count_sublist(span.split(), self.all_words)
                    # count tfidf of words making up span
                    sub_supports = sum([self.idf(word) for word in span.split()])
                    #print(f"{span}: {sub_supports}")
                    ranked_spans.append((span, support/sub_supports,support))
            if len(ranked_spans) > 0:
                ranked_spans = sorted(ranked_spans, key=lambda x: x[1], reverse=True)
               # print(f"best span: {ranked_spans[0]}, other spans: {ranked_spans[1:]}")
                if ranked_spans[0][2] > 1:
                    filtered[ranked_spans[0][0]] = stemmed_to_full_candidate[ranked_spans[0][0]]
                else:
                    continue
                    print(f"no support for {ranked_spans[0][0]}")
        return filtered

    def stemmed_to_word(self, stemmed_candidate):
        return " ".join([self.all_distinct_words[word] for word in stemmed_candidate.split()])           
    
    def phrase_hierarchy_graph(self, stemmed_candidates):
        
        G = nx.DiGraph()
        for candidate in stemmed_candidates:
            G.add_node(candidate)
        
        for doc in self.stemmed_transcriptions:
            # get all candidates that are in the document


            term_counts = {term: count_sublist(term.split(), doc) for term in stemmed_candidates}
            term_counts = {term: count for term, count in term_counts.items() if count > 0}
            print(term_counts)
            # from terms that appear at least once
            for term in term_counts:
                if term_counts[term] > 0:
   
                    # add edges to all other terms that appear at least once
                    for other_term in term_counts:
                        if other_term != term and term_counts[other_term] > 0:
                            # if edge doesnt exist, add it
                            if not G.has_edge(term, other_term):
                                G.add_edge(term, other_term,weight=1)
                            # if edge exists, increment weight
                            else:    
                                G[term][other_term]['weight'] += 1
            
        # hubs and authorities?

        return G


if __name__ == "__main__":
    import json

    # open candidates.json

    with open('data/candidates.json', 'r') as f:
        candidates = json.load(f)

    with open('data/transcriptions.json', 'r') as f:
        transcriptions = json.load(f)

    pp = CandidatePostProcessor(transcriptions)
    filtered = pp.filter_candidates(candidates)
    with open('data/filtered_candidates.json', 'w') as f:
        json.dump(filtered, f)
    print(filtered)
    G2 = pp.phrase_hierarchy_graph(list(filtered.keys()))
    nx.write_gml(G2, "phrase_hierarchy.gml")