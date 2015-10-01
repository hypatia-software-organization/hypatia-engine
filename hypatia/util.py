"""Miscellaneous utilities.
"""

def wrapline(text, font, maxwidth):
    """Wrap text using the given font to the given maximum width.

    Args:
        text (str): The text to wrap
        font (pygame.font.Font): The font to use to calculate width
        maxwidth (int): The maximum width to wrap to

    Returns:
        list(str): List of wrapped lines (with no line endings)

    Examples:
        >>> wrapline("text to wrap", font, 50)
        ['text to', 'wrap']
    """

    length = font.size(text)[0]

    if length <= maxwidth:
        return [text]

    stext = text.split()
    lines = []
    upto = 0

    while upto < len(stext):
        current = []

        for word in stext[upto:]:
            current.append(word)
            upto += 1

            width = font.size(" ".join(current))[0]
            if width > maxwidth:
                current.pop()
                upto -= 1

                lines.append(" ".join(current))
                current = []

    return lines
