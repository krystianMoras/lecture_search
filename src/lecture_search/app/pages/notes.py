import dash  # type: ignore
from dash import html  # type: ignore

dash.register_page(__name__)

layout = html.Div(
    children=[
        html.H1("Notes page"),
    ]
)
