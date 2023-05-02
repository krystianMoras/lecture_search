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

