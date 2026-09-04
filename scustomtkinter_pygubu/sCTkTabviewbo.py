#!/usr/bin/python3
"""
sCTkTabview

Built on top of CTkTabview.

UI source file: sCTkTabview.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from customtkinter import CTkTabview
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
    copy_custom_property,
)

from pygubu.plugins.customtkinter import nsctk
from pygubu.plugins.customtkinter.tabview import CTkTabviewBO, CTkTabviewTabBO
from scustomtkinter.sctk_tabview import sCTkTabview
from scustomtkinter.sctk_frame import sCTkFrame


#
# Builder definition section
#
widget_namespace = "scustomtkinter.sctk_tabview"
widget_classname = "sCTkTabview"
builder_namespace = "scustomtkinter"
section_name = "sCustomTkinter"


class sCTkTabviewBO(CTkTabviewBO):
    class_ = sCTkTabview

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        imports = [(widget_namespace, widget_classname)]
        imports.extend(self.code_extra_imports())
        return imports


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sCTkTabviewBO, widget_classname, ("ttk", section_name)
)


# =====================================================================
# sCTkTabview.Tab
#
# A tab is not a widget you construct -- it is created BY its parent tabview,
# through add(). So this builder object has class_ = None and overrides
# realize() to call the parent's add() rather than instantiating anything.
# That is CTkTabviewTabBO's design and this inherits it; only the naming,
# the parent constraint and the generated code differ.
#
# WHAT add() RETURNS. sCTkTabview.add() hands back an sCTkFrame page wrapper
# nested inside the native tab frame, not the native frame itself -- see the
# widget's own docs. That is exactly what a container builder object wants:
# children dropped onto the tab land in the wrapper, which is a themed sCTk
# widget rather than a bare ctk.CTkFrame. No extra work is needed here to get
# that; realize() simply returns whatever add() gives it.
# =====================================================================
class sCTkTabviewTabBO(CTkTabviewTabBO):
    # Only this tabview may hold this tab. Without the constraint the Designer
    # would offer sCTkTabview.Tab as a child of anything, and dropping one
    # elsewhere would fail at realize() when the parent turned out to have no
    # add() method.
    allowed_parents = (builder_id,)

    def realize(self, parent, extra_init_args: dict = None):
        """
        Creates the tab, renaming it if that name is already taken.

        Native CTkTabview.add() raises ValueError on a duplicate name. Inside
        the Designer that exception surfaces only on the console, where nobody
        is looking -- the tab silently fails to appear and the tree and the
        preview disagree about what exists.

        A unique suffix is appended instead, and written back into the widget
        metadata so the inspector's `label` field updates too. Typing "mark"
        for a second tab therefore produces a visible "mark_2" rather than an
        invisible error. That is feedback the user actually receives.

        Deliberately NOT done in sCTkTabview itself: the widget keeps raising,
        so application code that creates a duplicate tab still fails loudly
        rather than quietly getting a renamed one. This leniency is a
        design-time affordance, not a change to the widget's contract.
        """
        view = parent.get_child_master()
        name = self._get_tab_name()

        # _name_list is CTkTabview's own record of tab names, in order.
        existing = list(getattr(view, "_name_list", []))
        if name in existing:
            suffix = 2
            while f"{name}_{suffix}" in existing:
                suffix += 1
            name = f"{name}_{suffix}"
            # Write it back so the inspector and the generated code agree with
            # what is actually on screen.
            self.wmeta.properties["label"] = name

        self.widget = view.add(name)
        return self.widget

    @staticmethod
    def _find_tabview(widget):
        """Walk up from a page wrapper to the sCTkTabview that owns it."""
        node = widget
        for _ in range(6):          # page -> native tab frame -> tabview
            if node is None:
                return None
            if isinstance(node, sCTkTabview):
                return node
            node = getattr(node, "master", None)
        return None

    def configure(self, target=None):
        """
        Applies a changed `label` by renaming the live tab.

        CTkTabviewTabBO.configure() is a no-op -- `pass` -- so editing the
        label in the inspector updated the metadata but never touched the
        widget: the design area kept the old name while the preview, which
        rebuilds from scratch, showed the new one.

        EVERYTHING IS DERIVED FROM self.widget, deliberately. An earlier
        version stashed the parent view and the created name on the builder
        object during realize() and read them back here -- which failed,
        because Pygubu calls configure() on a builder object whose realize()
        never ran. Tracing showed those instances arriving with the new label
        correctly set but no instance state at all:

            [TabBO.configure] view=False old=None new='sue'

        The page wrapper is the only reliable anchor: walk up from it to find
        the tabview, then find the wrapper in that tabview's page registry to
        learn the name it is currently filed under.
        """
        widget = getattr(self, "widget", None)
        if widget is None:
            return

        view = self._find_tabview(widget)
        if view is None:
            return

        # The name this page is currently registered under, found by identity
        # rather than by trusting any stored value.
        old_name = None
        for name, page in getattr(view, "_sctk_pages", {}).items():
            if page is widget:
                old_name = name
                break
        if old_name is None:
            return

        new_name = self._get_tab_name()
        if new_name == old_name:
            return

        existing = [n for n in getattr(view, "_name_list", []) if n != old_name]
        if new_name in existing:
            suffix = 2
            while f"{new_name}_{suffix}" in existing:
                suffix += 1
            new_name = f"{new_name}_{suffix}"
            self.wmeta.properties["label"] = new_name

        try:
            view.rename(old_name, new_name)
        except Exception:
            # Widget torn down mid-edit, or a native rename this build of
            # CustomTkinter doesn't support. The preview rebuild still shows
            # the new label, so this degrades rather than breaks.
            return

    def code_realize(self, boparent, code_identifier=None):
        """
        Emits the tab creation line.

        Overridden only to keep the generated code honest about which class
        the returned page is: sCTkTabview.add() returns an sCTkFrame wrapper,
        so the comment tells a reader what they are holding. The call itself
        is identical to the parent implementation's.
        """
        view = boparent.code_child_master()
        tabid = self.code_identifier()
        tab_name = self._get_tab_name()
        return [f'{tabid} = {view}.add("{tab_name}")  # returns an sCTkFrame']


tab_builder_id = f"{builder_namespace}.sCTkTabviewTab"
register_widget(
    tab_builder_id,
    sCTkTabviewTabBO,
    f"{widget_classname}.Tab",
    ("ttk", section_name),
)

#
# Wire the parent/child relationship in both directions. Pygubu checks both:
# add_allowed_child() lets the Designer offer the tab when a tabview is
# selected, and allowed_parents on the class above stops it being offered
# anywhere else.
#
sCTkTabviewBO.add_allowed_child(tab_builder_id)

#
# CustomTkinter's own tab is still accepted, so existing .ui files that used
# CTkTabview.Tab inside an sCTkTabview keep loading. New designs should use
# sCTkTabview.Tab above -- it is the one that appears under the sCustomTkinter
# palette section.
#
sCTkTabviewBO.add_allowed_child(nsctk.CTkTabviewTab)
CTkTabviewTabBO.add_allowed_parent(builder_id)

# NOTE: an earlier version of this file also called
#     sCTkTabviewBO.add_allowed_child(sCTkFrame)
# passing the CLASS. add_allowed_child() takes a builder id STRING, so that
# call silently matched nothing and had no effect. Removed rather than
# corrected: a tabview's children are tabs, and a frame belongs inside a tab
# rather than directly in the tabview.