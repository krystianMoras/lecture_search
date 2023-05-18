import transformers  # type: ignore


class UCPhraseTokenizer:
    MAX_SENT_LEN = 64
    GPT_TOKEN = "Ġ"  # GPT2 tokenizer token for space
    LM_TOKENIZER = transformers.RobertaTokenizerFast.from_pretrained(
        "allenai/cs_roberta_base"
    )

    @staticmethod
    def get_batches(input_list, batch_size):
        return [
            input_list[i : i + batch_size]
            for i in range(0, len(input_list), batch_size)
        ]

    def tokenize_sents(self, sents):
        tokenized_sents = [
            self.LM_TOKENIZER.tokenize(" " + s["content"]) for s in sents
        ]
        return tokenized_sents

    def batch_tokenized_sents(self, tokenized_sents):
        cleaned_tokenized_sents = []
        for tokens in tokenized_sents:
            tokens_batch = UCPhraseTokenizer.get_batches(
                tokens, batch_size=self.MAX_SENT_LEN
            )
            cleaned_tokenized_sents += tokens_batch
        return cleaned_tokenized_sents

    def tokens_to_ids(self, tokens):
        widxs = [
            i for i, token in enumerate(tokens) if token.startswith(self.GPT_TOKEN)
        ]  # the indices of start of words
        ids = self.LM_TOKENIZER.convert_tokens_to_ids(tokens)
        return ids, widxs

    def sents_to_ids(self, tokenized_sents):
        id_sents = []
        for tokens in tokenized_sents:
            ids, widxs = self.tokens_to_ids(tokens)
            id_sents.append({"ids": ids, "widxs": widxs})
        return id_sents

    def tokenize_doc(self, doc_obj):
        doc_id = doc_obj["doc_id"]
        sents = doc_obj["sents"]
        tokenized_sents = self.tokenize_sents(sents)
        cleaned_tokenized_sents = self.batch_tokenized_sents(tokenized_sents)

        tokenized_doc = {"doc_id": doc_id, "tokenized_sents": cleaned_tokenized_sents}
        tokenized_id_doc = {
            "doc_id": doc_id,
            "sents": self.sents_to_ids(cleaned_tokenized_sents),
        }
        return tokenized_doc, tokenized_id_doc

    def roberta_tokens_to_str(self, tokens):
        return "".join(tokens).replace(self.GPT_TOKEN, " ").strip()

    def ids_to_tokens(self, ids):
        tokens = self.LM_TOKENIZER.convert_ids_to_tokens(ids)

        return tokens
