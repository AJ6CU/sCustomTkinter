#!/usr/bin/env python3
"""
Makes anchors unique per widget section in the merged manual.

THE PROBLEM. Every widget page carries its own `<a name="contents">`, its own
`#overview`, its own `#theming-sctkthemesjson`. Merged into one document those
collide: WeasyPrint warns

    WARNING: Anchor defined twice: 'where-the-file-lives'

and every internal link jumps to the first occurrence in the document rather
than the one in the section the reader is actually in. In a 147-page manual
that means clicking "Theming" on the spinbox page lands you on the buttons.

THE FIX, IN TWO PASSES. Each H2 starts a section, and every id inside it is
prefixed with that section's slug. Links are rewritten afterwards, not during,
because a link's target is not always in the same section as the link: the
Theming page's own contents list points at H2s further down the document, each
of which is a section in its own right. A single-pass, section-scoped rewrite
left those links pointing at names that no longer existed -- it turned 317
working links into broken ones.

So a link resolves in this order:

  1. the matching id in the SAME section, which is what a page's own contents
     list wants;
  2. otherwise the first matching id anywhere, which is what a cross-reference
     to another page wants, and is what the links did before any of this.

Run on the pandoc HTML, before the PDF step.
"""
import re
import sys


def slug(text):
    """Reduce a heading to a usable id fragment."""
    s = re.sub(r"<[^>]+>", "", text).lower()
    s = re.sub(r"[^a-z0-9 _-]", "", s)
    return re.sub(r"\s+", "-", s.strip())


def strip_pandoc_css(html):
    """
    Removes pandoc's own embedded stylesheet.

    --standalone embeds it, and it carries rules WeasyPrint does not implement:

        Ignored `text-rendering: optimizeLegibility`, unknown property
        Invalid media type ' (max-width: 600px) '
        Ignored `user-select: none`, unknown property

    Harmless in themselves, but they bury the warnings that matter. pandoc's
    --variable document-css=false is meant to suppress this and is silently
    ignored on some builds, so it is stripped here instead. manual.css is the
    only stylesheet the document needs.
    """
    return re.sub(r"<style>.*?</style>", "", html, flags=re.S)


def main(path):
    html = strip_pandoc_css(open(path, encoding="utf-8").read())

    # Split on H1 *and* H2. The merged manual has two kinds of page-level
    # heading: the cross-cutting sections and group dividers use H1, each
    # widget page uses H2. Splitting on H2 alone left every H1 page sitting in
    # the preamble with its anchors unrenamed, so they stayed duplicated.
    parts = re.split(r"(<h[12]\b[^>]*>)", html)
    if len(parts) < 3:
        print("no H2 sections found; nothing to do")
        return

    # ---- pass one: rename every id, recording where each one went ---------
    sections = []          # (prefix, chunk) in document order
    local_maps = []        # old id -> new id, per section
    global_map = {}        # old id -> new id, first occurrence wins

    for i in range(1, len(parts), 2):
        opening = parts[i]
        body = parts[i + 1] if i + 1 < len(parts) else ""
        chunk = opening + body

        heading = re.match(r"(.*?)</h[12]>", body, re.S)
        prefix = slug(heading.group(1)) if heading else f"section-{i}"

        mapping = {}
        seen = {}

        def rename(match, mapping=mapping, seen=seen, prefix=prefix):
            attr, value = match.group(1), match.group(2)
            new = f"{prefix}--{value}"
            count = seen.get(new, 0)
            seen[new] = count + 1
            if count:
                # The same name twice inside one section: the source markdown
                # often has an explicit <a name="sizing"></a> right above a
                # heading pandoc also gives id="sizing".
                new = f"{new}-{count + 1}"
            mapping.setdefault(value, new)
            return f'{attr}="{new}"'

        chunk = re.sub(r'\b(id|name)="([^"]+)"', rename, chunk)

        for old, new in mapping.items():
            global_map.setdefault(old, new)

        sections.append((prefix, chunk))
        local_maps.append(mapping)

    # Anything before the first heading keeps its own anchors, but its ids
    # still have to be resolvable -- pandoc numbers code-block lines there
    # (#cb1-1 and friends), and a link to one would otherwise be reported as
    # missing.
    for m in re.finditer(r'(?:id|name)="([^"]+)"', parts[0]):
        global_map.setdefault(m.group(1), m.group(1))

    # ---- pass two: rewrite links, local target preferred ------------------
    out = [parts[0]]
    unresolved = set()

    for (prefix, chunk), mapping in zip(sections, local_maps):

        def relink(match, mapping=mapping):
            target = match.group(1)
            new = mapping.get(target) or global_map.get(target)
            if new is None:
                unresolved.add(target)
                return match.group(0)
            return f'href="#{new}"'

        out.append(re.sub(r'href="#([^"]+)"', relink, chunk))

    # The preamble sits before the first H2 and keeps its own anchors, but its
    # links still point into the sections below.
    def relink_preamble(match):
        target = match.group(1)
        new = global_map.get(target)
        if new is None:
            unresolved.add(target)
            return match.group(0)
        return f'href="#{new}"'

    out[0] = re.sub(r'href="#([^"]+)"', relink_preamble, out[0])

    open(path, "w", encoding="utf-8").write("".join(out))
    print(f"anchors namespaced across {len(sections)} sections")
    if unresolved:
        print(f"  {len(unresolved)} link targets not found in the document:")
        for t in sorted(unresolved)[:10]:
            print(f"    #{t}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "docs/.manual.html")
