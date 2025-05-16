"""Custom element classes for text-related XML elements"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Callable, cast

from lxml import etree # Added for casting self to ElementBase

from pptx.enum.lang import MSO_LANGUAGE_ID
from pptx.enum.text import (
    MSO_AUTO_SIZE,
    MSO_TEXT_UNDERLINE_TYPE,
    MSO_VERTICAL_ANCHOR,
    PP_PARAGRAPH_ALIGNMENT,
)
from pptx.exc import InvalidXmlError
from pptx.oxml.parser import parse_xml
from pptx.oxml.dml.fill import CT_GradientFillProperties
from pptx.oxml.ns import nsdecls
from pptx.oxml.simpletypes import (
    ST_Coordinate32,
    ST_TextFontScalePercentOrPercentString,
    ST_TextFontSize,
    ST_TextIndentLevelType,
    ST_TextSpacingPercentOrPercentString,
    ST_TextSpacingPoint,
    ST_TextTypeface,
    ST_TextWrappingType,
    XsdBoolean,
    XsdString,
)
from pptx.oxml.xmlchemy import (
    BaseOxmlElement,
    Choice,
    OneAndOnlyOne,
    OneOrMore,
    OptionalAttribute,
    RequiredAttribute,
    ZeroOrMore,
    ZeroOrOne,
    ZeroOrOneChoice,
)
from pptx.util import Emu, Length
from .mathml_symbol_map import MATH_CHAR_TO_LATEX_CONVERSION

if TYPE_CHECKING:
    from pptx.oxml.action import CT_Hyperlink


class CT_RegularTextRun(BaseOxmlElement):
    """`a:r` custom element class"""

    get_or_add_rPr: Callable[[], CT_TextCharacterProperties]

    rPr: CT_TextCharacterProperties | None = ZeroOrOne(  # pyright: ignore[reportAssignmentType]
        "a:rPr", successors=("a:t",)
    )
    t: BaseOxmlElement = OneAndOnlyOne("a:t")  # pyright: ignore[reportAssignmentType]

    @property
    def text(self) -> str:
        """All text of (required) `a:t` child."""
        text = self.t.text
        # -- t.text is None when t element is empty, e.g. '<a:t/>' --
        return text or ""

    @text.setter
    def text(self, value: str):  # pyright: ignore[reportIncompatibleMethodOverride]
        self.t.text = self._escape_ctrl_chars(value)

    @staticmethod
    def _escape_ctrl_chars(s: str) -> str:
        """Return str after replacing each control character with a plain-text escape.

        For example, a BEL character (x07) would appear as "_x0007_". Horizontal-tab
        (x09) and line-feed (x0A) are not escaped. All other characters in the range
        x00-x1F are escaped.
        """
        return re.sub(r"([\x00-\x08\x0B-\x1F])", lambda match: "_x%04X_" % ord(match.group(1)), s)


class CT_TextBody(BaseOxmlElement):
    """`p:txBody` custom element class.

    Also used for `c:txPr` in charts and perhaps other elements.
    """

    add_p: Callable[[], CT_TextParagraph]
    p_lst: list[CT_TextParagraph]

    bodyPr: CT_TextBodyProperties = OneAndOnlyOne(  # pyright: ignore[reportAssignmentType]
        "a:bodyPr"
    )
    p: CT_TextParagraph = OneOrMore("a:p")  # pyright: ignore[reportAssignmentType]

    def clear_content(self):
        """Remove all `a:p` children, but leave any others.

        cf. lxml `_Element.clear()` method which removes all children.
        """
        for p in self.p_lst:
            self.remove(p)

    @property
    def defRPr(self) -> CT_TextCharacterProperties:
        """`a:defRPr` element of required first `p` child, added with its ancestors if not present.

        Used when element is a ``c:txPr`` in a chart and the `p` element is used only to specify
        formatting, not content.
        """
        p = self.p_lst[0]
        pPr = p.get_or_add_pPr()
        defRPr = pPr.get_or_add_defRPr()
        return defRPr

    @property
    def is_empty(self) -> bool:
        """True if only a single empty `a:p` element is present."""
        ps = self.p_lst
        if len(ps) > 1:
            return False

        if not ps:
            raise InvalidXmlError("p:txBody must have at least one a:p")

        if ps[0].text != "":
            return False
        return True

    @classmethod
    def new(cls):
        """Return a new `p:txBody` element tree."""
        xml = cls._txBody_tmpl()
        txBody = parse_xml(xml)
        return txBody

    @classmethod
    def new_a_txBody(cls) -> CT_TextBody:
        """Return a new `a:txBody` element tree.

        Suitable for use in a table cell and possibly other situations.
        """
        xml = cls._a_txBody_tmpl()
        txBody = cast(CT_TextBody, parse_xml(xml))
        return txBody

    @classmethod
    def new_p_txBody(cls):
        """Return a new `p:txBody` element tree, suitable for use in an `p:sp` element."""
        xml = cls._p_txBody_tmpl()
        return parse_xml(xml)

    @classmethod
    def new_txPr(cls):
        """Return a `c:txPr` element tree.

        Suitable for use in a chart object like data labels or tick labels.
        """
        xml = (
            "<c:txPr %s>\n"
            "  <a:bodyPr/>\n"
            "  <a:lstStyle/>\n"
            "  <a:p>\n"
            "    <a:pPr>\n"
            "      <a:defRPr/>\n"
            "    </a:pPr>\n"
            "  </a:p>\n"
            "</c:txPr>\n"
        ) % nsdecls("c", "a")
        txPr = parse_xml(xml)
        return txPr

    def unclear_content(self):
        """Ensure p:txBody has at least one a:p child.

        Intuitively, reverse a ".clear_content()" operation to minimum conformance with spec
        (single empty paragraph).
        """
        if len(self.p_lst) > 0:
            return
        self.add_p()

    @classmethod
    def _a_txBody_tmpl(cls):
        return "<a:txBody %s>\n" "  <a:bodyPr/>\n" "  <a:p/>\n" "</a:txBody>\n" % (nsdecls("a"))

    @classmethod
    def _p_txBody_tmpl(cls):
        return (
            "<p:txBody %s>\n" "  <a:bodyPr/>\n" "  <a:p/>\n" "</p:txBody>\n" % (nsdecls("p", "a"))
        )

    @classmethod
    def _txBody_tmpl(cls):
        return (
            "<p:txBody %s>\n"
            "  <a:bodyPr/>\n"
            "  <a:lstStyle/>\n"
            "  <a:p/>\n"
            "</p:txBody>\n" % (nsdecls("a", "p"))
        )


class CT_TextBodyProperties(BaseOxmlElement):
    """`a:bodyPr` custom element class."""

    _add_noAutofit: Callable[[], BaseOxmlElement]
    _add_normAutofit: Callable[[], CT_TextNormalAutofit]
    _add_spAutoFit: Callable[[], BaseOxmlElement]
    _remove_eg_textAutoFit: Callable[[], None]

    noAutofit: BaseOxmlElement | None
    normAutofit: CT_TextNormalAutofit | None
    spAutoFit: BaseOxmlElement | None

    eg_textAutoFit = ZeroOrOneChoice(
        (Choice("a:noAutofit"), Choice("a:normAutofit"), Choice("a:spAutoFit")),
        successors=("a:scene3d", "a:sp3d", "a:flatTx", "a:extLst"),
    )
    lIns: Length = OptionalAttribute(  # pyright: ignore[reportAssignmentType]
        "lIns", ST_Coordinate32, default=Emu(91440)
    )
    tIns: Length = OptionalAttribute(  # pyright: ignore[reportAssignmentType]
        "tIns", ST_Coordinate32, default=Emu(45720)
    )
    rIns: Length = OptionalAttribute(  # pyright: ignore[reportAssignmentType]
        "rIns", ST_Coordinate32, default=Emu(91440)
    )
    bIns: Length = OptionalAttribute(  # pyright: ignore[reportAssignmentType]
        "bIns", ST_Coordinate32, default=Emu(45720)
    )
    anchor: MSO_VERTICAL_ANCHOR | None = OptionalAttribute(  # pyright: ignore[reportAssignmentType]
        "anchor", MSO_VERTICAL_ANCHOR
    )
    wrap: str | None = OptionalAttribute(  # pyright: ignore[reportAssignmentType]
        "wrap", ST_TextWrappingType
    )

    @property
    def autofit(self):
        """The autofit setting for the text frame, a member of the `MSO_AUTO_SIZE` enumeration."""
        if self.noAutofit is not None:
            return MSO_AUTO_SIZE.NONE
        if self.normAutofit is not None:
            return MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
        if self.spAutoFit is not None:
            return MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT
        return None

    @autofit.setter
    def autofit(self, value: MSO_AUTO_SIZE | None):
        if value is not None and value not in MSO_AUTO_SIZE:
            raise ValueError(
                f"only None or a member of the MSO_AUTO_SIZE enumeration can be assigned to"
                f" CT_TextBodyProperties.autofit, got {value}"
            )
        self._remove_eg_textAutoFit()
        if value == MSO_AUTO_SIZE.NONE:
            self._add_noAutofit()
        elif value == MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE:
            self._add_normAutofit()
        elif value == MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT:
            self._add_spAutoFit()


class CT_TextCharacterProperties(BaseOxmlElement):
    """Custom element class for `a:rPr`, `a:defRPr`, and `a:endParaRPr`.

    'rPr' is short for 'run properties', and it corresponds to the |Font| proxy class.
    """

    get_or_add_hlinkClick: Callable[[], CT_Hyperlink]
    get_or_add_latin: Callable[[], CT_TextFont]
    _remove_latin: Callable[[], None]
    _remove_hlinkClick: Callable[[], None]

    eg_fillProperties = ZeroOrOneChoice(
        (
            Choice("a:noFill"),
            Choice("a:solidFill"),
            Choice("a:gradFill"),
            Choice("a:blipFill"),
            Choice("a:pattFill"),
            Choice("a:grpFill"),
        ),
        successors=(
            "a:effectLst",
            "a:effectDag",
            "a:highlight",
            "a:uLnTx",
            "a:uLn",
            "a:uFillTx",
            "a:uFill",
            "a:latin",
            "a:ea",
            "a:cs",
            "a:sym",
            "a:hlinkClick",
            "a:hlinkMouseOver",
            "a:rtl",
            "a:extLst",
        ),
    )
    latin: CT_TextFont | None = ZeroOrOne(  # pyright: ignore[reportAssignmentType]
        "a:latin",
        successors=(
            "a:ea",
            "a:cs",
            "a:sym",
            "a:hlinkClick",
            "a:hlinkMouseOver",
            "a:rtl",
            "a:extLst",
        ),
    )
    hlinkClick: CT_Hyperlink | None = ZeroOrOne(  # pyright: ignore[reportAssignmentType]
        "a:hlinkClick", successors=("a:hlinkMouseOver", "a:rtl", "a:extLst")
    )

    lang: MSO_LANGUAGE_ID | None = OptionalAttribute(  # pyright: ignore[reportAssignmentType]
        "lang", MSO_LANGUAGE_ID
    )
    sz: int | None = OptionalAttribute(  # pyright: ignore[reportAssignmentType]
        "sz", ST_TextFontSize
    )
    b: bool | None = OptionalAttribute("b", XsdBoolean)  # pyright: ignore[reportAssignmentType]
    i: bool | None = OptionalAttribute("i", XsdBoolean)  # pyright: ignore[reportAssignmentType]
    u: MSO_TEXT_UNDERLINE_TYPE | None = OptionalAttribute(  # pyright: ignore[reportAssignmentType]
        "u", MSO_TEXT_UNDERLINE_TYPE
    )

    def _new_gradFill(self):
        return CT_GradientFillProperties.new_gradFill()

    def add_hlinkClick(self, rId: str) -> CT_Hyperlink:
        """Add an `a:hlinkClick` child element with r:id attribute set to `rId`."""
        hlinkClick = self.get_or_add_hlinkClick()
        hlinkClick.rId = rId
        return hlinkClick


class CT_TextField(BaseOxmlElement):
    """`a:fld` field element, for either a slide number or date field."""

    get_or_add_rPr: Callable[[], CT_TextCharacterProperties]

    rPr: CT_TextCharacterProperties | None = ZeroOrOne(  # pyright: ignore[reportAssignmentType]
        "a:rPr", successors=("a:pPr", "a:t")
    )
    t: BaseOxmlElement | None = ZeroOrOne(  # pyright: ignore[reportAssignmentType]
        "a:t", successors=()
    )

    @property
    def text(self) -> str:  # pyright: ignore[reportIncompatibleMethodOverride]
        """The text of the `a:t` child element."""
        t = self.t
        if t is None:
            return ""
        return t.text or ""


class CT_TextFont(BaseOxmlElement):
    """Custom element class for `a:latin`, `a:ea`, `a:cs`, and `a:sym`.

    These occur as child elements of CT_TextCharacterProperties, e.g. `a:rPr`.
    """

    typeface: str = RequiredAttribute(  # pyright: ignore[reportAssignmentType]
        "typeface", ST_TextTypeface
    )


class CT_TextLineBreak(BaseOxmlElement):
    """`a:br` line break element"""

    get_or_add_rPr: Callable[[], CT_TextCharacterProperties]

    rPr = ZeroOrOne("a:rPr", successors=())

    @property
    def text(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Unconditionally a single vertical-tab character.

        A line break element can contain no text other than the implicit line feed it
        represents.
        """
        return "\v"


class CT_TextNormalAutofit(BaseOxmlElement):
    """`a:normAutofit` element specifying fit text to shape font reduction, etc."""

    fontScale: float = OptionalAttribute(  # pyright: ignore[reportAssignmentType]
        "fontScale", ST_TextFontScalePercentOrPercentString, default=100.0
    )


class CT_TextParagraph(BaseOxmlElement):
    """`a:p` custom element class"""

    get_or_add_endParaRPr: Callable[[], CT_TextCharacterProperties]
    get_or_add_pPr: Callable[[], CT_TextParagraphProperties]
    r_lst: list[CT_RegularTextRun]
    _add_br: Callable[[], CT_TextLineBreak]
    _add_r: Callable[[], CT_RegularTextRun]

    pPr: CT_TextParagraphProperties | None = ZeroOrOne(  # pyright: ignore[reportAssignmentType]
        "a:pPr", successors=("a:r", "a:br", "a:fld", "a14:m", "a:endParaRPr")
    )
    r = ZeroOrMore("a:r", successors=("a:br", "a:fld", "a14:m", "a:endParaRPr"))
    br = ZeroOrMore("a:br", successors=("a:fld", "a14:m", "a:endParaRPr"))
    fld = ZeroOrMore("a:fld", successors=("a14:m", "a:endParaRPr"))
    math = ZeroOrMore("a14:m", successors=("a:endParaRPr",))
    endParaRPr: CT_TextCharacterProperties | None = ZeroOrOne(
        "a:endParaRPr", successors=()
    )  # pyright: ignore[reportAssignmentType]

    def add_br(self) -> CT_TextLineBreak:
        """Return a newly appended `a:br` element."""
        return self._add_br()

    def add_r(self, text: str | None = None) -> CT_RegularTextRun:
        """Return a newly appended `a:r` element."""
        r = self._add_r()
        if text:
            r.text = text
        return r

    def append_text(self, text: str):
        """Append `a:r` and `a:br` elements to `p` based on `text`.

        Any `\n` or `\v` (vertical-tab) characters in `text` delimit `a:r` (run) elements and
        themselves are translated to `a:br` (line-break) elements. The vertical-tab character
        appears in clipboard text from PowerPoint at "soft" line-breaks (new-line, but not new
        paragraph).
        """
        # First, remove existing r, br, fld, and math children
        # (pPr and endParaRPr should be preserved if they exist)
        for child in list(self.content_children): # Iterate over a copy for safe removal
            self.remove(child)

        # Handle case of empty text, which should result in an empty paragraph (no runs/breaks)
        if not text:
            return

        # Split text by \n or \v, creating a sequence of text parts and separators
        parts = re.split(r"(\n|\v)", text)

        new_children_nodes: list[BaseOxmlElement] = []
        for part in parts:
            if not part: # Skip empty strings that might result from split
                continue

            new_node: BaseOxmlElement
            if part == "\n" or part == "\v":
                # Create <a:br/> element directly
                br_xml = "<a:br %s/>" % nsdecls("a")
                new_node = cast(BaseOxmlElement, parse_xml(br_xml))
            else:
                # This part is text for a run
                # self._new_r() creates <a:r><a:t/></a:r>
                new_node = cast(BaseOxmlElement, self._new_r())
                # CT_RegularTextRun.text.setter handles character escaping for its <a:t>
                cast(CT_RegularTextRun, new_node).text = part
            new_children_nodes.append(new_node)
        
        # Add the new children nodes in the collected order, respecting endParaRPr
        end_rpr_node = self.endParaRPr # Property to get the <a:endParaRPr> element or None
        
        if end_rpr_node is not None:
            # If endParaRPr exists, find its index to insert new nodes before it.
            try:
                target_idx = self.index(end_rpr_node)
                for node_to_add in new_children_nodes:
                    cast(etree.ElementBase, self).insert(target_idx, node_to_add)  # pyright: ignore
                    target_idx += 1 # Increment index to insert subsequent nodes in order
            except ValueError: 
                # This case (end_rpr_node exists but not found as child) should ideally not occur.
                # Fallback to appending all new children if end_rpr_node isn't a direct child.
                for node_to_add in new_children_nodes:
                    self.append(node_to_add)
        else:
            # No endParaRPr, so append all new children to the paragraph
            for node_to_add in new_children_nodes:
                self.append(node_to_add)

    @property
    def content_children(self) -> tuple[CT_RegularTextRun | CT_TextLineBreak | CT_TextField | CT_Math, ...]:
        """Sequence containing text-container child elements of this `a:p` element.

        These include `a:r`, `a:br`, `a:fld`, and `a14:m`.
        """
        return tuple(
            e for e in self if isinstance(e, (
                CT_RegularTextRun, CT_TextLineBreak, CT_TextField, CT_Math
            ))
        )

    @property
    def text(self) -> str:
        """str text contained in this paragraph."""
        #note this shadows the lxml _Element.text
        return "".join([child.text for child in self.content_children])

    @text.setter
    def text(self, value: str): # pyright: ignore[reportIncompatibleMethodOverride]
        """Set the text of this paragraph.
        
        Replaces all existing content (runs, breaks, fields, math).
        Parses `value` for newline characters (`\\n`, `\\v`) to create line breaks.
        """
        self.append_text(value)

    def _new_r(self):
        r_xml = "<a:r %s><a:t/></a:r>" % nsdecls("a")
        return parse_xml(r_xml)


class CT_TextParagraphProperties(BaseOxmlElement):
    """`a:pPr` custom element class."""

    get_or_add_defRPr: Callable[[], CT_TextCharacterProperties]
    _add_lnSpc: Callable[[], CT_TextSpacing]
    _add_spcAft: Callable[[], CT_TextSpacing]
    _add_spcBef: Callable[[], CT_TextSpacing]
    _remove_lnSpc: Callable[[], None]
    _remove_spcAft: Callable[[], None]
    _remove_spcBef: Callable[[], None]

    _tag_seq = (
        "a:lnSpc",
        "a:spcBef",
        "a:spcAft",
        "a:buClrTx",
        "a:buClr",
        "a:buSzTx",
        "a:buSzPct",
        "a:buSzPts",
        "a:buFontTx",
        "a:buFont",
        "a:buNone",
        "a:buAutoNum",
        "a:buChar",
        "a:buBlip",
        "a:tabLst",
        "a:defRPr",
        "a:extLst",
    )
    lnSpc: CT_TextSpacing | None = ZeroOrOne(  # pyright: ignore[reportAssignmentType]
        "a:lnSpc", successors=_tag_seq[1:]
    )
    spcBef: CT_TextSpacing | None = ZeroOrOne(  # pyright: ignore[reportAssignmentType]
        "a:spcBef", successors=_tag_seq[2:]
    )
    spcAft: CT_TextSpacing | None = ZeroOrOne(  # pyright: ignore[reportAssignmentType]
        "a:spcAft", successors=_tag_seq[3:]
    )
    defRPr: CT_TextCharacterProperties | None = ZeroOrOne(  # pyright: ignore[reportAssignmentType]
        "a:defRPr", successors=_tag_seq[16:]
    )
    lvl: int = OptionalAttribute(  # pyright: ignore[reportAssignmentType]
        "lvl", ST_TextIndentLevelType, default=0
    )
    algn: PP_PARAGRAPH_ALIGNMENT | None = OptionalAttribute(
        "algn", PP_PARAGRAPH_ALIGNMENT
    )  # pyright: ignore[reportAssignmentType]
    del _tag_seq

    @property
    def line_spacing(self) -> float | Length | None:
        """The spacing between baselines of successive lines in this paragraph.

        A float value indicates a number of lines. A |Length| value indicates a fixed spacing.
        Value is contained in `./a:lnSpc/a:spcPts/@val` or `./a:lnSpc/a:spcPct/@val`. Value is
        |None| if no element is present.
        """
        lnSpc = self.lnSpc
        if lnSpc is None:
            return None
        if lnSpc.spcPts is not None:
            return lnSpc.spcPts.val
        return cast(CT_TextSpacingPercent, lnSpc.spcPct).val

    @line_spacing.setter
    def line_spacing(self, value: float | Length | None):
        self._remove_lnSpc()
        if value is None:
            return
        if isinstance(value, Length):
            self._add_lnSpc().set_spcPts(value)
        else:
            self._add_lnSpc().set_spcPct(value)

    @property
    def space_after(self) -> Length | None:
        """The EMU equivalent of the centipoints value in `./a:spcAft/a:spcPts/@val`."""
        spcAft = self.spcAft
        if spcAft is None:
            return None
        spcPts = spcAft.spcPts
        if spcPts is None:
            return None
        return spcPts.val

    @space_after.setter
    def space_after(self, value: Length | None):
        self._remove_spcAft()
        if value is not None:
            self._add_spcAft().set_spcPts(value)

    @property
    def space_before(self):
        """The EMU equivalent of the centipoints value in `./a:spcBef/a:spcPts/@val`."""
        spcBef = self.spcBef
        if spcBef is None:
            return None
        spcPts = spcBef.spcPts
        if spcPts is None:
            return None
        return spcPts.val

    @space_before.setter
    def space_before(self, value: Length | None):
        self._remove_spcBef()
        if value is not None:
            self._add_spcBef().set_spcPts(value)


class CT_TextSpacing(BaseOxmlElement):
    """Used for `a:lnSpc`, `a:spcBef`, and `a:spcAft` elements."""

    get_or_add_spcPct: Callable[[], CT_TextSpacingPercent]
    get_or_add_spcPts: Callable[[], CT_TextSpacingPoint]
    _remove_spcPct: Callable[[], None]
    _remove_spcPts: Callable[[], None]

    # this should actually be a OneAndOnlyOneChoice, but that's not
    # implemented yet.
    spcPct: CT_TextSpacingPercent | None = ZeroOrOne(  # pyright: ignore[reportAssignmentType]
        "a:spcPct"
    )
    spcPts: CT_TextSpacingPoint | None = ZeroOrOne(  # pyright: ignore[reportAssignmentType]
        "a:spcPts"
    )

    def set_spcPct(self, value: float):
        """Set spacing to `value` lines, e.g. 1.75 lines.

        A ./a:spcPts child is removed if present.
        """
        self._remove_spcPts()
        spcPct = self.get_or_add_spcPct()
        spcPct.val = value

    def set_spcPts(self, value: Length):
        """Set spacing to `value` points. A ./a:spcPct child is removed if present."""
        self._remove_spcPct()
        spcPts = self.get_or_add_spcPts()
        spcPts.val = value


class CT_TextSpacingPercent(BaseOxmlElement):
    """`a:spcPct` element, specifying spacing in thousandths of a percent in its `val` attribute."""

    val: float = RequiredAttribute(  # pyright: ignore[reportAssignmentType]
        "val", ST_TextSpacingPercentOrPercentString
    )


class CT_TextSpacingPoint(BaseOxmlElement):
    """`a:spcPts` element, specifying spacing in centipoints in its `val` attribute."""

    val: Length = RequiredAttribute(  # pyright: ignore[reportAssignmentType]
        "val", ST_TextSpacingPoint
    )


# ===========================================================================
# MathML Element Classes
# ===========================================================================

class CT_MathText(BaseOxmlElement):
    """`m:t` custom element class for math text."""

    @property
    def text(self) -> str: # pyright: ignore[reportIncompatibleMethodOverride]
        """Text content of the element."""
        text_content = super().text
        return text_content or ""


class CT_MathVal(BaseOxmlElement):
    """Generic MathML element that primarily serves to hold an m:val attribute.
    Used for elements like <m:begChr m:val="value"/>.
    """
    val: str = RequiredAttribute("m:val", XsdString)  # pyright: ignore[reportAssignmentType]

    # The .text property and .to_latex() method were removed from CT_MathVal.
    # This class simply holds a 'val' attribute. Consumer classes are responsible
    # for retrieving this 'val' and processing it (e.g., via MATH_CHAR_TO_LATEX_CONVERSION)
    # as needed. CT_MathVal itself does not contain an <m:t> child.


class CT_MathRun(BaseOxmlElement):
    """`m:r` custom element class for a math run."""

    _tag_seq = ("a:rPr", "m:t")
    rPr: CT_TextCharacterProperties | None = ZeroOrOne("a:rPr", successors=_tag_seq[1:])  # pyright: ignore[reportAssignmentType]
    t: CT_MathText = OneAndOnlyOne("m:t")  # pyright: ignore[reportAssignmentType]
    del _tag_seq

    @property
    def text(self) -> str: # pyright: ignore[reportIncompatibleMethodOverride]
        """Text content of the `m:t` child."""
        return self.t.text

    def to_latex(self) -> str:
        """Return the text content for LaTeX conversion, with character mapping."""
        current_text = self.t.text # Direct access to CT_MathText's text
        
        unmapped_non_ascii_details: list[str] = []
        converted_parts: list[str] = []

        for char_from_xml in current_text:
            if char_from_xml in MATH_CHAR_TO_LATEX_CONVERSION:
                latex_equivalent = MATH_CHAR_TO_LATEX_CONVERSION[char_from_xml]
            else:
                latex_equivalent = None
            
            if latex_equivalent is not None:
                converted_parts.append(latex_equivalent)
            else:
                converted_parts.append(char_from_xml) # Keep original if not found
                if ord(char_from_xml) > 127: # If it's non-ASCII and wasn't in map
                    char_hex_code = hex(ord(char_from_xml))
                    # Simple diagnostic for unmapped non-ASCII
                    unmapped_non_ascii_details.append(
                        f"'{char_from_xml}' (ord: {ord(char_from_xml)}, hex: {char_hex_code})"
                    )

        final_converted_text = "".join(converted_parts)

        # Print collected details if any non-ASCII characters were unmapped
        if unmapped_non_ascii_details:
            print(
                f"INFO: CT_MathRun encountered unmapped non-ASCII characters in text run '{current_text}': "
                f"Details (char, ord, hex): {'; '.join(unmapped_non_ascii_details)}"
            )

        return final_converted_text


class CT_MathBaseArgument(BaseOxmlElement):
    """`m:e` custom element class, representing a base argument for math structures."""
    r = ZeroOrMore("m:r")
    d = ZeroOrMore("m:d")
    sSub = ZeroOrMore("m:sSub")
    rad = ZeroOrMore("m:rad")
    f = ZeroOrMore("m:f")
    sSup = ZeroOrMore("m:sSup")
    nary = ZeroOrMore("m:nary")
    func = ZeroOrMore("m:func")
    groupChr = ZeroOrMore("m:groupChr")
    m = ZeroOrMore("m:m")  # Matrix
    bar = ZeroOrMore("m:bar") # Bar
    sPre = ZeroOrMore("m:sPre") # Prescript
    eqArr = ZeroOrMore("m:eqArr") # Equation Array (can be base)
    sSubSup = ZeroOrMore("m:sSubSup")
    acc = ZeroOrMore("m:acc")

    r_lst: list[CT_MathRun]
    d_lst: list[CT_MathDelimiter]
    sSub_lst: list[CT_MathSubscript]
    rad_lst: list[CT_MathRad]
    f_lst: list[CT_MathFraction]
    sSup_lst: list[CT_MathSuperscript]
    nary_lst: list[CT_MathNary]
    func_lst: list[CT_MathFunc]
    groupChr_lst: list[CT_MathGroupChar]
    m_lst: list[CT_MathMatrix]
    bar_lst: list[CT_MathBar]
    sPre_lst: list[CT_MathPrescript]
    eqArr_lst: list[CT_MathEqArray]
    sSubSup_lst: list[CT_MathSubSup]
    acc_lst: list[CT_MathAccent]

    def to_latex(self) -> str:
        latex_parts: list[str] = []
        for child in self:
            child_latex = ""
            if hasattr(child, "to_latex"):
                method_to_latex = getattr(child, "to_latex")
                if callable(method_to_latex):
                    child_latex = method_to_latex()
            if child_latex:
                latex_parts.append(child_latex)
        return "".join(latex_parts)


class CT_MathDelimiterProperties(BaseOxmlElement):
    """`m:dPr` custom element class for delimiter properties."""
    _tag_seq = ("m:begChr", "m:sepChr", "m:endChr", "m:grow", "m:shp", "m:ctrlPr")
    begChr: CT_MathVal | None = ZeroOrOne("m:begChr", successors=_tag_seq[1:]) # pyright: ignore[reportAssignmentType]
    sepChr: CT_MathVal | None = ZeroOrOne("m:sepChr", successors=_tag_seq[2:]) # pyright: ignore[reportAssignmentType]
    endChr: CT_MathVal | None = ZeroOrOne("m:endChr", successors=_tag_seq[3:]) # pyright: ignore[reportAssignmentType]
    del _tag_seq


class CT_MathDelimiter(BaseOxmlElement):
    """`m:d` custom element class for delimiters (parentheses, brackets, etc.)."""
    dPr: CT_MathDelimiterProperties | None = ZeroOrOne("m:dPr") # pyright: ignore[reportAssignmentType]
    e = OneOrMore("m:e")
    e_lst: list[CT_MathBaseArgument]

    def to_latex(self) -> str:
        begin_char_raw = "("
        end_char_raw = ")"
        sep_char_raw = None

        if self.dPr is not None:
            if self.dPr.begChr is not None:
                begin_char_raw = self.dPr.begChr.val
            if self.dPr.endChr is not None:
                end_char_raw = self.dPr.endChr.val
            if self.dPr.sepChr is not None:
                sep_char_raw = self.dPr.sepChr.val

        # Check if this delimiter is specifically for a standard matrix type
        is_std_matrix_wrapper = False
        std_matrix_env_name = None
        matrix_content_for_std_env = ""

        if len(self.e_lst) == 1 and len(self.e_lst[0]) == 1 and isinstance(self.e_lst[0][0], CT_MathMatrix):
            matrix_node = cast(CT_MathMatrix, self.e_lst[0][0])
            
            matrix_delimiters_map = {
                ("(", ")"): "pmatrix",
                ("[", "]"): "bmatrix",
                ("{", "}"): "Bmatrix", # amsmath
                ("|", "|"): "vmatrix",
                ("‖", "‖"): "Vmatrix", # U+2016 for ‖ (DOUBLE VERTICAL LINE)
                ("\u2016", "\u2016"): "Vmatrix",
            }
            # Also check for Unicode equivalents from MATH_CHAR_TO_LATEX_CONVERSION if they are keys in the map
            # This part can be complex if MATH_CHAR_TO_LATEX_CONVERSION maps to the same chars.
            # For now, direct char check is primary.

            if (begin_char_raw, end_char_raw) in matrix_delimiters_map:
                std_matrix_env_name = matrix_delimiters_map[(begin_char_raw, end_char_raw)]
                # Get raw matrix rows content from CT_MathMatrix
                rows_latex_parts = [row.to_latex() for row in matrix_node.mr_lst]
                matrix_content_for_std_env = " \\\\ ".join(rows_latex_parts)
                is_std_matrix_wrapper = True
        
        if is_std_matrix_wrapper and std_matrix_env_name:
            return f"\\begin{{{std_matrix_env_name}}} {matrix_content_for_std_env} \\end{{{std_matrix_env_name}}}"

        # Fallback to generic \left \right delimiter processing
        # Enhanced delimiter map, prioritizing specific LaTeX commands for paired delimiters
        delimiter_map = {
            "(": "(", ")": ")",                            # U+0028, U+0029
            "[": "[", "]": "]",                            # U+005B, U+005D
            "{": "\\{", "}": "\\}",                          # U+007B, U+007D
            "|": ("\\lvert ", "\\rvert "),                   # U+007C VERTICAL LINE
            "\u2016": ("\\lVert ", "\\rVert "),                 # ‖ (DOUBLE VERTICAL LINE, U+2016)
            "<": "\\langle ", ">": "\\rangle ",                # U+003C, U+003E (LESS-THAN, GREATER-THAN) - often used for ang brackets
            "\u27E8": "\\langle ", "\u27E9": "\\rangle ",      # ⟨, ⟩ (MATHEMATICAL ANGLE BRACKETS, U+27E8, U+27E9)
            "\u3008": "\\langle ", "\u3009": "\\rangle ",      # 〈, 〉 (CJK ANGLE BRACKETS, U+3008, U+3009)
            "\u2308": "\\lceil ", "\u2309": "\\rceil ",         # ⌈, ⌉ (LEFT CEILING, RIGHT CEILING, U+2308, U+2309)
            "\u230A": "\\lfloor ", "\u230B": "\\rfloor ",       # ⌊, ⌋ (LEFT FLOOR, RIGHT FLOOR, U+230A, U+230B)
            "/": "/", "\\": "\\backslash ",                     # U+002F SOLIDUS, U+005C REVERSE SOLIDUS
            # Arrows as delimiters (can be used with \left, \right)
            "\u2191": "\\uparrow ",                          # ↑ (UPWARDS ARROW, U+2191)
            "\u2193": "\\downarrow ",                        # ↓ (DOWNWARDS ARROW, U+2193)
            "\u2195": "\\updownarrow ",                      # ↕ (UP DOWN ARROW, U+2195)
            "\u21D1": "\\Uparrow ",                         # ⇑ (UPWARDS DOUBLE ARROW, U+21D1)
            "\u21D3": "\\Downarrow ",                       # ⇓ (DOWNWARDS DOUBLE ARROW, U+21D3)
            "\u21D5": "\\Updownarrow ",                     # ⇕ (UP DOWN DOUBLE ARROW, U+21D5)
            # Corners (typically not paired with \left/\right in the same way, but can be beg/end char)
            "\u231C": "\\ulcorner ", "\u231D": "\\urcorner ", # ⌜, ⌝ (UPPER LEFT CORNER, UPPER RIGHT CORNER)
            "\u231E": "\\llcorner ", "\u231F": "\\lrcorner ", # ⌞, ⌟ (LOWER LEFT CORNER, LOWER RIGHT CORNER)
        }

        # Use MATH_CHAR_TO_LATEX_CONVERSION as a fallback or for single char representations
        # if not found in the specific delimiter_map.
        begin_latex_entry = delimiter_map.get(begin_char_raw)
        if begin_latex_entry is None:
            begin_latex_entry = MATH_CHAR_TO_LATEX_CONVERSION.get(begin_char_raw, begin_char_raw)

        end_latex_entry = delimiter_map.get(end_char_raw)
        if end_latex_entry is None:
            end_latex_entry = MATH_CHAR_TO_LATEX_CONVERSION.get(end_char_raw, end_char_raw)
        
        begin_latex = begin_latex_entry[0] if isinstance(begin_latex_entry, tuple) else begin_latex_entry
        end_latex = end_latex_entry[0] if isinstance(end_latex_entry, tuple) else end_latex_entry

        # If the raw characters were the same and the map entry was a tuple (implying distinct left/right forms)
        if begin_char_raw == end_char_raw and isinstance(begin_latex_entry, tuple) and len(begin_latex_entry) == 2:
            end_latex = begin_latex_entry[1]
        # Or if the end delimiter itself has a distinct right form in a tuple
        elif isinstance(end_latex_entry, tuple) and len(end_latex_entry) == 2:
            end_latex = end_latex_entry[1]
        
        # Ensure trailing space for commands, but not for single characters
        if begin_latex.startswith("\\") and begin_latex[-1].isalpha() and not begin_latex.endswith(" "):
            begin_latex += " "
        if end_latex.startswith("\\") and end_latex[-1].isalpha() and not end_latex.endswith(" "):
            end_latex += " "

        if not self.e_lst:
            actual_begin_delimiter = begin_latex.strip()
            if not actual_begin_delimiter: # handles empty string if raw char was ''
                 actual_begin_delimiter = "."
            actual_end_delimiter = end_latex.strip()
            if not actual_end_delimiter:
                actual_end_delimiter = "."
            return f"\\left{actual_begin_delimiter} \\right{actual_end_delimiter}"

        content_parts = [child_e.to_latex() for child_e in self.e_lst]
        
        separator_latex = ""
        if sep_char_raw:
            separator_latex = MATH_CHAR_TO_LATEX_CONVERSION.get(sep_char_raw, sep_char_raw)
            if separator_latex.strip() in ["+", "-", "\\pm", "\\times", "\\div", "\\cdot", "=", "<", ">", "\\le", "\\ge", "\\equiv", "\\approx"]:
                separator_latex = f" {separator_latex.strip()} "

        content_latex = separator_latex.join(content_parts) if sep_char_raw and separator_latex else "".join(content_parts)
        
        actual_begin_delimiter = begin_latex
        if not actual_begin_delimiter.strip():
            actual_begin_delimiter = "."
        
        actual_end_delimiter = end_latex
        if not actual_end_delimiter.strip(): 
            actual_end_delimiter = "."
        
        # The main issue is between \left{DELIM} and content_latex.
        # If DELIM is a command (e.g., \lVert) and content_latex starts with a letter (e.g., 'a'),
        # a space is needed: \left\lVert a \right...
        # If DELIM is a char (e.g., '('), no space: \left(a\right...
        
        final_begin_part = actual_begin_delimiter
        if final_begin_part.startswith("\\") and final_begin_part[-1].isalpha():
            # It's a command like \lVert, \langle, etc. that needs a space if followed by non-delimiter content.
            # Check if content_latex itself starts with a grouping character or another command
            if content_latex and not (content_latex.startswith(("{", "(", "[")) or content_latex.startswith("\\")):
                final_begin_part += " " # Add space only if not there
        
        # Similar logic for content_latex and actual_end_delimiter is usually not needed
        # as \right handles its spacing with the delimiter that follows it.
        # However, ensure the end delimiter itself is stripped of leading/trailing spaces from the map.
        actual_end_delimiter = actual_end_delimiter.strip()

        return f"\\left{final_begin_part}{content_latex}\\right{actual_end_delimiter}"


class CT_MathSubscriptArgument(BaseOxmlElement):
    """`m:sub` custom element class."""
    e: CT_MathBaseArgument | None = ZeroOrOne("m:e")  # pyright: ignore[reportAssignmentType]
    r = ZeroOrMore("m:r")
    d = ZeroOrMore("m:d")
    sSub = ZeroOrMore("m:sSub")
    rad = ZeroOrMore("m:rad")
    f = ZeroOrMore("m:f")
    sSup = ZeroOrMore("m:sSup")
    nary = ZeroOrMore("m:nary")
    func = ZeroOrMore("m:func")
    groupChr = ZeroOrMore("m:groupChr")
    eqArr = ZeroOrMore("m:eqArr") # Equation Array

    r_lst: list[CT_MathRun]
    d_lst: list[CT_MathDelimiter]
    sSub_lst: list[CT_MathSubscript]
    rad_lst: list[CT_MathRad]
    f_lst: list[CT_MathFraction]
    sSup_lst: list[CT_MathSuperscript]
    nary_lst: list[CT_MathNary]
    func_lst: list[CT_MathFunc]
    groupChr_lst: list[CT_MathGroupChar]
    eqArr_lst: list[CT_MathEqArray]

    def to_latex(self) -> str:
        if self.e is not None:
            return self.e.to_latex()
        latex_parts: list[str] = []
        for child in self:
            child_latex = ""
            if hasattr(child, "to_latex"):
                method_to_latex = getattr(child, "to_latex")
                if callable(method_to_latex):
                    child_latex = method_to_latex()
            if child_latex:
                latex_parts.append(child_latex)
        return "".join(latex_parts)


class CT_MathSubscript(BaseOxmlElement):
    """`m:sSub` custom element class for subscript structures."""
    e: CT_MathBaseArgument = OneAndOnlyOne("m:e")  # pyright: ignore[reportAssignmentType]
    sub: CT_MathSubscriptArgument = OneAndOnlyOne("m:sub")  # pyright: ignore[reportAssignmentType]

    def to_latex(self) -> str:
        base_latex = self.e.to_latex()
        subscript_latex = self.sub.to_latex()
        if len(subscript_latex) > 1 or any(c in subscript_latex for c in r"\\ {}[]()^_"):
            return f"{base_latex}_{{{subscript_latex}}}"
        if not subscript_latex:
             return base_latex
        return f"{base_latex}_{subscript_latex}"


class CT_MathDegree(BaseOxmlElement):
    """`m:deg` custom element class, container for the degree expression `m:e`."""
    e: CT_MathBaseArgument | None = ZeroOrOne("m:e") # pyright: ignore[reportAssignmentType]

    def to_latex(self) -> str:
        if self.e is not None:
            return self.e.to_latex()
        return ""


class CT_MathDegreeHide(BaseOxmlElement):
    """`m:degHide` element, its `val` attribute (xsd:boolean) indicates hide state."""
    val: XsdBoolean = OptionalAttribute("m:val", XsdBoolean, default=True) # pyright: ignore[reportAssignmentType]


class CT_MathRadPr(BaseOxmlElement):
    """`m:radPr` custom element class for radical properties."""
    _tag_seq = ("m:degHide", "m:ctrlPr")
    degHide: CT_MathDegreeHide | None = ZeroOrOne("m:degHide", successors=_tag_seq[1:]) # pyright: ignore[reportAssignmentType]
    del _tag_seq


class CT_MathRad(BaseOxmlElement):
    """`m:rad` custom element class for radicals (roots)."""
    radPr: CT_MathRadPr | None = ZeroOrOne("m:radPr", successors=("m:deg", "m:e")) # pyright: ignore[reportAssignmentType]
    deg: CT_MathDegree | None = ZeroOrOne("m:deg", successors=("m:e",)) # pyright: ignore[reportAssignmentType]
    e: CT_MathBaseArgument = OneAndOnlyOne("m:e") # pyright: ignore[reportAssignmentType]

    def to_latex(self) -> str:
        base_latex = self.e.to_latex()
        degree_latex = ""
        if self.deg is not None:
            deg_content = self.deg.to_latex()
            if deg_content.strip():
                degree_latex = deg_content

        hide_degree_flag = False
        if self.radPr is not None and self.radPr.degHide is not None:
            hide_degree_flag = self.radPr.degHide.val

        if degree_latex and not hide_degree_flag:
            return f"\\sqrt[{degree_latex}]{{{base_latex}}}"
        return f"\\sqrt{{{base_latex}}}"


class CT_MathNumerator(BaseOxmlElement):
    """`m:num` custom element class, container for the numerator expression."""
    e: CT_MathBaseArgument | None = ZeroOrOne("m:e")  # pyright: ignore[reportAssignmentType]
    r = ZeroOrMore("m:r")
    d = ZeroOrMore("m:d")
    sSub = ZeroOrMore("m:sSub")
    rad = ZeroOrMore("m:rad")
    f = ZeroOrMore("m:f")
    sSup = ZeroOrMore("m:sSup")
    nary = ZeroOrMore("m:nary")
    func = ZeroOrMore("m:func")
    groupChr = ZeroOrMore("m:groupChr")
    
    r_lst: list[CT_MathRun]
    d_lst: list[CT_MathDelimiter]
    sSub_lst: list[CT_MathSubscript]
    rad_lst: list[CT_MathRad]
    f_lst: list[CT_MathFraction]
    sSup_lst: list[CT_MathSuperscript]
    nary_lst: list[CT_MathNary]
    func_lst: list[CT_MathFunc]
    groupChr_lst: list[CT_MathGroupChar]

    def to_latex(self) -> str:
        if self.e is not None:
            return self.e.to_latex()
        latex_parts: list[str] = []
        for child in self:
            child_latex = ""
            if hasattr(child, "to_latex"):
                method_to_latex = getattr(child, "to_latex")
                if callable(method_to_latex):
                    child_latex = method_to_latex()
            if child_latex:
                latex_parts.append(child_latex)
        return "".join(latex_parts)


class CT_MathDenominator(BaseOxmlElement):
    """`m:den` custom element class, container for the denominator expression."""
    e: CT_MathBaseArgument | None = ZeroOrOne("m:e")  # pyright: ignore[reportAssignmentType]
    r = ZeroOrMore("m:r")
    d = ZeroOrMore("m:d")
    sSub = ZeroOrMore("m:sSub")
    rad = ZeroOrMore("m:rad")
    f = ZeroOrMore("m:f")
    sSup = ZeroOrMore("m:sSup")
    nary = ZeroOrMore("m:nary")
    func = ZeroOrMore("m:func")
    groupChr = ZeroOrMore("m:groupChr")

    r_lst: list[CT_MathRun]
    d_lst: list[CT_MathDelimiter]
    sSub_lst: list[CT_MathSubscript]
    rad_lst: list[CT_MathRad]
    f_lst: list[CT_MathFraction]
    sSup_lst: list[CT_MathSuperscript]
    nary_lst: list[CT_MathNary]
    func_lst: list[CT_MathFunc]
    groupChr_lst: list[CT_MathGroupChar]

    def to_latex(self) -> str:
        if self.e is not None:
            return self.e.to_latex()
        latex_parts: list[str] = []
        for child in self:
            child_latex = ""
            if hasattr(child, "to_latex"):
                method_to_latex = getattr(child, "to_latex")
                if callable(method_to_latex):
                    child_latex = method_to_latex()
            if child_latex:
                latex_parts.append(child_latex)
        return "".join(latex_parts)


class CT_MathFractionPr(BaseOxmlElement):
    """`m:fPr` custom element class for fraction properties."""
    pass


class CT_MathFraction(BaseOxmlElement):
    """`m:f` custom element class for fractions."""
    fPr: CT_MathFractionPr | None = ZeroOrOne("m:fPr", successors=("m:num", "m:den")) # pyright: ignore[reportAssignmentType]
    num: CT_MathNumerator = OneAndOnlyOne("m:num") # pyright: ignore[reportAssignmentType]
    den: CT_MathDenominator = OneAndOnlyOne("m:den") # pyright: ignore[reportAssignmentType]

    def to_latex(self) -> str:
        num_latex = self.num.to_latex()
        den_latex = self.den.to_latex()
        return f"\\frac{{{num_latex}}}{{{den_latex}}}"


class CT_MathSuperscriptArgument(BaseOxmlElement):
    """`m:sup` custom element class."""
    e: CT_MathBaseArgument | None = ZeroOrOne("m:e")  # pyright: ignore[reportAssignmentType]
    r = ZeroOrMore("m:r")
    d = ZeroOrMore("m:d")
    sSub = ZeroOrMore("m:sSub")
    rad = ZeroOrMore("m:rad")
    f = ZeroOrMore("m:f")
    sSup = ZeroOrMore("m:sSup")
    nary = ZeroOrMore("m:nary")
    func = ZeroOrMore("m:func")
    groupChr = ZeroOrMore("m:groupChr")
    eqArr = ZeroOrMore("m:eqArr") # Equation Array

    r_lst: list[CT_MathRun]
    d_lst: list[CT_MathDelimiter]
    sSub_lst: list[CT_MathSubscript]
    rad_lst: list[CT_MathRad]
    f_lst: list[CT_MathFraction]
    sSup_lst: list[CT_MathSuperscript]
    nary_lst: list[CT_MathNary]
    func_lst: list[CT_MathFunc]
    groupChr_lst: list[CT_MathGroupChar]
    eqArr_lst: list[CT_MathEqArray]
    
    def to_latex(self) -> str:
        if self.e is not None:
            return self.e.to_latex()
        latex_parts: list[str] = []
        for child in self:
            child_latex = ""
            if hasattr(child, "to_latex"):
                method_to_latex = getattr(child, "to_latex")
                if callable(method_to_latex):
                    child_latex = method_to_latex()
            if child_latex:
                latex_parts.append(child_latex)
        return "".join(latex_parts)


class CT_MathSuperscriptPr(BaseOxmlElement):
    """`m:sSupPr` custom element class for superscript properties."""
    pass


class CT_MathSuperscript(BaseOxmlElement):
    """`m:sSup` custom element class for superscript structures."""
    sSupPr: CT_MathSuperscriptPr | None = ZeroOrOne(  # pyright: ignore[reportAssignmentType]
        "m:sSupPr", successors=("m:e", "m:sup")
    )
    e: CT_MathBaseArgument = OneAndOnlyOne("m:e")  # pyright: ignore[reportAssignmentType]
    sup: CT_MathSuperscriptArgument = OneAndOnlyOne("m:sup")  # pyright: ignore[reportAssignmentType]

    def to_latex(self) -> str:
        base_latex = self.e.to_latex()
        sup_latex = self.sup.to_latex()
        if len(sup_latex) > 1 or any(c in sup_latex for c in r"\\ {}[]()^_"):
            return f"{base_latex}^{{{sup_latex}}}"
        return f"{base_latex}^{sup_latex}"


class CT_MathNaryPr(BaseOxmlElement):
    """`m:naryPr` custom element class for N-ary operator properties."""
    _tag_seq = ("m:chr", "m:limLoc", "m:grow", "m:subHide", "m:supHide", "m:ctrlPr")
    chr: CT_MathVal | None = ZeroOrOne("m:chr", successors=_tag_seq[1:]) # pyright: ignore[reportAssignmentType]
    subHide: CT_MathVal | None = ZeroOrOne("m:subHide", successors=_tag_seq[4:]) # pyright: ignore[reportAssignmentType]
    supHide: CT_MathVal | None = ZeroOrOne("m:supHide", successors=_tag_seq[5:]) # pyright: ignore[reportAssignmentType]
    del _tag_seq


class CT_MathNary(BaseOxmlElement):
    """`m:nary` custom element class for N-ary operators (sum, integral, etc.)."""
    naryPr: CT_MathNaryPr | None = ZeroOrOne("m:naryPr", successors=("m:sub", "m:sup", "m:e")) # pyright: ignore[reportAssignmentType]
    sub: CT_MathSubscriptArgument | None = ZeroOrOne("m:sub", successors=("m:sup", "m:e")) # pyright: ignore[reportAssignmentType]
    sup: CT_MathSuperscriptArgument | None = ZeroOrOne("m:sup", successors=("m:e",)) # pyright: ignore[reportAssignmentType]
    e: CT_MathBaseArgument = OneAndOnlyOne("m:e") # pyright: ignore[reportAssignmentType]

    def to_latex(self) -> str:
        op_char_xml = ""
        hide_sub = False
        hide_sup = False

        if self.naryPr is not None:
            if self.naryPr.chr is not None:
                op_char_xml = self.naryPr.chr.val
            if self.naryPr.subHide is not None and self.naryPr.subHide.val in ("on", "1", "true"):
                hide_sub = True
            if self.naryPr.supHide is not None and self.naryPr.supHide.val in ("on", "1", "true"):
                hide_sup = True
        
        op_latex = ""
        is_integral = False
        
        # Priority for well-known N-ary operators from XML char
        if not op_char_xml:  # Default for m:nary if no m:chr is present is integral
            op_latex = "\\int " 
            is_integral = True
        elif op_char_xml == "∫" or op_char_xml == "\u222B":
            op_latex = "\\int "
            is_integral = True
        elif op_char_xml == "∬" or op_char_xml == "\u222C":
            op_latex = "\\iint "
            is_integral = True
        elif op_char_xml == "∭" or op_char_xml == "\u222D":
            op_latex = "\\iiint "
            is_integral = True
        elif op_char_xml == "∮" or op_char_xml == "\u222E":
            op_latex = "\\oint "
            is_integral = True
        elif op_char_xml == "∯" or op_char_xml == "\u222F":
            op_latex = MATH_CHAR_TO_LATEX_CONVERSION.get(op_char_xml, "\\oiint ") 
            is_integral = True
        elif op_char_xml == "∰" or op_char_xml == "\u2230": # Volume Integral
            op_latex = MATH_CHAR_TO_LATEX_CONVERSION.get(op_char_xml, "\\oiiint ") # \oiiint or similar, was \iiint
            is_integral = True
        elif op_char_xml == "∑" or op_char_xml == "\u2211":
            op_latex = "\\sum "
        elif op_char_xml == "∏" or op_char_xml == "\u220F":
            op_latex = "\\prod "
        elif op_char_xml == "∐" or op_char_xml == "\u2210":
            op_latex = "\\coprod "
        elif op_char_xml == "⋃" or op_char_xml == "\u22C3":
            op_latex = "\\bigcup "
        elif op_char_xml == "⋂" or op_char_xml == "\u22C2":
            op_latex = "\\bigcap "
        elif op_char_xml == "⋀" or op_char_xml == "\u22C0":
            op_latex = "\\bigwedge "
        elif op_char_xml == "⋁" or op_char_xml == "\u22C1":
            op_latex = "\\bigvee "
        elif op_char_xml == "⨆" or op_char_xml == "\u2A06":
            op_latex = "\\bigsqcup "
        elif op_char_xml == "⨄" or op_char_xml == "\u2A04":
            op_latex = "\\biguplus "
        elif op_char_xml == "⨁" or op_char_xml == "\u2A01":
            op_latex = "\\bigoplus "
        elif op_char_xml == "⨂" or op_char_xml == "\u2A02":
            op_latex = "\\bigotimes "
        elif op_char_xml == "⨀" or op_char_xml == "\u2A00":
            op_latex = "\\bigodot "
        elif op_char_xml == "⨌" or op_char_xml == "\u2A0C": # QUADRUPLE INTEGRAL
             op_latex = "\\iiiint " # Or potentially \idotsint if m:sub/m:sup are present
             is_integral = True
        else:
            # Fallback to the main symbol map for other characters
            op_latex = MATH_CHAR_TO_LATEX_CONVERSION.get(op_char_xml, op_char_xml)
            # If it's a multi-char string not starting with \, treat as operator name
            if not op_latex.startswith("\\") and len(op_latex) > 1:
                 op_latex = f"\\operatorname{{{op_latex}}} " # Added space
            elif op_latex.startswith("\\") and not op_latex.endswith(" "): # Ensure space for commands
                 op_latex += " "


        sub_latex_str = ""
        if self.sub is not None and not hide_sub:
            processed_sub = self.sub.to_latex()
            if processed_sub: 
                 sub_latex_str = f"_{{{processed_sub}}}" if len(processed_sub) > 1 or any(c in processed_sub for c in r"\\ {}[]()^_") else f"_{processed_sub}"

        sup_latex_str = ""
        if self.sup is not None and not hide_sup:
            processed_sup = self.sup.to_latex()
            if processed_sup: 
                sup_latex_str = f"^{{{processed_sup}}}" if len(processed_sup) > 1 or any(c in processed_sup for c in r"\\ {}[]()^_") else f"^{processed_sup}"

        expr_latex = self.e.to_latex()
        
        spacing = " " # Default space after operator and its scripts
        if is_integral and expr_latex:
            # Add thin space \, before differentials like 'dx', 'dy' if pattern matches.
            # Regex: (anything ending not whitespace)(d then a letter)
            # Ensure expr_latex is not empty before regex
            if expr_latex: # Removed isinstance(expr_latex, str) as it's always true
                match_differential = re.match(r"(.*\S)(d[a-zA-Z])$", expr_latex)
                if match_differential:
                    # Insert \, between the main part and the differential
                    expr_latex = f"{match_differential.group(1)}\\,{match_differential.group(2)}"
                    spacing = ""  # \, provides spacing, so no extra leading space for expr_latex
                elif not expr_latex.startswith(("{", "(", "[")) and not expr_latex.startswith("\\left"):
                    # If no differential pattern, but it's an integral and expr_latex is simple, keep default space.
                    pass # Default space will be applied
                else:
                    spacing = "" # No space if expr_latex starts with a delimiter or is empty
            else: # expr_latex might be empty
                spacing = ""


        elif not expr_latex or (expr_latex.startswith(("{", "(", "[")) or expr_latex.startswith("\\left") or expr_latex.startswith("\\begin")): # Removed isinstance
            spacing = "" # No space if expression is empty or starts with a delimiter/environment

        return f"{op_latex.strip()}{sub_latex_str}{sup_latex_str}{spacing}{expr_latex}"


class CT_MathFuncPr(BaseOxmlElement):
    """`m:funcPr` custom element class for function properties."""
    pass


class CT_MathLimLow(BaseOxmlElement):
    """`m:limLow` custom element class for 'limit from below' structures like lim."""
    e: CT_MathBaseArgument = OneAndOnlyOne("m:e") # pyright: ignore[reportAssignmentType]
    lim: CT_MathBaseArgument = OneAndOnlyOne("m:lim") # pyright: ignore[reportAssignmentType]

    def to_latex(self) -> str:
        func_name_latex = self.e.to_latex().strip()
        if not func_name_latex.startswith("\\") and any(c.isalpha() for c in func_name_latex) and len(func_name_latex) > 1:
            func_name_latex = f"\\operatorname{{{func_name_latex}}}"
        lim_expr_latex = self.lim.to_latex()
        return f"{func_name_latex}_{{{lim_expr_latex}}}"


class CT_MathFName(BaseOxmlElement):
    """`m:fName` custom element class for the 'name' part of a function."""
    r = ZeroOrMore("m:r")
    limLow: CT_MathLimLow | None = ZeroOrOne("m:limLow") # pyright: ignore[reportAssignmentType]
    r_lst: list[CT_MathRun]

    def to_latex(self) -> str:
        if self.limLow is not None:
            return self.limLow.to_latex()
        name_parts = [child.to_latex() for child in self.r_lst]
        raw_name = "".join(name_parts).strip()
        
        # Expanded list of known functions
        known_functions_needing_backslash = {
            "sin", "cos", "tan", "log", "ln", "exp", "det", "gcd", "lim", "mod", "max", "min",
            "arcsin", "sinh", "arccos", "cosh", "arctan", "tanh", "cot", "coth", "sec", "csc",
            "lg", "inf", "sup", "liminf", "limsup", "arg", "deg", "dim", "hom", "ker", "Pr", "sgn"
        }

        if raw_name.startswith("\\"):
            return raw_name
        if raw_name in known_functions_needing_backslash:
            return f"\\{raw_name} " # Added space
        # Check if it's a known operator from the full map that might appear as fName text
        # This is less common for fName, which is usually text, but good for robustness
        mapped_operator = MATH_CHAR_TO_LATEX_CONVERSION.get(raw_name)
        if mapped_operator and mapped_operator.startswith("\\"):
            return mapped_operator # Assumes map includes trailing space if needed

        if len(raw_name) > 1 and all(c.isalpha() for c in raw_name): # Multi-char text function
            return f"\\operatorname{{{raw_name}}} " # Added space
        return raw_name # Single char or other cases


class CT_MathFunc(BaseOxmlElement):
    """`m:func` custom element class for functions."""
    funcPr: CT_MathFuncPr | None = ZeroOrOne("m:funcPr", successors=("m:fName", "m:e")) # pyright: ignore[reportAssignmentType]
    fName: CT_MathFName = OneAndOnlyOne("m:fName") # pyright: ignore[reportAssignmentType]
    e: CT_MathBaseArgument = OneAndOnlyOne("m:e") # pyright: ignore[reportAssignmentType]

    def to_latex(self) -> str:
        fname_latex = self.fName.to_latex()  # Preserves trailing space if CT_MathFName adds it
        arg_latex = self.e.to_latex()

        # Heuristic: if fname_latex contains _{...} or ^{...} and ends with '}',
        # it's likely a limit-like structure where the argument is part of the name.
        # e.g., \lim_{x \to 0} or output from CT_MathLimLow
        is_lim_like_structure = ("_" in fname_latex or "^" in fname_latex) and \
                                fname_latex.strip().endswith("}")
        
        arg_is_enclosed = False
        if arg_latex: # only check if arg_latex is not empty
            first_char = arg_latex[0]
            last_char = arg_latex[-1]
            if (first_char == '(' and last_char == ')') or \
               (first_char == '[' and last_char == ']') or \
               (first_char == '{' and last_char == '}'):
                arg_is_enclosed = True

        if is_lim_like_structure:
            # For structures like \lim_{x \to 0} where fname_latex is the entire operator part.
            # We usually want a space before the main argument (e.g., \lim_{x \to 0} x).
            # fname_latex from CT_MathLimLow already forms the complete "lim..." part.
            # We rstrip() to handle cases where CT_MathFName might give an unwanted trailing space
            # if it wasn't a limLow structure but still matched the heuristic.
            space_needed = " " if arg_latex and not fname_latex.rstrip().endswith(" ") else ""
            return f"{fname_latex.rstrip()}{space_needed}{arg_latex}"
        else:
            # For standard functions like \sin x or \operatorname{foo}(bar)
            # CT_MathFName for \sin or \operatorname{foo} should return with a trailing space.
            # We strip this space before adding parentheses or the already-enclosed argument.
            stripped_fname = fname_latex.rstrip()
            if not arg_is_enclosed and arg_latex:
                return f"{stripped_fname}({arg_latex})"
            else: # Argument is already enclosed or is empty
                return f"{stripped_fname}{arg_latex}"


class CT_MathGroupChrPr(BaseOxmlElement):
    """`m:groupChrPr` custom element class for group character properties."""
    _tag_seq = ("m:chr", "m:pos", "m:vertJc", "m:ctrlPr")
    chr: CT_MathVal | None = ZeroOrOne("m:chr", successors=_tag_seq[1:]) # pyright: ignore[reportAssignmentType]
    pos: CT_MathVal | None = ZeroOrOne("m:pos", successors=_tag_seq[2:]) # pyright: ignore[reportAssignmentType]
    del _tag_seq


class CT_MathGroupChar(BaseOxmlElement):
    """`m:groupChr` custom element class for grouped characters (accents)."""
    groupChrPr: CT_MathGroupChrPr | None = ZeroOrOne("m:groupChrPr", successors=("m:e",)) # pyright: ignore[reportAssignmentType]
    e: CT_MathBaseArgument = OneAndOnlyOne("m:e") # pyright: ignore[reportAssignmentType]

    def to_latex(self) -> str:
        base_latex = self.e.to_latex()
        accent_char_xml = ""
        char_pos_xml = "" # Default position might be top if not specified

        if self.groupChrPr is not None:
            if self.groupChrPr.chr is not None:
                accent_char_xml = self.groupChrPr.chr.val
            if self.groupChrPr.pos is not None:
                char_pos_xml = self.groupChrPr.pos.val
            else: # Explicitly default to top if pos is not present
                char_pos_xml = "top" 
            
        if char_pos_xml == "top":
            if accent_char_xml == "→" or accent_char_xml == "\u2192": return f"\\vec{{{base_latex}}}"
            if accent_char_xml == "←" or accent_char_xml == "\u2190": return f"\\overleftarrow{{{base_latex}}}"
            if accent_char_xml == "\u0305" or accent_char_xml == "_": return f"\\bar{{{base_latex}}}" # Macron or underscore
            if accent_char_xml == "\u0302" or accent_char_xml == "^": return f"\\hat{{{base_latex}}}" # Circumflex
            if accent_char_xml == "\u0303" or accent_char_xml == "~": return f"\\tilde{{{base_latex}}}" # Tilde
            if accent_char_xml == "\u0307": return f"\\dot{{{base_latex}}}" # Dot above
            if accent_char_xml == "\u0308": return f"\\ddot{{{base_latex}}}" # Diaeresis
            if accent_char_xml == "\u0301": return f"\\acute{{{base_latex}}}" # Acute
            if accent_char_xml == "\u0300": return f"\\grave{{{base_latex}}}" # Grave
            if accent_char_xml == "\u030C": return f"\\check{{{base_latex}}}" # Caron (check)
            if accent_char_xml == "\u0306": return f"\\breve{{{base_latex}}}" # Breve
            # For overbrace/underbrace, m:groupChr is not the typical element.
            # Those are usually m:rad or special constructs if OMML supports them directly like that.
            # PowerPoint UI for "Overbar" and "Underbar" uses m:bar. "Accents" uses m:acc.
            # GroupChar with pos=top for things like arrows seems to be its main MathML use.
            # If other accent_char_xml values appear for 'top', use MATH_CHAR_TO_LATEX_CONVERSION
            mapped_accent = MATH_CHAR_TO_LATEX_CONVERSION.get(accent_char_xml)
            if mapped_accent and mapped_accent.startswith("\\"):
                # Assuming it's a command like \widehat, \widetilde for wider accents
                # Check if it's a known accent command that takes an arg
                simple_accents = {"\\vec", "\\bar", "\\hat", "\\tilde", "\\dot", "\\ddot", "\\acute", "\\grave", "\\check", "\\breve"}
                if any(mapped_accent.startswith(s) for s in simple_accents):
                     return f"{mapped_accent.strip()}{{{base_latex}}}"
            # Fallback for unhandled top accents via groupChr
            if accent_char_xml: # If an accent was specified but not directly handled
                 return f"{{{accent_char_xml}}}{{{base_latex}}}" # Default rendering of the char itself above

        # Note: m:groupChrPr also has m:vertJc (vertical justification) which is not handled here.
        # It also does not explicitly handle underaccents (pos="bot") well with this structure,
        # m:bar is more typical for underbar.
        return f"{{{base_latex}}}" # Default if no specific accent processing applies


class CT_MathAccentProperties(BaseOxmlElement):
    """`m:accPr` custom element class for accent properties."""
    _tag_seq = ("m:chr", "m:ctrlPr")
    chr: CT_MathVal | None = ZeroOrOne("m:chr", successors=_tag_seq[1:])  # pyright: ignore[reportAssignmentType]
    del _tag_seq


class CT_MathAccent(BaseOxmlElement):
    """`m:acc` custom element class for accented characters (typically placed above)."""
    accPr: CT_MathAccentProperties | None = ZeroOrOne("m:accPr", successors=("m:e",))  # pyright: ignore[reportAssignmentType]
    e: CT_MathBaseArgument = OneAndOnlyOne("m:e")  # pyright: ignore[reportAssignmentType]

    def to_latex(self) -> str:
        base_latex = self.e.to_latex()
        accent_char_xml = ""

        if self.accPr is not None and self.accPr.chr is not None:
            accent_char_xml = self.accPr.chr.val
        
        # Accent mapping for m:acc. Note: m:acc implies accent is above.
        # Characters like U+0303 (Combining Tilde) are often used in m:val.
        if accent_char_xml == "\u0303" or accent_char_xml == "~":  # Tilde (Combining or ASCII)
            return f"\\tilde{{{base_latex}}}"
        if accent_char_xml == "\u0302" or accent_char_xml == "^":  # Hat (Combining or ASCII)
            return f"\\hat{{{base_latex}}}"
        if accent_char_xml == "\u0305" or accent_char_xml == "_":  # Macron (Combining Overline or ASCII underscore for bar)
            return f"\\bar{{{base_latex}}}"
        if accent_char_xml == "\u0307":                            # Dot (Combining Dot Above)
            return f"\\dot{{{base_latex}}}"
        if accent_char_xml == "\u0308":                            # Double Dot (Combining Diaeresis)
            return f"\\ddot{{{base_latex}}}"
        if accent_char_xml == "→" or accent_char_xml == "\u2192":  # Vector arrow
            return f"\\vec{{{base_latex}}}"
        if accent_char_xml == "\u0301":                            # Acute Accent (Combining Acute Accent)
            return f"\\acute{{{base_latex}}}"
        if accent_char_xml == "\u0300":                            # Grave Accent (Combining Grave Accent)
            return f"\\grave{{{base_latex}}}"
        if accent_char_xml == "\u030C":                            # Caron (Combining Caron U+030C)
            return f"\\check{{{base_latex}}}"
        if accent_char_xml == "\u0306":                            # Breve (Combining Breve U+0306)
            return f"\\breve{{{base_latex}}}"
        # Add more mappings as needed for m:acc elements.
        
        # Fallback for unhandled or unspecified accent characters
        if accent_char_xml: # If an accent character was specified but not in map
            # Attempt to use a LaTeX command if the accent_char_xml is a known command character
            # (e.g. if someone put '\hat' directly in m:val of m:chr)
            # This is less likely as m:val usually contains the Unicode char itself.
            mapped_accent = MATH_CHAR_TO_LATEX_CONVERSION.get(accent_char_xml)
            if mapped_accent and mapped_accent.startswith("\\"):
                # Basic check if it looks like an accent command
                simple_accents = {"\\tilde", "\\hat", "\\bar", "\\dot", "\\ddot", "\\vec", "\\acute", "\\grave", "\\check", "\\breve"}
                if any(mapped_accent.strip().startswith(s) for s in simple_accents):
                    return f"{mapped_accent.strip()}{{{base_latex}}}"
                # If it's some other operator, treat it like operatorname
                return f"\\operatorname{{{mapped_accent.strip()}}}{{{base_latex}}}"
            # If not in map, and not a combining mark already handled, it might be a literal character.
            # This case is tricky: is it a character meant to be an accent, or just text?
            # For safety, if it's a non-combining character, put it before the base.
            # If it's an unknown combining mark, LaTeX might handle it if base_latex is simple.
            # Defaulting to putting the character literally.
            return f"{{{accent_char_xml}}}{{{base_latex}}}"


        return f"{{{base_latex}}}" # Default if no accent char or unrecognized


class CT_MathSubSupProperties(BaseOxmlElement):
    """`m:sSubSupPr` custom element class for subscript-superscript properties."""
    # This element typically holds <m:ctrlPr> for formatting control characters,
    # but it's not directly used by the to_latex logic of the sSubSup structure itself.
    pass


class CT_MathSubSup(BaseOxmlElement):
    """`m:sSubSup` custom element class for expressions with both subscript and superscript."""
    sSubSupPr: CT_MathSubSupProperties | None = ZeroOrOne(  # pyright: ignore[reportAssignmentType]
        "m:sSubSupPr", successors=("m:e", "m:sub", "m:sup")
    )
    e: CT_MathBaseArgument = OneAndOnlyOne("m:e")  # pyright: ignore[reportAssignmentType]
    sub: CT_MathSubscriptArgument = OneAndOnlyOne("m:sub")  # pyright: ignore[reportAssignmentType]
    sup: CT_MathSuperscriptArgument = OneAndOnlyOne("m:sup")  # pyright: ignore[reportAssignmentType]

    def to_latex(self) -> str:
        base_latex = self.e.to_latex()
        sub_latex = self.sub.to_latex()
        sup_latex = self.sup.to_latex()

        sub_str = ""
        if sub_latex:
            # Add braces if subscript is multi-character or contains LaTeX control sequences
            if len(sub_latex) > 1 or any(c in sub_latex for c in r"\\ {}[]()^_"):
                sub_str = f"_{{{sub_latex}}}"
            else:
                sub_str = f"_{sub_latex}"

        sup_str = ""
        if sup_latex:
            # Add braces if superscript is multi-character or contains LaTeX control sequences
            if len(sup_latex) > 1 or any(c in sup_latex for c in r"\\ {}[]()^_"):
                sup_str = f"^{{{sup_latex}}}"
            else:
                sup_str = f"^{sup_latex}"
        
        return f"{base_latex}{sub_str}{sup_str}"


class CT_OMath(BaseOxmlElement):
    """`m:oMath` custom element class, representing a math equation."""
    r = ZeroOrMore("m:r")
    d = ZeroOrMore("m:d")
    sSub = ZeroOrMore("m:sSub")
    rad = ZeroOrMore("m:rad")
    f = ZeroOrMore("m:f")
    sSup = ZeroOrMore("m:sSup")
    nary = ZeroOrMore("m:nary")
    func = ZeroOrMore("m:func")
    groupChr = ZeroOrMore("m:groupChr")
    sSubSup = ZeroOrMore("m:sSubSup")
    acc = ZeroOrMore("m:acc")
    m = ZeroOrMore("m:m")  # Matrix
    bar = ZeroOrMore("m:bar") # Bar
    sPre = ZeroOrMore("m:sPre") # Prescript
    eqArr = ZeroOrMore("m:eqArr") # Equation Array

    r_lst: list[CT_MathRun]
    d_lst: list[CT_MathDelimiter]
    sSub_lst: list[CT_MathSubscript]
    rad_lst: list[CT_MathRad]
    f_lst: list[CT_MathFraction]
    sSup_lst: list[CT_MathSuperscript]
    nary_lst: list[CT_MathNary]
    func_lst: list[CT_MathFunc]
    groupChr_lst: list[CT_MathGroupChar]
    sSubSup_lst: list[CT_MathSubSup]
    acc_lst: list[CT_MathAccent]
    m_lst: list[CT_MathMatrix]
    bar_lst: list[CT_MathBar]
    sPre_lst: list[CT_MathPrescript]
    eqArr_lst: list[CT_MathEqArray]

    def to_latex(self) -> str:
        latex_parts: list[str] = []
        for child in self:
            child_latex = ""
            if hasattr(child, "to_latex"):
                method_to_latex = getattr(child, "to_latex")
                if callable(method_to_latex):
                    child_latex = method_to_latex()
            if child_latex:
                latex_parts.append(child_latex)
        return "".join(latex_parts)


class CT_MathOmathPara(BaseOxmlElement):
    """`m:oMathPara` custom element class, a container for an `m:oMath` element and its paragraph properties."""
    oMath: CT_OMath = OneAndOnlyOne("m:oMath")  # pyright: ignore[reportAssignmentType]

    def to_latex(self) -> str:
        return self.oMath.to_latex()


class CT_Math(BaseOxmlElement):
    """`a14:m` custom element class.
    This element serves as a container for either an `m:oMathPara` element (typically for block math)
    or an `m:oMath` element (typically for inline math).
    """
    # According to ECMA-376, Part 1, 4th ed., CT_MathFormula (which a14:m maps to)
    # has a choice of m:oMathPara or m:oMath, with minOccurs="1" and maxOccurs="1".
    # We define them as ZeroOrOne here and implement the choice logic and validation
    # in the to_latex method.
    oMathPara: CT_MathOmathPara | None = ZeroOrOne("m:oMathPara", successors=())  # pyright: ignore[reportAssignmentType]
    oMath: CT_OMath | None = ZeroOrOne("m:oMath", successors=())  # pyright: ignore[reportAssignmentType]

    def to_latex(self) -> str:
        """Converts the contained math content (either m:oMathPara or m:oMath) to LaTeX."""
        if self.oMathPara is not None:
            return self.oMathPara.to_latex()
        elif self.oMath is not None:
            return self.oMath.to_latex()
        else:
            # This state implies the a14:m element is missing its required
            # m:oMathPara or m:oMath child, violating the schema.
            raise InvalidXmlError(
                "Required m:oMathPara or m:oMath child not found in a14:m element."
            )

    @property
    def text(self, verbose: bool = False) -> str: # pyright: ignore[reportIncompatibleMethodOverride]
        """Returns the LaTeX representation of the math content, enclosed in '$'."""
        try:
            from lxml import etree
            if verbose:
                print("--- CT_Math XML (a14:m content) ---")
                print(etree.tostring(self, pretty_print=True, encoding="unicode"))
                print("-----------------------------------")
        except ImportError:
            if verbose:
                print("--- CT_Math XML (lxml.etree not available for pretty print) ---")
        except Exception as e:
            if verbose:
                print(f"--- Error printing CT_Math XML: {e} ---")


        latex_content = self.to_latex()
        # If to_latex successfully returns (i.e., valid math content was found and converted),
        # and that content happens to be an empty string, f"${latex_content}$" will correctly produce "$$".
        # If to_latex raises InvalidXmlError due to a malformed a14:m, that error will propagate.
        return f"${latex_content}$"

class CT_MathBarProperties(BaseOxmlElement):
    """`m:barPr` custom element class for bar properties."""
    _tag_seq = ("m:pos", "m:ctrlPr")
    pos: CT_MathVal | None = ZeroOrOne("m:pos", successors=_tag_seq[1:])  # pyright: ignore[reportAssignmentType]
    del _tag_seq

class CT_MathBar(BaseOxmlElement):
    """`m:bar` custom element class for overbar/underbar."""
    barPr: CT_MathBarProperties | None = ZeroOrOne("m:barPr", successors=("m:e",))  # pyright: ignore[reportAssignmentType]
    e: CT_MathBaseArgument = OneAndOnlyOne("m:e")  # pyright: ignore[reportAssignmentType]

    def to_latex(self) -> str:
        base_latex = self.e.to_latex()
        pos = "top"
        if self.barPr is not None and self.barPr.pos is not None:
            pos = self.barPr.pos.val
        
        if pos == "top":
            # \overline for multi-char, \bar for single plain char
            if len(base_latex) > 1 and not (base_latex.startswith("\\") and " " not in base_latex.strip()):
                 return f"\\overline{{{base_latex}}}"
            return f"\\bar{{{base_latex}}}" # Use \bar for single chars or commands
        elif pos == "bot": # bottom
            # \underline for multi-char
            if len(base_latex) > 1 and not (base_latex.startswith("\\") and " " not in base_latex.strip()):
                return f"\\underline{{{base_latex}}}"
            return f"\\underline{{{base_latex}}}" # single char also with underline
        return base_latex # Should not happen if pos is only top/bot

class CT_MathMatrixColumnProperties(BaseOxmlElement):
    """`m:mcPr` custom element class for matrix column properties."""
    count: CT_MathVal | None = ZeroOrOne("m:count") # pyright: ignore[reportAssignmentType]
    mcJc: CT_MathVal | None = ZeroOrOne("m:mcJc") # pyright: ignore[reportAssignmentType]
    # Other properties like m:space...

class CT_MathMatrixColumn(BaseOxmlElement):
    """`m:mc` custom element class for a matrix column specification."""
    mcPr: CT_MathMatrixColumnProperties | None = ZeroOrOne("m:mcPr") # pyright: ignore[reportAssignmentType]

class CT_MathMatrixColumns(BaseOxmlElement):
    """`m:mcs` custom element class for matrix columns specifier."""
    mc = ZeroOrMore("m:mc")
    mc_lst: list[CT_MathMatrixColumn]

class CT_MathMatrixProperties(BaseOxmlElement):
    """`m:mPr` custom element class for matrix properties."""
    mcs: CT_MathMatrixColumns | None = ZeroOrOne("m:mcs") # pyright: ignore[reportAssignmentType]
    # Other properties like m:baseJc, m:plcHide, m:rSp, m:cSp, m:cGp ...

class CT_MathMatrixRow(BaseOxmlElement):
    """`m:mr` custom element class for a matrix row."""
    e = ZeroOrMore("m:e")
    e_lst: list[CT_MathBaseArgument]

    def to_latex(self) -> str:
        return " & ".join(child_e.to_latex() for child_e in self.e_lst)

class CT_MathMatrix(BaseOxmlElement):
    """`m:m` custom element class for matrices."""
    mPr: CT_MathMatrixProperties | None = ZeroOrOne("m:mPr", successors=("m:mr",))  # pyright: ignore[reportAssignmentType]
    mr = OneOrMore("m:mr")
    mr_lst: list[CT_MathMatrixRow]

    def to_latex(self) -> str:
        rows_latex = [row.to_latex() for row in self.mr_lst]
        # CT_MathMatrix now *always* produces content for a plain `matrix` environment.
        # The decision to use pmatrix, bmatrix, etc., is handled by CT_MathDelimiter
        # if it wraps this matrix with the corresponding standard delimiters.
        matrix_env = "matrix" 
        
        rows_final = " \\\\ ".join(rows_latex)
        return f"\\begin{{{matrix_env}}} {rows_final} \\end{{{matrix_env}}}"

class CT_MathEqArrayProperties(BaseOxmlElement):
    """`m:eqArrPr` custom element class for equation array properties."""
    # Properties like baseJc, maxDist, objDist, rSp, etc.
    pass

class CT_MathEqArray(BaseOxmlElement):
    """`m:eqArr` custom element class for equation arrays (e.g., multiline sub/sup)."""
    eqArrPr: CT_MathEqArrayProperties | None = ZeroOrOne("m:eqArrPr", successors=("m:e",))  # pyright: ignore[reportAssignmentType]
    e = OneOrMore("m:e")
    e_lst: list[CT_MathBaseArgument]

    def to_latex(self) -> str:
        lines_latex = [line.to_latex() for line in self.e_lst]
        # For use in subscripts/superscripts, stack them. \substack could be an option.
        # Or simply using \\ inside the {} for sub/sup.
        # Let's use \begin{smallmatrix} ... \end{smallmatrix} or simply \\ for simple cases.
        # \substack requires amsmath. For broader compatibility, manual stacking with \\ within {}
        if len(lines_latex) > 1:
            lines_final = " \\\\ ".join(lines_latex)
            return f"\\begin{{subarray}}{{c}} {lines_final} \\end{{subarray}}"
        return "".join(lines_latex)


class CT_MathPrescriptProperties(BaseOxmlElement):
    """`m:sPrePr` custom element class for prescript properties."""
    pass

class CT_MathPrescript(BaseOxmlElement):
    """`m:sPre` (subSupBefore) custom element class for prescripts."""
    sPrePr: CT_MathPrescriptProperties | None = ZeroOrOne("m:sPrePr", successors=("m:sub", "m:sup", "m:e"))  # pyright: ignore[reportAssignmentType]
    sub: CT_MathSubscriptArgument | None = ZeroOrOne("m:sub", successors=("m:sup", "m:e"))  # pyright: ignore[reportAssignmentType]
    sup: CT_MathSuperscriptArgument | None = ZeroOrOne("m:sup", successors=("m:e",))  # pyright: ignore[reportAssignmentType]
    e: CT_MathBaseArgument = OneAndOnlyOne("m:e")  # pyright: ignore[reportAssignmentType]

    def to_latex(self) -> str:
        base_latex = self.e.to_latex()
        sub_latex = self.sub.to_latex() if self.sub is not None else ""
        sup_latex = self.sup.to_latex() if self.sup is not None else ""

        # prescript_parts list removed as it wasn't directly used for final construction
        
        final_sub_str = ""
        # Check self.sub is not None before accessing sub_latex content for it
        if self.sub is not None and sub_latex: 
            if len(sub_latex) > 1 or any(c in sub_latex for c in r"\\ {}[]()^_"):
                final_sub_str = f"{{{sub_latex}}}"
            else:
                final_sub_str = sub_latex
        
        final_sup_str = ""
        # Check self.sup is not None before accessing sup_latex content for it
        if self.sup is not None and sup_latex: 
            if len(sup_latex) > 1 or any(c in sup_latex for c in r"\\ {}[]()^_"):
                final_sup_str = f"{{{sup_latex}}}"
            else:
                final_sup_str = sup_latex

        if final_sub_str or final_sup_str: 
            return f"{{}}_{{{final_sub_str}}}^{{{final_sup_str}}}{base_latex}"
        return base_latex
