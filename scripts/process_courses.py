from enum import Enum
from pathlib import Path
import pycozo
import re
from typing import List, Dict, Tuple, Optional
import pypdf
from nltk import sent_tokenize
import srt
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from hashlib import sha256


class AssetType(str, Enum):
    VIDEO = "video"
    TEXT = "text"
    PDF = "pdf"
    KADZINSKI_NOTES_PDF = "kadzinski_notes_pdf"


def read_pdf_kadzinski_notes(course_dir: Path, kadzinski_notes_path:str) -> List[str]:
    kadzinski_notes_pattern = re.compile(r"\[[0-9]+\]")
    pdf_path = course_dir / kadzinski_notes_path
    doc = pypdf.PdfReader(open(pdf_path, "rb")).pages
    notes = []
    for page in doc:
        page_text = page.extract_text()
        for match in kadzinski_notes_pattern.finditer(page_text):
            notes.append(page_text[match.end() :])
    return notes


def read_pdf_text(course_dir:Path, pdf_path:str) -> List[str]:
    pdf_path = course_dir / pdf_path
    doc = pypdf.PdfReader(open(pdf_path, "rb")).pages
    text = []
    for page in doc:
        text.append(page.extract_text())
    return text


def parse_course_dir(course_dir: Path) -> Dict[str, Dict[str, List[str]]]:
    files_relation = {
        "courses_files": {"headers": ["id", "path", "type", "lecture", "course"], "rows": []}
    }

    for course in course_dir.iterdir():
        if not course.is_dir():
            continue
        for lecture in course.iterdir():
            if not lecture.is_dir():
                continue
            for asset in lecture.iterdir():
                if not asset.is_file():
                    continue
                asset_type = None
                if asset.suffix == ".mp4":
                    asset_type = AssetType.VIDEO
                elif asset.suffix == ".txt":
                    asset_type = AssetType.TEXT
                elif asset.suffix == ".pdf":
                    if asset.stem.endswith("-notes"):
                        asset_type = AssetType.KADZINSKI_NOTES_PDF
                    else:
                        asset_type = AssetType.PDF
                if asset_type is not None:
                    # sha256 encode path
                    asset_id = sha256(asset.relative_to(course_dir).as_posix().encode()).hexdigest()
                    files_relation["courses_files"]["rows"].append(
                        [
                            asset_id,
                            str(
                                asset.relative_to(course_dir).as_posix()
                            ),
                            asset_type.value,
                            lecture.name,
                            course.name,
                        ]
                    )
                else:
                    print("Unknown asset type: ", asset)
    return files_relation

# import json


# def write_array_to_file(path, array):
#     with open(path, "w") as f:
#         json.dump(array, f)


# def update_files(force=False):

#     try:
#         cozo_db.create_fts_index(client)
#     except:
#         print("FTS index already exists")

#     try:
#         cozo_db.create_passages_relations(client)
#     except:
#         print("Passages relations already exists")
#     if force:
#         embed_slides(client)
#         embed_videos(client)

#     try:
#         cozo_db.create_hnsw_index(client)
#     except:
#         print("HNSW index already exists")

import pandas as pd

def make_passages_slides(sentences, file_id):
    # change sentences to df grouped by slide_id sorted by sentence_i
    sentences = pd.DataFrame(sentences)
    sentences = sentences.groupby(["slide_i"])
    passages = []
    for name, group in sentences:
        candidate_passage = ""
        if len(group) < 3:
            # merge all sentences into one passage
            candidate_passage = " ".join(group.sentence)
            end_idx = len(group)
            start_idx = 0
            passage_id = str(uuid.uuid4())
            passages.append(
                {
                    "passage": candidate_passage,
                    "passage_id": passage_id,
                    "file_id": file_id,
                    "slide_i": group.slide_i.iloc[0],
                    "sentence_start": start_idx,
                    "sentence_end": end_idx,
                }
            )

        for start_idx in range(0, len(group)-3):
            # sliding window of 3 sentences
            end_idx = start_idx + 3
            candidate_passage = " ".join(group.sentence.iloc[start_idx:end_idx])

            passage_id = str(uuid.uuid4())
            passages.append(
                {
                    "passage": candidate_passage,
                    "passage_id": passage_id,
                    "file_id": file_id,
                    "slide_i": group.slide_i.iloc[0],
                    "sentence_start": start_idx,
                    "sentence_end": end_idx,
                }
            )

            if end_idx >= len(group):
                break

    return passages

def make_passages_videos(sentences, file_id):
    # sliding window of 3 sentences
    passages = []
    sentences = pd.DataFrame(sentences)
    for start_idx in range(0, len(sentences)-3):
        
        end_idx = start_idx + 3
        candidate_passage = " ".join(sentences.sentence.iloc[start_idx:end_idx])
        passage_id = str(uuid.uuid4())
        # passage_id => file_id, start_time, end_time
        passages.append(
            {
                "passage": candidate_passage,
                "passage_id": passage_id,
                "file_id": file_id,
                "start_time": sentences.start_time.iloc[start_idx],
                "end_time": sentences.end_time.iloc[end_idx],
            }
        )
    return passages


def passage_relation_slides(passages, bi_encoder):

    for passage in tqdm(passages, desc="Embedding passages", total=len(passages)):
        passage["embedding"] = bi_encoder.encode(passage["passage"])

    # passage_id => file_id, slide_id, sentence_start, sentence_end
    # passages {passage_id => embedding:<F32;384>, type:String}
    passage_relation = {
        "passages_slides": {
            "headers": [
                "passage_id",
                "file_id",
                "slide_i",
                "sentence_start",
                "sentence_end",
            ],
            "rows": [],
        },
        "passages": {
            "headers": [
                "passage_id",
                "embedding",
                "type",
            ],
            "rows": [],
        }
    }
    for passage in passages:
        passage_relation["passages_slides"]["rows"].append(
            [
                passage["passage_id"],
                passage["file_id"],
                passage["slide_i"],
                passage["sentence_start"],
                passage["sentence_end"],
            ]
        )
        passage_relation["passages"]["rows"].append(
            [
                passage["passage_id"],
                passage["embedding"].tolist(),
                "slide",
            ]
        )

    return passage_relation



def passage_relation_videos(passages, bi_encoder):

    for passage in tqdm(passages, desc="Embedding passages", total=len(passages)):
        passage["embedding"] = bi_encoder.encode(passage["passage"])

    # passage_id => file_id, start_time, end_time}
    # passages {passage_id => embedding:<F32;384>, type:String}
    passage_relation = {
        "passages_videos": {
            "headers": [
                "passage_id",
                "file_id",
                "start_time",
                "end_time",
            ],
            "rows": [],
        },
        "passages": {
            "headers": [
                "passage_id",
                "embedding",
                "type",
            ],
            "rows": [],
        }
    }
    for passage in passages:
        passage_relation["passages_videos"]["rows"].append(
            [
                passage["passage_id"],
                passage["file_id"],
                passage["start_time"],
                passage["end_time"],
            ]
        )
        passage_relation["passages"]["rows"].append(
            [
                passage["passage_id"],
                passage["embedding"].tolist(),
                "video",
            ]
        )
    return passage_relation

def sentence_split_slides(slide_texts):
    sentences = []
    for slide_number, paragraph in  enumerate(slide_texts):
        for sentence_number, sentence in enumerate(sent_tokenize(paragraph)):
            sentences.append(
                {
                    "slide_i": slide_number,
                    "sentence_i": sentence_number,
                    "sentence": sentence,
                }
            )
    return sentences

import lecture_search.utils.srt_connector as srt_connector
def sentence_split_videos(srt_file_path):
    subtitles = srt_connector.SrtConnector.parse_srt_file(srt_file_path)
    merged_subtitles = srt_connector.SrtConnector.merge_sentences(subtitles)

    sentences = []
    for subtitle in merged_subtitles:
        sentences.append(
            {
                "start_time": subtitle.start.total_seconds(),
                "end_time": subtitle.end.total_seconds(),
                "sentence": subtitle.content,
            }
        )
    return sentences

    

import uuid
def sentence_relation_slides(slide_sentences, file_id, type:AssetType):
    relation = {
        "sentences": {
            # sentence_id => sentence, type:String
            "headers": ["sentence_id", "sentence", "type"],
            "rows": [],
        },
        "slides_sentences": {
            # sentence_id => file_id, slide_i, sentence_i
            "headers": ["sentence_id", "file_id", "slide_i", "sentence_i"],
            "rows": [],
        }
    }

    for sentence in slide_sentences:
        sentence_id = str(uuid.uuid4())
        relation["sentences"]["rows"].append([sentence_id, sentence["sentence"], type])
        relation["slides_sentences"]["rows"].append([sentence_id, file_id, sentence["slide_i"], sentence["sentence_i"]])
    return relation

def sentence_relation_videos(video_sentences, file_id, type:AssetType):
    relation = {
        "sentences": {
            # sentence_id => sentence, type:String
            "headers": ["sentence_id", "sentence", "type"],
            "rows": [],
        },
        "videos_sentences": {
            # sentence_id => file_id, start, end
            "headers": ["sentence_id", "file_id", "start_time", "end_time"],
            "rows": [],
        }
    }

    for sentence in video_sentences:
        sentence_id = str(uuid.uuid4())
        relation["sentences"]["rows"].append([sentence_id, sentence["sentence"], type])
        relation["videos_sentences"]["rows"].append([sentence_id, file_id, sentence["start_time"], sentence["end_time"]])
    return relation

import argparse
from pathlib import Path

import pycozo

def check_relation_exists(client, relation):
    relations = client.run("::relations")
    # relations is a pandas dataframe relation name is in "name" column
    return relation in relations["name"].values

def check_file_processed(client, file_id, type):
    if type == AssetType.PDF or type == AssetType.KADZINSKI_NOTES_PDF:
        return client.run("?[count(file_id)] := *slides_sentences[sentence_id, file_id, slide_i, sentence_i], file_id=$file_id", {"file_id":file_id}).values[0][0] > 0
    elif type == AssetType.VIDEO:
        return client.run("?[count(file_id)] := *videos_sentences[sentence_id, file_id, start_time, end_time], file_id=$file_id", {"file_id":file_id}).values[0][0] > 0

def check_index_exists(client,relation, index):
    indices = client.run(f"::indices {relation}") 

    return index in indices["name"].values

from tqdm import tqdm

if __name__ == "__main__":
    bi_encoder = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")
    bi_encoder.max_seq_length = 256
    top_k = 32

    parser = argparse.ArgumentParser()
    parser.add_argument("--course_dir", required=True, help="Course directory")

    args = parser.parse_args()

    course_dir = Path(args.course_dir)

    cozo_client = pycozo.Client("sqlite", str(course_dir / "cozo_test.db"))

    # create course relation if not exists

    if not check_relation_exists(cozo_client, "courses_files"):
        cozo_client.run(":create courses_files {id => path, type, lecture, course}")
    # parse course directory
    course_relation = parse_course_dir(course_dir)
    # import course relation
    cozo_client.import_relations(course_relation)

    if not check_relation_exists(cozo_client, "sentences"):
        cozo_client.run(":create sentences {sentence_id => sentence, type:String}")

    if not check_relation_exists(cozo_client, "slides_sentences"):
        cozo_client.run(":create slides_sentences {sentence_id => file_id, slide_i, sentence_i}")

    if not check_relation_exists(cozo_client, "videos_sentences"):
        cozo_client.run(":create videos_sentences {sentence_id => file_id, start_time, end_time}")

    if not check_relation_exists(cozo_client, "passages"):
        cozo_client.run(":create passages {passage_id => embedding:<F32;384>, type:String}")

    if not check_relation_exists(cozo_client, "passages_videos"):
        cozo_client.run(":create passages_videos {passage_id => file_id, start_time, end_time}")
    
    if not check_relation_exists(cozo_client, "passages_slides"):
        cozo_client.run(":create passages_slides {passage_id => file_id, slide_i, sentence_start, sentence_end}")


    for asset in tqdm(course_relation["courses_files"]["rows"], desc="Processing assets", unit="assets", total=len(course_relation["courses_files"]["rows"])):
        if check_file_processed(cozo_client, asset[0], asset[2]):
            continue
        if not (course_dir / asset[1]).exists():
            continue
        if asset[2] == AssetType.KADZINSKI_NOTES_PDF:
            texts = read_pdf_kadzinski_notes(course_dir, asset[1])
            sentences = sentence_split_slides(texts)
            sentences_relation = sentence_relation_slides(sentences, asset[0], asset[2])
            passages = make_passages_slides(sentences, asset[0])
            passages_relation = passage_relation_slides(passages, bi_encoder)


        if asset[2] == AssetType.PDF:
            texts = read_pdf_text(course_dir, asset[1])
            sentences = sentence_split_slides(texts)
            sentences_relation = sentence_relation_slides(sentences, asset[0], asset[2])
            passages = make_passages_slides(sentences, asset[0])
            passages_relation = passage_relation_slides(passages, bi_encoder)
        
        if asset[2] == AssetType.VIDEO:
            srt_path = (course_dir / asset[1]).with_suffix(".srt")
            if not srt_path.exists():
                continue
            sentences = sentence_split_videos(srt_path)
            sentences_relation = sentence_relation_videos(sentences, asset[0], asset[2])
            passages = make_passages_videos(sentences, asset[0])
            passages_relation = passage_relation_videos(passages, bi_encoder)

        cozo_client.import_relations(sentences_relation)
        cozo_client.import_relations(passages_relation)
    
    if not check_index_exists(cozo_client, "passages", "semantic"):
        cozo_client.run(
            """
            ::hnsw create passages:semantic {
            dim: 384,
            m: 50,
            dtype: F32,
            fields: [embedding],
            distance: Cosine,
            ef_construction: 20,
            extend_candidates: false,
            keep_pruned_connections: false,
        }
        """)
    if not check_index_exists(cozo_client, "sentences", "keyword"):
        cozo_client.run(
            """
            ::fts create sentences:keyword {
            extractor: sentence,
            tokenizer: Simple,
            filters: [Lowercase,AlphaNumOnly, Stemmer('English')],
        }
        """
        )










