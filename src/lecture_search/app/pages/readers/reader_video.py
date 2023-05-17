# import dash
# from dash import html, dcc, callback, Input, Output, State, Patch, ALL
# import dash_bootstrap_components as dbc
# import dash_mantine_components as dmc
# from pathlib import Path
# import dash_player
# from subtitle_fetcher import VideoSubtitles
# import yaml
# from dash_selectable import DashSelectable
# from dash_extensions import EventListener
# from dash_iconify import DashIconify
# import candidate_utils


# dash.register_page(__name__,
#                    path_template="/reader/video/<asset_name>",)


# subtitles = None

# event = {
#     "event": "mouseup",
#     "props": ["srcElement.className", "srcElement.innerText"],
# }
# yaml_config = yaml.load(open("config.yaml", "r").read(), Loader=yaml.FullLoader)

# video_player = dash_player.DashPlayer(
#     id="video-player",
#     url="https://www.youtube.com/watch?v=3KqjNVRfBP4",
#     controls=True,
#     playing=False,
#     width="100%",
#     height="60%",
# )


# content_card = dmc.Card(
#     children=[
#         video_player,
#     ],
#     withBorder=True,
#     shadow="sm",
#     radius="md",
#     id="content_card",
# )

# all_phrases_table = dash.dash_table.DataTable(
#     id="all_phrases",
#     columns=[
#         {"name": "phrase", "id": "phrase"},
#     ],
#     data=[],
#     row_deletable=True,
#     style_cell={"textAlign": "left"},
#     editable=True,
#     filter_action="native",
#     fixed_rows={"headers": True},
#     style_table={"height": "300px", "overflowY": "auto"},
# )

# transcription_phrases_card = dmc.Card(
#     children=[
#         dbc.Row(
#             [
#                 html.H4("Transcription"),
#                 EventListener(
#                     DashSelectable(
#                         id="dash-selectable",
#                         children=[
#                             dmc.Paper("subtitles here", id="transcription"),
#                         ],
#                     ),
#                     events=[event],
#                     logging=True,
#                     id="el",
#                 ),
#             ],
#             id="transcription-row",
#         ),
#         dbc.Row(
#             [
#                 html.H4("Phrases"),
#                 html.P("current:", style={"margin-left": "10px"}),
#                 dmc.Group(
#                     id="current_phrases",
#                 ),
#                 html.P("all:", style={"margin-left": "10px"}),
#                 all_phrases_table,
#             ]
#         ),
#     ],
#     withBorder=True,
#     shadow="sm",
#     radius="md",
#     id="phrases-card",
# )


# def layout(asset_name):
#     return dbc.Row(
#     [
#                 dbc.Col(
#                     [
#                         content_card,
#                     ],
#                     md=7,
#                     id="content_col",
#                 ),
#                 dbc.Col(
#                     [
#                         transcription_phrases_card,
#                     ],
#                     md=5,
#                     id="phrases_col",
#                 ),
#             ]
# )


# @callback(
#     Output("transcription", "children"),
#     Output("current_phrases", "children"),
#     Input("video-player", "currentTime"),
#     Input("selected_phrases", "data"),
#     prevent_initial_call=True,
# )
# def update_transcription(currentTime, selected_phrases):
#     global subtitles
#     if subtitles is None:
#         return dash.no_update, dash.no_update
#     if currentTime is None:
#         currentTime = 0
#     subtitle = subtitles.find_subtitle(float(currentTime))
#     candidates = candidate_utils.get_candidates(subtitle, selected_phrases)
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

#     if selected_phrases is None or len(selected_phrases) == 0:
#         return subtitle, badges
#     new_text = [subtitle]

#     for i in selected_phrases:
#         newArray = []
#         for x in new_text:
#             if isinstance(x, str):
#                 for y in range(len(x.split(i))):
#                     newArray.append(x.split(i)[y])
#                     if y != len(x.split(i)) - 1:
#                         newArray.append(html.Span(i, className="variable-value val1"))
#             else:
#                 newArray.append(x)
#         new_text = newArray
#     return new_text, badges


# @callback(
#     Output("video-player", "url"),
#     Output("video-player", "currentTime"),
#     Input("url", "value"),
# )
# def load_video(url):
#     global subtitles
#     path = Path(url)
#     asset_url = dash.get_asset_url("videos/" + path.name)
#     transcription_url = Path(yaml_config["transcriptions_path"]) / (path.stem + ".srt")
#     subtitles = VideoSubtitles(transcription_url)
#     return asset_url, float(0)


# @callback(
#     Output("selected_phrases", "data", allow_duplicate=True),
#     Input("el", "n_events"),
#     State("el", "event"),
#     State("dash-selectable", "selectedValue"),
#     prevent_initial_call=True,
# )
# def click_event(n_events, e, value):
#     if e is None:
#         return dash.no_update
#     if value is None:
#         return dash.no_update
#     value = value.strip()
#     if len(value) < 2:
#         return dash.no_update
#     patch = Patch()
#     patch.append(value)
#     return patch


# @callback(
#     Output("all_phrases", "data"),
#     Output("selected_phrases", "data"),
#     Input("selected_phrases", "data"),
#     Input("all_phrases", "data"),
#     prevent_initial_call=True,
# )
# def update_phrases(selected_phrases, all_phrases):
#     triggered_id = dash.callback_context.triggered_id
#     if triggered_id == "selected_phrases":
#         return [{"phrase": phrase} for phrase in selected_phrases], dash.no_update
#     elif triggered_id == "all_phrases":
#         return dash.no_update, [phrase["phrase"] for phrase in all_phrases]


# @callback(
#     Output("selected_phrases", "data", allow_duplicate=True),
#     Input({"type": "phrase", "index": ALL}, "n_clicks"),
#     State({"type": "phrase", "index": ALL}, "id"),
#     prevent_initial_call=True,
# )
# def remove_phrase(n_clicks, ids):
#     triggered_id = dash.callback_context.triggered_id
#     if triggered_id is not None:
#         for n_click, id in zip(n_clicks, ids):
#             if id == triggered_id:
#                 print(triggered_id)
#                 if n_click is not None:
#                     phrase = triggered_id["index"]
#                     patch = Patch()
#                     patch.remove(phrase)
#                     return patch
#                 return dash.no_update
#     return dash.no_update
