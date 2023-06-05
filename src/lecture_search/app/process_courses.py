from enum import Enum
import lecture_search.app.cozo_client as cozo_db
from pathlib import Path
import pycozo
import re
from typing import List, Dict, Tuple, Optional
import pypdf
from nltk import sent_tokenize
import srt
from sentence_transformers import SentenceTransformer, CrossEncoder, util
from tqdm import tqdm


class AssetType(str, Enum):
    VIDEO = "video"
    TEXT = "text"
    PDF = "pdf"
    KADZINSKI_NOTES_PDF = "kadzinski_notes_pdf"


ASSETS_PATH = Path("./src/lecture_search/app/assets")
COURSES_PATH = ASSETS_PATH / "courses"
PROCESSED_PATH = ASSETS_PATH / "processed"


bi_encoder = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")
bi_encoder.max_seq_length = 256
top_k = 32


def parse_file_relation(path):
    files_relation = {
        "courses_files": {"headers": ["path", "type", "lecture", "course"], "rows": []}
    }

    for course in path.iterdir():
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
                    files_relation["courses_files"]["rows"].append(
                        [
                            str(
                                asset.relative_to(
                                    "./src/lecture_search/app/assets"
                                ).as_posix()
                            ),
                            asset_type.value,
                            lecture.name,
                            course.name,
                        ]
                    )
                else:
                    print("Unknown asset type: ", asset)

    return files_relation


def pdf_sentences_relation(path, paragraphs):
    slide_sentences_relation = {
        "slide_sentences": {
            "headers": ["path", "slide_id", "sentence_id", "sentence"],
            "rows": [],
        }
    }
    for slide_id, paragraph in enumerate(paragraphs):
        sentences = sent_tokenize(paragraph.replace("\n", " "))
        for sentence_id, sentence in enumerate(sentences):
            slide_sentences_relation["slide_sentences"]["rows"].append(
                [path, slide_id, sentence_id, sentence]
            )
    return slide_sentences_relation


def video_sentences_relation(path, subtitles):
    video_sentences_relation = {
        "video_sentences": {"headers": ["path", "start", "end", "sentence"], "rows": []}
    }
    for subtitle in subtitles:
        video_sentences_relation["video_sentences"]["rows"].append(
            [
                path,
                subtitle.start.total_seconds(),
                subtitle.end.total_seconds(),
                subtitle.content,
            ]
        )
    return video_sentences_relation


import json


def write_array_to_file(path, array):
    with open(path, "w") as f:
        json.dump(array, f)


def update_files(force=False):
    client = pycozo.Client(
        "sqlite", r"./src/lecture_search/app/assets/database_test.db"
    )
    try:
        cozo_db.create_course_files_relation(client)
    except:
        print("File relation already exists")

    # find all files
    file_relation = parse_file_relation(COURSES_PATH)
    cozo_db.import_relations(client, file_relation)

    try:
        cozo_db.create_reference_assets_relation(client)
    except:
        print("Reference relation already exists")

    try:
        cozo_db.create_slide_sentences_relation(client)
    except:
        print("Slide sentences relation already exists")

    try:
        cozo_db.create_video_sentences_relation(client)
    except:
        print("Video sentences relation already exists")

    kadzinski = cozo_db.get_files(client, type=AssetType.KADZINSKI_NOTES_PDF)
    for row in kadzinski.itertuples():
        text_path = PROCESSED_PATH / Path(row.path).with_suffix(".json").name
        if not text_path.exists():
            text = read_pdf_kadzinski_notes(row.path)
            relation = pdf_sentences_relation(row.path, text)
            cozo_db.import_relations(client, relation)

    pdf = cozo_db.get_files(client, type=AssetType.PDF)
    for row in pdf.itertuples():
        text_path = PROCESSED_PATH / Path(row.path).with_suffix(".json").name
        if not text_path.exists():
            text = read_pdf_text(row.path)
            relation = pdf_sentences_relation(row.path, text)
            cozo_db.import_relations(client, relation)

    video = cozo_db.get_files(client, type=AssetType.VIDEO)
    for row in video.itertuples():
        text_path = PROCESSED_PATH / Path(row.path).with_suffix(".srt").name
        if not text_path.exists():
            print("Transcription for", row.path, "missing")
        elif False:
            subtitles = list(srt.parse(open(text_path, "r").read()))
            relation = video_sentences_relation(row.path, subtitles)
            cozo_db.import_relations(client, relation)

    try:
        cozo_db.create_fts_index(client)
    except:
        print("FTS index already exists")

    try:
        cozo_db.create_passages_relations(client)
    except:
        print("Passages relations already exists")
    if force:
        embed_slides(client)
        embed_videos(client)

    try:
        cozo_db.create_hnsw_index(client)
    except:
        print("HNSW index already exists")

def read_pdf_kadzinski_notes(kadzinski_notes_path):
    kadzinski_notes_pattern = re.compile(r"\[[0-9]+\]")
    pdf_path = ASSETS_PATH / kadzinski_notes_path
    doc = pypdf.PdfReader(open(pdf_path, "rb")).pages
    notes = []
    for page in doc:
        page_text = page.extract_text()
        for match in kadzinski_notes_pattern.finditer(page_text):
            notes.append(page_text[match.end() :])
    return notes


def read_pdf_text(pdf_path):
    pdf_path = ASSETS_PATH / pdf_path
    doc = pypdf.PdfReader(open(pdf_path, "rb")).pages
    text = []
    for page in doc:
        text.append(page.extract_text())
    return text


def make_passages_slides(sentences):
    passages = []
    for name, group in sentences:
        candidate_passage = ""
        end_idx = 0
        for start_idx in range(0, len(group)):
            candidate_passage = ""
            end_idx = start_idx
            next_passage = group.sentence.iloc[end_idx]

            while len(next_passage) < 256 and end_idx < len(group):
                candidate_passage = next_passage
                next_passage += group.sentence.iloc[end_idx]
                end_idx = min(end_idx + 1, len(group))
            if len(candidate_passage) == 0:
                end_idx = start_idx
                candidate_passage = group.sentence.iloc[start_idx]

            # print(candidate_passage)
            passages.append(
                {
                    "passage": candidate_passage,
                    "path": group.path.iloc[0],
                    "slide_id": group.slide_id.iloc[0],
                    "start_sentence_id": start_idx,
                    "end_sentence_id": end_idx,
                }
            )

            if end_idx == len(group):
                break

    return passages


def embed_slides(client):
    sentences = cozo_db.get_slide_sentences(client)
    passages = make_passages_slides(sentences)

    for passage in tqdm(passages, desc="Embedding passages", total=len(passages)):
        passage["embedding"] = bi_encoder.encode(passage["passage"])

    passage_relation = {
        "passages_slides": {
            "headers": [
                "path",
                "slide_id",
                "start_sentence_id",
                "end_sentence_id",
                "embedding",
            ],
            "rows": [],
        }
    }
    for passage in passages:
        passage_relation["passages_slides"]["rows"].append(
            [
                passage["path"],
                passage["slide_id"],
                passage["start_sentence_id"],
                passage["end_sentence_id"],
                passage["embedding"].tolist(),
            ]
        )

    cozo_db.import_relations(client, passage_relation)


def make_passages_videos(sentences):
    passages = []
    for name, group in sentences:
        candidate_passage = ""
        end_idx = 0
        for start_idx in range(0, len(group)):
            candidate_passage = ""
            end_idx = start_idx
            next_passage = group.sentence.iloc[end_idx]

            while len(next_passage) < 256 and end_idx < len(group):
                candidate_passage = next_passage
                next_passage += group.sentence.iloc[end_idx]
                end_idx = min(end_idx + 1, len(group))
            if len(candidate_passage) == 0:
                end_idx = start_idx
                candidate_passage = group.sentence.iloc[start_idx]

            # print(candidate_passage)
            print(start_idx, end_idx)
            passages.append(
                {
                    "passage": candidate_passage,
                    "path": group.path.iloc[0],
                    "start": group.start.iloc[start_idx],
                    "end": group.end.iloc[min(end_idx, len(group) - 1)],
                }
            )

            if end_idx == len(group):
                break

    return passages


def embed_videos(client):
    sentences = cozo_db.get_video_sentences(client)
    print(sentences)
    passages = make_passages_videos(sentences)

    for passage in tqdm(passages, desc="Embedding passages", total=len(passages)):
        passage["embedding"] = bi_encoder.encode(passage["passage"])

    passage_relation = {
        "passages_videos": {
            "headers": [
                "path",
                "start",
                "end",
                "embedding",
            ],
            "rows": [],
        }
    }
    for passage in passages:
        passage_relation["passages_videos"]["rows"].append(
            [
                passage["path"],
                passage["start"],
                passage["end"],
                passage["embedding"].tolist(),
            ]
        )

    cozo_db.import_relations(client, passage_relation)


update_files(force=False)
