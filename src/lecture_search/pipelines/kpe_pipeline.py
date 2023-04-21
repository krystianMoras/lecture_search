from torchdata.datapipes.iter import FileOpener, JsonParser, FlatMapper
from pathlib import Path



from torchdata.datapipes.iter import IterDataPipe
import torch
class UCPhraseDataPipe(IterDataPipe):
    # beggining of sentence token id is 0 for roberta
    # pad token id is 1 for roberta
    def __init__(self, source_dp: IterDataPipe,bos_token_id:int=0,pad_token_id:int=1, is_train:bool=False,MAX_WORD_GRAM:int = 5,MAX_SUBWORD_GRAM:int = 10,) -> None:
        super().__init__()
        self.source_dp = source_dp
        self.is_train = is_train
        self.MAX_WORD_GRAM = MAX_WORD_GRAM
        self.MAX_SUBWORD_GRAM = MAX_SUBWORD_GRAM
        self.bos_token_id = bos_token_id
        self.pad_token_id = pad_token_id

    
    @staticmethod
    def get_possible_spans(word_idxs, num_wordpieces, max_word_gram, max_subword_gram):
        possible_spans = []
        num_words = len(word_idxs)
        max_gram = min(max_word_gram, num_words)
        for len_span in range(max_gram, 1, -1):
            for i in range(num_words - len_span + 1):
                l_idx = word_idxs[i]
                r_idx = word_idxs[i + len_span] - 1 if i + len_span < num_words else num_wordpieces - 1
                if r_idx - l_idx + 1 <= max_subword_gram:
                    possible_spans.append((l_idx, r_idx))
        return possible_spans
    
    def __iter__(self):
        for sentence_batch in self.source_dp:
            
            input_ids_batch = []
            input_masks_batch = []
            pos_spans_batch = []
            neg_spans_batch = []
            possible_spans_batch = []

            max_len = max([len(sentence['ids']) for i,sentence in sentence_batch])
           # print(max_len)
            for i,sentence in sentence_batch:
                input_id = sentence['ids']
                word_idxs = sentence['widxs']
                if not self.is_train:
                    possible_spans = UCPhraseDataPipe.get_possible_spans(word_idxs, len(input_id), self.MAX_WORD_GRAM, self.MAX_SUBWORD_GRAM)
                len_diff = max_len - len(input_id)
                assert len_diff >= 0, 'Input ids must have been sorted!'
                input_ids_batch.append([self.bos_token_id] + input_id + [self.pad_token_id] * len_diff)
                input_masks_batch.append([1] + [1] * len(input_id) + [0] * len_diff)
                if self.is_train:
                    pos_spans = sentence['pos_spans']
                    neg_spans = sentence['neg_spans']
                    pos_spans_batch.append(pos_spans)
                    neg_spans_batch.append(neg_spans)
                
                else:
                    possible_spans_batch.append(possible_spans)
            original_sentence_ids = [i for i,sentence in sentence_batch]
            if self.is_train:
                yield original_sentence_ids,torch.tensor(input_ids_batch),torch.tensor(input_masks_batch),pos_spans_batch,neg_spans_batch
            else:
                yield original_sentence_ids,torch.tensor(input_ids_batch),torch.tensor(input_masks_batch),possible_spans_batch






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
        output = self.inference(list(ucphrased)[:1])
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

    def get_candidates(self,original_sentence_ids,sent_id_to_doc_id, result, threshold=0.1):

        candidates = {}
        for sentence_id, span_probs in result.items():
            for l_idx, r_idx, prob in span_probs:
                if prob > threshold:
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
    candidates = pipeline(["data/tokenized_id_transcriptions.json"])
    
    # save to txt
    with open('candidates.json', 'w') as f:
        json.dump(candidates, f)


