import pycozo
import pandas as pd
from pathlib import Path
import nltk
from sentence_transformers import SentenceTransformer

cozo_client = None
bi_encoder = None

# Poor man's singletons
def get_bi_encoder():
    global bi_encoder
    if bi_encoder is None:
        bi_encoder = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")
    return bi_encoder

def get_client(db_path: str):
    global cozo_client
    if cozo_client is None:
        cozo_client = pycozo.Client("sqlite", db_path)
    return cozo_client


def full_text_search(cozo_client, search_string: str):
    search_string = search_string.lower()
    search_string = nltk.word_tokenize(search_string)
    # stem every word in search string
    stemmer = nltk.stem.PorterStemmer()
    search_string = [stemmer.stem(word) for word in search_string]
    search_string = " ".join(search_string)
    print(search_string)
    sentences = cozo_client.run(
        """
        ?[sentence_id, type, sentence] := ~sentences:keyword {sentence_id,type, sentence |
            query: $query,
            k: 15
        }
        """,
        {"query": search_string},
    )
    sentences["path"] = [None] * len(sentences)
    sentences["start_time"] = [None] * len(sentences)
    sentences["end_time"] = [None] * len(sentences)
    sentences["slide_i"] = [None] * len(sentences)
    sentences["sentence_i"] = [None] * len(sentences)

    
    for row in sentences.itertuples():
        if row.type == "video":
            sentence_result = cozo_client.run(
                """
                ?[sentence_id, path, start_time, end_time] := *videos_sentences[sentence_id, file_id, start_time, end_time], sentence_id=$sentence_id, *courses_files[id,path, type, lecture, course], id=file_id
                """, {"sentence_id": row.sentence_id}
            )
            sentences.loc[row.Index, "path"] = sentence_result.path.tolist()[0]
            sentences.loc[row.Index, "start_time"] = sentence_result.start_time.tolist()[0]
            sentences.loc[row.Index, "end_time"] = sentence_result.end_time.tolist()[0]
        if row.type == "kadzinski_notes_pdf" or row.type == "pdf":
            sentence_result = cozo_client.run(
                """
                ?[sentence_id, path, slide_i, sentence_i] := *slides_sentences[sentence_id, file_id, slide_i, sentence_i], sentence_id=$sentence_id, *courses_files[id,path, type, lecture, course], id=file_id
                """, {"sentence_id": row.sentence_id}
            )
            sentences.loc[row.Index, "path"] = sentence_result.path.tolist()[0]
            sentences.loc[row.Index, "slide_i"] = sentence_result.slide_i.tolist()[0]
            sentences.loc[row.Index, "sentence_i"] = sentence_result.sentence_i.tolist()[0]
    return sentences.to_dict("records")

def decode_passage(cozo_client, passage_id, passage_type):
    result_passage = {}
    if passage_type == "slide":
        
        sent_results= cozo_client.run("""
            passage[file_id,slide_i, sentence_start, sentence_end] := *passages_slides[passage_id, file_id, slide_i, sentence_start, sentence_end] , passage_id=$passage_id
            ?[sentence_id, path, slide_i, sentence_i] := *slides_sentences[sentence_id, file_id, slide_i, sentence_i], passage[file_id,slide_i, sentence_start, sentence_end], sentence_i>=sentence_start, sentence_i<sentence_end, *courses_files[id,path, type, lecture, course], id=file_id
            :order slide_i, sentence_i
            """, {"passage_id": passage_id})
        
        slide_i = sent_results.slide_i.tolist()[0]

        result_passage["slide_i"] = slide_i

    if passage_type == "video":

        sent_results = cozo_client.run("""
            passage[file_id, start_time_p, end_time_p] := *passages_videos[passage_id, file_id, start_time_p, end_time_p] , passage_id=$passage_id
            ?[sentence_id, path, start_time, end_time] := *videos_sentences[sentence_id, file_id, start_time, end_time], passage[file_id, start_time_p, end_time_p], start_time>=start_time_p, end_time<end_time_p, *courses_files[id,path, type, lecture, course], id=file_id
            :order start_time
            """, {"passage_id": passage_id})
        
        start_time = sent_results.start_time.tolist()[0]
        end_time = sent_results.end_time.tolist()[0]
        
        result_passage["start_time"] = start_time
        result_passage["end_time"] = end_time
        


    sentence_ids = sent_results.sentence_id.tolist()
    path = sent_results.path.tolist()[0]
    result_passage["path"] = path

    sentences = cozo_client.run("""
    ?[sentence_id, sentence] := *sentences[sentence_id, sentence, type], sentence_id in $sentence_ids
    """, {"sentence_ids": sentence_ids})
    total_passage = " ".join([sentences[sentences.sentence_id == sentence_id].sentence.values[0] for sentence_id in sentence_ids])

    result_passage["sentence"] = total_passage
    return result_passage

def semantic_search(cozo_client, search_string: str, bi_encoder: SentenceTransformer):
    query_embedding = bi_encoder.encode(search_string)

    results = cozo_client.run(
            """
            ?[dist, passage_id, type] := ~passages:semantic{ passage_id, type, embedding |
                query: q,
                k: 10,
                ef: 200,
                bind_distance: dist,
            }, q = vec($query),
            :order dist
        """,
            {"query": query_embedding.tolist()},
        )

    results["sentence"] = [None] * len(results)
    results["path"] = [None] * len(results)
    results["slide_i"] = [None] * len(results)
    results["start_time"] = [None] * len(results)
    results["end_time"] = [None] * len(results)

    for row in results.itertuples():
        passage_id = row.passage_id
        passage_type = row.type

        result_passage = decode_passage(cozo_client, passage_id, passage_type)
        # insert passage into results
        for key in result_passage:
            results.at[row.Index, key] = result_passage[key]
    return results.to_dict(orient="records")

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