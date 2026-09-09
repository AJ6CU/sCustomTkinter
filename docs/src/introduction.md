# Introduction

sCustomTkinter extends [CustomTkinter](https://customtkinter.tomschimansky.com/) with a set of widgets built for instrument panels and control applications — meters, dials, tables, file pickers — alongside themed variants of the standard controls. Every colour and font comes from one file, so an application can be restyled without touching its code.

This manual opens with four sections worth reading before the reference.

**Theming** is the one to read first. It covers `sCTkThemes.json`, how a local copy overrides the bundled one, and the several ways a hand-edited theme file can break. Widgets fail loudly on a missing key rather than substituting a guess, so knowing the format saves time.

**Scrolling** covers the container widgets and how wheel and trackpad input is handled across platforms. Read it if you are using `sCTkScrollableFrame` or `sCTkScrollArea`, or if scrolling feels wrong on your hardware.

**List Properties** is short. Several widgets take a list of strings — column headings, menu items, dial labels — and they all accept the same formats. Learn it once.

**Designer Hints** covers working in Pygubu Designer: how images resolve, why some widgets cannot be selected on the canvas, and what the green background means. Skip it if you build your interfaces in code.

The rest of the manual is reference, grouped into Containers, Controls and Display, Menus, and Additional Widgets. Each widget page has a screenshot in both light and dark modes, its constructor and properties, its public methods, and the theme block it reads — that last section is the place to start if you want to restyle something.

Most pages end with a runnable example. They are meant to be copied and run as they are.

Where a page explains why something works the way it does, or records a limitation, it is usually because the alternative was tried and did not work. Those notes are worth reading before assuming a behaviour is a bug.
