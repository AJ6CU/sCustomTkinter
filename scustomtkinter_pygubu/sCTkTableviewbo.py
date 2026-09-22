import pygubu
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
    register_custom_property
)
from scustomtkinter.sctk_tableview import sCTkTableview
from scustomtkinter.sctk_tableview import sCTkTableview
from scustomtkinter.themeable_widget import parse_list_property

widget_namespace = "scustomtkinter.sctk_tableview"
widget_classname = "sCTkTableview"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkTableviewBO(BuilderObject):
    """
    Pygubu Designer visual studio object builder registration helper subclass.
    🚀 PROPERTY SEQUENCE PATCH: Rearranged so that structural grid counts
    load and evaluate BEFORE the string column parser executes!
    """
    class_ = sCTkTableview

    # 📐 Structural options declared first, layout payload definitions placed dead last!
    OPTIONS_CUSTOM = ('num_columns', 'num_rows', 'grid_mode', 'show_headers', 'header_line_width', 'outline_width',
                      'outline_radius', 'state', 'cell_bg_color', 'cell_alt_bg_color',
                      'editable_columns', 'edit_trigger', 'select_rows', 'columns')
    properties = OPTIONS_CUSTOM

    container = False

    @classmethod
    def setup_properties(cls):
        super().setup_properties()
        for prop in cls.OPTIONS_CUSTOM:
            if prop not in cls.properties:
                cls.properties = cls.properties + (prop,)

    def get_layout_properties(self):
        props = super().get_layout_properties() if hasattr(super(), 'get_layout_properties') else {}
        for custom_prop in self.OPTIONS_CUSTOM:
            props.pop(custom_prop, None)
        return props

    def layout(self):
        if hasattr(self, 'wmeta') and hasattr(self.wmeta, 'layout_properties'):
            clean_properties = dict(self.wmeta.layout_properties)
            for custom_prop in self.OPTIONS_CUSTOM:
                clean_properties.pop(custom_prop, None)
            self.wmeta.layout_properties = clean_properties
        super().layout()

    def _process_property_value(self, name, value):
        if name == 'columns':
            # Shared parser: accepts ["A", "B"], "A, B" or a real list, so this
            # property behaves identically to sCTkSelector's items and
            # sCTkDialSelector's labels. The previous comma-only split turned
            # the quoted-list form into garbage -- ['["A"', '"B"]'].
            return parse_list_property(value)

        if value is None or str(value).strip() == "":
            return None
        if name in ('num_columns', 'num_rows', 'header_line_width', 'outline_radius'):
            return int(str(value).strip())
        if name in ('show_headers', 'select_rows'):
            return str(value).lower() in ("true", "1", "yes")
        # editable_columns stays a string -- "1, 2" -- and the widget parses
        # it, the same way it parses `columns`. Blank already returned None
        # above, which is the widget's "every column" default.
        return str(value)

    def _get_init_args(self, extra_init_args=None):
        args = super()._get_init_args(extra_init_args)
        w_props = self.wmeta.properties if (hasattr(self, 'wmeta') and hasattr(self.wmeta, 'properties')) else {}

        args['num_columns'] = int(w_props.get('num_columns') if w_props.get('num_columns') else 3)
        args['num_rows'] = int(w_props.get('num_rows') if w_props.get('num_rows') else 1)
        args['grid_mode'] = str(w_props.get('grid_mode') if w_props.get('grid_mode') else "zebra")

        # FIXED: Pass state down during rebuild instantiation passes!
        args['state'] = str(w_props.get('state') if w_props.get('state') else "normal")

        raw_cols = w_props.get('columns')
        if raw_cols:
            args['columns'] = self._process_property_value('columns', raw_cols)
            args['num_columns'] = len(args['columns'])

        args['show_headers'] = self._process_property_value('show_headers', w_props.get('show_headers') or True)

        # Editing and selection. Absent, each keeps the widget's default --
        # every column editable, by double-click, no row highlighted -- so a
        # table already in a .ui file is unchanged.
        args['editable_columns'] = self._process_property_value(
            'editable_columns', w_props.get('editable_columns'))
        args['edit_trigger'] = str(w_props.get('edit_trigger') or "double")
        args['select_rows'] = bool(self._process_property_value(
            'select_rows', w_props.get('select_rows') or "False"))
        return args

    def _set_property(self, backend_widget, pname, value):
        """Intercepts and forces live visual canvas property redraw updates instantly."""
        if pname in self.OPTIONS_CUSTOM:
            processed_val = self._process_property_value(pname, value)
            backend_widget.configure(**{pname: processed_val})
        else:
            super()._set_property(backend_widget, pname, value)

    def set_property(self, name, value):
        # 1. Update the runtime property backing variables
        if hasattr(self, 'wmeta') and hasattr(self.wmeta, 'properties'):
            self.wmeta.properties[name] = value

        # 2. Call our custom _set_property to handle real-time color repainting on the active canvas object
        if hasattr(self, 'widget') and self.widget:
            self._set_property(self.widget, name, value)

        # 3. FIXED: Force full visual object recreation on layout structural edits OR state swaps
        # to ensure Pygubu-Designer forces a total clean redrawing window sync pass!
        if name in ('num_columns', 'num_rows', 'columns', 'show_headers', 'state', 'grid_mode'):
            if hasattr(self, "builder") and hasattr(self.builder, "recreate_widget"):
                try:
                    self.builder.recreate_widget(self)
                except Exception:
                    pass


    def code_get_configure_properties(self, code_identifier, entry):
        return []

    def code_get_init_args(self, code_identifier, entry):
        init_args = {}
        w_props = self.wmeta.properties if (hasattr(self, 'wmeta') and hasattr(self.wmeta, 'properties')) else {}
        for prop in self.OPTIONS_CUSTOM:
            value = w_props.get(prop)
            if value is not None and value != '':
                processed = self._process_property_value(prop, value)
                if processed is not None:
                    init_args[prop] = repr(processed)
        return init_args


# =============================================================================
#   🎨 INSPECTOR PANEL PROPERTY REGISTRATION (ORDER ENFORCED)
# =============================================================================
builder_id = f"{builder_namespace}.{widget_classname}"

register_custom_property(builder_id, 'num_columns', 'naturalnumber')
register_custom_property(builder_id, 'num_rows', 'naturalnumber')
register_custom_property(builder_id, 'grid_mode', 'choice', values=('zebra', 'grid', 'none'))
register_custom_property(builder_id, 'show_headers', 'choice', values=('True', 'False'))
register_custom_property(builder_id, 'header_line_width', 'naturalnumber')
register_custom_property(builder_id, 'outline_width', 'integernumber')
register_custom_property(builder_id, 'outline_radius', 'naturalnumber')
register_custom_property(builder_id, 'state', 'choice', values=('normal', 'disabled'))
register_custom_property(builder_id, 'cell_bg_color', 'entry')
register_custom_property(builder_id, 'cell_alt_bg_color', 'entry')

register_custom_property(
    builder_id, 'editable_columns', 'entry',
    help="Which columns can be edited, by index -- e.g. 1, 2. Blank means "
         "every column. The rest are read-only.")
register_custom_property(
    builder_id, 'edit_trigger', 'choice', values=('double', 'select'),
    help="double: double-click a cell to edit it. select: click a cell in the "
         "row that is already selected, which leaves double-click free for "
         "bind_activate_callback.")
register_custom_property(
    builder_id, 'select_rows', 'choice', values=('True', 'False'),
    help="Highlight the row last clicked. Always on with edit_trigger "
         "'select', which needs a selection to work.")

# 👑 Columns text registration placed dead last!
register_custom_property(builder_id, 'columns', 'entry', "","Enter list of columns e.g., ['One','Two','Three']")

register_widget(builder_id, sCTkTableviewBO, 'sCTkTableview', ("ttk", section_name))
