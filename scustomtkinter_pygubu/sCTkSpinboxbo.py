import pygubu
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
    register_custom_property
)
from sCTkSpinbox import sCTkSpinbox

widget_namespace = "sCTkSpinbox"
widget_classname = "sCTkSpinbox"
builder_namespace = "custom_widgets"
section_name = "sCustomTkinter"


class sCTkSpinboxBO(BuilderObject):
    class_ = sCTkSpinbox

    # 📐 STREAMLINED PROPERTY MATRIX: Removed textvariable entirely to isolate programmatic get/set paths!
    # Centralized typography assets and custom configuration keys match your widget core exactly.
    OPTIONS_CUSTOM = ('from_', 'to', 'step_size', 'format', 'button_width',
                      'button_height', 'button_side', 'orientation',
                      'arrow_font_size',  'arrow_up_char',
                      'arrow_down_char', 'arrow_right_char', 'arrow_left_char',
                      'state', 'justify', 'placeholder_text', 'values', 'wrap')

    properties = OPTIONS_CUSTOM
    command_properties = ("command",)

    container = False

    @classmethod
    def setup_properties(cls):
        super().setup_properties()
        for prop in cls.OPTIONS_CUSTOM:
            if prop not in cls.properties:
                cls.properties = cls.properties + (prop,)

    def _process_property_value(self, name, value):
        """Sanitizes property input types, protecting string specifiers from truncation."""
        if value is None or str(value).strip() == "":
            return None
        if name in ('button_width', 'button_height', 'arrow_font_size'):
            return int(str(value).strip())
        if name in ('from_', 'to', 'step_size'):
            return float(str(value).strip())
        if name == 'wrap':
            return str(value).lower() in ("true", "1", "yes")
        # Custom characters, values strings, and format masks pass completely un-mangled
        return str(value).strip()

    def _get_init_args(self, extra_init_args=None):
        """Assembles early configuration properties sequentially into initialization pools."""
        args = super()._get_init_args(extra_init_args)
        w_props = self.wmeta.properties if (hasattr(self, 'wmeta') and hasattr(self.wmeta, 'properties')) else {}

        for prop in self.OPTIONS_CUSTOM:
            if prop == 'command':
                continue
            val = w_props.get(prop)
            if val is not None and str(val).strip() != "":
                args[prop] = self._process_property_value(prop, val)

        if 'from_' not in args or args['from_'] is None:
            args['from_'] = 0.0

        return args

    def set_property(self, name, value):
        """Routes dynamic inspector panel property adjustments straight into the live instance."""
        if hasattr(self, 'wmeta') and hasattr(self.wmeta, 'properties'):
            self.wmeta.properties[name] = value

        if hasattr(self, 'widget') and self.widget:
            if name == 'command':
                processed = self.builder.get_callback(value)
            else:
                processed = self._process_property_value(name, value)

            if processed is not None or name == 'command':
                self.widget.configure(**{name: processed})

    def code_get_configure_properties(self, code_identifier, entry):
        """Instructs Pygubu's compiler to pipe callbacks through native channels."""
        return ['command']

    def code_get_init_args(self, code_identifier, entry):
        """Emits pristine syntax definitions for compilation into final exported Python scripts."""
        init_args = {}
        w_props = self.wmeta.properties if (hasattr(self, 'wmeta') and hasattr(self.wmeta, 'properties')) else {}
        for prop in self.OPTIONS_CUSTOM:
            if prop == 'command':
                continue
            value = w_props.get(prop)
            if value is not None and value != '':
                processed = self._process_property_value(prop, value)
                if processed is not None:
                    # Enforce clean string literal encapsulation inside the code emitter pipelines
                    if prop in ('format', 'values', 'button_side', 'orientation', 'justify',
                                'placeholder_text', 'arrow_up_char', 'arrow_down_char',
                                'arrow_right_char', 'arrow_left_char'):
                        init_args[prop] = f'"{processed}"'
                    else:
                        init_args[prop] = repr(processed)
        return init_args


# =============================================================================
#   🎨 INSPECTOR PANEL PROPERTY REGISTRATION (ORDER ENFORCED)
# =============================================================================
# Ensure this section sits firmly flush against the left wall margin!
builder_id = f"{builder_namespace}.{widget_classname}"

register_custom_property(builder_id, 'format', 'entry')
register_custom_property(builder_id, 'from_', 'entry')
register_custom_property(builder_id, 'to', 'entry')
register_custom_property(builder_id, 'step_size', 'entry')
register_custom_property(builder_id, 'values', 'entry')
register_custom_property(builder_id, 'wrap', 'choice', values=('True', 'False'))
register_custom_property(builder_id, 'button_width', 'naturalnumber')
register_custom_property(builder_id, 'button_height', 'naturalnumber')
register_custom_property(builder_id, 'button_side', 'choice', values=('right', 'left', 'split'))
register_custom_property(builder_id, 'orientation', 'choice', values=('vertical', 'horizontal'))
register_custom_property(builder_id, 'arrow_font_size', 'naturalnumber')

register_custom_property(builder_id, 'arrow_up_char', 'entry')
register_custom_property(builder_id, 'arrow_down_char', 'entry')
register_custom_property(builder_id, 'arrow_right_char', 'entry')
register_custom_property(builder_id, 'arrow_left_char', 'entry')

register_custom_property(builder_id, 'state', 'choice', values=('normal', 'disabled'))
register_custom_property(builder_id, 'justify', 'choice', values=('left', 'center', 'right'))
register_custom_property(builder_id, 'placeholder_text', 'entry')
register_custom_property(builder_id, 'command', 'commandentry')

# FLUSH MARGIN LEFT SCOPE EXECUTION FOR PYGUBU DISCOVERY
register_widget(builder_id, sCTkSpinboxBO, 'sCTkSpinbox', ("ttk", section_name))
