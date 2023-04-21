# DISCLAIMER : Work in progress

contributions, comments, suggestions are welcome

# Overview

User should be able to provide materials (lecture slides, videos, articles) and a list of concepts / terms they need to learn. The algorithm should provide a "curriculum", extracted materials in an extensible manner e.g. to learn about multiplication, you should be familiar with addition, provide excerpt from materials about multiplication and suggest reading on addition.

Additionally support simple question answering on provided materials with LLM's


### Material fetching

For key phrase extraction (KPE) task we are using [https://github.com/xgeric/UCPhrase-exp](UCPhrase) .


KPE + Heuristics -> Co-occurence matrix -> graph distance based fetching of documents 

e.g. user asks for materials on multiplication -> addition should be in close distance -> fetch all documents with this key phrase

### Reranking 

using **Retrieve and Re-rank** method described in

    https://www.sbert.net/examples/applications/retrieve_rerank/README.html

### Local question answering with llm's

for agent https://github.com/jerryjliu/llama_index

running ~7B models on just cpu with 16gb ram -> https://github.com/ggerganov/llama.cpp

alpaca model, though in future will probably switch to stablelm tuned with OA data





