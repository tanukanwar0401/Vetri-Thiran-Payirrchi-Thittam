from __future__ import annotations

import html
import re


def sanitize_text(
    text: str
) -> str:
    """
    Normalize common typography and remove
    problematic control characters.
    """

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )

    text = "".join(
        character
        for character in text
        if (
            character in "\n\r\t"
            or ord(character) >= 32
        )
    )

    return re.sub(
        r"[ \t]+",
        " ",
        text
    ).strip()


def text_to_html(
    text: str
) -> str:
    """
    Convert Markdown-like generated text
    into safe HTML for Streamlit preview.
    """

    lines = sanitize_text(
        text
    ).splitlines()

    output = []

    in_list = False

    def close_list():

        nonlocal in_list

        if in_list:

            output.append(
                "</ol>"
            )

            in_list = False

    for raw_line in lines:

        line = raw_line.strip()

        if not line:

            close_list()

            continue

        if line.startswith("### "):

            close_list()

            output.append(
                f"<h3>{html.escape(line[4:])}</h3>"
            )

        elif line.startswith("## "):

            close_list()

            output.append(
                f"<h2>{html.escape(line[3:])}</h2>"
            )

        elif line.startswith("# "):

            close_list()

            output.append(
                f"<h1>{html.escape(line[2:])}</h1>"
            )

        elif re.match(
            r"^\d+\.\s+",
            line
        ):

            if not in_list:

                output.append(
                    "<ol>"
                )

                in_list = True

            content = re.sub(
                r"^\d+\.\s+",
                "",
                line
            )

            output.append(
                f"<li>{html.escape(content)}</li>"
            )

        elif line.startswith("- "):

            close_list()

            output.append(
                "<div class='bullet'>"
                f"• {html.escape(line[2:])}"
                "</div>"
            )

        else:

            close_list()

            parts = re.split(
                r"(\*\*.*?\*\*)",
                line
            )

            rendered = ""

            for part in parts:

                if (
                    part.startswith("**")
                    and part.endswith("**")
                ):

                    rendered += (
                        "<strong>"
                        + html.escape(
                            part[2:-2]
                        )
                        + "</strong>"
                    )

                else:

                    rendered += html.escape(
                        part
                    )

            output.append(
                f"<p>{rendered}</p>"
            )

    close_list()

    return "\n".join(output)