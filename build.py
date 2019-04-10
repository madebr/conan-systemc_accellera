#!/usr/bin/env python

from bincrafters import build_template_default
import os

if __name__ == "__main__":
    assert "CPPSTD" in os.environ
    builder = build_template_default.get_builder(pure_c=False)

    for b in builder.items:
        b.settings["compiler.cppstd"] = os.environ["CPPSTD"]

    builder.run()
