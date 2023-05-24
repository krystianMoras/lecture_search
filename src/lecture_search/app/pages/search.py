import dash  # type: ignore
from dash import html  # type: ignore
import lecture_search.app.cozo_client as cozodb
from pathlib import Path
import fitz
import base64
import dash_mantine_components as dmc

dash.register_page(__name__, path_template="/search")


def build_kadzinski_notes_result(result):
    path = Path("./src/lecture_search/app/assets") / result["referred_to"]

    doc = fitz.open(path)
    page = doc[result["slide_id"]]
    pix = page.get_pixmap()
    bytes = pix.tobytes()
    dataurl = "data:image/png;base64," + base64.b64encode(bytes).decode("utf-8")
    image = html.Img(src=dataurl, style={"height": "50vh"})

    return dmc.Card(
        [
            dmc.Group(
                [
                    dmc.CardSection(image),
                    dmc.CardSection(
                        dmc.Paper(result["sentence"], shadow="sm", p="sm", radius="sm")
                    ),
                    dmc.Anchor(
                        "Open in context ->",
                        href=result["referred_to"] + f"?page={result['slide_id']}",
                        style={"bottom": "15", "right": "15"},
                    ),
                ],
                style={"flex-direction": "column"},
            )
        ],
        # visible border
        style={"border": "1px solid black"},
    )


def build_pdf_result(result):
    path = Path("./src/lecture_search/app/assets") / result["referred_to"]

    doc = fitz.open(path)
    page = doc[result["slide_id"]]
    pix = page.get_pixmap()
    bytes = pix.tobytes()
    dataurl = "data:image/png;base64," + base64.b64encode(bytes).decode("utf-8")
    image = html.Img(src=dataurl, style={"height": "50vh"})

    return dmc.Card(
        [
            dmc.Group(
                [
                    dmc.CardSection(image),
                    # right bot corner
                    dmc.Anchor(
                        "Open in context ->",
                        href=result["referred_to"] + f"?page={result['slide_id']}",
                        style={"bottom": "15", "right": "15"},
                    ),
                ],
                style={"flex-direction": "column"},
            ),
        ],
        # visible border
        style={"border": "1px solid black"},
    )


def build_results(results):
    result_cards = []
    for result in results:
        if result["referred_type"] == "kadzinski_notes_pdf":
            result_cards.append(build_kadzinski_notes_result(result))
        elif result["referred_type"] == "pdf":
            result_cards.append(build_pdf_result(result))
    return result_cards


def preprocess_query(query):
    # replace non alphanumeric characters with space
    query = "".join(
        [c if c.isalnum() else " " for c in query.lower().replace("\n", " ")]
    )
    return query


def layout(query, type):
    # slide_id, referred_to, sentence, referred_type
    if type == "key_word":
        query = preprocess_query(query)
        results = cozodb.full_text_search(query)
    elif type == "semantic":
        results = cozodb.semantic_search(query)
    return html.Div(
        [
            html.H1("Search page"),
            html.Div(children=build_results(results)),
        ]
    )
