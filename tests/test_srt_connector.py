# import timedelta
from datetime import timedelta

import srt

from lecture_search.utils.srt_connector import SrtConnector


def test_parse_srt_file():
    assert SrtConnector.parse_srt_file("filethatdoesnotexist") == []

    assert len(SrtConnector.parse_srt_file("tests/test.srt")) == 8


# run this function with
def test_merge_sentences():
    subtitle_1 = srt.Subtitle(
        index=1,
        start=timedelta(seconds=0),
        end=timedelta(seconds=1),
        content="Hello world, today",
    )
    subtitle_2 = srt.Subtitle(
        index=2,
        start=timedelta(seconds=1),
        end=timedelta(seconds=2),
        content="is a good day.",
    )
    subtitle_3 = srt.Subtitle(
        index=3, start=timedelta(seconds=2), end=timedelta(seconds=3), content="How"
    )
    subtitle_4 = srt.Subtitle(
        index=4,
        start=timedelta(seconds=3),
        end=timedelta(seconds=4),
        content="are you?",
    )
    subtitle_5 = srt.Subtitle(
        index=5,
        start=timedelta(seconds=4),
        end=timedelta(seconds=5),
        content="I am fine!",
    )
    subtitles = [subtitle_1, subtitle_2, subtitle_3, subtitle_4, subtitle_5]
    merged_subtitles = SrtConnector.merge_sentences(subtitles)
    assert len(merged_subtitles) == 3
    assert merged_subtitles[0].content == "Hello world, today is a good day."
    assert merged_subtitles[1].content == "How are you?"
    assert merged_subtitles[2].content == "I am fine!"
    assert merged_subtitles[0].start == timedelta(seconds=0)
    assert merged_subtitles[0].end == timedelta(seconds=2)


def test_subtitles_to_json():
    subtitle_1 = srt.Subtitle(
        index=1,
        start=timedelta(seconds=0),
        end=timedelta(seconds=1),
        content="Hello world",
    )
    subtitle_2 = srt.Subtitle(
        index=2,
        start=timedelta(seconds=1),
        end=timedelta(seconds=2),
        content="How are you",
    )
    subtitle_3 = srt.Subtitle(
        index=3,
        start=timedelta(seconds=2),
        end=timedelta(seconds=3),
        content="I am fine",
    )
    subtitles = [subtitle_1, subtitle_2, subtitle_3]
    json = SrtConnector.subtitles_to_json(subtitles, "test")

    assert json["doc_id"] == "test"
    assert len(json["sents"]) == 3
    assert json["sents"][0]["index"] == 1
    assert json["sents"][1]["start"] == 1
    assert json["sents"][1]["end"] == 2
    assert json["sents"][2]["content"] == "I am fine"


# run with pytest -s tests/test_srt_preprocess.py
