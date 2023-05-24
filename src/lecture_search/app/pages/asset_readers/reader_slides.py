from dash_extensions.enrich import DashBlueprint, html, Output, Input, State
from dash import callback, clientside_callback
import dash
import fitz
import base64
import dash_mantine_components as dmc
import lecture_search.app.cozo_client as cozodb
from pathlib import Path
import json

bp = DashBlueprint()
bp.layout = html.Div(
    [
        html.Div(id="placeholder_scroll", style={"visibility": "hidden"}),
        html.Div(id="pdf-container"),
    ],
    id="pdf-container-wrapper",
    style={"overflow": "scroll", "height": "90vh"},
)
# change scroll state of overflow
clientside_callback(
    """
    function(children,page){
        console.log(page)
        var pdfChildren = document.getElementById("pdf-container").children
        console.log(children)
        // get height for page number child
        var totalOffset = 0;
        if (children.length > 0) {
            for (var i = 0; i < page; i++) {
                totalOffset += pdfChildren[i].offsetHeight;
            }
            document.getElementById("pdf-container-wrapper").scrollTo(0,totalOffset);
        }
        return "";
    }
    """,
    Output("placeholder_scroll", "children"),
    Input("pdf-container", "children"),
    State("page", "data"),
)


def build_slides(file_path):
    doc = fitz.open(file_path)
    slide_imgs = []
    for page in doc:
        pix = page.get_pixmap()
        bytes = pix.tobytes()
        dataurl = "data:image/png;base64," + base64.b64encode(bytes).decode("utf-8")
        image = html.Img(src=dataurl, style={"width": "100%"})
        slide_imgs.append(image)
    return slide_imgs


@callback(
    Output("pdf-container", "children"),
    Input("file_path", "data"),
)
def on_click(file_path):
    if file_path is None:
        return dash.no_update

    slides_paths = cozodb.get_assets_for_asset(file_path, "slides")

    if len(slides_paths) > 0:
        path_to_slide_images = (
            Path("./src/lecture_search/app/assets") / slides_paths.reference[0]
        )
    else:
        path_to_slide_images = Path("./src/lecture_search/app/assets") / file_path

    slide_imgs = build_slides(path_to_slide_images)

    text_paths = cozodb.get_assets_for_asset(file_path, "text")

    slide_texts_array = None
    if len(text_paths) > 0:
        path_to_text = Path("./src/lecture_search/app/assets") / text_paths.reference[0]
        with open(path_to_text, "r") as f:
            slide_texts_array = json.load(f)

    slide_divs = []
    for i, slide in enumerate(slide_imgs):
        children = []
        children.append(dmc.CardSection(slide))

        if slide_texts_array is not None:
            text_section = dmc.CardSection(
                dmc.Paper(children=slide_texts_array[i], shadow="sm", p=8, radius="sm")
            )
            children.append(text_section)

        slide_divs.append(dmc.Card(children))
    return slide_divs
