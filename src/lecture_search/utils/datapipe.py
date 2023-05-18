import typing

from torchdata.datapipes.iter import IterDataPipe  # type: ignore

from lecture_search.utils.ucphrase_pipe import UCPhraseDataPipe


def process_docs(docs_pipe: IterDataPipe) -> typing.Tuple[IterDataPipe, IterDataPipe]:
    """Process a pipe of documents into document sentence counts and sentences for UCPhraseModel"""
    doc_len = docs_pipe.map(lambda x: (x["doc_id"], len(x["sents"])))
    sent_id_to_ids = docs_pipe.flatmap(lambda x: x["sents"]).enumerate()
    sents = sent_id_to_ids.max_token_bucketize(
        max_token_count=64 * 128,
        len_fn=lambda x: len(x[1]["ids"]),
        include_padding=True,
    )
    sents = UCPhraseDataPipe(sents, is_train=False)
    return doc_len, sent_id_to_ids, sents
