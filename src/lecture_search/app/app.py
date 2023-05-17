from dash import Dash, html, dcc, Input, Output, State, ALL, MATCH
import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import yaml
from dash_extensions.enrich import DashProxy
from pathlib import Path

yaml_config = yaml.load(open("config.yaml", "r").read(), Loader=yaml.FullLoader)


videos_path = Path(yaml_config["videos_path"])

all_video_files = [
    (f.name, str(f))
    for f in videos_path.iterdir()
    if f.is_file() and f.suffix == ".mp4"
]

text_path = Path(yaml_config["text_path"])

all_text_files = [
    (f.name, str(f)) for f in text_path.iterdir() if f.is_file() and f.suffix == ".txt"
]


asset_folder = yaml_config["assets_path"]
abs_path_to_assets_folder = Path(asset_folder).absolute()
app = DashProxy(
    __name__,
    use_pages=True,
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
                    dmc.Button("Change context", id="open-drawer"),
                ]
            ),
            dbc.Col(
                [
                    dmc.Anchor("Notes", href="/notes"),
                ]
            ),
            dbc.Col(
                [
                    dmc.Anchor(
                        "Search",
                        href="/search",
                    ),
                ]
            ),
            dbc.Col(
                [
                    dmc.Anchor("Reader", href="/reader"),
                ]
            ),
        ],  # align everything to left
        justify="start",
        align="left",
    ),
    color="dark",
    dark=True,
)
drawer = dmc.Drawer(
    id="drawer-position",
    position="top",
    zIndex=10000,
    title=html.H1("Current files"),
    children=[
        dmc.Group(
            [
                dmc.Checkbox(
                    label=file_name,
                    value=file_path,
                    id={"type": "file_checkbox", "file_name": file_name},
                    checked=True,
                )
                for file_name, file_path in all_video_files + all_text_files
            ],
            position="center",
        )
    ],
    padding="15",
)


body = html.Div(
    [
        dash.page_container,
    ]
)


app.layout = html.Div(
    [
        dcc.Store(id="selected_files", data=[]),
        navbar,
        drawer,
        body,
    ]
)


@app.callback(
    Output("selected_files", "data"),
    Input({"type": "file_checkbox", "file_name": ALL}, "checked"),
    State({"type": "file_checkbox", "file_name": ALL}, "value"),
    State({"type": "file_checkbox", "file_name": ALL}, "label"),
)
def update_selected_files(checked, values, labels):
    filtered = []
    for value, check, label in zip(values, checked, labels):
        if check:
            filtered.append({"label": label, "value": value})
    return filtered


@app.callback(
    Output("drawer-position", "opened"),
    Input("open-drawer", "n_clicks"),
    prevent_initial_call=True,
)
def open_drawer(n_clicks):
    return True


if __name__ == "__main__":
    app.run_server(debug=True)
