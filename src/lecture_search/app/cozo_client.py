import pycozo
import pandas as pd
from pathlib import Path

# singleton instance
try:
    cozo_client = pycozo.Client(
        "sqlite", r"src\lecture_search\app\assets\database_test.db"
    )
except:
    cozo_client = None
from sentence_transformers import SentenceTransformer, CrossEncoder, util

bi_encoder = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")


def get_client():
    return cozo_client


def full_text_search(search_string: str):
    return cozo_client.run(
        """
        ?[slide_id, path, sentence] := ~slide_sentences:full_text_search {slide_id,path, sentence |
            query: $query,
            k: 15
        }
        
        """,
        {"query": search_string},
    ).to_dict(orient="records")


def semantic_search(search_string: str, isVideo=False):
    query_embedding = bi_encoder.encode(search_string)

    if not isVideo:
        results_slides = cozo_client.run(
            """
            ?[dist, path, slide_id, start_sentence_id, end_sentence_id] := ~passages_slides:semantic{ path, slide_id, start_sentence_id, end_sentence_id, embedding |
                query: q,
                k: 5,
                ef: 200,
                bind_distance: dist,
            }, q = vec($query),
            :order dist
        """,
            {"query": query_embedding.tolist()},
        )
        results_slides["sentence"] = [None] * len(results_slides)
        for row in results_slides.itertuples():
            path, slide_id, start_sentence_id, end_sentence_id = (
                row.path,
                row.slide_id,
                row.start_sentence_id,
                row.end_sentence_id,
            )

            passage = cozo_client.run(
                """
                ?[path, slide_id, sentence_id, sentence] := *slide_sentences[path, slide_id, sentence_id, sentence], path=$path, slide_id=$slide_id, sentence_id >= $start_sentence_id, sentence_id <= $end_sentence_id
            """,
                {
                    "path": path,
                    "slide_id": slide_id,
                    "start_sentence_id": start_sentence_id,
                    "end_sentence_id": end_sentence_id,
                },
            ).sentence.tolist()

            # insert passage into results
            results_slides.at[row.Index, "sentence"] = " ".join(passage)
        return results_slides.to_dict(orient="records")

    else:
        results_videos = cozo_client.run(
            """
            ?[dist, path, start, end] := ~passages_videos:semantic{ path, start, end, embedding |
                query: q,
                k: 10,
                ef: 200,
                bind_distance: dist,
            }, q = vec($query),
            :order dist
        """,
            {"query": query_embedding.tolist()},
        )

        results_videos["sentence"] = [None] * len(results_videos)
        for row in results_videos.itertuples():
            path, start_time, end_time = (
                row.path,
                row.start,
                row.end,
            )

            passage = cozo_client.run(
                """
                ?[path, start, end, sentence] := *video_sentences[path, start, end, sentence], path=$path, start>=$start_time, end<=$end_time
                :order path, start
            """,
                {
                    "path": path,
                    "start_time": start_time,
                    "end_time": end_time,
                },
            ).sentence.tolist()

            # insert passage into results
            results_videos.at[row.Index, "sentence"] = " ".join(passage)

        return results_videos.to_dict(orient="records")


def create_course_files_relation(client):
    return client.run(
        """
    :create courses_files {path => type, lecture, course}
    """
    )


def create_reference_assets_relation(client):
    return client.run(
        """
    :create reference_assets {reference, referred_to, type}
"""
    )


def import_relations(client, relation):
    return client.import_relations(relation)


def assign_text_to_pdf(client, slides_path: Path, text_path: Path):
    return client.run(
        """
            ?[reference, referred_to, type] <- [[$reference, $referred_to, $type]]
            :put reference_assets {reference, referred_to, type}
        """,
        {
            "reference": text_path.as_posix(),
            "referred_to": slides_path.as_posix(),
            "type": "text",
        },
    )


def get_files(client, type=None, course=None, lecture=None):
    type_filter = ""
    course_filter = ""
    lecture_filter = ""
    if type:
        type_filter = f', type="{type}"'
    if course:
        course_filter = f', course="{course}"'
    if lecture:
        lecture_filter = f', lecture="{lecture}"'
    return client.run(
        f"""
    ?[path, type, lecture, course] := *courses_files[path, type, lecture, course] {type_filter}{course_filter}{lecture_filter}
    """
    )


def create_slide_sentences_relation(client):
    return client.run(
        """
    :create slide_sentences {path, slide_id, sentence_id => sentence}
    """
    )


def create_video_sentences_relation(client):
    return client.run(
        """
    :create video_sentences {path, start, end => sentence}
    """
    )


def create_fts_index(client):
    client.run(
        """
        ::fts create slide_sentences:full_text_search {
        extractor: sentence,
        tokenizer: Simple,
        filters: [Lowercase,AlphaNumOnly, Stemmer('English')],
    }
    """
    )
    client.run(
        """
        ::fts create video_sentences:full_text_search {
        extractor: sentence,
        tokenizer: Simple,
        filters: [Lowercase,AlphaNumOnly, Stemmer('English')],
    }
    """
    )


def get_slide_sentences(client):
    sentences = client.run(
        """
    ?[slide_id,sentence_id, path, sentence] := *slide_sentences[path, slide_id, sentence_id, sentence]
    :order path, slide_id, sentence_id
    """
    ).groupby(["path", "slide_id"])
    return sentences


def get_video_sentences(client):
    sentences = client.run(
        """
    ?[start, end, path, sentence] := *video_sentences[path, start, end, sentence]
    :order path, start, end
    """
    ).groupby(["path"])
    return sentences


def create_passages_relations(client):
    # client.run(
    #     """
    #     :create passages_slides {path:String, slide_id:Int, start_sentence_id:Int, end_sentence_id:Int => embedding:<F32;384>}
    # """
    # )
    client.run(
        """
        :create passages_videos {path:String, start:Float, end:Float => embedding:<F32;384>}
    """
    )


def create_hnsw_index(client):
    client.run(
        """
        ::hnsw create passages_slides:semantic {
        dim: 384,
        m: 50,
        dtype: F32,
        fields: [embedding],
        distance: Cosine,
        ef_construction: 20,
        extend_candidates: false,
        keep_pruned_connections: false,
    }
    """
    )
    client.run(
        """
        ::hnsw create passages_videos:semantic {
        dim: 384,
        m: 50,
        dtype: F32,
        fields: [embedding],
        distance: Cosine,
        ef_construction: 20,
        extend_candidates: false,
        keep_pruned_connections: false,
    }
    """
    )
