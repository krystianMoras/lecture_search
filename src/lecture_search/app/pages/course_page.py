import dash

from dash import html, dcc, callback
from urllib.parse import unquote
import lecture_search.app.pages.asset_readers.reader_slides as reader_slides
from dash_extensions.EventListener import EventListener

dash.register_page(
    __name__, path_template="/courses/<course_name>/<lecture_name>/<asset_name>"
)
event = {"event": "scroll", "props": ["target.scrollTop", "target.scrollLeft"]}


def layout(course_name, lecture_name, asset_name, page=None):
    if page is None:
        page = 0
    app = dash.get_app()
    # decode url and special characters
    course_name = unquote(course_name)
    lecture_name = unquote(lecture_name)
    asset_name = unquote(asset_name)
    path = f"courses/{course_name}/{lecture_name}/{asset_name}"
    if asset_name.endswith(".pdf"):
        content = reader_slides.bp.embed(app)
    else:
        content = html.Div("Not implemented yet")
    return html.Div(
        [
            dcc.Store("file_path", data=path),
            dcc.Store("page", data=page),
            html.H2(lecture_name),
            EventListener(
                content,
                events=[event],
                logging=True,
                id="el",
            ),
        ]
    )

