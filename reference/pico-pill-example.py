#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-fasthtml",
# ]
# ///
#
from fasthtml.common import * 

app, rt = fast_app(
    pico=True,
    hdrs=(
        Style("""
        fieldset {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4em;
            border: none;
        }

        label.pill {
            display: inline-block;
            padding: 0.3em 0.9em;
            border-radius: 999px;
            border: 1px solid var(--pico-primary);
            cursor: pointer;
            user-select: none;
            font-size: 0.9em;
            line-height: 1.5;
            transition: all 0.2s;
        }

        /* unchecked state */
        input[type="checkbox"]:not(:checked) + label.pill {
            background: transparent;
            color: var(--pico-primary);
        }

        /* checked state */
        input[type="checkbox"]:checked + label.pill {
            background: var(--p ico-primary);
            color: white;
            box-shadow: 0 0 0 2px var(--pico-primary);
        }
    """),
    ))

@app.get("/")
def home():
    return Titled("FastHTML",
        P("Example of pill-shaped checkboxes that act as toggle buttons. Thank-you to @curtis on FastHTML discord for getting this sorted out.")
        Fieldset(
            Legend("Toggle fields to search (default is all)"),
            Input(type="checkbox", id="short", hidden=True),
            Label("short", _for="short", cls="pill"),
            Input(type="checkbox", id="long", hidden=True),
            Label("short", _for="long", cls="pill"),
        ), 
    )

serve()
