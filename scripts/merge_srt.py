# read srt
import lecture_search.utils.srt_connector as srt_connector
import nltk

english_vocab = set(w.lower() for w in nltk.corpus.words.words())
srt_files = [
    r"assets\transcriptions\Decision Analysis Introduction to Multiple Objective Optimization - Classical Optimization Methods.srt",
    r"assets\transcriptions\Decision Analysis Introduction to Evolutionary Multiple Objective Optimization.srt",
    r"assets\transcriptions\Decision Analysis Game Theory - Solution Concepts in Strategic Games.srt",
    r"assets\transcriptions\Decision Analysis Game Theory - Congestion and Extensive Games.srt",
]

for srt_file in srt_files:
    subtitles = srt_connector.SrtConnector.parse_srt_file(srt_file)
    merged_subtitles = srt_connector.SrtConnector.merge_sentences(subtitles)
    # within each sentence, merge word with next one if it is a word

    for i in range(len(merged_subtitles)):
        content = merged_subtitles[i].content
        current_sentence = ""
        current_word = ""
        for word in merged_subtitles[0].content.split():
            current_word += word
            if current_word.lower() in english_vocab:
                current_sentence += " " + current_word
                current_word = ""

    srt_connector.SrtConnector.save_srt(srt_file + "1", merged_subtitles)
