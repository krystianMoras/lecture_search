
def pipeline(files):
    key_phrases = model(files)
    key_phrases = filter(key_phrases)
    key_phrases += heuristics(files)
    return key_phrases

# pass files to the pipeline
files = []

key_phrases = pipeline(files) # key phrases are already filtered, 

# visualize the key phrases and their relation

visualize(key_phrases)

# create index from key phrases

index = create_index(key_phrases)

# create index from embeddings

index = create_index(files)

# merge two indexes somehow

composite = merge(index1, index2)

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

