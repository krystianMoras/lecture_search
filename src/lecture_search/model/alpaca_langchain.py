from langchain.llms import LlamaCpp
from llama_index import LLMPredictor, ServiceContext
from typing import List, Tuple
from llama_index import Document
from lecture_search.data_connectors.slide_notes_connector import SlideNotesConnector
from pathlib import Path
from llama_index.docstore import SimpleDocumentStore
from llama_index.node_parser import SimpleNodeParser
from lecture_search.indices.keyphrase_index import KeyPhraseTableIndex
from langchain.llms.base import LLM
from llama_index import PromptHelper
import json 

class LlamaTest(LlamaCpp):
    

    def _call(self, prompt: str, stop = None) -> str:
        print(prompt,len(prompt.split()))
        return super()._call(prompt, stop)
def get_service(path: str) -> ServiceContext:
    """Get LLM."""
    llm = LlamaTest(model_path=path,n_ctx=1024)
 #   print(isinstance(llm, LlamaCpp), isinstance(llm, LLM))
    llm_predictor = LLMPredictor(llm=llm)
    max_input_size = 512
    num_output = 256
    max_chunk_overlap = 64
    prompt_helper = PromptHelper(max_input_size, num_output, max_chunk_overlap)
   # prompt_helper = PromptHelper.from_llm_predictor(llm_predictor)

    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)
    return service_context

def get_documents(paths: List[Path], da_pattern: str) -> Tuple[List[Document], SimpleDocumentStore]:
    documents = SlideNotesConnector().load_data(paths,da_pattern)

    nodes = SimpleNodeParser().get_nodes_from_documents(documents)
    docstore = SimpleDocumentStore()
    docstore.add_documents(nodes)
    return nodes, docstore

def get_key_phrases(path: str) -> List[str]:
    with open(path, "r") as f:
        key_phrases_filtered = json.load(f)
    return key_phrases_filtered.keys()

def get_index(alpaca_path, slides_paths, da_pattern, key_phrases_path):
    service_context = get_service(alpaca_path)
    nodes, docstore = get_documents(slides_paths, da_pattern)

    key_phrases = get_key_phrases(key_phrases_path)

    key_phrase_table_index = KeyPhraseTableIndex(nodes = nodes,service_context=service_context,key_phrases=key_phrases)
    return key_phrase_table_index, key_phrases

if __name__ == "__main__":
    key_phrase_table_index,key_phrases = get_index(r"models\ggml-vicuna-7b-1.1-q4_0.bin", [Path("decision_analysis/da-lec1-notes.pdf"),Path("decision_analysis/da-lec2-notes.pdf")], r'\[[0-9]+\]', r"data/filtered_candidates.json")
    print(key_phrase_table_index.query("Describe partial ranking?",key_phrases=key_phrases))
