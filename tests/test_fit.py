from PIL import Image

from aura.render import render


def test_default_size_fits_terminal(monkeypatch):
    monkeypatch.setenv("COLUMNS", "150")
    monkeypatch.setenv("LINES", "45")
    tall = Image.new("RGB", (400, 800), (90, 160, 60))
    lines = render(tall).split("\n")
    assert len(lines) <= 45 - 3 + 1  # leaves room for the prompt


def test_explicit_width_still_wins(monkeypatch):
    monkeypatch.setenv("COLUMNS", "80")
    monkeypatch.setenv("LINES", "30")
    tall = Image.new("RGB", (400, 800), (90, 160, 60))
    assert len(render(tall, width=100).split("\n")) == 100  # 800/400*100*0.5
