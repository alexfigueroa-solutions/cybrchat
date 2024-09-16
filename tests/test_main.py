import pytest
from cybrchat.main import display_markdown

def test_display_markdown(capsys):
    display_markdown("Test ")
    captured = capsys.readouterr()
    assert "Test" in captured.out
    assert "Copy code (language: python):" in captured.out
    assert "print('Hello')" in captured.out
