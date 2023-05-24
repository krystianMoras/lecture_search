import pycozo
import pandas as pd

# singleton instance

cozo_client = pycozo.Client("sqlite", r"src\lecture_search\app\assets\database.db")
from sentence_transformers import SentenceTransformer, CrossEncoder, util

bi_encoder = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")


def get_client():
    return cozo_client


def get_assets_for_asset(asset_path: str, type: str = None) -> pd.DataFrame:
    if type is None:
        return cozo_client.run(
            """
        ?[reference, referred_to, type] := *reference_assets[reference, referred_to, type], referred_to=$asset_path
        """,
            {"asset_path": asset_path},
        )
    return cozo_client.run(
        """
        ?[reference, referred_to, type] := *reference_assets[reference, referred_to, type], referred_to=$asset_path, type=$type
        """,
        {"asset_path": asset_path, "type": type},
    )


def full_text_search(search_string: str):
    return cozo_client.run(
        """
        results[slide_id, path, sentence] := ~slide_sentences:full_text_search {slide_id,path, sentence |
            query: $query,
            k: 1000
        }
        ?[slide_id, referred_to, sentence, referred_type] := results[slide_id, path, sentence], *reference_assets[reference, referred_to, asset_type], reference=path, *courses_files[referred_to, referred_type, lecture, course]

        """,
        {"query": search_string},
    ).to_dict(orient="records")


def semantic_search(search_string: str):
    query_embedding = bi_encoder.encode(search_string)

    results = cozo_client.run(
        """
        ?[dist, path, referred_to, referred_type, slide_id, start_sentence_id, end_sentence_id] := ~passages:semantic{ path, slide_id, start_sentence_id, end_sentence_id, embedding |
            query: q,
            k: 10,
            ef: 2000,
            bind_distance: dist,
        }, q = vec($query),  *reference_assets[reference, referred_to, asset_type], reference=path, *courses_files[referred_to, referred_type, lecture, course]
        :order dist
    """,
        {"query": query_embedding.tolist()},
    )
    results["sentence"] = [None] * len(results)
    for row in results.itertuples():
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
        results.at[row.Index, "sentence"] = " ".join(passage)

    return results.to_dict(orient="records")
