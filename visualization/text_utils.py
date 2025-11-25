"""
Text formatting utilities for visualization.

Provides functions to format names and labels for display,
removing underscores and applying proper capitalization.
"""


def format_display_name(name: str) -> str:
    """
    Format a name for display by removing underscores and title-casing.

    Converts internal names like "player_0" or "community_chest" to
    display-friendly names like "Player 0" or "Community Chest".

    Args:
        name: Internal name (may contain underscores)

    Returns:
        Display-friendly formatted name

    Examples:
        >>> format_display_name("player_0")
        'Player 0'
        >>> format_display_name("community_chest")
        'Community Chest'
        >>> format_display_name("go_to_jail")
        'Go To Jail'
        >>> format_display_name("The Regent Theatre")
        'The Regent Theatre'
    """
    # Replace underscores with spaces
    formatted = name.replace("_", " ")

    # Apply title case
    formatted = formatted.title()

    return formatted


def format_player_name(player_id: int, prefix: str = "Player") -> str:
    """
    Format a player name for display.

    Args:
        player_id: Player ID number
        prefix: Prefix to use (default: "Player")

    Returns:
        Formatted player name

    Examples:
        >>> format_player_name(0)
        'Player 0'
        >>> format_player_name(1, "P")
        'P 1'
    """
    return f"{prefix} {player_id}"


def format_tile_type(tile_type: str) -> str:
    """
    Format a tile type for display.

    Args:
        tile_type: Tile type name (may contain underscores)

    Returns:
        Display-friendly tile type

    Examples:
        >>> format_tile_type("community_chest")
        'Community Chest'
        >>> format_tile_type("go_to_jail")
        'Go To Jail'
    """
    return format_display_name(tile_type)


def truncate_name(name: str, max_length: int = 15, ellipsis: str = "...") -> str:
    """
    Truncate a name if it exceeds max length.

    Args:
        name: Name to potentially truncate
        max_length: Maximum length before truncation
        ellipsis: String to append when truncating

    Returns:
        Truncated name

    Examples:
        >>> truncate_name("Very Long Property Name", 10)
        'Very Lo...'
        >>> truncate_name("Short", 10)
        'Short'
    """
    if len(name) <= max_length:
        return name

    truncate_at = max_length - len(ellipsis)
    if truncate_at <= 0:
        return ellipsis[:max_length]

    return name[:truncate_at] + ellipsis


def wrap_text(text: str, max_width: int, font) -> list[str]:
    """
    Wrap text to fit within a maximum width in pixels.

    Breaks text into multiple lines that fit within the specified pixel width
    when rendered with the given font. Tries to break at word boundaries.

    Args:
        text: Text to wrap
        max_width: Maximum width in pixels
        font: Pygame font object to measure text width

    Returns:
        List of text lines that fit within max_width

    Examples:
        >>> # Assuming a font object
        >>> wrap_text("Very Long Property Name", 100, font)
        ['Very Long', 'Property Name']
        >>> wrap_text("Short", 100, font)
        ['Short']
    """
    # If text fits, return as single line
    text_surface = font.render(text, True, (0, 0, 0))
    if text_surface.get_width() <= max_width:
        return [text]

    words = text.split()
    lines = []
    current_line = []

    for word in words:
        # Try adding word to current line
        test_line = ' '.join(current_line + [word])
        test_surface = font.render(test_line, True, (0, 0, 0))

        if test_surface.get_width() <= max_width:
            # Word fits on current line
            current_line.append(word)
        else:
            # Word doesn't fit
            if current_line:
                # Save current line and start new one
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                # Single word is too long, need to break it
                # Add it anyway to avoid infinite loop
                current_line.append(word)

    # Add remaining line
    if current_line:
        lines.append(' '.join(current_line))

    return lines
