import lecture_search.utils.kpe_pipeline as kpe_pipeline
from lecture_search.utils.tokenizer import UCPhraseTokenizer
from lecture_search.model.ucphrase_model import EmbedModel
import torch


def test_kpe_pipeline():
    doc_objs = [
        {
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
                    "content": "This is another This is sentence.",
                },
            ],
        },
        {
            "doc_id": "test_doc2",
            "sents": [
                {
                    "index": 1,
                    "start": 0,
                    "end": 1,
                    "content": "This is crazy!",
                },
                {
                    "index": 2,
                    "start": 0,
                    "end": 1,
                    "content": "This is another crazy sentence.",
                },
            ],
        },
    ]

    tokenizer = UCPhraseTokenizer()
    model = EmbedModel()
    model.load_state_dict(torch.load("models/ucphrase/ucphrase.pt"))
    pipeline = kpe_pipeline.KeyPhraseExtractionPipeline(
        model=model, tokenizer=tokenizer
    )
    batches = list(pipeline.preprocess(doc_objs))
    assert pipeline.sent_id_to_ids == {
        0: [152, 16, 10, 1296, 3645, 4],
        1: [152, 16, 277, 152, 16, 3645, 4],
        2: [152, 16, 5373, 328],
        3: [152, 16, 277, 5373, 3645, 4],
    }
    assert pipeline.sent_id_to_doc_id == {
        0: "test_doc",
        1: "test_doc",
        2: "test_doc2",
        3: "test_doc2",
    }
    outputs = pipeline._forward(batches)
    candidates = pipeline.postprocess(outputs)
    assert len(candidates["test_doc"]) == 22
