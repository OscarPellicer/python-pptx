"""Custom element classes for text-related XML elements"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Callable, cast

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
        for idx, r_str in enumerate(re.split("\n|\v", text)):
            #breaks are only added _between_ items, not at start---
            if idx > 0:
                self.add_br()
            #runs that would be empty are not added---
            if r_str:
                self.add_r(r_str)

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
    def text(self) -> str:  # pyright: ignore[reportIncompatibleMethodOverride]
        """str text contained in this paragraph."""
        #note this shadows the lxml _Element.text---
        return "".join([child.text for child in self.content_children])

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


_MATH_CHAR_TO_LATEX_CONVERSION = {
    # Math Italic Small
    "𝑎": "a", "𝑏": "b", "𝑐": "c", "𝑑": "d", "𝑒": "e", "𝑓": "f", "𝑔": "g", "ℎ": "h",
    "𝑖": "i", "𝑗": "j", "𝑘": "k", "𝑙": "l", "𝑚": "m", "𝑛": "n", "𝑜": "o", "𝑝": "p",
    "𝑞": "q", "𝑟": "r", "𝑠": "s", "𝑡": "t", "𝑢": "u", "𝑣": "v", "𝑤": "w", "𝑥": "x",
    "𝑦": "y", "𝑧": "z",
    # Math Italic Capital
    "𝐴": "A", "𝐵": "B", "𝐶": "C", "𝐷": "D", "𝐸": "E", "𝐹": "F", "𝐺": "G", "𝐻": "H",
    "𝐼": "I", "𝐽": "J", "𝐾": "K", "𝐿": "L", "𝑀": "M", "𝑁": "N", "𝑂": "O", "𝑃": "P",
    "𝑄": "Q", "𝑅": "R", "𝑆": "S", "𝑇": "T", "𝑈": "U", "𝑉": "V", "𝑊": "W", "𝑋": "X",
    "𝑌": "Y", "𝑍": "Z",
    # Symbols
    "×": "\\times ",
    "÷": "\\div ",
    "−": "-",  # Minus sign (U+2212) to hyphen-minus
    "∗": "*",  # Asterisk operator (U+2217) to asterisk
    "·": "\\cdot ",  # Middle dot (U+00B7)
    "→": "\\to ",  # Rightwards arrow (U+2192)
    "∞": "\\infty ",  # Infinity (U+221E)
    # Greek letters (add more as needed)
    "α": "\\alpha ", "β": "\\beta ", "γ": "\\gamma ", "δ": "\\delta ", "ε": "\\epsilon ",
    "ζ": "\\zeta ", "η": "\\eta ", "θ": "\\theta ", "ι": "\\iota ", "κ": "\\kappa ",
    "λ": "\\lambda ", "μ": "\\mu ", "ν": "\\nu ", "ξ": "\\xi ", "ο": "o", "π": "\\pi ",
    "ρ": "\\rho ", "σ": "\\sigma ", "τ": "\\tau ", "υ": "\\upsilon ", "φ": "\\phi ",
    "χ": "\\chi ", "ψ": "\\psi ", "ω": "\\omega ",
    "Γ": "\\Gamma ", "Δ": "\\Delta ", "Θ": "\\Theta ", "Λ": "\\Lambda ", "Ξ": "\\Xi ",
    "Π": "\\Pi ", "Σ": "\\Sigma ", "Φ": "\\Phi ", "Ψ": "\\Psi ", "Ω": "\\Omega ",
}


class CT_MathVal(BaseOxmlElement):
    """Generic MathML element that primarily serves to hold an m:val attribute.
    Used for elements like <m:begChr m:val="value"/>.
    """
    val: str = RequiredAttribute("m:val", XsdString)  # pyright: ignore[reportAssignmentType]


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
        current_text = self.text
        converted_text = "".join(
            _MATH_CHAR_TO_LATEX_CONVERSION.get(char, char) for char in current_text
        )
        return converted_text


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
        latex_parts: list[str] = []
        for child in self:
            child_latex = ""
            if hasattr(child, "to_latex") and callable(child.to_latex):
                child_latex = child.to_latex()
            if child_latex:
                latex_parts.append(child_latex)
        return "".join(latex_parts)


class CT_MathDelimiterProperties(BaseOxmlElement):
    """`m:dPr` custom element class for delimiter properties."""
    _tag_seq = ("m:begChr", "m:sepChr", "m:endChr", "m:grow", "m:shp", "m:ctrlPr")
    begChr: CT_MathVal | None = ZeroOrOne("m:begChr", successors=_tag_seq[1:]) # pyright: ignore[reportAssignmentType]
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

        if self.dPr is not None:
            if self.dPr.begChr is not None:
                begin_char_raw = self.dPr.begChr.val
            if self.dPr.endChr is not None:
                end_char_raw = self.dPr.endChr.val

        delimiter_map = {
            "(": "(", ")": ")",
            "[": "[", "]": "]",
            "{": "\\{", "}": "\\}",
            "|": ("\\lvert", "\\rvert"),
            "‖": ("\\lVert", "\\rVert"),
            "<": "\\langle", ">": "\\rangle",
            "⌈": "\\lceil", "⌉": "\\rceil",
            "⌊": "\\lfloor", "⌋": "\\rfloor",
            "/": "/",
            "\\": "\\backslash",
            "↑": "\\uparrow",
            "↓": "\\downarrow",
            "↕": "\\updownarrow",
            '〈': '\\langle', '〉': '\\rangle',
        }

        begin_latex_entry = delimiter_map.get(begin_char_raw, begin_char_raw)
        end_latex_entry = delimiter_map.get(end_char_raw, end_char_raw)

        begin_latex = begin_latex_entry[0] if isinstance(begin_latex_entry, tuple) else begin_latex_entry
        end_latex = end_latex_entry[1] if isinstance(end_latex_entry, tuple) else end_latex_entry
        
        if begin_char_raw == end_char_raw and isinstance(begin_latex_entry, tuple) and len(begin_latex_entry) == 2:
             begin_latex = begin_latex_entry[0]
             end_latex = begin_latex_entry[1]

        if not self.e_lst:
            return f"\\left{begin_latex}\\right{end_latex}"

        content_latex = "".join(child_e.to_latex() for child_e in self.e_lst)

        final_begin_latex = begin_latex
        if begin_latex.startswith("\\") and content_latex:
            final_begin_latex += " " 

        final_end_latex = end_latex

        return f"\\left{final_begin_latex}{content_latex}\\right{final_end_latex}"


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
            if hasattr(child, "to_latex") and callable(child.to_latex):
                child_latex = child.to_latex()
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
            if hasattr(child, "to_latex") and callable(child.to_latex):
                child_latex = child.to_latex()
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
            if hasattr(child, "to_latex") and callable(child.to_latex):
                child_latex = child.to_latex()
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
            if hasattr(child, "to_latex") and callable(child.to_latex):
                child_latex = child.to_latex()
            if child_latex:
                latex_parts.append(child_latex)
        return "".join(latex_parts)


class CT_MathSuperscriptPr(BaseOxmlElement):
    """`m:sSupPr` custom element class for superscript properties."""
    pass


class CT_MathSuperscript(BaseOxmlElement):
    """`m:sSup` custom element class for superscript structures."""
    sSupPr: CT_MathSuperscriptPr | None = ZeroOrOne("m:sSupPr", successors=("m:e", "m:sup")) # pyright: ignore[reportAssignmentType]
    e: CT_MathBaseArgument = OneAndOnlyOne("m:e") # pyright: ignore[reportAssignmentType]
    sup: CT_MathSuperscriptArgument = OneAndOnlyOne("m:sup") # pyright: ignore[reportAssignmentType]

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
    del _tag_seq


class CT_MathNary(BaseOxmlElement):
    """`m:nary` custom element class for N-ary operators (sum, integral, etc.)."""
    naryPr: CT_MathNaryPr | None = ZeroOrOne("m:naryPr", successors=("m:sub", "m:sup", "m:e")) # pyright: ignore[reportAssignmentType]
    sub: CT_MathSubscriptArgument | None = ZeroOrOne("m:sub", successors=("m:sup", "m:e")) # pyright: ignore[reportAssignmentType]
    sup: CT_MathSuperscriptArgument | None = ZeroOrOne("m:sup", successors=("m:e",)) # pyright: ignore[reportAssignmentType]
    e: CT_MathBaseArgument = OneAndOnlyOne("m:e") # pyright: ignore[reportAssignmentType]

    def to_latex(self) -> str:
        op_char_xml = ""
        if self.naryPr is not None and self.naryPr.chr is not None:
            op_char_xml = self.naryPr.chr.val
        
        op_latex = ""
        if not op_char_xml: 
            op_latex = "\\int" 
        elif op_char_xml == "∫":
            op_latex = "\\int"
        elif op_char_xml == "∑":
            op_latex = "\\sum"
        elif op_char_xml == "∏":
            op_latex = "\\prod"
        elif op_char_xml == "∐": 
            op_latex = "\\coprod"
        elif op_char_xml == "⋃": 
            op_latex = "\\bigcup"
        elif op_char_xml == "⋂":
            op_latex = "\\bigcap"
        else:
            op_latex = _MATH_CHAR_TO_LATEX_CONVERSION.get(op_char_xml, op_char_xml)
            if not op_latex.startswith("\\") and len(op_latex) > 1 :
                 op_latex = f"\\operatorname{{{op_latex}}}"

        sub_latex_str = ""
        if self.sub is not None:
            processed_sub = self.sub.to_latex()
            if processed_sub: 
                 sub_latex_str = f"_{{{processed_sub}}}" if len(processed_sub) > 1 or any(c in processed_sub for c in r"\\ {}[]()^_") else f"_{processed_sub}"

        sup_latex_str = ""
        if self.sup is not None:
            processed_sup = self.sup.to_latex()
            if processed_sup: 
                sup_latex_str = f"^{{{processed_sup}}}" if len(processed_sup) > 1 or any(c in processed_sup for c in r"\\ {}[]()^_") else f"^{processed_sup}"

        expr_latex = self.e.to_latex()
        spacing = " " if expr_latex and op_latex.startswith("\\") else ""
        return f"{op_latex}{sub_latex_str}{sup_latex_str}{spacing}{expr_latex}"


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
        known_functions_needing_backslash = {"sin", "cos", "tan", "log", "ln", "exp", "det", "gcd", "lim", "mod", "max", "min"}
        if raw_name.startswith("\\"):
            return raw_name
        if raw_name in known_functions_needing_backslash:
            return f"\\{raw_name}"
        if len(raw_name) > 1 and all(c.isalpha() for c in raw_name):
            return f"\\operatorname{{{raw_name}}}"
        return raw_name


class CT_MathFunc(BaseOxmlElement):
    """`m:func` custom element class for functions."""
    funcPr: CT_MathFuncPr | None = ZeroOrOne("m:funcPr", successors=("m:fName", "m:e")) # pyright: ignore[reportAssignmentType]
    fName: CT_MathFName = OneAndOnlyOne("m:fName") # pyright: ignore[reportAssignmentType]
    e: CT_MathBaseArgument = OneAndOnlyOne("m:e") # pyright: ignore[reportAssignmentType]

    def to_latex(self) -> str:
        fname_latex = self.fName.to_latex()
        arg_latex = self.e.to_latex()
        if "_" in fname_latex or "^" in fname_latex or fname_latex.endswith("}"):
             return f"{fname_latex} {arg_latex}"
        return f"{fname_latex}({arg_latex})"


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
        char_pos_xml = ""

        if self.groupChrPr is not None:
            if self.groupChrPr.chr is not None:
                accent_char_xml = self.groupChrPr.chr.val
            if self.groupChrPr.pos is not None:
                char_pos_xml = self.groupChrPr.pos.val
            
        if char_pos_xml == "top":
            if accent_char_xml == "→": return f"\\vec{{{base_latex}}}"
            if accent_char_xml == "←": return f"\\overleftarrow{{{base_latex}}}"
            if accent_char_xml == "\u0305": return f"\\bar{{{base_latex}}}"
            if accent_char_xml == "\u0302": return f"\\hat{{{base_latex}}}"
            if accent_char_xml == "\u0303": return f"\\tilde{{{base_latex}}}"
            if accent_char_xml == "\u0307": return f"\\dot{{{base_latex}}}"
            if accent_char_xml == "\u0308": return f"\\ddot{{{base_latex}}}"
        return f"{{{base_latex}}}"


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
        latex_parts: list[str] = []
        for child in self:
            child_latex = ""
            if hasattr(child, "to_latex") and callable(child.to_latex):
                child_latex = child.to_latex()
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
    oMathPara: CT_MathOmathPara | None = ZeroOrOne("m:oMathPara", successors=())
    oMath: CT_OMath | None = ZeroOrOne("m:oMath", successors=())

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
    def text(self) -> str: # pyright: ignore[reportIncompatibleMethodOverride]
        """Returns the LaTeX representation of the math content, enclosed in '$'."""
        latex_content = self.to_latex()
        # If to_latex successfully returns (i.e., valid math content was found and converted),
        # and that content happens to be an empty string, f"${latex_content}$" will correctly produce "$$".
        # If to_latex raises InvalidXmlError due to a malformed a14:m, that error will propagate.
        return f"${latex_content}$"
