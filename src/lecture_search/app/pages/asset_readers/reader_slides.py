from dash_extensions.enrich import DashBlueprint, html, Output, Input, State
from dash import callback, clientside_callback
import base64
from pypdf import PdfReader

from pathlib import Path
from dash_pdf import DashPdfDocument, DashPdfPage


bp = DashBlueprint()
bp.layout = html.Div(
    [
        html.Div(id="placeholder_scroll", style={"visibility": "hidden"}),
        html.Div(id="pdf-container"),
    ],
    id="pdf-container-wrapper",
    style={"overflow": "scroll", "height": "90vh"},
)
# change scroll state of overflow
clientside_callback(
    """
    function(children,page){
        // delay to wait for pdf to load
        setTimeout(function(){
            
            var pdfChildren = document.getElementById("pdf-container").children[0].children;
            // get height for page number child
            var totalOffset = 0;
            if (children.length > 0) {
                for (var i = 0; i < page; i++) {
                    totalOffset += pdfChildren[i.toString()].offsetHeight;
                }
                document.getElementById("pdf-container-wrapper").scrollTo(0,totalOffset);
            }
            return "";
        }
        , 1000);
    }
    """,
    Output("placeholder_scroll", "children"),
    Input("pdf-container", "children"),
    State("page", "data"),
)


@callback(
    Output("pdf-container", "children"),
    Input("file_path", "data"),
)
def on_click(file_path):
    path_to_slides = Path("./src/lecture_search/app/assets") / file_path
    with open(path_to_slides, "rb") as pdf_file:
        readpdf = PdfReader(pdf_file)
        totalpages = len(readpdf.pages)
    with open(path_to_slides, "rb") as pdf_file:
        encoded_string = base64.b64encode(pdf_file.read())
        # add "data:application/pdf;base64," to the front of encoded_string
        encoded_string = "data:application/pdf;base64," + encoded_string.decode("utf-8")
        return DashPdfDocument(
            file=encoded_string,
            id="pdf-container",
            children=[
                DashPdfPage(pageNumber=i, id=f"page-{i}", width=900)
                for i in range(1, totalpages)
            ],
        )
