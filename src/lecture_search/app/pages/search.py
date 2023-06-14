import dash  # type: ignore
from dash import html  # type: ignore
import lecture_search.app.cozo_client as cozodb
from pathlib import Path
import base64
import dash_mantine_components as dmc
from dash_pdf import DashPdfDocument, DashPdfPage
import lecture_search.app.constants as constants

dash.register_page(__name__, path_template="/search")


def build_pdf_result(result):
    path_to_slides = constants.courses_dir / result["path"]
    with open(path_to_slides, "rb") as pdf_file:
        encoded_string = base64.b64encode(pdf_file.read())
        # add "data:application/pdf;base64," to the front of encoded_string
        encoded_string = "data:application/pdf;base64," + encoded_string.decode("utf-8")
        pageNumber = result["slide_i"] + 1
        pdf = DashPdfDocument(
            file=encoded_string,
            children=[DashPdfPage(pageNumber=pageNumber, width=700)],
        )
        return dmc.Card(
            [
                dmc.Group(
                    [
                        dmc.CardSection(pdf),
                        dmc.CardSection(
                            dmc.Paper(
                                result["sentence"], shadow="sm", p="sm", radius="sm"
                            )
                        ),
                        # right bot corner
                        dmc.Anchor(
                            "Open in context ->",
                            href=result["path"] + f"?page={result['slide_i']}",
                            style={"bottom": "15", "right": "15"},
                        ),
                    ],
                    style={"flex-direction": "column"},
                ),
            ],
            # visible border
            style={"border": "1px solid black"},
        )


def build_video_result(result):
    path_to_video = constants.courses_dir / result["path"]
    return dmc.Card(
        [
            dmc.Group(
                [
                    dmc.CardSection(
                        # grey text of path
                        children=[
                            dmc.Text(
                                result["path"],
                                style={"color": "grey", "font-size": "10px"},
                            ),
                            # blue text of time converted from seconds to hh:mm:ss
                            dmc.Text(
                                f"{int(result['start_time']//3600)}:{int((result['start_time']%3600)//60)}:{int(result['start_time']%60)} -> {int(result['end_time']//3600)}:{int((result['end_time']%3600)//60)}:{int(result['end_time']%60)}",
                                style={"color": "blue", "font-size": "10px"},
                            ),
                            dmc.Paper(
                                result["sentence"], shadow="sm", p="sm", radius="sm"
                            ),
                        ]
                    ),
                    # right bot corner
                    dmc.Anchor(
                        "Open in context ->",
                        href=result["path"] + f"?startTime={result['start_time']}",
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
        if result["path"].endswith(".pdf"):
            result_cards.append(build_pdf_result(result))
        if result["path"].endswith(".mp4"):
            result_cards.append(build_video_result(result))

    return result_cards


def preprocess_query(query):
    # replace non alphanumeric characters with space
    query = "".join(
        [c if c.isalnum() else " " for c in query.lower().replace("\n", " ")]
    )
    return query

def layout(query, type):
    # slide_id, referred_to, sentence, referred_type
    cozo_client = cozodb.get_client(str(constants.courses_dir / "cozo_test.db"))
    if type == "key_word":
        query = preprocess_query(query)
        results = cozodb.full_text_search(cozo_client, query)
    elif type == "semantic":
        bi_encoder = cozodb.get_bi_encoder()
        results = cozodb.semantic_search(cozo_client,query, bi_encoder)
    return html.Div(
        [
            html.Div(children=build_results(results)),
        ]
    )
