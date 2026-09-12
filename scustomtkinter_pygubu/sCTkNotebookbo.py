#!/usr/bin/python3
"""
sCTkNotebook

Pygubu builder objects for the vertical-tab notebook and for the tabs
themselves.

A TAB IS NOT A WIDGET. It is created by its notebook, through add(), so the
tab builder object has no class of its own to instantiate -- it calls the
parent's add() and hands back the sCTkFrame that comes out. Generated code
reads:

    tab1 = notebook1.add("Receiver")

which is the same arrangement sCTkTabviewbo uses for CTkTabview's tabs, and
for the same reason.
"""
import tkinter as tk

from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
    register_custom_property,
)
from pygubu.plugins.customtkinter.widgets import CTkFrameBO

from scustomtkinter.sctk_notebook import sCTkNotebook

widget_namespace = "scustomtkinter.sctk_notebook"
widget_classname = "sCTkNotebook"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkNotebookBO(CTkFrameBO):
    class_ = sCTkNotebook

    OPTIONS_CUSTOM = (
        "side", "tab_width", "tab_style", "text_orientation",
        "show_page_border", "show_tab_separators", "state",
    )
    properties = CTkFrameBO.properties + OPTIONS_CUSTOM

    OPTIONS_CUSTOM_DEFAULTS = {
        "side": "left",
        "tab_width": "34",
        "tab_style": "rounded",
        "text_orientation": "auto",
        "show_page_border": "True",
        "show_tab_separators": "False",
        "state": "normal",
    }

    # A container, but only for its own tabs -- see allowed_children below.
    container = True
    container_layout = False

    def realize(self, parent, extra_init_args: dict = None):
        """
        Builds the notebook with its own properties as constructor arguments.

        side and tab_style are validated by the widget and raise on a bad
        value, so they have to arrive as real values rather than being set
        afterwards -- a half-built widget in the Designer is worse than a
        clear error.
        """
        if extra_init_args is None:
            extra_init_args = {}

        props = self.wmeta.properties
        init_args = {
            "side": props.get("side", "left"),
            "tab_style": props.get("tab_style", "rounded"),
            "text_orientation": props.get("text_orientation", "auto"),
            "tab_width": int(props.get("tab_width", 34) or 34),
            "show_page_border": self._as_bool(props.get("show_page_border", "True")),
            "show_tab_separators": self._as_bool(
                props.get("show_tab_separators", "False")),
            "state": props.get("state", "normal"),
        }

        for prop in self.OPTIONS_CUSTOM:
            extra_init_args.pop(prop, None)
        init_args.update(extra_init_args)

        real_master = parent.widget if hasattr(parent, "widget") else parent
        self.widget = self.class_(real_master, **init_args)
        return self.widget

    @staticmethod
    def _as_bool(value):
        """
        Parses the Designer's strings.

        bool("False") is True, which would switch on every option whose
        dropdown said otherwise.
        """
        if isinstance(value, str):
            return value.strip().lower() in ("true", "1", "yes", "on")
        return bool(value)

    def _process_property_value(self, pname, value):
        if pname == "tab_width":
            return int(value)
        if pname in ("show_page_border", "show_tab_separators"):
            return self._as_bool(value)
        return super()._process_property_value(pname, value)

    def _code_set_property(self, targetid, pname, value, code_bag):
        """Booleans and the width emit as tokens; the rest keep their quotes."""
        if pname in ("show_page_border", "show_tab_separators", "tab_width"):
            code_bag[pname] = str(value).strip("'\"")
        elif pname in ("side", "tab_style", "text_orientation", "state"):
            code_bag[pname] = f"'{str(value).strip(chr(39) + chr(34))}'"
        else:
            super()._code_set_property(targetid, pname, value, code_bag)

    def code_imports(self):
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(builder_id, sCTkNotebookBO, widget_classname,
                ("ttk", section_name))


# ---------------------------------------------------------------------------
# The tab
# ---------------------------------------------------------------------------
class sCTkNotebookTabBO(BuilderObject):
    """
    A page in an sCTkNotebook.

    Has no class_ of its own: a tab is made by the notebook's add(), which
    returns the sCTkFrame that children are then parented to.
    """

    class_ = None
    container = True
    container_layout = True
    layout_required = False
    allow_bindings = False
    properties = ("label",)
    OPTIONS_CUSTOM_DEFAULTS = {"label": "Tab"}

    def realize(self, parent, extra_init_args: dict = None):
        """
        Asks the parent notebook for a page.

        DUPLICATE NAMES ARE RENAMED, NOT REJECTED. The widget's own add()
        raises ValueError on a name already in use, which is right for
        application code -- but inside the Designer that exception surfaces
        only on the console, where nobody sees it, and the tab silently fails
        to appear while the tree and the preview disagree. A numeric suffix is
        appended instead, visibly, in both the tab strip and the property
        field. Same accommodation sCTkTabviewbo makes.
        """
        master = parent.widget if hasattr(parent, "widget") else parent
        label = self.wmeta.properties.get("label", self.wmeta.identifier)

        existing = master.tabs()
        if label in existing:
            suffix = 2
            while f"{label}_{suffix}" in existing:
                suffix += 1
            label = f"{label}_{suffix}"
            self.wmeta.properties["label"] = label

        self._label = label
        self.widget = master.add(label)
        return self.widget

    def _set_property(self, target_widget, pname, value):
        """
        Rebuilds the notebook when a tab is renamed.

        A tab's label is consumed by realize() -- it is the name add() was
        called with -- so changing it afterwards cannot be expressed by
        configuring the existing page. Without a rebuild the strip went on
        showing the old caption until some unrelated edit forced a repaint.

        recreate_widget() is what the Designer itself does when you add or
        delete a widget, which is why doing that by hand made the change
        appear. It hangs off _set_property, NOT set_property: the Designer
        edits a property through the former, and the latter is never called.
        """
        if pname == "label":
            # CONSUMED HERE, never delegated.
            #
            # The base implementation forwards an unknown property to
            # widget.configure(), and a page is an ordinary sCTkFrame:
            #
            #     Failed to set property 'label' on class 'None'.
            #     Error: ['label'] are not supported arguments.
            #
            # The label is not a property of the page -- it is the name its
            # notebook filed it under, consumed by realize().
            #
            # RENAMED THROUGH THE NOTEBOOK, not by rebuilding the tab.
            # Rebuilding re-runs realize(), which calls add() again while the
            # old name is still registered -- so the strip kept the old
            # caption until something forced a repaint. rename() re-keys the
            # page in place and redraws, which is what the widget provides it
            # for.
            new_label = str(value)
            old_label = getattr(self, "_label", None)
            if old_label and new_label and new_label != old_label:
                try:
                    notebook = self._find_notebook(target_widget)
                    if notebook is not None:
                        notebook.rename(old_label, new_label)
                        self._label = new_label
                except Exception:
                    # A duplicate name, or a page not yet attached. The .ui
                    # data is already updated either way.
                    pass
            return

        super()._set_property(target_widget, pname, value)

    @staticmethod
    def _find_notebook(page):
        """
        Climbs from a page to the notebook that owns it.

        A page is parented to the notebook's internal page host, not to the
        notebook, so the immediate parent is the wrong object.
        """
        try:
            top = page.winfo_toplevel()
            widget = page
            for _ in range(4):
                parent_name = widget.winfo_parent()
                if not parent_name:
                    return None
                widget = top.nametowidget(parent_name)
                if hasattr(widget, "rename") and hasattr(widget, "tabs"):
                    return widget
        except Exception:
            pass
        return None

    def configure(self, target=None):
        """Nothing to configure: the label was consumed by realize()."""
        pass

    def layout(self, target=None, *args, **kwargs):
        """The notebook grids its own pages; a tab takes no layout."""
        pass

    def code_realize(self, boparent, code_identifier=None):
        identifier = code_identifier or self.code_identifier()
        label = self.wmeta.properties.get("label", "Tab")
        return (f'{identifier} = {boparent.code_child_master()}'
                f'.add("{label}")',)

    def code_configure(self, targetid=None):
        return tuple()

    def code_layout(self, targetid=None, parentid=None):
        return tuple()


tab_builder_id = f"{builder_id}.Tab"
register_widget(tab_builder_id, sCTkNotebookTabBO, "sCTkNotebook.Tab",
                ("ttk", section_name))

# A tab has nowhere else to live, so it is offered only inside a notebook.
sCTkNotebookTabBO.allowed_parents = (builder_id,)
sCTkNotebookBO.allowed_children = (tab_builder_id,)


# ---------------------------------------------------------------------------
# Inspector properties
# ---------------------------------------------------------------------------
register_custom_property(
    builder_id, "side", "choice", values=("left", "right"),
    state="readonly", default_value="left",
    help="Which edge the tab strip sits on.")

register_custom_property(
    builder_id, "tab_width", "naturalnumber", default_value="34",
    help="Width of the strip in pixels. Explicit rather than measured, "
         "because the strip takes space from the pages. Horizontal text "
         "needs this wide enough to hold the longest label.")

register_custom_property(
    builder_id, "tab_style", "choice", values=("rounded", "angled"),
    state="readonly", default_value="rounded",
    help="Rounded matches the rest of the library. Angled cuts the outer "
         "corners, the shape of a real notebook divider.")

register_custom_property(
    builder_id, "text_orientation", "choice",
    values=("auto", "up", "down", "horizontal"),
    state="readonly", default_value="auto",
    help="auto reads outside-in and flips with the side. up and down pin the "
         "direction whichever side the strip is on. horizontal lays the text "
         "flat and needs a wider tab_width.")

register_custom_property(
    builder_id, "show_page_border", "choice", values=("True", "False"),
    state="readonly", default_value="True",
    help="Draws the outline around the page, broken where the selected tab "
         "meets it.")

register_custom_property(
    builder_id, "show_tab_separators", "choice", values=("True", "False"),
    state="readonly", default_value="False",
    help="A line between adjacent tabs. Earns its keep with horizontal text, "
         "where stacked labels can run together; rarely otherwise.")

register_custom_property(
    builder_id, "state", "choice", values=("normal", "disabled"),
    state="readonly", default_value="normal",
    help="Disabled dims the strip and stops tab selection. It does not "
         "cascade to the widgets on a page.")

register_custom_property(
    tab_builder_id, "label", "entry", default_value="Tab",
    help="The tab's caption, and the name add() is called with. A duplicate "
         "is renamed with a numeric suffix rather than rejected.")
