import lecture_search.utils.tokenizer as tokenizer


def test_tokenize_doc():
    doc_obj = {
        "doc_id": "test_doc",
        "sents": [
            {
                "index": 1,
                "start": 0,
                "end": 1,
                "content": "This is a test sentence.",
            },
            {
                "index": 2,
                "start": 0,
                "end": 1,
                "content": "This is another test sentence.",
            },
        ],
    }
    expected_tokenized = {
        "doc_id": "test_doc",
        "tokenized_sents": [
            ["ĠThis", "Ġis", "Ġa", "Ġtest", "Ġsentence", "."],
            ["ĠThis", "Ġis", "Ġanother", "Ġtest", "Ġsentence", "."],
        ],
    }
    expected_id_tokenized = {
        "doc_id": "test_doc",
        "sents": [
            {"ids": [152, 16, 10, 1296, 3645, 4], "widxs": [0, 1, 2, 3, 4]},
            {"ids": [152, 16, 277, 1296, 3645, 4], "widxs": [0, 1, 2, 3, 4]},
        ],
    }
    tokenized_doc, tokenized_id_doc = tokenizer.UCPhraseTokenizer().tokenize_doc(
        doc_obj
    )
    assert tokenized_doc == expected_tokenized
    assert tokenized_id_doc == expected_id_tokenized
