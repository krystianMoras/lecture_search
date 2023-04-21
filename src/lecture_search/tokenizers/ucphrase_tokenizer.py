import transformers
from pathlib import Path
import json
from nltk.tokenize import sent_tokenize

from nltk.stem.snowball import SnowballStemmer
STEMMER = SnowballStemmer('porter', ignore_stopwords=False)


def stem_word(w):
    return STEMMER.stem(w)


def stem_cand(c):
    return ' '.join([stem_word(w) for w in c.split()]).lower()

import string
PUNCS = set(string.punctuation) - {'-'}

class UCPhraseTokenizer:

    MAX_SENT_LEN = 64
    GPT_TOKEN = 'Ġ' # GPT2 tokenizer token for space
    LM_TOKENIZER = transformers.RobertaTokenizerFast.from_pretrained("allenai/cs_roberta_base")

    @staticmethod
    def split_sentences(text):
        return sent_tokenize(text)
    
    @staticmethod
    def get_batches(input_list, batch_size):
        return [input_list[i: i + batch_size] for i in range(0, len(input_list), batch_size)]
    
    def tokenize_text(self, text):
        sents = UCPhraseTokenizer.split_sentences(text)
        tokenized_sents = [self.LM_TOKENIZER.tokenize(' ' + s, add_special_tokens=False) for s in sents]
        cleaned_tokenized_sents = []
        for tokens in tokenized_sents:
            tokens_batch = UCPhraseTokenizer.get_batches(tokens, batch_size=self.MAX_SENT_LEN)
            cleaned_tokenized_sents += tokens_batch
        return cleaned_tokenized_sents
    
    def tokenize_doc(self, doc_id, doc_text):
        tokenized_sents = self.tokenize_text(doc_text)
        tokenized_doc = {'doc_id': doc_id, 'tokenized_sents': tokenized_sents}

        tokenized_id_doc = {'doc_id': doc_id, 'sents': []}
        for tokens in tokenized_sents:
            widxs = [i for i, token in enumerate(tokens) if token.startswith(self.GPT_TOKEN)]  # the indices of start of words
            ids = self.LM_TOKENIZER.convert_tokens_to_ids(tokens)
            tokenized_id_doc['sents'].append({'ids': ids, 'widxs': widxs})
        return tokenized_doc, tokenized_id_doc
    
    def tokenize_docs(self, docs:dict,tokenized_docs_path:Path,tokenized_id_docs_path:Path):

        tokenized_docs = []
        tokenized_id_docs = []
        for doc_id,doc_text in docs.items():
            tokenized_doc, tokenized_id_doc = self.tokenize_doc(doc_id,doc_text)
            tokenized_docs.append(tokenized_doc)
            tokenized_id_docs.append(tokenized_id_doc)

        
        with open(tokenized_docs_path,"w") as f:
            json.dump(tokenized_docs,f)
        with open(tokenized_id_docs_path,"w") as f:
            json.dump(tokenized_id_docs,f)

    def roberta_tokens_to_str(self,tokens):
        return ''.join(tokens).replace(self.GPT_TOKEN, ' ').strip()
    
    def sentence_ids_to_tokens(self,sentence_ids):
        tokens = self.LM_TOKENIZER.convert_ids_to_tokens(sentence_ids)

        return tokens
    
    def stem(self,word):
        return self.LM_TOKENIZER.stem(word)
    
    def filter_punctuation(self,cands):
        return [c for c in cands if not (c[0] in PUNCS or c[-1] in PUNCS)]




if __name__ == "__main__":
    with open("data/transcriptions.json","r") as f:
        transcriptions = json.load(f)
    UCPhraseTokenizer().tokenize_docs(transcriptions,Path("data")/"tokenized_transcriptions.json",Path("data")/"tokenized_id_transcriptions.json")