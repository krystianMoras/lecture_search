from llama_index.node_parser import SimpleNodeParser
from typing import Set, List
from nltk import word_tokenize
from nltk.stem import SnowballStemmer
import string

STEMMER = SnowballStemmer('porter', ignore_stopwords=False)
from llama_index.indices.keyword_table.query import BaseGPTKeywordTableQuery

class KeyPhraseTableQuery(BaseGPTKeywordTableQuery):
    def __init__(self,key_phrases: Set[str], **kwargs) -> None:

        self.key_phrases = key_phrases
        super().__init__(**kwargs)

    def _get_keywords(self, query_str: str) -> List[str]:
        """Extract keywords."""
        words = word_tokenize(query_str)
        # remove punctuation from words
        words = [w for w in words if w not in string.punctuation]
        stemmed = " ".join([STEMMER.stem(w) for w in words])
        phrases = [phrase for phrase in self.key_phrases if phrase in stemmed]
        return phrases
    


from llama_index.indices.keyword_table.base import BaseGPTKeywordTableIndex
from typing import Any, Optional, Sequence, Set
from llama_index.indices.base import QueryMap
from llama_index.indices.query.schema import QueryMode


class KeyPhraseTableIndex(BaseGPTKeywordTableIndex):
    """KeywordTableIndex with a restricted set of keywords."""
    def __init__(
        self,
        key_phrases: Set[str],
        **kwargs: Any,
    ) -> None:
        """Initialize params."""
        self.key_phrases = key_phrases
        super().__init__(
            **kwargs,
        )

    @classmethod
    def get_query_map(self) -> QueryMap:
        print("get query map")
        """Get query map."""
        return {
            QueryMode.DEFAULT: KeyPhraseTableQuery,
        }

    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract keywords from text."""
        words = word_tokenize(text)
        # remove punctuation from words
        words = [w for w in words if w not in string.punctuation]
        stemmed = " ".join([STEMMER.stem(w) for w in words])
        phrases = [phrase for phrase in self.key_phrases if phrase in stemmed]
        return set(phrases)
    
import llama_index.indices.registry
from llama_index.data_structs.struct_type import IndexStructType
llama_index.indices.registry.INDEX_STRUCT_TYPE_TO_INDEX_CLASS [IndexStructType.KEYWORD_TABLE] = KeyPhraseTableIndex

llama_index.indices.registry.INDEX_STRUT_TYPE_TO_QUERY_MAP = {
    index_type: index_cls.get_query_map()
    for index_type, index_cls in llama_index.indices.registry.INDEX_STRUCT_TYPE_TO_INDEX_CLASS.items()
}


if __name__ == "__main__":
    
    from llama_index import LLMPredictor, ServiceContext

    from langchain.llms.fake import FakeListLLM
    from langchain.llms.base import LLM

    class FakeListLLM(LLM):
        """Fake LLM wrapper for testing purposes."""

        i: int = 0

        @property
        def _llm_type(self) -> str:
            return "fake-list"

        def _call(self, prompt: str, stop = None) -> str:
            return prompt

        @property
        def _identifying_params(self):
            return {}
    llm = FakeListLLM()
    llm_predictor = LLMPredictor(llm=llm)

    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)


    import networkx as nx
    G = nx.read_gml(r"data/phrase_hierarchy.gml")

    from lecture_search.utils.slide_notes_connector import SlideNotesConnector
    from pathlib import Path
    da_pattern = r'\[[0-9]+\]'
    documents = SlideNotesConnector().load_data([Path("decision_analysis/da-lec1-notes.pdf"),Path("decision_analysis/da-lec2-notes.pdf")],da_pattern)

    nodes = SimpleNodeParser().get_nodes_from_documents(documents)

    key_phrase_table_index = KeyPhraseTableIndex(nodes = nodes,service_context=service_context,key_phrases=set(G.nodes))
    print(key_phrase_table_index.query("preference index",mode=QueryMode.DEFAULT,key_phrases=set(G.nodes)))