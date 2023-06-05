import dash_mantine_components as dmc

from dash import ALL, Input, Output, State, dcc, html

import dash
from dash_iconify import DashIconify
from pathlib import Path
import lecture_search.app.search_bar
from dash_extensions.enrich import DashProxy, NoOutputTransform


app = DashProxy(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    transforms=[NoOutputTransform()],
)

asset_path = Path("./src/lecture_search/app/assets/")

file_suffix_icon_map = {
    ".pdf": "mdi:file-pdf-outline",
    ".mp4": "mdi:play",
}


def build_lecture_section(lecture):
    lecture_path = lecture["path"]
    files = [
        {
            "name": file.name,
            "path": file,
        }
        for file in lecture_path.iterdir()
        if file.is_file()
    ]
    file_links = [
        dmc.NavLink(
            label=file["name"],
            icon=DashIconify(icon=file_suffix_icon_map[file["path"].suffix]),
            href="/" + str(file["path"].relative_to(asset_path)),
        )
        for file in files
    ]
    return file_links


def build_course_section(course):
    course_path = course["path"]
    lectures = [
        {
            "name": lecture.name,
            "path": lecture,
        }
        for lecture in course_path.iterdir()
        if lecture.is_dir()
    ]
    lecture_sections = html.Div(
        [
            dmc.NavLink(
                label=lecture["name"],
                childrenOffset=28,
                children=build_lecture_section(lecture),
            )
            for lecture in lectures
        ]
    )
    return lecture_sections


def build_sidebar():
    asset_path = Path("./src/lecture_search/app/assets/")
    courses_path = asset_path / "courses"
    courses = [
        {
            "name": course.name,
            "path": course,
        }
        for course in courses_path.iterdir()
        if course.is_dir()
    ]
    course_headers = [
        html.Div(
            [
                course["name"],
                dmc.Divider(variant="solid", size="xs"),
            ],
            className="mantine-16kf70y",
        )
        for course in courses
    ]
    course_sections = [build_course_section(course) for course in courses]
    # take one from course headers then one from course sections
    sidebar_section = []
    for i in range(len(course_headers)):
        sidebar_section.append(course_headers[i])
        sidebar_section.append(course_sections[i])
    return sidebar_section


sidebar = html.Div(
    [
        dmc.Stack(
            [
                html.H2("Courses"),
                *build_sidebar(),
            ],
            className="mantine-1pfv4rc",
        )
    ],
    className="sidebar",
)


app.layout = dmc.MantineProvider(
    children=html.Div(
        [
            sidebar,
            html.Div(
                [
                    html.Div(id="url_callback_placeholder"),
                    dcc.Dropdown(
                        id="dropdown",
                        placeholder="Search materials",
                        searchable=True,
                        # fix on top
                        style={
                            "position": "sticky",
                            "top": "0",
                            "zIndex": "1",
                            "width": "100%",
                        },
                    ),
                    dash.page_container,
                ],
                className="content_app",
            ),
        ]
    ),
)

import json


@app.callback(
    Output("url_callback_placeholder", "children"),
    Input("dropdown", "value"),
)
def search_event(value):
    if value is not None:
        print(value)
        search = json.loads(value)
        #
        return dcc.Location(
            id="url",
            href=f"/search?query={search['query']}&type={search['type']}",
        )
    return dash.no_update


if __name__ == "__main__":
    app.run_server(debug=True)
