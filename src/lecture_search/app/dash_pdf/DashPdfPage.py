# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DashPdfPage(Component):
    """A DashPdfPage component.


Keyword arguments:

- id (string; optional):
    id of the component.

- annotations (list of dicts; optional):
    Annotations to be displayed  Example          const annotation = {
    annotationFlags: 0,              annotationType: 2,
    borderStyle: {                  width: 0,                  style:
    1,                  horizontalCornerRadius: 0,
    verticalCornerRadius: 0,              },              rotation: 0,
    dest: \"\",              contentsObj: {                  str:
    \"\",                  dst: \"ltr\",              },
    subtype: \"Link\",          }          annotation.url =
    \"obsidian://open?vault=Personal&file=university%2Fin%C5%BCynierka%2Ftest\"
    annotation.rect = [left, top - height, left + width, top];.

    `annotations` is a list of dicts with keys:

    - annotationFlags (number; optional)

    - annotationType (number; optional)

    - borderStyle (dict; optional)

        `borderStyle` is a dict with keys:

        - horizontalCornerRadius (number; optional)

        - style (number; optional)

        - verticalCornerRadius (number; optional)

        - width (number; optional)

    - contentsObj (dict; optional)

        `contentsObj` is a dict with keys:

        - dst (string; optional)

        - str (string; optional)

    - dest (string; optional)

    - id (string; optional)

    - rect (list of numbers; optional)

    - rotation (number; optional)

    - subtype (string; optional)

    - url (string; optional)

- pageNumber (number; default 1):
    Page number to be displayed.

- selection (dict; optional):
    selection, annotation object, None if no selection.

    `selection` is a dict with keys:

    - annotationFlags (number; optional)

    - annotationType (number; optional)

    - borderStyle (dict; optional)

        `borderStyle` is a dict with keys:

        - horizontalCornerRadius (number; optional)

        - style (number; optional)

        - verticalCornerRadius (number; optional)

        - width (number; optional)

    - contentsObj (dict; optional)

        `contentsObj` is a dict with keys:

        - dst (string; optional)

        - str (string; optional)

    - dest (string; optional)

    - id (string; optional)

    - rect (list of numbers; optional)

    - rotation (number; optional)

    - subtype (string; optional)

    - url (string; optional)

- textItems (list of dicts; optional):
    text rects.

    `textItems` is a list of dicts with keys:

    - dir (string; optional)

    - fontName (string; optional)

    - hasEOL (boolean; optional)

    - rect (list of numbers; optional)

    - str (string; optional)

- width (number; default 500):
    Width of the page."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_pdf'
    _type = 'DashPdfPage'
    @_explicitize_args
    def __init__(self, pageNumber=Component.UNDEFINED, width=Component.UNDEFINED, annotations=Component.UNDEFINED, id=Component.UNDEFINED, selection=Component.UNDEFINED, textItems=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'annotations', 'pageNumber', 'selection', 'textItems', 'width']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'annotations', 'pageNumber', 'selection', 'textItems', 'width']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DashPdfPage, self).__init__(**args)
