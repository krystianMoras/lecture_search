from lecture_search.utils.datapipe import process_docs
from torchdata.datapipes.iter import IterableWrapper
import typing


class KeyPhraseExtractionPipeline:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.tokenized_docs = []
        self.tokenized_id_docs = []
        self.sent_id_to_doc_id = {}
        self.sent_id_to_ids = {}

    def _tokenize(self, doc_obj):
        return self.tokenizer.tokenize_doc(doc_obj)

    def preprocess(self, json_docs: typing.List[typing.Dict]):
        for doc_obj in json_docs:
            tokenized_doc, tokenized_id_doc = self._tokenize(doc_obj)
            self.tokenized_docs.append(tokenized_doc)
            self.tokenized_id_docs.append(tokenized_id_doc)
        pipe = IterableWrapper(self.tokenized_id_docs)
        doc_len, sent_id_to_ids, sents = process_docs(pipe)
        self.sent_id_to_ids = {k: v["ids"] for k, v in sent_id_to_ids}
        total_sents = 0
        for doc_id, number_of_sentences_in_doc in doc_len:
            self.sent_id_to_doc_id.update(
                {total_sents + i: doc_id for i in range(number_of_sentences_in_doc)}
            )
            total_sents += number_of_sentences_in_doc
        return sents

    def _forward(self, model_inputs):
        return self.model.predict(model_inputs)

    def postprocess(self, model_outputs):
        return self.get_candidates(model_outputs)

    def get_candidates(self, result) -> typing.Dict:
        candidates = {}
        for sentence_id, span_probs in result.items():
            for l_idx, r_idx, prob in span_probs:
                doc_id = self.sent_id_to_doc_id[sentence_id]

                tokens = self.tokenizer.ids_to_tokens(
                    self.sent_id_to_ids[sentence_id][l_idx : r_idx + 1]
                )
                candidate = self.tokenizer.roberta_tokens_to_str(tokens)
                if doc_id not in candidates:
                    candidates[doc_id] = {}
                if candidate in candidates[doc_id]:
                    candidates[doc_id][candidate] = max(
                        candidates[doc_id][candidate], prob
                    )
                else:
                    candidates[doc_id][candidate] = prob

        return candidates

    def __call__(self, json_docs: typing.List[typing.Dict]) -> typing.Dict:
        sents = self.preprocess(json_docs)
        model_inputs = self._forward(sents)
        result = self.postprocess(model_inputs)
        return result
