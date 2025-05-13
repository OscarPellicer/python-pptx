"""Utility functions for loading files for unit testing."""

import os
import sys
import re

_thisdir = os.path.split(__file__)[0]
test_file_dir = os.path.abspath(os.path.join(_thisdir, "..", "test_files"))


def absjoin(*paths: str):
    return os.path.abspath(os.path.join(*paths))


def snippet_bytes(snippet_file_name: str):
    """Return bytes read from snippet file having `snippet_file_name`."""
    snippet_file_path = os.path.join(test_file_dir, "snippets", "%s.txt" % snippet_file_name)
    with open(snippet_file_path, "rb") as f:
        content_bytes = f.read()
    return content_bytes.replace(b"\r\n", b"\n").strip()


def snippet_seq(name: str, offset: int = 0, count: int = sys.maxsize):
    """
    Return a tuple containing the unicode text snippets read from the snippet
    file having *name*. Snippets are delimited by a blank line. If specified,
    *count* snippets starting at *offset* are returned.
    """
    path = os.path.join(test_file_dir, "snippets", "%s.txt" % name)
    with open(path, "rb") as f:
        text = f.read().decode("utf-8")
    snippets = re.split(r"(?:\r?\n){2,}", text.strip())
    start, end = offset, offset + count
    # Filter out empty strings that can result from re.split if there are e.g. 3+ newlines
    processed_snippets = [s for s in snippets if s.strip()]
    return tuple(processed_snippets[start:end])


def snippet_text(snippet_file_name: str):
    """
    Return the unicode text read from the test snippet file having
    *snippet_file_name*.
    """
    snippet_file_path = os.path.join(test_file_dir, "snippets", "%s.txt" % snippet_file_name)
    with open(snippet_file_path, "rb") as f:
        snippet_bytes = f.read()
    return snippet_bytes.decode("utf-8").replace("\r\n", "\n")


def testfile(name: str):
    """
    Return the absolute path to test file having *name*.
    """
    return absjoin(test_file_dir, name)


def testfile_bytes(*segments: str):
    """Return bytes of file at path formed by adding `segments` to test file dir."""
    path = os.path.join(test_file_dir, *segments)
    with open(path, "rb") as f:
        return f.read()
