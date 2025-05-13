"""Parser configuration and related functions for python-pptx oxml."""

from __future__ import annotations

from lxml import etree

# Configure etree XML parser
element_class_lookup = etree.ElementNamespaceClassLookup()
oxml_parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False)
oxml_parser.set_element_class_lookup(element_class_lookup)


def parse_xml(xml: str | bytes):
    """Return root lxml element obtained by parsing XML character string in `xml`."""
    return etree.fromstring(xml, oxml_parser) 