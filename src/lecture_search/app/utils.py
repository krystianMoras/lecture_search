import json
import string
from typing import List, Tuple

from nltk import SnowballStemmer  # type: ignore
from nltk.tokenize import word_tokenize  # type: ignore

STEMMER = SnowballStemmer("porter", ignore_stopwords=False)


def get_transcriptions(transcriptions_path: str) -> dict:
    with open(transcriptions_path, "r") as f:
        transcriptions = json.load(f)
        return transcriptions


def get_words_stem_map(paragraph: str) -> Tuple[List[str], List[str]]:
    # remove punctuation
    paragraph = paragraph.translate(str.maketrans("", "", string.punctuation))
    words: List[str] = word_tokenize(paragraph)
    words_stemmed = [STEMMER.stem(word) for word in words]
    return words, words_stemmed


def get_filtered_candidates(path_to_filtered: str) -> Tuple[List[str], List[str]]:
    with open(path_to_filtered, "r") as f:
        filtered_candidates = json.load(f)
        return list(filtered_candidates.keys()), list(filtered_candidates.values())


def find_all_occurrences(search: List[str], searched: List[str]):
    all_indices = [i for i, x in enumerate(searched) if x == search[0]]
    occurence_ids = []
    for index in all_indices:
        if search == searched[index : index + len(search)]:
            occurence_ids.append(index)
    return occurence_ids


def find_words_to_highlight(
    candidates: List[str],
    words: List[str],
    words_stemmed: List[str],
) -> List[str]:
    highlights = []
    for candidate in candidates:
        candidate_split = candidate.split(" ")

        occurences = find_all_occurrences(candidate_split, words_stemmed)
        if len(occurences) > 0:
            # reverse stemming to get the original words
            for occurence in occurences:
                highlight = " ".join(
                    words[occurence : occurence + len(candidate_split)]
                )
                highlights.append(highlight)
    # remove duplicates
    highlights = list(set(highlights))
    return highlights


if __name__ == "__main__":
    transcriptions = get_transcriptions("data/transcriptions.json")
    words, words_stemmed = get_words_stem_map(list(transcriptions.values())[0])
    candidates, _ = get_filtered_candidates("data/filtered_candidates.json")
