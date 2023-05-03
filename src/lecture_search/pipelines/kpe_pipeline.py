from torchdata.datapipes.iter import FileOpener, JsonParser, FlatMapper
from pathlib import Path
from lecture_search.pipelines.ucphrase_pipe import UCPhraseDataPipe
import torch





from lecture_search.tokenizers.ucphrase_tokenizer import UCPhraseTokenizer
from lecture_search.model.ucphrase_model import EmbedModel
from lecture_search.tokenizers.ucphrase_tokenizer import stem_cand

class KPEPipeline:

    def __init__(self, model:EmbedModel, tokenizer:UCPhraseTokenizer, is_train: bool = False, MAX_WORD_GRAM: int = 5, MAX_SUBWORD_GRAM: int = 10):
        self.model = model
        self.tokenizer = tokenizer
        self.is_train = is_train
        self.MAX_WORD_GRAM = MAX_WORD_GRAM
        self.MAX_SUBWORD_GRAM = MAX_SUBWORD_GRAM

    def __call__(self, files: list):
        # an input to pipeline should be a list of pdf files probably
        flatmap, sent_id_to_doc_id, ucphrased = KPEPipeline.preprocess_files(files, self.is_train)
        original_sentence_ids = list(flatmap) # this probably makes datapipes useless
        output = self.inference(list(ucphrased))
        # with open("span_probs.json", "w") as f:
        #     json.dump(output,f)
        candidates = self.get_candidates(original_sentence_ids,sent_id_to_doc_id, output)
        return candidates
    
    @staticmethod
    def preprocess_files(files: list, is_train: bool = False):
        # generally figure out how to do it with datapipes but its hacky for now
        jsonpipe = FileOpener(files, mode="b").parse_json_files()
        json_files = list(jsonpipe)
        pointer = 0
        sent_id_to_doc_id= {}
        for json_file in json_files:
            for doc in json_file[1]:
                # get number of sentences
                num_sents = len(doc['sents'])
                for i in range(num_sents):
                    sent_id_to_doc_id[pointer] = doc['doc_id']
                    pointer += 1
                
        flatmap = jsonpipe.flatmap(lambda x: x[1]).flatmap(lambda x: x["sents"]).enumerate() # sentence id, sentence
        max_token_bucketized = flatmap.max_token_bucketize(max_token_count=64*128,len_fn=lambda x: len(x[1]['ids']),include_padding=True)
        ucphrased = UCPhraseDataPipe(max_token_bucketized, is_train=False)

        return flatmap, sent_id_to_doc_id, ucphrased

    def inference(self, ucphrased):
        self.model.eval()
        
        return self.model.predict(ucphrased) # improve this

    def get_candidates(self,original_sentence_ids,sent_id_to_doc_id, result, threshold=0.9):

        candidates = {}
        for sentence_id, span_probs in result.items():
            for l_idx, r_idx, prob in span_probs:
                if prob > threshold:
                    print(prob)
                    tokens = self.tokenizer.sentence_ids_to_tokens(original_sentence_ids[sentence_id][1]["ids"][l_idx: r_idx + 1])
                    candidate = self.tokenizer.roberta_tokens_to_str(tokens)
                    doc_id = sent_id_to_doc_id[sentence_id]
                    if doc_id not in candidates:
                        candidates[doc_id] = []
                    candidates[doc_id].append(candidate)

                    # candidate = stem_cand(candidate)
                    # candidates.add(candidate)
        
        return candidates



if __name__ == "__main__":
    from lecture_search.model.ucphrase_model import EmbedModel
    from lecture_search.tokenizers.ucphrase_tokenizer import UCPhraseTokenizer
    import json
    model = EmbedModel()
    model.load_state_dict(torch.load('models/ucphrase.pt'))
    tokenizer = UCPhraseTokenizer()

    pipeline = KPEPipeline(model, tokenizer, is_train=False)
    candidates = pipeline(["data/tokenized_id_arxiv.json"])
    
    # save to txt
    with open('candidates_arxiv.json', 'w') as f:
        json.dump(candidates, f)


