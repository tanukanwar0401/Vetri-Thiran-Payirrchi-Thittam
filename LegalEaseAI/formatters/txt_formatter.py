from backend.formatters.common import sanitize_text


def format_txt(
    text: str
) -> bytes:
    """
    Convert generated text into UTF-8 TXT.
    """

    return sanitize_text(
        text
    ).encode(
        "utf-8"
    )