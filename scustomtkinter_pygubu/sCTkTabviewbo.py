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