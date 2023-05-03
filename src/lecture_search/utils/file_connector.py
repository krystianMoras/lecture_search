import spacy

nlp = spacy.load('en_core_web_sm')


def merge_phrases(doc):
    with doc.retokenize() as retokenizer:
        for np in list(doc.noun_chunks):
            attrs = {
                "tag": np.root.tag_,
                "lemma": np.root.lemma_,
                "ent_type": np.root.ent_type_,
            }
            retokenizer.merge(np, attrs=attrs)
    return doc

class FileConnector:

    @staticmethod
    def to_json(file):
        raise NotImplementedError

    @staticmethod
    def get_nouns(text):

        spacy_tokens = nlp(text)
        spacy_tokens = merge_phrases(spacy_tokens)
        nouns = set()
        for token in spacy_tokens:
            if token.pos_ == "NOUN":
                nouns.add(token.text)
        return nouns
    
    @staticmethod
    def get_raw_text(file):
        raise NotImplementedError



        