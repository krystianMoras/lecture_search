from pathlib import Path

import dash  # type: ignore
import dash_mantine_components as dmc  # type: ignore
import dash_player  # type: ignore
from dash import callback  # type: ignore
from dash_extensions.enrich import (
    DashBlueprint,
    Input,  # type: ignore
    Output,
    State,
    dcc,
    html,
)

import lecture_search.app.constants as constants
from lecture_search.app.subtitle_fetcher import find_subtitle, parse_subtitles

bp = DashBlueprint()
bp.layout = html.Div(
    [
        dcc.Store("subtitles", data={}),
        dash_player.DashPlayer(
            id="video-player",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            controls=True,
            playing=False,
            width="75%",
            height="60%",
            intervalCurrentTime=500,
        ),
        dmc.Paper(
            children=[
                html.H2("Subtitles:"),
                html.Div(
                    id="subtitle-container",
                    children=[
                        dmc.Paper(
                            id="subtitle",
                            children="Hello test subtitle",
                            shadow="sm",
                            p="sm",
                            radius="sm",
                        ),
                    ],
                ),
            ],
            style={
                "display": "flex",
                "flex-direction": "column",
                "width": "25%",
                "padding": "10px",
            },
            shadow="sm",
            radius="sm",
        ),
    ],
    style={"display": "flex", "flex-direction": "row"},
)


@callback(
    Output("subtitle-container", "children"),
    Input("video-player", "currentTime"),
    State("subtitles", "data"),
)
def update_subtitle(current_time, subtitles):
    if subtitles == {}:
        return "no subtitles"
    min_times, max_times, texts = subtitles
    subtitle_children = []
    found_subtitles = find_subtitle(min_times, max_times, texts, current_time, future=5)
    print(found_subtitles)
    for subtitle in found_subtitles:
        subtitle_children.append(
            dmc.Paper(
                id="subtitle",
                children=subtitle,
                shadow="sm",
                p="sm",
                radius="sm",
            )
        )
    return subtitle_children


@callback(
    Output("video-player", "url"),
    Output("video-player", "seekTo"),
    Output("video-player", "playing"),
    Input("startTime", "data"),
    Input("file_path", "data"),
)
def load_video(start_time, file_path):
    path = dash.get_asset_url(file_path)
    return path, float(start_time), True


@callback(
    Output("subtitles", "data"),
    Input("file_path", "data"),
)
def load_subtitles(file_path):
    path_to_subtitles = constants.courses_dir / Path(file_path).with_suffix(".srt")
    print(path_to_subtitles)

    if path_to_subtitles.exists():
        return parse_subtitles(path_to_subtitles)
