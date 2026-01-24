from __future__ import annotations

from docx.document import Document as _Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def ensure_multilevel_heading_numbering(doc: _Document) -> None:
    """
    Настраивает многоуровневую нумерацию для Heading 1–3.

    - Heading 1 -> уровень 0 (1., 2., 3., ...).
    - Heading 2 -> уровень 1 (1.1., 1.2., ...).
    - Heading 3 -> уровень 2 (1.1.1., 1.1.2., ...).
    """
    numbering_part = doc.part.numbering_part
    numbering_elm = numbering_part.element

    abstract_num = OxmlElement("w:abstractNum")
    abstract_num.set(qn("w:abstractNumId"), "1")

    for ilvl, fmt, text in [
        ("0", "decimal", "%1."),
        ("1", "decimal", "%1.%2."),
        ("2", "decimal", "%1.%2.%3."),
    ]:
        lvl = OxmlElement("w:lvl")
        lvl.set(qn("w:ilvl"), ilvl)

        num_fmt = OxmlElement("w:numFmt")
        num_fmt.set(qn("w:val"), fmt)
        lvl.append(num_fmt)

        lvl_text = OxmlElement("w:lvlText")
        lvl_text.set(qn("w:val"), text)
        lvl.append(lvl_text)

        start = OxmlElement("w:start")
        start.set(qn("w:val"), "1")
        lvl.append(start)

        ppr = OxmlElement("w:pPr")
        ind = OxmlElement("w:ind")
        ind.set(qn("w:left"), "0")
        ind.set(qn("w:hanging"), "0")
        ppr.append(ind)
        lvl.append(ppr)

        abstract_num.append(lvl)

    numbering_elm.append(abstract_num)

    num = OxmlElement("w:num")
    num.set(qn("w:numId"), "1")
    abstract_ref = OxmlElement("w:abstractNumId")
    abstract_ref.set(qn("w:val"), "1")
    num.append(abstract_ref)
    numbering_elm.append(num)

    style_map = {
        "Heading 1": ("0", "1"),
        "Heading 2": ("1", "1"),
        "Heading 3": ("2", "1"),
    }

    for style_name, (ilvl, num_id) in style_map.items():
        try:
            style = doc.styles[style_name]
        except KeyError:
            continue

        style_elm = style.element
        ppr = style_elm.get_or_add_pPr()

        num_pr = OxmlElement("w:numPr")

        ilvl_elm = OxmlElement("w:ilvl")
        ilvl_elm.set(qn("w:val"), ilvl)
        num_pr.append(ilvl_elm)

        num_id_elm = OxmlElement("w:numId")
        num_id_elm.set(qn("w:val"), num_id)
        num_pr.append(num_id_elm)

        ppr.append(num_pr)
