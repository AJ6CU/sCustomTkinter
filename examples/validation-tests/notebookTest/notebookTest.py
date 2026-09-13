#!/usr/bin/python3
"""
notebookTest

notebookTest

UI source file: NotebookTest.ui
"""
import pathlib
import tkinter as tk
import pygubu
from notebookTestui import notebookTestUI

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "NotebookTest.ui"
RESOURCE_PATHS = [PROJECT_PATH]


class notebookTest(notebookTestUI):
    def __init__(self, master=None):
        super().__init__(
            master,
            project_ui=PROJECT_UI,
            resource_paths=RESOURCE_PATHS,
            translator=None,
            on_first_object_cb=None
        )
        self.builder.connect_callbacks(self)


if __name__ == "__main__":
    app = notebookTest()
    app.run()
