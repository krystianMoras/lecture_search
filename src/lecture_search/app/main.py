import argparse
from pathlib import Path

import dash  # type: ignore
import dash_mantine_components as dmc  # type: ignore
from dash import Input, Output, dcc, html  # type: ignore
from dash_extensions.enrich import DashProxy, NoOutputTransform  # type: ignore
from dash_iconify import DashIconify  # type: ignore
import json
import lecture_search.app.constants as constants

parser = argparse.ArgumentParser()
# courses assets path
parser.add_argument("--courses_dir", type=str, required=True)

args = parser.parse_args()

courses_dir = Path(args.courses_dir)
constants.courses_dir = courses_dir

app = DashProxy(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    transforms=[NoOutputTransform()],
    assets_folder=courses_dir,
)


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
            href="/" + str(file["path"].relative_to(courses_dir)),
        )
        for file in files
        if file["path"].suffix in file_suffix_icon_map.keys()
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
    courses = [
        {
            "name": course.name,
            "path": course,
        }
        for course in courses_dir.iterdir()
        if course.is_dir()
    ]
    course_headers = [
        html.Div(
            [
                course["name"],
                dmc.Divider(variant="solid", size="xs"),
            ],
            # .mantine-16kf70y::after {
            #     content: "";
            #     flex: 1 1 0%;
            #     border-top: 1px solid rgb(206, 212, 218);
            #     margin-left: 10px;
            # }
            style={
                "fontFamily": "Inter, sans-serif",
                "color": "inherit",
                "fontSize": "12px",
                "lineHeight": "1.55",
                "textDecoration": "none",
                "display": "flex",
                "-mozBoxAlign": "center",
                "alignItems": "center",
                "marginTop": "2px",
            },
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
            style={
                "display": "flex",
                "flexDirection": "column",
                "-mozBoxAlign": "stretch",
                "alignItems": "stretch",
                "-mozBoxPack": "start",
                "justifyContent": "flex-start",
                "gap": "0px",
                "paddingRight": "25px",
                "paddingLeft": "25px",
            },
        )
    ],
    style={
        "fontFamily": "Inter, sans-serif",
        "top": "70px",
        "bottom": "30px",
        "zIndex": "1000",
        "width": "300px",
        "position": "fixed",
        "boxSizing": "border-box",
        "display": "flex",
        "flexDirection": "column",
        "backgroundColor": "rgb(255, 255, 255)",
        "overflow": "scroll",
        "borderRight": "1px solid rgb(233, 236, 239)",
    },
)


app.layout = dmc.MantineProvider(
    children=html.Div(
        [
            dcc.Store(id="course_dir", data=str(courses_dir)),
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
                style={
                    "padding": "10px",
                    "marginLeft": "320px",
                },
            ),
        ]
    ),
)


@app.callback(
    Output("url_callback_placeholder", "children"),
    Input("dropdown", "value"),
)
def search_event(value):
    if value is not None:
        search = json.loads(value)
        #
        return dcc.Location(
            id="url",
            href=f"/search?query={search['query']}&type={search['type']}",
        )
    return dash.no_update


if __name__ == "__main__":
    app.run_server(debug=True)
