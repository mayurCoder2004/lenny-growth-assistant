import nh3


ALLOWED_TAGS = {
    "p",
    "br",
    "strong",
    "em",
    "b",
    "i",
    "u",
    "blockquote",
    "ul",
    "ol",
    "li",
    "h1",
    "h2",
    "h3",
    "h4",
    "code",
    "pre",
    "a",
}


ALLOWED_ATTRIBUTES = {
    "a": {
        "href",
        "title",
    },
}


def sanitize_html(content: str) -> str:
    if not content or not content.strip():
        return ""

    return nh3.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes={"http", "https", "mailto"},
    )
