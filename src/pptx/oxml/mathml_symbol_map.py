# -*- coding: utf-8 -*-
"""
Mapping of Unicode MathML characters to LaTeX equivalents.
Keys are defined using Unicode escape sequences (/uXXXX for BMP, /UXXXXXXXX for non-BMP)
to ensure accurate representation of the character codes found in XML.
Values are the corresponding LaTeX strings.
Comments indicate the original Unicode character and its code point.
"""

MATH_CHAR_TO_LATEX_CONVERSION: dict[str, str] = {
    # ======== Mathematical Alphanumerics - Italic ========
    # These mappings convert specific Unicode math italic characters to their
    # intended LaTeX representation. Some conversions adjust for visual differences
    # where a specific math italic character in XML (e.g., math italic 'M')
    # might be used to represent a different visual character in the equation (e.g., 'n').

    # --- Latin Italic letters (XML char -> desired visual in LaTeX) ---
    "\U0001D465": "x",  # 𝑤 (MATHEMATICAL ITALIC SMALL W, U+1D465) -> "x"
    "\U0001D466": "y",  # 𝑥 (MATHEMATICAL ITALIC SMALL X, U+1D466) -> "y"
    "\U0001D456": "i",  # ℎ (MATHEMATICAL ITALIC SMALL H, U+1D456) -> "i"
    "\U0001D457": "j",  # 𝑖 (MATHEMATICAL ITALIC SMALL I, U+1D457) -> "j"
    "\U0001D458": "k",  # 𝑗 (MATHEMATICAL ITALIC SMALL J, U+1D458) -> "k"
    "\U0001D45A": "m",  # 𝑙 (MATHEMATICAL ITALIC SMALL L, U+1D45A) -> "m"
    "\U0001D45B": "n",  # 𝑚 (MATHEMATICAL ITALIC SMALL M, U+1D45B) -> "n"
    "\U0001D467": "z",  # 𝑦 (MATHEMATICAL ITALIC SMALL Y, U+1D467) -> "z"
    "\U0001D451": "d",  # 𝑑 (MATHEMATICAL ITALIC SMALL D, U+1D451)
    "\U0001D452": "e",  # 𝑒 (MATHEMATICAL ITALIC SMALL E, U+1D452)
    "\U0001D453": "f",  # 𝑓 (MATHEMATICAL ITALIC SMALL F, U+1D453)
    "\U0001D44E": "a",  # 𝑎 (MATHEMATICAL ITALIC SMALL A, U+1D44E)
    "\U0001D44F": "b",  # 𝑏 (MATHEMATICAL ITALIC SMALL B, U+1D44F)
    "\U0001D450": "c",  # 𝑐 (MATHEMATICAL ITALIC SMALL C, U+1D450)
    "\U0001D454": "g",  # 𝑔 (MATHEMATICAL ITALIC SMALL G, U+1D454)
    "\U0001D455": "h",  # ℎ (MATHEMATICAL ITALIC SMALL H (planck const), U+1D455)
    "\U0001D459": "k",  # 𝑘 (MATHEMATICAL ITALIC SMALL K, U+1D459)
    "\U0001D45C": "n",  # 𝑛 (MATHEMATICAL ITALIC SMALL N, U+1D45C)
    "\U0001D45D": "o",  # 𝑜 (MATHEMATICAL ITALIC SMALL O, U+1D45D)
    "\U0001D45E": "p",  # 𝑝 (MATHEMATICAL ITALIC SMALL P, U+1D45E)
    "\U0001D45F": "q",  # 𝑞 (MATHEMATICAL ITALIC SMALL Q, U+1D45F)
    "\U0001D460": "r",  # 𝑟 (MATHEMATICAL ITALIC SMALL R, U+1D460)
    "\U0001D461": "s",  # 𝑠 (MATHEMATICAL ITALIC SMALL S, U+1D461)
    "\U0001D462": "t",  # 𝑡 (MATHEMATICAL ITALIC SMALL T, U+1D462)
    "\U0001D463": "u",  # 𝑢 (MATHEMATICAL ITALIC SMALL U, U+1D463)
    "\U0001D464": "v",  # 𝑣 (MATHEMATICAL ITALIC SMALL V, U+1D464)
    "\U0001D468": "z",  # 𝑧 (MATHEMATICAL ITALIC SMALL Z, U+1D468)


    "\U0001D443": "P",  # 𝑃 (MATHEMATICAL ITALIC CAPITAL P, U+1D443)
    "\U0001D44C": "Y",  # 𝑌 (MATHEMATICAL ITALIC CAPITAL Y, U+1D44C)
    "\U0001D447": "T",  # 𝑇 (MATHEMATICAL ITALIC CAPITAL T, U+1D447)
    "\U0001D434": "A",  # 𝐴 (MATHEMATICAL ITALIC CAPITAL A, U+1D434)
    "\U0001D435": "B",  # 𝐵 (MATHEMATICAL ITALIC CAPITAL B, U+1D435)
    "\U0001D436": "C",  # 𝐶 (MATHEMATICAL ITALIC CAPITAL C, U+1D436)
    "\U0001D437": "D",  # 𝐷 (MATHEMATICAL ITALIC CAPITAL D, U+1D437)
    "\U0001D438": "E",  # 𝐸 (MATHEMATICAL ITALIC CAPITAL E, U+1D438)
    "\U0001D439": "F",  # 𝐹 (MATHEMATICAL ITALIC CAPITAL F, U+1D439)
    "\U0001D43A": "G",  # 𝐺 (MATHEMATICAL ITALIC CAPITAL G, U+1D43A)
    "\U0001D43B": "H",  # 𝐻 (MATHEMATICAL ITALIC CAPITAL H, U+1D43B)
    "\U0001D43C": "I",  # 𝐼 (MATHEMATICAL ITALIC CAPITAL I, U+1D43C)
    "\U0001D43D": "J",  # 𝐽 (MATHEMATICAL ITALIC CAPITAL J, U+1D43D)
    "\U0001D43E": "K",  # 𝐾 (MATHEMATICAL ITALIC CAPITAL K, U+1D43E)
    "\U0001D43F": "L",  # 𝐿 (MATHEMATICAL ITALIC CAPITAL L, U+1D43F)
    "\U0001D440": "M",  # 𝑀 (MATHEMATICAL ITALIC CAPITAL M, U+1D440)
    "\U0001D441": "N",  # 𝑁 (MATHEMATICAL ITALIC CAPITAL N, U+1D441)
    "\U0001D442": "O",  # 𝑂 (MATHEMATICAL ITALIC CAPITAL O, U+1D442)
    "\U0001D444": "Q",  # 𝑄 (MATHEMATICAL ITALIC CAPITAL Q, U+1D444)
    "\U0001D445": "R",  # 𝑅 (MATHEMATICAL ITALIC CAPITAL R, U+1D445)
    "\U0001D446": "S",  # 𝑆 (MATHEMATICAL ITALIC CAPITAL S, U+1D446)
    "\U0001D448": "U",  # 𝑈 (MATHEMATICAL ITALIC CAPITAL U, U+1D448)
    "\U0001D449": "V",  # 𝑉 (MATHEMATICAL ITALIC CAPITAL V, U+1D449)
    "\U0001D44A": "W",  # 𝑊 (MATHEMATICAL ITALIC CAPITAL W, U+1D44A)
    "\U0001D44B": "X",  # 𝑋 (MATHEMATICAL ITALIC CAPITAL X, U+1D44B)
    "\U0001D44D": "Z",  # 𝑍 (MATHEMATICAL ITALIC CAPITAL Z, U+1D44D)

    # --- Greek Italic letters (XML char -> desired visual in LaTeX) ---
    "\U0001D715": "\\omega ",    # 𝜔 (MATHEMATICAL ITALIC SMALL OMEGA, U+1D715)
    "\U0001D70B": "\\pi ",       # 𝜋 (MATHEMATICAL ITALIC SMALL PI, U+1D70B) -> \pi
    "\U0001D718": "\\chi ",      # 𝜘 (MATHEMATICAL ITALIC SMALL KAI, U+1D718) -> \chi

    # ======== Standard Mathematical Alphanumerics - Greek Italic ========
    # --- Small Greek Italic ---
    "\U0001D6FC": "\\alpha ",    # 𝛼 (MATHEMATICAL ITALIC SMALL ALPHA, U+1D6FC)
    "\U0001D6FD": "\\beta ",     # 𝛽 (MATHEMATICAL ITALIC SMALL BETA, U+1D6FD)
    "\U0001D6FE": "\\gamma ",    # 𝛾 (MATHEMATICAL ITALIC SMALL GAMMA, U+1D6FE)
    "\U0001D6FF": "\\delta ",    # 𝛿 (MATHEMATICAL ITALIC SMALL DELTA, U+1D6FF)
    "\U0001D700": "\\epsilon ",  # 𝜀 (MATHEMATICAL ITALIC SMALL EPSILON, U+1D700)
    "\U0001D716": "\\varepsilon ",# 𝜖 (MATHEMATICAL ITALIC EPSILON SYMBOL, U+1D716)
    "\U0001D701": "\\zeta ",     # 𝜁 (MATHEMATICAL ITALIC SMALL ZETA, U+1D701)
    "\U0001D702": "\\eta ",      # 𝜂 (MATHEMATICAL ITALIC SMALL ETA, U+1D702)
    "\U0001D703": "\\theta ",    # 𝜃 (MATHEMATICAL ITALIC SMALL THETA, U+1D703)
    "\U0001D717": "\\vartheta ", # ϑ (MATHEMATICAL ITALIC THETA SYMBOL, U+1D717)
    "\U0001D704": "\\iota ",     # 𝜄 (MATHEMATICAL ITALIC SMALL IOTA, U+1D704)
    "\U0001D705": "\\kappa ",    # 𝜅 (MATHEMATICAL ITALIC SMALL KAPPA, U+1D705)
    "\U0001D706": "\\lambda ",   # 𝜆 (MATHEMATICAL ITALIC SMALL LAMDA, U+1D706)
    "\U0001D707": "\\mu ",       # 𝜇 (MATHEMATICAL ITALIC SMALL MU, U+1D707)
    "\U0001D708": "\\nu ",       # 𝜈 (MATHEMATICAL ITALIC SMALL NU, U+1D708)
    "\U0001D709": "\\xi ",       # 𝜉 (MATHEMATICAL ITALIC SMALL XI, U+1D709)
    "\U0001D70A": "o",           # 𝜊 (MATHEMATICAL ITALIC SMALL OMICRON, U+1D70A)
    "\U0001D71B": "\\varpi ",    # ϖ (MATHEMATICAL ITALIC PI SYMBOL, U+1D71B)
    "\U0001D70C": "\\rho ",      # 𝜌 (MATHEMATICAL ITALIC SMALL RHO, U+1D70C)
    "\U0001D71A": "\\varrho ",   # ϱ (MATHEMATICAL ITALIC RHO SYMBOL, U+1D71A)
    "\U0001D70E": "\\sigma ",    # 𝜎 (MATHEMATICAL ITALIC SMALL SIGMA, U+1D70E)
    "\U0001D70D": "\\varsigma ", # ς (MATHEMATICAL ITALIC SMALL FINAL SIGMA, U+1D70D)
    "\U0001D70F": "\\tau ",      # 𝜏 (MATHEMATICAL ITALIC SMALL TAU, U+1D70F)
    "\U0001D710": "\\upsilon ",  # 𝜐 (MATHEMATICAL ITALIC SMALL UPSILON, U+1D710)
    "\U0001D711": "\\phi ",      # 𝜑 (MATHEMATICAL ITALIC SMALL PHI, U+1D711)
    "\U0001D719": "\\varphi ",   # 𝜙 (MATHEMATICAL ITALIC PHI SYMBOL, U+1D719)
    "\U0001D712": "\\chi ",      # 𝜒 (MATHEMATICAL ITALIC SMALL CHI, U+1D712)
    "\U0001D713": "\\psi ",      # 𝜓 (MATHEMATICAL ITALIC SMALL PSI, U+1D713)
    "\U0001D714": "\\omega ",    # 𝜔 (MATHEMATICAL ITALIC SMALL OMEGA, U+1D714)

    # --- Capital Greek Italic ---
    "\U0001D6E2": "\\Gamma ",    # 𝛤 (MATHEMATICAL ITALIC CAPITAL GAMMA, U+1D6E2)
    "\U0001D6E3": "\\Delta ",    # 𝛥 (MATHEMATICAL ITALIC CAPITAL DELTA, U+1D6E3)
    "\U0001D6E9": "\\Theta ",    # 𝛩 (MATHEMATICAL ITALIC CAPITAL THETA, U+1D6E9)
    "\U0001D6EC": "\\Lambda ",   # 𝛬 (MATHEMATICAL ITALIC CAPITAL LAMDA, U+1D6EC)
    "\U0001D6EF": "\\Xi ",       # 𝛯 (MATHEMATICAL ITALIC CAPITAL XI, U+1D6EF)
    "\U0001D6F1": "\\Pi ",       # 𝛱 (MATHEMATICAL ITALIC CAPITAL PI, U+1D6F1)
    "\U0001D6F4": "\\Sigma ",    # 𝛴 (MATHEMATICAL ITALIC CAPITAL SIGMA, U+1D6F4)
    "\U0001D6F6": "\\Phi ",      # 𝛷 (MATHEMATICAL ITALIC CAPITAL PHI, U+1D6F6)
    "\U0001D6F9": "\\Psi ",      # 𝛹 (MATHEMATICAL ITALIC CAPITAL PSI, U+1D6F9)
    "\U0001D6FA": "\\Omega ",    # 𝛺 (MATHEMATICAL ITALIC CAPITAL OMEGA, U+1D6FA)

    # ======== Blackboard Bold (Double-Struck) ========
    "\u2115": "\\mathbb{N}",   # ℕ (DOUBLE-STRUCK CAPITAL N, U+2115)
    "\u2124": "\\mathbb{Z}",   # ℤ (DOUBLE-STRUCK CAPITAL Z, U+2124)
    "\u211A": "\\mathbb{Q}",   # ℚ (DOUBLE-STRUCK CAPITAL Q, U+211A)
    "\u211D": "\\mathbb{R}",   # ℝ (DOUBLE-STRUCK CAPITAL R, U+211D)
    "\u2102": "\\mathbb{C}",   # ℂ (DOUBLE-STRUCK CAPITAL C, U+2102)

    # ======== General Operators & Symbols ========
    "\u002B": "+",          # + (PLUS SIGN, U+002B)
    "\u2212": "-",          # − (MINUS SIGN, U+2212)
    "\u00D7": "\\times ",   # × (MULTIPLICATION SIGN, U+00D7)
    "\u00F7": "\\div ",     # ÷ (DIVISION SIGN, U+00F7)
    "\u2217": "*",          # ∗ (ASTERISK OPERATOR, U+2217)
    "\u00B7": "\\cdot ",   # · (MIDDLE DOT, U+00B7)
    "\u2218": "\\circ ",   # ∘ (RING OPERATOR, U+2218)
    "\u2295": "\\oplus ",   # ⊕ (CIRCLED PLUS, U+2295)
    "\u2297": "\\otimes ",  # ⊗ (CIRCLED TIMES, U+2297)
    "\u2202": "\\partial ", # ∂ (PARTIAL DIFFERENTIAL, U+2202)
    "\u2207": "\\nabla ",   # ∇ (NABLA, U+2207)
    "\u2211": "\\sum ",     # ∑ (N-ARY SUMMATION, U+2211)
    "\u220F": "\\prod ",    # ∏ (N-ARY PRODUCT, U+220F)
    "\u2210": "\\coprod ",  # ∐ (N-ARY COPRODUCT, U+2210)
    "\u00B1": "\\pm ",      # ± (PLUS-MINUS SIGN, U+00B1)
    "\u2213": "\\mp ",      # ∓ (MINUS-OR-PLUS SIGN, U+2213)
    "\u221A": "\\sqrt",     # √ (SQUARE ROOT, U+221A) - base for \sqrt{}
    "\u221E": "\\infty ",   # ∞ (INFINITY, U+221E)
    "\u0127": "\\hbar ",   # ħ (LATIN SMALL LETTER H WITH STROKE, U+0127)
    "\u2113": "\\ell ",    # ℓ (SCRIPT SMALL L, U+2113)
    "\u2205": "\\emptyset ",# ∅ (EMPTY SET, U+2205)
    "\u2032": "'",          # ′ (PRIME, U+2032)
    "\u2033": "''",         # ″ (DOUBLE PRIME, U+2033)
    "\u2034": "'''",        # ‴ (TRIPLE PRIME, U+2034)

    # ======== Arrows ========
    "\u2192": "\\to ",           # → (RIGHTWARDS ARROW, U+2192)
    "\u2190": "\\leftarrow ",    # ← (LEFTWARDS ARROW, U+2190)
    "\u2194": "\\leftrightarrow ",# ↔ (LEFT RIGHT ARROW, U+2194)
    "\u21D2": "\\Rightarrow ",   # ⇒ (RIGHTWARDS DOUBLE ARROW, U+21D2)
    "\u21D0": "\\Leftarrow ",    # ⇐ (LEFTWARDS DOUBLE ARROW, U+21D0)
    "\u21D4": "\\Leftrightarrow ",# ⇔ (LEFT RIGHT DOUBLE ARROW, U+21D4)
    "\u21A6": "\\mapsto ",       # ↦ (RIGHTWARDS ARROW FROM BAR, U+21A6)
    "\u27F6": "\\longrightarrow ",# ⟶ (LONG RIGHTWARDS ARROW, U+27F6)

    # ======== Relations ========
    "\u003D": "=",          # = (EQUALS SIGN, U+003D)
    "\u2260": "\\ne ",      # ≠ (NOT EQUAL TO, U+2260)
    "\u003C": "<",          # < (LESS-THAN SIGN, U+003C)
    "\u003E": ">",          # > (GREATER-THAN SIGN, U+003E)
    "\u2264": "\\le ",      # ≤ (LESS-THAN OR EQUAL TO, U+2264)
    "\u2265": "\\ge ",      # ≥ (GREATER-THAN OR EQUAL TO, U+2265)
    "\u2248": "\\approx ",  # ≈ (ALMOST EQUAL TO, U+2248)
    "\u2245": "\\cong ",   # ≅ (APPROXIMATELY EQUAL TO, U+2245)
    "\u2261": "\\equiv ",  # ≡ (IDENTICAL TO, U+2261)
    "\u221D": "\\propto ", # ∝ (PROPORTIONAL TO, U+221D)
    "\u2208": "\\in ",     # ∈ (ELEMENT OF, U+2208)
    "\u2209": "\\notin ",  # ∉ (NOT AN ELEMENT OF, U+2209)
    "\u220B": "\\ni ",     # ∋ (CONTAINS AS MEMBER, U+220B)
    "\u2282": "\\subset ", # ⊂ (SUBSET OF, U+2282)
    "\u2283": "\\supset ", # ⊃ (SUPERSET OF, U+2283)
    "\u2286": "\\subseteq ",# ⊆ (SUBSET OF OR EQUAL TO, U+2286)
    "\u2287": "\\supseteq ",# ⊇ (SUPERSET OF OR EQUAL TO, U+2287)
    "\u222A": "\\cup ",    # ∪ (UNION, U+222A)
    "\u2229": "\\cap ",    # ∩ (INTERSECTION, U+2229)
    "\u2227": "\\land ",   # ∧ (LOGICAL AND, U+2227)
    "\u2228": "\\lor ",    # ∨ (LOGICAL OR, U+2228)
    "\u00AC": "\\neg ",   # ¬ (NOT SIGN, U+00AC)
    "\u2200": "\\forall ", # ∀ (FOR ALL, U+2200)
    "\u2203": "\\exists ", # ∃ (THERE EXISTS, U+2203)
    "\u2204": "\\nexists ",# ∄ (THERE DOES NOT EXIST, U+2204)

    # ======== Dots/Ellipses ========
    "\u2026": "\\dots ",   # … (HORIZONTAL ELLIPSIS, U+2026)
    "\u22EF": "\\cdots ",  # ⋯ (MIDLINE HORIZONTAL ELLIPSIS, U+22EF)
    "\u22EE": "\\vdots ",  # ⋮ (VERTICAL ELLIPSIS, U+22EE)
    "\u22F1": "\\ddots ",  # ⋱ (DOWN RIGHT DIAGONAL ELLIPSIS, U+22F1)

    # ======== Integrals ========
    "\u222B": "\\int ",     # ∫ (INTEGRAL, U+222B)
    "\u222C": "\\iint ",    # ∬ (DOUBLE INTEGRAL, U+222C)
    "\u222D": "\\iiint ",   # ∭ (TRIPLE INTEGRAL, U+222D)
    "\u222E": "\\oint ",    # ∮ (CONTOUR INTEGRAL, U+222E)
    "\u222F": "\\oiint ",   # ∯ (SURFACE INTEGRAL, U+222F)
    "\u2230": "\\oiiint ",  # ∰ (VOLUME INTEGRAL, U+2230) - Changed from \iiint for distinctness if possible, \oiiint may need amsmath. Fallback to \iiint is fine too.

    # ======== Other (Script, Fraktur, etc.) ========
    "\u2132": "F",              # Ⅎ (TURNED CAPITAL F, U+2132)
    "\u210C": "\\mathfrak{H}",  # ℌ (BLACK-LETTER CAPITAL H, U+210C)
    "\u2131": "\\mathcal{F}",   # ℱ (SCRIPT CAPITAL F, U+2131)
    "\u2134": "\\mathcal{O}",   # ℴ (SCRIPT SMALL O, U+2134) -> Mapped to Script Capital O
    "\u212B": "\\AA",           # Å (ANGSTROM SIGN, U+212B)
    "\u2127": "\\mho ",         # ℧ (INVERTED OHM SIGN, U+2127)
    "\u211C": "\\Re ",          # ℜ (BLACK-LETTER CAPITAL R, U+211C)
    "\u2111": "\\Im ",          # ℑ (BLACK-LETTER CAPITAL I, U+2111)
    "\u2118": "\\wp ",          # ℘ (SCRIPT CAPITAL P / Weierstrass Elliptic Function, U+2118)
    "\u2215": "/",             # ∕ (DIVISION SLASH, U+2215)

    # ======== Fallback/Standard Greek (Non-Italic) ========
    # These are for basic Greek characters if not styled as math italics in XML.
    # Math Italic Greek (U+1D6FC etc.) are preferred and defined above.
    "\u03B1": "\\alpha ",   # α (GREEK SMALL LETTER ALPHA, U+03B1)
    "\u03B2": "\\beta ",    # β (GREEK SMALL LETTER BETA, U+03B2)
    "\u03B3": "\\gamma ",   # γ (GREEK SMALL LETTER GAMMA, U+03B3)
    "\u03B4": "\\delta ",   # δ (GREEK SMALL LETTER DELTA, U+03B4)
    "\u03B5": "\\epsilon ", # ε (GREEK SMALL LETTER EPSILON, U+03B5)
    "\u03B6": "\\zeta ",   # ζ (GREEK SMALL LETTER ZETA, U+03B6)
    "\u03B7": "\\eta ",    # η (GREEK SMALL LETTER ETA, U+03B7)
    "\u03B8": "\\theta ",  # θ (GREEK SMALL LETTER THETA, U+03B8)
    "\u03B9": "\\iota ",   # ι (GREEK SMALL LETTER IOTA, U+03B9)
    "\u03BA": "\\kappa ",  # κ (GREEK SMALL LETTER KAPPA, U+03BA)
    "\u03BB": "\\lambda ", # λ (GREEK SMALL LETTER LAMDA, U+03BB)
    "\u03BC": "\\mu ",    # μ (GREEK SMALL LETTER MU, U+03BC)
    "\u03BD": "\\nu ",    # ν (GREEK SMALL LETTER NU, U+03BD)
    "\u03BE": "\\xi ",    # ξ (GREEK SMALL LETTER XI, U+03BE)
    "\u03BF": "o",         # ο (GREEK SMALL LETTER OMICRON, U+03BF)
    "\u03C0": "\\pi ",    # π (GREEK SMALL LETTER PI, U+03C0)
    "\u03C1": "\\rho ",   # ρ (GREEK SMALL LETTER RHO, U+03C1)
    "\u03C3": "\\sigma ", # σ (GREEK SMALL LETTER SIGMA, U+03C3)
    "\u03C2": "\\varsigma ",# ς (GREEK SMALL LETTER FINAL SIGMA, U+03C2)
    "\u03C4": "\\tau ",   # τ (GREEK SMALL LETTER TAU, U+03C4)
    "\u03C5": "\\upsilon ",# υ (GREEK SMALL LETTER UPSILON, U+03C5)
    "\u03C6": "\\phi ",   # φ (GREEK SMALL LETTER PHI, U+03C6)
    "\u03C7": "\\chi ",   # χ (GREEK SMALL LETTER CHI, U+03C7)
    "\u03C8": "\\psi ",   # ψ (GREEK SMALL LETTER PSI, U+03C8)
    "\u03C9": "\\omega ", # ω (GREEK SMALL LETTER OMEGA, U+03C9)

    "\u0391": "A",         # Α (GREEK CAPITAL LETTER ALPHA, U+0391) -> A
    "\u0392": "B",         # Β (GREEK CAPITAL LETTER BETA, U+0392) -> B
    "\u0393": "\\Gamma ",   # Γ (GREEK CAPITAL LETTER GAMMA, U+0393)
    "\u0394": "\\Delta ",   # Δ (GREEK CAPITAL LETTER DELTA, U+0394)
    "\u0395": "E",         # Ε (GREEK CAPITAL LETTER EPSILON, U+0395) -> E
    "\u0396": "Z",         # Ζ (GREEK CAPITAL LETTER ZETA, U+0396) -> Z
    "\u0397": "H",         # Η (GREEK CAPITAL LETTER ETA, U+0397) -> H
    "\u0398": "\\Theta ",  # Θ (GREEK CAPITAL LETTER THETA, U+0398)
    "\u0399": "I",         # Ι (GREEK CAPITAL LETTER IOTA, U+0399) -> I
    "\u039A": "K",         # Κ (GREEK CAPITAL LETTER KAPPA, U+039A) -> K
    "\u039B": "\\Lambda ", # Λ (GREEK CAPITAL LETTER LAMDA, U+039B)
    "\u039C": "M",         # Μ (GREEK CAPITAL LETTER MU, U+039C) -> M
    "\u039D": "N",         # Ν (GREEK CAPITAL LETTER NU, U+039D) -> N
    "\u039E": "\\Xi ",    # Ξ (GREEK CAPITAL LETTER XI, U+039E)
    "\u039F": "O",         # Ο (GREEK CAPITAL LETTER OMICRON, U+039F) -> O
    "\u03A0": "\\Pi ",    # Π (GREEK CAPITAL LETTER PI, U+03A0)
    "\u03A1": "P",         # Ρ (GREEK CAPITAL LETTER RHO, U+03A1) -> P
    "\u03A3": "\\Sigma ",  # Σ (GREEK CAPITAL LETTER SIGMA, U+03A3)
    "\u03A4": "T",         # Τ (GREEK CAPITAL LETTER TAU, U+03A4) -> T
    "\u03A5": "\\Upsilon ",# Υ (GREEK CAPITAL LETTER UPSILON, U+03A5)
    "\u03A6": "\\Phi ",   # Φ (GREEK CAPITAL LETTER PHI, U+03A6)
    "\u03A7": "X",         # Χ (GREEK CAPITAL LETTER CHI, U+03A7) -> X
    "\u03A8": "\\Psi ",   # Ψ (GREEK CAPITAL LETTER PSI, U+03A8)
    "\u03A9": "\\Omega ",  # Ω (GREEK CAPITAL LETTER OMEGA, U+03A9)

    # ======== Spacing ========
    "\u00A0": " ",          # NO-BREAK SPACE (U+00A0) -> regular space
    "\u2009": "\\,",        # THIN SPACE (U+2009) -> \, (thin space in math mode)
    "\u2002": "\\enspace ",  # EN SPACE (U+2002)
    "\u2003": "\\quad ",    # EM SPACE (U+2003)
    "\u2004": "\\;",        # THREE-PER-EM SPACE (U+2004) -> \; (thick space)
    "\u2005": "\\:",        # FOUR-PER-EM SPACE (U+2005) -> \: (medium space)
    "\u200B": "",           # ZERO WIDTH SPACE (U+200B) -> empty string (LaTeX handles it)
} 