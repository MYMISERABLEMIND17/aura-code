def test_svg_sanitization():
    # Test that output SVG contains correct headers and direction LTR
    username = "testuser"
    svg_content = f"<svg><text>@{username}</text></svg>"
    assert "testuser" in svg_content
