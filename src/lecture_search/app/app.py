import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import html
from dash import Input, Output, State

import dash_player

from dash import MATCH, ALL
from typing import List
from dash import dcc
import dash_utils
import utils
import json
import srt
from pathlib import Path
import bisect
import yaml

yaml_config = yaml.load(open("config.yaml", "r").read(), Loader=yaml.FullLoader)

videos_path = Path(yaml_config["videos_path"])

all_video_files = [
    (f.name, str(f))
    for f in videos_path.iterdir()
    if f.is_file() and f.suffix == ".mp4"
]

CONFIG = {"video_subtitles": None, "video_path": None}


class VideoSubtitles:
    def __init__(self, srt_path):
        self.srt_path = srt_path
        self.parser = srt.parse(open(srt_path, "r").read())
        self.min_times = []
        self.max_times = []
        self.texts = []
        self._parse_subtitles()

    def _parse_subtitles(self):
        for p in self.parser:
            self.min_times.append(p.start.total_seconds())
            self.max_times.append(p.end.total_seconds())
            self.texts.append(p.content)

    def find_subtitle(self, time):
        idx = bisect.bisect_left(self.max_times, time)
        if (
            idx < len(self.max_times)
            and self.min_times[idx] <= time <= self.max_times[idx]
        ):
            return self.texts[idx]
        else:
            return None


with open("data/results.json", "r") as f:
    results = json.load(f)
candidates = []

for doc in results:
    candidates.extend(results[doc])

# get absolute path to assets folder
asset_folder = yaml_config["assets_path"]
abs_path_to_assets_folder = Path(asset_folder).absolute()
print(abs_path_to_assets_folder)
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    assets_folder=abs_path_to_assets_folder,
)


navbar = dbc.Navbar(
    dbc.Row(
        [
            dbc.Col(
                [
                    dbc.NavbarBrand("", className="ms-2"),
                ]
            ),
            dbc.Col(
                [
                    dmc.Button(
                        "Export to Obsidian",
                        leftIcon=DashIconify(
                            icon="simple-icons:obsidian", width=20, color="#6F5AC7"
                        ),
                        variant="gradient",
                        gradient={"from": "indigo", "to": "purple"},
                        id="export-obsidian",
                    ),
                ]
            ),
        ],  # align everything to left
        justify="start",
        align="left",
    ),
    color="dark",
    dark=True,
)

text_card = dmc.Card(
    children=[
        dbc.Row(
            [
                dbc.Col(html.H2("Video"), width=6),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dmc.Select(
                            id="url",
                            placeholder="Select video",
                            data=[
                                {"label": name, "value": path}
                                for name, path in all_video_files
                            ],
                            value=all_video_files[0][1],
                        ),
                    ],
                    md=10,
                ),
                dbc.Col(
                    [
                        dmc.Button(
                            "Load",
                            id="load-button",
                            color="blue",
                            variant="outline",
                        ),
                    ],
                    md=2,
                ),
            ]
        ),
        dash_player.DashPlayer(
            id="video-player",
            url="https://www.youtube.com/watch?v=3KqjNVRfBP4",
            controls=True,
            playing=False,
        ),
        dbc.Row(
            [
                dbc.Col(html.H2("Transcription"), width=6),
            ]
        ),
        dmc.Paper(
            [
                dmc.Highlight(
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla vitae elit libero, a pharetra augue. Nullam id dolor id nibh ultricies vehicula ut id elit. Nulla vitae elit libero, a pharetra augue. Nullam id dolor id nibh ultricies vehicula ut id elit.",
                    highlight=candidates,
                    id="transcription",
                ),
            ],
        ),
    ],
    withBorder=True,
    shadow="sm",
    radius="md",
    id="slides-card",
)

actions_column = [
    dbc.Row(
        [
            dmc.Card(
                shadow="sm",
                radius="md",
                withBorder=True,
                children=[
                    html.H4("Key Phrases"),
                    dmc.Group(
                        id="phrases",
                        children=dash_utils.get_candidate_badges(candidates),
                    ),
                ],
            )
        ],
    ),
    dbc.Row(
        [
            dmc.Card(
                shadow="sm",
                radius="md",
                withBorder=True,
                children=[
                    html.H3("Chat"),
                ],
            )
        ],
    ),
]


body = dbc.Row(
    [
        dbc.Col(text_card, md=8),  # z jakiegoś powodu 12 to 100% xD?
        dbc.Col(actions_column, md=4),
    ],
    className="ml-auto flex-nowrap mt-3 mt-md-0",
)


app.layout = dmc.NotificationsProvider(
    html.Div(
        [
            navbar,
            body,
        ]
    ),
    position="top-center",
)


@app.callback(
    Output("transcription", "children"),
    Input("video-player", "currentTime"),
)
def update_transcription(currentTime):
    if CONFIG["video_subtitles"] is None:
        return "No subtitles loaded"

    subtitle = CONFIG["video_subtitles"].find_subtitle(float(currentTime))
    return subtitle


@app.callback(
    Output("video-player", "url"),
    Output("video-player", "currentTime"),
    Input("load-button", "n_clicks"),
    State("url", "value"),
)
def load_video(n_clicks, url):
    path = Path(url)
    asset_url = app.get_asset_url("videos/" + path.name)
    print(asset_url)
    srt_path = Path(yaml_config["transcriptions_path"]) / (path.stem + ".srt")
    CONFIG["video_subtitles"] = VideoSubtitles(srt_path)
    print(CONFIG["video_subtitles"].find_subtitle(0))
    return asset_url, float(0)


if __name__ == "__main__":
    app.run_server(debug=True)
