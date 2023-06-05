# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DashPdfDocument(Component):
    """A DashPdfDocument component.


Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Children of DashPdfDocument, list of DashPdfPage or other
    components.

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- file (string; optional):
    File to be displayed, url or base64 string."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_pdf'
    _type = 'DashPdfDocument'
    @_explicitize_args
    def __init__(self, children=None, file=Component.UNDEFINED, id=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'file']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'file']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(DashPdfDocument, self).__init__(children=children, **args)
