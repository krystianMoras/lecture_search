# import string
# from pathlib import Path

# import dash  # type: ignore
# import dash_mantine_components as dmc  # type: ignore
# from dash import ALL, Input, Output, Patch, State, callback, dcc, html  # type: ignore
# from dash_extensions import EventListener  # type: ignore
# from dash_iconify import DashIconify  # type: ignore
# from dash_selectable import DashSelectable  # type: ignore

# import lecture_search.app.candidate_utils as candidate_utils

# dash.register_page(
#     __name__,
#     path_template="/reader/text/<asset_name>",
# )


# event = {
#     "event": "mouseup",
#     "props": ["srcElement.className", "srcElement.innerText"],
# }


# current_text = None
# current_asset = None
# current_paragraph_i = 0


# def layout(asset_name):
#     global current_text
#     global current_asset
#     current_asset = asset_name
#     current_text = get_text(asset_name)
#     page_selection = dmc.Group(
#         [
#             dmc.Button(
#                 "Previous",
#                 id="previous-button",
#             ),
#             dmc.NumberInput(
#                 id="page-number",
#                 value=1,
#                 type="number",
#                 min="1",
#                 max=str(len(current_text)),
#                 style={"width": "50px"},
#             ),
#             dmc.Text(" / " + str(len(current_text))),
#             dmc.Button(
#                 "Next",
#                 id="next-button",
#             ),
#         ],
#         position="center",
#         # row
#         style={"width": "100%", "flex-direction": "row"},
#     )
#     return html.Div(
#         [
#             dcc.Store("selected_phrases", data=[]),
#             dcc.Store("stemmed_phrases", data=[]),
#             dcc.Store("current_paragraph", data="Lorem Ipsum"),
#             html.Div(id="save_placeholder"),
#             # page counter with editable page number
#             page_selection,
#             dmc.Card(
#                 shadow="sm",
#                 radius="md",
#                 withBorder=True,
#                 children=[
#                     EventListener(
#                         DashSelectable(
#                             id="dash-selectable",
#                             children=dmc.Paper(
#                                 shadow="sm",
#                                 p="xs",
#                                 children=[],
#                                 id="text_content",
#                             ),
#                         ),
#                         events=[event],
#                         logging=True,
#                         id="el",
#                     ),
#                     dmc.Group(id="phrases"),
#                 ],
#             ),
#         ],
#         id="text_content",
#     )


# def get_text(url):
#     path = Path(url)
#     asset_url = "./assets/text/" + path.name

#     text = open(asset_url, "r").read()

#     paragraphs = text.split("\n")

#     return paragraphs


# @callback(
#     Output("selected_phrases", "data", allow_duplicate=True),
#     Output("stemmed_phrases", "data", allow_duplicate=True),
#     Input("el", "n_events"),
#     State("el", "event"),
#     State("dash-selectable", "selectedValue"),
#     prevent_initial_call=True,
# )
# def click_event(n_events, e, value):
#     if e is None:
#         raise dash.exceptions.PreventUpdate()
#     if value is None:
#         raise dash.exceptions.PreventUpdate()
#     value = value.strip()
#     if len(value) < 2:
#         raise dash.exceptions.PreventUpdate()

#     patch_phrase, patch_stemmed = Patch(), Patch()
#     patch_phrase.append(value)

#     candidate = candidate_utils.candidate_from_str(value)
#     patch_stemmed.append(candidate)
#     return patch_phrase, patch_stemmed


# @callback(
#     Output("phrases", "children"),
#     Input("selected_phrases", "data"),
#     Input("current_paragraph", "data"),
# )
# def get_badges(selected_phrases, text):
#     candidates = candidate_utils.get_candidates(text, selected_phrases)
#     badges = []
#     for candidate in candidates:
#         badges.append(
#             dmc.Badge(
#                 candidate,
#                 color="blue",
#                 variant="outline",
#                 size="lg",
#                 mb="xs",
#                 mr="xs",
#                 leftSection=dmc.ActionIcon(
#                     DashIconify(icon="mdi:close"),
#                     variant="transparent",
#                     color="blue",
#                     size="xs",
#                     id={"type": "phrase", "index": candidate},
#                 ),
#             )
#         )
#     return badges


# @callback(
#     Output("text_content", "children"),
#     Input("stemmed_phrases", "data"),
#     Input("current_paragraph", "data"),
# )
# def get_highlighted_text(selected_phrases, text):
#     if text is None:
#         raise dash.exceptions.PreventUpdate()

#     if selected_phrases is None or len(selected_phrases) == 0:
#         return text

#     new_text = []
#     words, occurences = candidate_utils.mark_text(text, selected_phrases)

#     current_phrase = ""
#     for word, occurence in zip(words, occurences):
#         altered_word = word if word in string.punctuation else " " + word

#         if occurence:
#             current_phrase += altered_word
#         else:
#             if current_phrase != "":
#                 new_text.append(" ")
#                 new_text.append(
#                     html.Span(current_phrase[1:], className="variable-value val1")
#                 )
#                 current_phrase = ""
#             new_text.append(altered_word)

#     return new_text


# @callback(
#     Output("selected_phrases", "data", allow_duplicate=True),
#     Output("stemmed_phrases", "data", allow_duplicate=True),
#     Input("selected_files", "data"),
#     prevent_initial_call=True,
# )
# def reset_phrases(selected_files):
#     filenames = [Path(file["value"]).stem for file in selected_files]
#     phrases = candidate_utils.get_phrases_for_context(filenames, " ".join(current_text))
#     phrases_stemmed = [candidate_utils.candidate_from_str(phrase) for phrase in phrases]
#     return phrases, phrases_stemmed


# @callback(
#     Output("selected_phrases", "data", allow_duplicate=True),
#     Output("stemmed_phrases", "data", allow_duplicate=True),
#     Input({"type": "phrase", "index": ALL}, "n_clicks"),
#     State({"type": "phrase", "index": ALL}, "id"),
#     State("selected_phrases", "data"),
#     prevent_initial_call=True,
# )
# def remove_phrase(n_clicks, ids, current_phrases):
#     triggered_id = dash.callback_context.triggered_id
#     if triggered_id is not None:
#         for n_click, id in zip(n_clicks, ids):
#             if id == triggered_id:
#                 if n_click is not None:
#                     phrase = triggered_id["index"]
#                     i = current_phrases.index(phrase)
#                     patch = Patch()
#                     stemmed_patch = Patch()
#                     del patch[i]
#                     del stemmed_patch[i]
#                     return patch, stemmed_patch
#                 return dash.no_update, dash.no_update
#     return dash.no_update, dash.no_update


# @callback(
#     Output("current_paragraph", "data"),
#     Input("page-number", "value"),
# )
# def update_paragraph(current_page):
#     return current_text[current_page - 1]


# @callback(
#     Output("page-number", "value"),
#     Input("previous-button", "n_clicks"),
#     Input("next-button", "n_clicks"),
#     State("page-number", "value"),
#     State("page-number", "max"),
# )
# def change_page_number(previous, next, current_page, max_page):
#     triggered_id = dash.callback_context.triggered_id
#     current_paragraph_i = int(current_page)
#     max_page = int(max_page)
#     if triggered_id == "previous-button":
#         current_paragraph_i = current_paragraph_i - 1 if current_paragraph_i > 1 else 1
#     elif triggered_id == "next-button":
#         current_paragraph_i = (
#             current_paragraph_i + 1 if current_paragraph_i < max_page else max_page
#         )
#     return current_paragraph_i


# @callback(
#     Output("save_placeholder", "children"),
#     Input("selected_phrases", "data"),
# )
# def save_phrases(selected_phrases):
#     candidate_utils.save_phrases(
#         "./data/annotated_decision_analysis.json", selected_phrases, current_asset
#     )
#     return dash.no_update
