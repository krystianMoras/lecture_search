import json
import typing

from nltk import SnowballStemmer  # type: ignore
from nltk.tokenize import word_tokenize  # type: ignore

STEMMER = SnowballStemmer("porter", ignore_stopwords=False)
phrases_path = r"data\results_decision_analysis.json"


def get_phrases_for_context(filenames, current_text):
    with open(phrases_path, "r") as f:
        phrases = json.load(f)

    phrases_for_context = set()

    for file in filenames:
        if file not in phrases:
            continue
        phrases_for_context.update(phrases[file])
    phrases_for_context = {
        phrase for phrase in phrases_for_context if phrase in current_text
    }
    return list(phrases_for_context)


def get_candidates(text, phrases):
    words = word_tokenize(text)
    stemmed_words = []
    for word in words:
        stemmed_words.append(STEMMER.stem(word).lower())
    candidates = []
    for phrase in phrases:
        stemmed_phrase = [STEMMER.stem(word.lower()) for word in phrase.split(" ")]
        if find_occurence(stemmed_phrase, stemmed_words):
            candidates.append(phrase)
    return candidates


def save_phrases(path, phrases, doc_id):
    try:
        with open(path, "r") as f:
            last_json = json.load(f)
            last_json[doc_id] = phrases
    except FileNotFoundError:
        last_json = {doc_id: phrases}

    with open(path, "w") as f:
        json.dump(last_json, f)


def find_occurence(search: typing.List[str], searched: typing.List[str]):
    all_indices = [i for i, x in enumerate(searched) if x == search[0]]
    for index in all_indices:
        if search == searched[index : index + len(search)]:
            return True
    return False


def find_all_occurrences(search: typing.List[str], searched: typing.List[str]):
    all_indices = [i for i, x in enumerate(searched) if x == search[0]]
    occurence_ids = []
    for index in all_indices:
        if search == searched[index : index + len(search)]:
            occurence_ids.append((index, index + len(search)))
    return occurence_ids


def find_occurences_to_highlight(
    candidates: typing.List[str], words_stemmed: typing.List[str]
) -> typing.List[bool]:
    all_occurences = []
    for candidate in candidates:
        candidate_split = candidate.split(" ")

        occurences = find_all_occurrences(candidate_split, words_stemmed)
        if len(occurences) > 0:
            all_occurences.extend(occurences)

    occurences = [False] * len(words_stemmed)
    for start, end in all_occurences:
        occurences[start:end] = [True] * (end - start)
    return occurences


def candidate_from_str(candidate_str):
    return " ".join([STEMMER.stem(word) for word in candidate_str.split(" ")]).lower()


def mark_text(text, phrases_stemmed):
    words = word_tokenize(text)
    stemmed_words = []
    for word in words:
        stemmed_words.append(STEMMER.stem(word).lower())

    return words, find_occurences_to_highlight(phrases_stemmed, stemmed_words)
