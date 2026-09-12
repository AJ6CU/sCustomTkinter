#!/usr/bin/python3
"""
sCTkSelector Builder Object
"""
import pygubu
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
    register_custom_property
)
from scustomtkinter.sctk_selector import sCTkSelector
from scustomtkinter.themeable_widget import parse_list_property
from pygubu.plugins.customtkinter.widgets import CTkFrameBO

widget_namespace = "scustomtkinter.sctk_selector"
widget_classname = "sCTkSelector"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkSelectorBO(BuilderObject):
    class_ = sCTkSelector

    # OPTIONS_STANDARD = ('height', 'width')
    # 1. Append 'state' to your custom options tuple array
    # grid_propagate is deliberately absent. pack_propagate() and
    # grid_propagate() control whether a container resizes to fit its CHILDREN,
    # and which applies depends on how those children are managed -- this
    # widget packs its own, so grid_propagate could never have an effect. It
    # was offered anyway, which made it look like a knob that did nothing.
    OPTIONS_CUSTOM = ('items', 'multiple_choices', 'pack_propagate', 'state')
    properties = CTkFrameBO.properties + OPTIONS_CUSTOM

    OPTIONS_CUSTOM_DEFAULTS = {
        'multiple_choices': 'True',
        'items': '["Item 1", "Item 2"]',
        'pack_propagate': 'True',
        'state': 'normal'
    }

    # NOT a container. sCTkSelector builds and manages its own checkbox list
    # from the `items` property, laying them out inside its internal
    # checkboxes_frame. A child dropped in from the Designer would land in an
    # unmanaged position and be destroyed by the next rebuild -- which happens
    # whenever `items` changes. It inherits sCTkFrame and composes an
    # sCTkScrollableFrame internally, which is what made it LOOK like a
    # container to the Designer.
    container = False
    container_layout = False

    def realize(self, parent, extra_init_args: dict = None):
        if extra_init_args is None:
            extra_init_args = {}

        # Shared parser: accepts the quoted-list form, a bare comma-separated
        # string, or a real list -- see parse_list_property(). The inspector
        # default is the quoted-list form, which is what Pygubu Designer users
        # expect and is the only one of the two text forms that can express a
        # value containing a comma.
        items_val = self.wmeta.properties.get('items', '["Item 1", "Item 2"]')
        items_arg = parse_list_property(items_val, default=["Item 1", "Item 2"])

        mult_choice = self.wmeta.properties.get('multiple_choices', 'True')
        mult_choice_arg = str(mult_choice).lower() in ['true', '1', 'yes']

        p_prop = self.wmeta.properties.get('pack_propagate', 'True')
        p_prop_arg = str(p_prop).lower() in ['true', '1', 'yes']

        # 2. Extract designer state choice
        state_arg = self.wmeta.properties.get('state', 'normal')

        init_args = {
            'items': items_arg,
            'multiple_choices': mult_choice_arg,
            'pack_propagate': p_prop_arg,
            'state': state_arg
        }

        for prop in self.OPTIONS_CUSTOM:
            extra_init_args.pop(prop, None)

        init_args.update(extra_init_args)
        real_master = parent.widget if hasattr(parent, 'widget') else parent
        self.widget = self.class_(real_master, **init_args)
        return self.widget

    def set_property(self, name, value):
        """
        Rebuilds the widget after a structural change.

        Some properties cannot be expressed by configuring the existing
        widget. A size only takes effect once Tk runs a geometry pass, and
        turning pack_propagate back on merely tells it what to do at the next
        one -- in an application the next event triggers that invisibly, but in
        the Designer nothing else happens, so clearing a height appeared to do
        nothing until an unrelated edit forced a repaint. `items` rebuilds the
        checkbox list outright.

        recreate_widget() is what the Designer itself does when you add or
        delete a widget, which is why doing that by hand made the change
        appear. sCTkTableviewBO uses the same call for the same reason.

        Deliberately NOT used for colours: rebuilding on every keystroke in a
        colour field would be unpleasant, and a colour needs no rebuild.
        """
        print("[selbo] set_property:", name, repr(value))
        super().set_property(name, value)

        if name in ("width", "height", "items", "pack_propagate"):
            if hasattr(self, "builder") and hasattr(self.builder, "recreate_widget"):
                try:
                    self.builder.recreate_widget(self)
                except Exception:
                    # A widget not yet realized, or a builder that does not
                    # offer the call. Losing the rebuild costs a stale canvas,
                    # not correctness -- the .ui data is already updated.
                    pass
    def _set_property(self, target_widget, pname, value):
        print("[selbo] _set_property:", pname, repr(value))
        super()._set_property(target_widget, pname, value)

    def _code_set_property(self, targetid, pname, value, code_bag):
        """
        The low-level code generation interception layer.
        Ensures lists and booleans write as raw tokens, while text properties
        like 'state' write out with proper Python string quotes.
        """
        # 1. Handle properties that MUST be generated as raw unquoted Python code/tokens
        if pname in ('items', 'multiple_choices', 'pack_propagate'):
            clean_string = str(value).strip("'\"")
            code_bag[pname] = clean_string

        # 2. FIXED: Handle properties that MUST keep their string quote wrappers
        elif pname == 'state':
            # Force it to explicitly keep single quotes, preventing NameErrors at runtime
            clean_string = str(value).strip("'\"")
            code_bag[pname] = f"'{clean_string}'"

        else:
            super()._code_set_property(targetid, pname, value, code_bag)


builder_id = f"{builder_namespace}.{widget_classname}"

register_widget(
    builder_id, sCTkSelectorBO, widget_classname, ("ttk", section_name)
)

register_custom_property(
    builder_id,
    'items',
    'entry',
    help='Preferred: ["A", "B", "C"]. Bare comma-separated (A, B, C) also works, but cannot contain a comma inside a value.'
)

register_custom_property(builder_id, 'multiple_choices', 'choice', values=('True', 'False'))
# 4. Register the new UI type as a dropdown option selection field
register_custom_property(builder_id, 'state', 'choice', values=('normal', 'disabled'))

# 2. Register custom UI types as standard True/False dropdown pickers
register_custom_property(
    builder_id, 'pack_propagate', 'choice', values=('True', 'False'),
    help="False stops the widget resizing to fit its checkboxes, so an "
         "explicit width and height are honoured."
)
