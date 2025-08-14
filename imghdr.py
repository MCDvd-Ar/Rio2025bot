# Minimal shim for Python 3.13 where imghdr was removed (PEP 594).
# Our bot doesn't upload images, so basic detection is enough.
def what(file, h=None):
    if h is None:
        try:
            with open(file, "rb") as f:
                h = f.read(32)
        except Exception:
            return None
    if h.startswith(b"\xff\xd8"):
        return "jpeg"
    if h.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if h[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if h.startswith(b"BM"):
        return "bmp"
    return None
