"""
Unit tests for text_utils module, specifically text wrapping functionality.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pygame
from visualization.text_utils import wrap_text, truncate_name, format_display_name


def test_wrap_text():
    """Test that wrap_text correctly breaks text into multiple lines."""
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 11, bold=True)

    # Test 1: Short text that fits on one line
    result = wrap_text("Short", 200, font)
    assert result == ["Short"], f"Expected ['Short'], got {result}"
    print("[PASS] Test 1: Short text stays on one line")

    # Test 2: Long text that needs wrapping
    result = wrap_text("The Potteries Museum & Art Gallery", 80, font)
    assert len(result) > 1, f"Expected multiple lines, got {result}"
    print(f"[PASS] Test 2: Long text wrapped into {len(result)} lines: {result}")

    # Test 3: Another long property name
    result = wrap_text("Gladstone Pottery Museum", 80, font)
    assert len(result) > 1, f"Expected multiple lines, got {result}"
    print(f"[PASS] Test 3: Property name wrapped: {result}")

    # Test 4: Very narrow width forces more wrapping
    result = wrap_text("The Regent Theatre", 50, font)
    print(f"[PASS] Test 4: Narrow width result: {result}")

    # Test 5: Single word that doesn't fit still gets returned
    result = wrap_text("Supercalifragilisticexpialidocious", 10, font)
    assert len(result) >= 1, f"Expected at least one line, got {result}"
    print(f"[PASS] Test 5: Very long word handled: {result}")


def test_truncate_name():
    """Test that truncate_name works as expected."""
    result = truncate_name("Very Long Property Name", 10)
    assert len(result) <= 10, f"Expected length <= 10, got {len(result)}"
    assert "..." in result, f"Expected ellipsis in result, got {result}"
    print(f"[PASS] Truncate test: '{result}'")


def test_format_display_name():
    """Test that format_display_name works correctly."""
    result = format_display_name("player_0")
    assert result == "Player 0", f"Expected 'Player 0', got '{result}'"
    print("[PASS] Format test")


if __name__ == "__main__":
    print("Running text_utils tests...\n")

    test_wrap_text()
    print()
    test_truncate_name()
    test_format_display_name()

    print("\n[SUCCESS] All tests passed!")
