import dash

from dash import html, dcc, callback
from urllib.parse import unquote
import lecture_search.app.pages.asset_readers.reader_slides as reader_slides
import lecture_search.app.pages.asset_readers.reader_video as reader_video
from dash_extensions.EventListener import EventListener

dash.register_page(
    __name__, path_template="/<course_name>/<lecture_name>/<asset_name>"
)
event = {"event": "scroll", "props": ["target.scrollTop", "target.scrollLeft"]}


def layout(course_name, lecture_name, asset_name, page=None, startTime=None):
    if page is None:
        page = 0
    if startTime is None:
        startTime = 0

    app = dash.get_app()
    # decode url and special characters
    course_name = unquote(course_name)
    lecture_name = unquote(lecture_name)
    asset_name = unquote(asset_name)
    path = f"{course_name}/{lecture_name}/{asset_name}"
    print(path)
    if asset_name.endswith(".pdf"):
        content = reader_slides.bp.embed(app)
    elif asset_name.endswith(".mp4"):
        content = reader_video.bp.embed(app)
    else:
        content = html.Div("Not implemented yet")
    return html.Div(
        [
            dcc.Store("file_path", data=path),
            dcc.Store("page", data=page),
            dcc.Store("startTime", data=startTime),
            html.H2(lecture_name),
            EventListener(
                content,
                events=[event],
                logging=True,
                id="el",
            ),
        ]
    )
