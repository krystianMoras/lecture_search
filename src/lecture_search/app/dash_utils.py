import dash
import dash_mantine_components as dmc
import typing
import utils

def get_transcription_cards(transcriptions:dict) -> typing.List[dmc.Paper]:
    
    #print(words_stem_map)
    _,candidates = utils.get_filtered_candidates("data/filtered_candidates.json")

    
    papers = []
    for lecture_slide_id in transcriptions:
        words,words_stemmed = utils.get_words_stem_map(transcriptions[lecture_slide_id])
        highlights = utils.find_words_to_highlight(candidates, words, words_stemmed)
        papers.append(
            dmc.Paper(
                [
                    dmc.Highlight(transcriptions[lecture_slide_id],highlight=highlights),
                ],
                shadow="sm",
                p="xs",
                withBorder=True
        )
    )
    return papers

def get_candidate_badges(candidates) -> typing.List[dmc.Badge]:
    badges = []
    for candidate in candidates:
        badges.append(
            dmc.Badge(
                candidate,
                color="blue",
                variant="outline",
                size="lg",
                mb="xs",
                mr="xs",
            )
        )
    return badges