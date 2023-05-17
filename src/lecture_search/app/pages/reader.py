# import dash
# from dash import html, dcc, callback, Input, Output, State, Patch, ALL
# import dash_bootstrap_components as dbc
# import dash_mantine_components as dmc
# from pathlib import Path
# import dash_player
# from subtitle_fetcher import VideoSubtitles
# import yaml

# from dash_iconify import DashIconify
# import candidate_utils

# dash.register_page(__name__)


# yaml_config = yaml.load(open("config.yaml", "r").read(), Loader=yaml.FullLoader)
# subtitles = None

# select = dbc.Row(
#     [
#         dbc.Col(
#             [
#                 dmc.Button(
#                     "Previous",
#                     id="previous-button",
#                 )
#             ],
#         ),
#         dbc.Col(
#             [
#                 dmc.Select(
#                     id="url",
#                     placeholder="Select video",
#                 ),
#             ],
#         ),
#         dbc.Col(
#             children=[
#                 dmc.Button(
#                     "Next",
#                     id="next-button",
#                 ),
#             ],
#         ),
#     ]
# )


# layout = html.Div(
#     children=[
#         select,
#         dcc.Store("selected_phrases", data=[]),
#         html.Div([], id="reader_layout"),
#     ],
# )


# @callback(
#     Output("url", "data"),
#     Output("url", "value"),
#     Input("selected_files", "data"),
#     Input("previous-button", "n_clicks"),
#     Input("next-button", "n_clicks"),
#     State("url", "value"),
# )
# def update_url(selected_files, previous, next, current_url):
#     triggered_id = dash.callback_context.triggered_id
#     if triggered_id == "selected_files":
#         for file in selected_files:
#             if file["value"] == current_url:
#                 return selected_files, dash.no_update

#         return selected_files, selected_files[0]["value"]

#     selected_index = None
#     for i, file in enumerate(selected_files):
#         if file["value"] == current_url:
#             selected_index = i
#             break
#     if triggered_id == "previous-button":
#         # get id of previous video
#         previous_index = (selected_index - 1) % len(selected_files)
#         # get url of previous video
#         previous_url = selected_files[previous_index]["value"]
#         return dash.no_update, previous_url
#     elif triggered_id == "next-button":
#         # get id of next video
#         next_index = (selected_index + 1) % len(selected_files)
#         # get url of next video
#         next_url = selected_files[next_index]["value"]
#         return dash.no_update, next_url
#     else:
#         return selected_files, selected_files[0]["value"]


# @callback(
#     Output("selected_phrases", "data", allow_duplicate=True),
#     Input("selected_files", "data"),
#     prevent_initial_call=True,
# )
# def reset_phrases(selected_files):
#     filenames = [Path(file["value"]).stem for file in selected_files]

#     phrases = candidate_utils.get_phrases_for_context(filenames)
#     return phrases


# @callback(Output("reader_layout", "children"), Input("url", "value"))
# def update_layout(url):
#     if url is None:
#         return dash.no_update
#     path = Path(url)

#     if path.suffix == ".mp4":
#         return dcc.Location("reader/video/" + path.name, id="reader-video-location")
#     if path.suffix == ".txt":
#         return dcc.Location("reader/text/" + path.name, id="reader-text-location")
