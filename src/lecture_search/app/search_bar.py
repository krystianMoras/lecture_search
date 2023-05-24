import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import dcc, html, callback
import json
from dash_iconify import DashIconify


@callback(
    Output("dropdown", "options"),
    Input("dropdown", "search_value"),
    State("dropdown", "value"),
)
def click_event(search_value, value):
    if not search_value:
        raise PreventUpdate
    return [
        {
            "search": search_value,
            "label": html.Div(
                [
                    DashIconify(icon="mdi-file-document-outline"),
                    html.Span(
                        "semantic:",
                        style={
                            "border-radius": "3px",
                            # pinkish color
                            "color": "#f50d57",
                            "background-color": "#ffe6f0",
                        },
                    ),
                    " ",
                    search_value,
                ]
            ),
            "value": json.dumps({"type": "semantic", "query": search_value}),
        },
        {
            "search": search_value,
            "label": html.Div(
                [
                    DashIconify(icon="mdi-file-document-outline"),
                    html.Span(
                        "key word:",
                        style={
                            "border-radius": "3px",
                            # greenish color
                            "color": "#0d9e57",
                            "background-color": "#e6ffe6",
                        },
                    ),
                    " ",
                    search_value,
                ]
            ),
            "value": json.dumps({"type": "key_word", "query": search_value}),
        },
    ]
