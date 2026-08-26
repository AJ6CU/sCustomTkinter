#!/usr/bin/python3
"""
sCTk

A clean, zero-overhead wrapper subclass of ctk.CTk.
Eliminitates the need for end-users to import customtkinter directly,
acting as the singular core application window root for the sCustomTkinter library.
"""
import customtkinter as ctk

class sCTk(ctk.CTk):
    def __init__(self, fg_color=None, **kwargs):
        # 🔑 THE HOOK PASS: Explicitly scoop up and forward all positional/keyword arguments
        # directly up to the native CustomTkinter top-level application root constructor safely.
        super().__init__(fg_color=fg_color, **kwargs)
