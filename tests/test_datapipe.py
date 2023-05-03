import lecture_search.utils.datapipe as datapipe
from torchdata.datapipes.iter import IterableWrapper


# run with pytest -s -v tests\test_datapipe.py
def test_datapipe():
    id_tokenized = [
        {
            "doc_id": "test_doc",
            "sents": [
                {"ids": [152, 16, 10, 1296, 3645, 4], "widxs": [0, 1, 2, 3, 4]},
                {"ids": [152, 16, 277, 1296, 3645], "widxs": [0, 1, 2, 3]},
            ],
        },
        {
            "doc_id": "test_doc2",
            "sents": [
                {"ids": [152, 16, 10, 1296, 3645, 4], "widxs": [0, 1, 2, 3, 4]},
                {"ids": [152, 16, 277, 1296, 3645], "widxs": [0, 1, 2, 3]},
            ],
        },
    ]

    doc_len, sent_id_to_ids, sents = datapipe.process_docs(IterableWrapper(id_tokenized))
    assert list(doc_len) == [("test_doc", 2), ("test_doc2", 2)]
    sents_list = list(sents)
    assert len(sents_list) == 1
    assert (
        len(sents_list[0]) == 4
    )  # original_sentence_ids, input_ids, input_masks, possible_spans
    assert sents_list[0][0] == [1, 3, 0, 2]  # sorted from shortest to longest
    assert list(sents_list[0][1].size()) == [4, 7]
    assert sents_list[0][1][0][0] == 0  # beggining of sentence
    assert sents_list[0][1][0][6] == 1  # padding
    assert list(sents_list[0][2].size()) == [4, 7]
    assert sents_list[0][2][0][6] == 0  # padding
