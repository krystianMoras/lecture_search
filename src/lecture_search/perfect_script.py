from pathlib import Path
from lecture_search.data_connectors.slide_notes_connector import SlideNotesConnector
from lecture_search.model.ucphrase_model import EmbedModel
from lecture_search.tokenizers.ucphrase_tokenizer import UCPhraseTokenizer
import json
from lecture_search.pipelines.kpe_pipeline import KPEPipeline
from lecture_search.pipelines.candidate_filter import CandidatePostProcessor
import torch


import yaml


with open("config.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

def load_model(path):

    model = EmbedModel()

    model.load_state_dict(torch.load(path))

    return model

def get_transcriptions(paths, da_pattern,transcriptions_path):

    SlideNotesConnector().load_data(paths,da_pattern,transcriptions_path)

def tokenize_transcriptions(tokenizer:UCPhraseTokenizer,transcriptions_path:Path,tokenized_transcriptions_path:Path,tokenized_id_transcriptions_path:Path) -> None:
    with open(transcriptions_path,"r") as f:
        transcriptions = json.load(f)

    tokenizer.tokenize_docs(transcriptions,tokenized_transcriptions_path,tokenized_id_transcriptions_path)

def extract_key_phrases(slides_paths):



    get_transcriptions(slides_paths, config["da_pattern"], Path(config["transcriptions_path"]))
    tokenizer = UCPhraseTokenizer()
    tokenize_transcriptions(tokenizer,Path(config["transcriptions_path"]),Path(config["tokenized_transcriptions_path"]),Path(config["tokenized_id_transcriptions_path"]))
    model = load_model(config["ucp_model_path"])
    kpe_pipeline = KPEPipeline(model,tokenizer)
    candidates = kpe_pipeline([Path(config["tokenized_id_transcriptions_path"])])

    with open(config["transcriptions_path"], 'r') as f:
        transcriptions = json.load(f)

    pp = CandidatePostProcessor(transcriptions)
    filtered = pp.filter_candidates(candidates)

    with open(config["filtered_candidates_path"], 'w') as f:
        json.dump(filtered, f)

if __name__ == "__main__":
    slides_paths = [Path("decision_analysis/da-lec1-notes.pdf"),
                    Path("decision_analysis/da-lec2-notes.pdf"),
                    Path("decision_analysis/da-lec3-notes.pdf"),
                    Path("decision_analysis/da-lec4-notes.pdf"),
                    Path("decision_analysis/da-lec5-notes.pdf"),
                    Path("decision_analysis/da-lec6-notes.pdf"),
                    Path("decision_analysis/da-lec7-notes.pdf"),
                    Path("decision_analysis/da-lec8-notes.pdf"),
                    Path("decision_analysis/da-lec9-notes.pdf"),
                    Path("decision_analysis/da-lec10-notes.pdf"),
                    Path("decision_analysis/da-lec11-notes.pdf"),
                    Path("decision_analysis/da-lec12-notes.pdf"),]
    extract_key_phrases(slides_paths)

def create_index(key_phrases):

    # create index from key phrases
    
    return index

# gradio interface

# user asks a question

question = input()

# search the index

llm_answer,materials = search(question, composite)

def search(question, composite):
    # search the index
    return llm_answer, materials_chronologically_and_hierarchally_ordered

# show answer and materials

show(llm_answer, materials)

# selectible key phrases then export to obsidian

selections = key_phrase_graph,get_selections()

# export to obsidian

export(selections)

