# DISCLAIMER : Work in progress

contributions, comments, suggestions are welcome

# Overview

User should be able to provide materials (lecture slides, videos, articles) and a list of concepts / terms they need to learn. The algorithm should provide a "curriculum", extracted materials in an extensible manner e.g. to learn about multiplication, you should be familiar with addition, provide excerpt from materials about multiplication and suggest reading on addition.

Additionally support simple question answering on provided materials with LLM's


### Material fetching

For key phrase extraction (KPE) task we are using https://github.com/xgeric/UCPhrase-exp .


KPE + Heuristics -> Co-occurence matrix -> graph distance based fetching of documents 

e.g. user asks for materials on multiplication -> addition should be in close distance -> fetch all documents with this key phrase


### Local question answering with llm's

for agent https://github.com/jerryjliu/llama_index

running ~7B models on just cpu with 16gb ram -> https://github.com/ggerganov/llama.cpp

vicuna 7b -> https://huggingface.co/eachadea/ggml-vicuna-7b-1.1





