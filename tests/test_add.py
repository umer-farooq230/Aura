from PIL import Image, ImageDraw

from aura import registry
from aura.addimg import add_pictures, ahash, is_duplicate, trim_border
from aura.cli import main


def _framed(size=200, pad=40, inner=(200, 40, 40)):
    im = Image.new("RGB", (size, size), (255, 255, 255))
    ImageDraw.Draw(im).rectangle((pad, pad, size - pad, size - pad), fill=inner)
    return im


def test_trim_removes_plain_border():
    out = trim_border(_framed())
    assert out.size[0] < 200 and out.size[1] < 200


def test_trim_leaves_busy_pictures_alone():
    im = Image.effect_noise((100, 100), 80).convert("RGB")
    assert trim_border(im).size == im.size


def test_duplicate_detection():
    a = _framed()
    assert is_duplicate(ahash(a), ahash(a.resize((120, 120))))
    assert not is_duplicate(ahash(a), ahash(Image.effect_noise((200, 200), 90).convert("RGB")))


def test_add_numbers_and_skips_duplicates(tmp_path, monkeypatch):
    monkeypatch.setenv("AURA_HOME", str(tmp_path / "home"))
    src = tmp_path / "pic.png"
    _framed().save(src)

    target = registry.user_dir()
    assert add_pictures("goku", [str(src)], target, existing={}) == 1
    assert (target / "goku_1.png".replace(".png", ".jpg")).exists()

    # same picture again -> skipped
    found = registry.discover()
    assert list(found["goku"]) == [1]
    assert add_pictures("goku", [str(src)], target, existing=found["goku"]) == 0


def test_user_pictures_never_overwrite_bundled(tmp_path, monkeypatch):
    monkeypatch.setenv("AURA_HOME", str(tmp_path))
    d = tmp_path / "images"
    d.mkdir()
    _framed().save(d / "piccolo_1.jpg")  # same number as a bundled one, if any exist
    found = registry.discover()
    assert len(found["piccolo"]) == len(set(found["piccolo"]))


def test_cli_add_then_show(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("AURA_HOME", str(tmp_path / "home"))
    src = tmp_path / "x.png"
    _framed().save(src)
    assert main(["add", "zed", str(src)]) == 0
    capsys.readouterr()
    assert main(["--zed", "-1", "--width", "30"]) == 0
    assert len(capsys.readouterr().out.strip().splitlines()) > 5
    assert main(["--file", str(src), "--width", "30"]) == 0
