import json
import typing
from enum import Enum
from functools import singledispatch
from pathlib import Path

import numpy as np
import torch
from nltk.corpus import stopwords  # type: ignore

import lecture_search.utils.kpe_pipeline as kpe_pipeline
from lecture_search.model.ucphrase_model import EmbedModel
from lecture_search.utils.slide_notes_connector import SlideNotesConnector
from lecture_search.utils.srt_connector import SrtConnector
from lecture_search.utils.tokenizer import UCPhraseTokenizer


@singledispatch
def to_serializable(val):
    """Used by default."""
    return str(val)


@to_serializable.register(np.float32)
def ts_float32(val: np.float32):
    """Used if *val* is an instance of numpy.float32."""
    return np.float64(val)


class FileTypes(str, Enum):
    PDF = ".pdf"
    DOCX = ".docx"
    TXT = ".txt"
    SRT = ".srt"


connector_map = {
    FileTypes.SRT.value: SrtConnector,
    FileTypes.PDF.value: SlideNotesConnector,
}


class KeyPhraseExtractor:
    def __init__(self, model_path, results_path: Path) -> None:
        self.results_path = results_path
        # initialize model, tokenizer, pipeline
        self.tokenizer = UCPhraseTokenizer()
        self.model = EmbedModel()
        self.model.load_state_dict(torch.load(model_path))
        self.pipeline = kpe_pipeline.KeyPhraseExtractionPipeline(
            model=self.model, tokenizer=self.tokenizer
        )
        pass

    def get_connector(self, file_path: Path):
        file_type = file_path.suffix
        # get appropriate file connector
        connector = connector_map[file_type]
        return connector

    def extract_from_files(
        self,
        file_paths: typing.List[str],
        candidate_file_name: str,
        save_intermediate=True,
    ):
        objs = []
        doc_id_to_path = {}
        for path in file_paths:
            file_path = Path(path)
            connector = self.get_connector(file_path)
            doc_id_to_path[file_path.stem] = file_path

            # get json obj
            json_obj = connector.to_json(file_path)

            if save_intermediate:
                # write obj to file
                with open(
                    self.results_path / file_path.with_suffix(".json").name, "w"
                ) as f:
                    json.dump(json_obj, f)
            objs.append(json_obj)

        # extract keyphrases
        candidates = self.pipeline(objs)

        # write raw keyphrases to file
        if save_intermediate:
            with open(self.results_path / ("raw_" + candidate_file_name), "w") as f:
                json.dump(candidates, f, default=to_serializable)

        # filter candidates
        filtered_candidates = self.filter_candidates(candidates, doc_id_to_path)

        # write filtered keyphrases to file
        with open(self.results_path / candidate_file_name, "w") as f:
            json.dump(filtered_candidates, f)

    def filter_candidates(self, candidates, doc_id_to_path):
        threshold = 0.9
        doc_filtered_candidates = {}
        for doc_id, candidate_probs in candidates.items():
            thresholded = {k for k, v in candidate_probs.items() if v > threshold}
            character_filtered = {
                cand
                for cand in thresholded
                if not any(
                    (len(w) == 1 and w.islower()) or w in stopwords.words("english")
                    for w in cand.split()
                )
            }

            # get raw text
            file_path = doc_id_to_path[doc_id]
            connector = self.get_connector(file_path)
            raw_text = connector.get_raw_text(file_path)
            # get nouns
            nouns = connector.get_nouns(raw_text)
            # filter candidates
            noun_filtered = {
                candidate
                for candidate in character_filtered
                for noun in nouns
                if candidate in noun
            }
            doc_filtered_candidates[doc_id] = list(noun_filtered)
        return doc_filtered_candidates


if __name__ == "__main__":
    kpe = KeyPhraseExtractor(
        model_path="models/ucphrase/ucphrase.pt", results_path=Path("./data")
    )
    kpe.extract_from_files(
        [
            r"assets\transcriptions\Natural language processing - lecture 4 Attention and Transformer.wav.srt.srt",
            r"assets\transcriptions\Natural language processing - lecture 6 Named Entity Recognition (NER).wav.srt.srt",
            r"assets\transcriptions\Natural language processing - lecture 7 GPT.wav.srt.srt",
        ],
        "candidates_nlp.json",
    )
