import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import html
from dash import Input, Output, State

# from cytotools.app.components.filetree import FileTree
from dash import MATCH, ALL
from typing import List
from dash import dcc
import dash_utils
import utils

transcriptions = utils.get_transcriptions("data/transcriptions.json")
_,candidates = utils.get_filtered_candidates("data/filtered_candidates.json")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


offcanvas = dbc.Offcanvas(
    children=dmc.Container(
        [
            # select folder button
            dmc.Button(
                "Select folder",
                leftIcon=DashIconify(icon="mdi:folder", width=20),
                id="select-folder",
            ),
            dmc.NavLink(id="filetree"),
        ]
    ),
    id="offcanvas-backdrop",
    title=dmc.ActionIcon(
        DashIconify(icon="mdi:menu", width=20),
        size="lg",
        id="offcanvas-backdrop-close",
        n_clicks=0,
        mb=10,
    ),
    is_open=False,
    backdrop=False,
    close_button=False,
)

navbar = dbc.Navbar(
    dbc.Row(
        [
            dbc.Col(
                [
                    dmc.ActionIcon(
                        DashIconify(icon="mdi:menu", width=20),
                        size="lg",
                        id="offcanvas-backdrop-open",
                        n_clicks=0,
                        mb=10,
                        # margin
                        ml=10,
                    ),
                ]
            ),
            dbc.Col(
                [
                    dbc.NavbarBrand("", className="ms-2"),
                ]
            ),
            dbc.Col(
                [
                    dmc.Button(
                        "Export to Obsidian",
                        leftIcon=DashIconify(icon="simple-icons:obsidian", width=20,color="#6F5AC7"),
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
                dbc.Col(        dcc.Upload(
            id="upload-data",
            children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            # Allow multiple files to be uploaded
            multiple=True,
        ),width=4),
        dbc.Col([
    dmc.ChipGroup([
                    dmc.Chip("Chip 1"),
                    dmc.Chip("Chip 2"),
                    dmc.Chip("Chip 3"),
                    dmc.Chip("Chip 4"),
                    dmc.Chip("Chip 5"),
                    dmc.Chip("Chip 6"),
                    dmc.Chip("Chip 7"),
                    dmc.Chip("Chip 8"),
                    dmc.Chip("Chip 9"),
                    dmc.Chip("Chip 10"),
                    dmc.Chip("Chip 11"),
                    dmc.Chip("Chip 12"),
                    dmc.Chip("Chip 13"),
                    dmc.Chip("Chip 14"),
                    dmc.Chip("Chip 15"),
                    dmc.Chip("Chip 16"),
                    dmc.Chip("Chip 17"),
                    dmc.Chip("Chip 18"),
                ])
        ])
                
            ]),

        dbc.Row(
            [
                dbc.Col(html.H2("Transcriptions"), width=6),
            ]
        ),
        *dash_utils.get_transcription_cards(transcriptions),
        
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
                    html.H3("Phrase extraction"),
                    dmc.Button(
                        "Extract phrases",
                        leftIcon=DashIconify(icon="mdi:format-list-bulleted", width=20),
                        id="extract-phrases",
                    ),
                    html.H4("Phrases"),
                    dmc.Group(
                        id="phrases",
                        children=dash_utils.get_candidate_badges(candidates)
                    )
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
            offcanvas,
        ]
    ),
    position="top-center",
)


@app.callback(
    Output("offcanvas-backdrop", "is_open"),
    Input("offcanvas-backdrop-open", "n_clicks"),
    Input("offcanvas-backdrop-close", "n_clicks"),
    State("offcanvas-backdrop", "is_open"),
)
def toggle_offcanvas(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(Output('output-image-upload', 'children'),
              Input('upload-image', 'contents'),
              State('upload-image', 'filename'),
              State('upload-image', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

if __name__ == "__main__":
    app.run_server(debug=True)
