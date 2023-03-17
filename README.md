# DISCLAIMER : Work in progress

contributions, comments, suggestions are welcome

# Overview

This project's aim is to extend functionality of ekursy (moodle) platform, by enabling:

- semantic search
- knowledge graph mining

User should be able to provide materials (lecture slides, videos, articles) and a list of concepts / terms they need to learn. The algorithm should provide a "curriculum", extracted materials in an extensible manner e.g. to learn about multiplication, you should be familiar with addition, provide excerpt from materials about multiplication and suggest reading on addition.

### Semantic search

For retrieval method 

using **Retrieve and Re-rank** method described in

    https://www.sbert.net/examples/applications/retrieve_rerank/README.html

    *possible improvement might be using bm25+ ce instead


based on empirical testing this has much better results than the lfqa method

    https://haystack.deepset.ai/tutorials/12_lfqa - even with generative model

^ https://paperswithcode.com/paper/beir-a-heterogenous-benchmark-for-zero-shot


For quick summarization/explanation

    abstractive (generative) question answering models :

    https://huggingface.co/vblagoje/bart_lfqa -too much ELI5 influence, might need tuning / different model
### Knowledge graph mining


research needed, might go with 

    https://paperswithcode.com/paper/pack-together-entity-and-relation-extraction
    https://paperswithcode.com/paper/scideberta-learning-deberta-for-science
    


## Libraries / technologies :

    
    https://www.sbert.net/ - sentence transformers
    https://haystack.deepset.ai/ - pipelines, huggingface integration, support for common nlp tasks, easy to extend/augment




