import dash  # type: ignore
import dash_mantine_components as dmc  # type: ignore
from dash import Patch, dcc  # type: ignore
from dash.exceptions import PreventUpdate  # type: ignore
from dash_extensions import EventListener  # type: ignore
from dash_extensions.enrich import Input  # type: ignore
from dash_extensions.enrich import ALL, DashProxy, Output, State, html
from dash_iconify import DashIconify  # type: ignore
from dash_selectable import DashSelectable  # type: ignore

app = DashProxy()
event = {
    "event": "mouseup",
    "props": ["srcElement.className", "srcElement.innerText"],
}
text_that_is_being_selected = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit."

app.layout = html.Div(
    [
        dcc.Store("selected_phrases", data=[]),
        EventListener(
            DashSelectable(
                id="dash-selectable",
                children=[
                    html.Div(text_that_is_being_selected, id="original"),
                ],
            ),
            events=[event],
            logging=True,
            id="el",
        ),
        dmc.Group(
            id="phrases",
        ),
    ]
)


@app.callback(
    Output("phrases", "children"),
    Input("selected_phrases", "data"),
    prevent_initial_call=True,
)
def update_phrases(selected_phrases):
    badges = []

    for phrase in selected_phrases:
        badges.append(
            dmc.Badge(
                phrase,
                color="blue",
                variant="outline",
                size="lg",
                mb="xs",
                mr="xs",
                leftSection=dmc.ActionIcon(
                    DashIconify(icon="mdi:close"),
                    variant="transparent",
                    color="blue",
                    size="xs",
                    id={"type": "phrase", "index": phrase},
                ),
            )
        )

    return badges


@app.callback(
    Output("original", "children"),
    Input("selected_phrases", "data"),
    prevent_initial_call=True,
)
def update_original_text(selected_phrases):
    new_text = [text_that_is_being_selected]

    for i in selected_phrases:
        newArray = []
        for x in new_text:
            if isinstance(x, str):
                for y in range(len(x.split(i))):
                    newArray.append(x.split(i)[y])
                    if y != len(x.split(i)) - 1:
                        newArray.append(
                            html.Span(i, className="variable-value sync val1")
                        )
            else:
                newArray.append(x)
        new_text = newArray
    return new_text


@app.callback(
    Output("selected_phrases", "data", allow_duplicate=True),
    Input({"type": "phrase", "index": ALL}, "n_clicks"),
    State({"type": "phrase", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def remove_phrase(n_clicks, ids):
    triggered_id = dash.callback_context.triggered_id
    if triggered_id is not None:
        for n_click, id in zip(n_clicks, ids):
            if id == triggered_id:
                print(triggered_id)
                if n_click is not None:
                    phrase = triggered_id["index"]
                    patch = Patch()
                    patch.remove(phrase)
                    return patch
                return dash.no_update
    return dash.no_update


@app.callback(
    Output("selected_phrases", "data", allow_duplicate=True),
    Input("el", "n_events"),
    State("el", "event"),
    State("dash-selectable", "selectedValue"),
    prevent_initial_call=True,
)
def click_event(n_events, e, value):
    if e is None:
        raise PreventUpdate()
    if value is None:
        return dash.no_update
    value = value.strip()
    if len(value) < 2:
        return dash.no_update
    patch = Patch()
    patch.append(value)
    return patch


if __name__ == "__main__":
    app.run_server(debug=True)
