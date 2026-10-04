"""Run: python3 test_busy_tube.py  (no dependencies needed)"""
import busy_tube as bt

FEED = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns:media="http://search.yahoo.com/mrss/"
      xmlns="http://www.w3.org/2005/Atom">
 <title>Some Channel</title>
 <entry>
  <yt:videoId>AAA</yt:videoId><title>New</title><published>2026-10-03T10:00:00+00:00</published>
  <media:group><media:description>desc A</media:description></media:group>
 </entry>
 <entry>
  <yt:videoId>BBB</yt:videoId><title>Old</title><published>2026-10-01T10:00:00+00:00</published>
  <media:group><media:description>desc B</media:description></media:group>
 </entry>
</feed>"""

CID = "UC_x5XG1OV2P6uZZ5FSM9Ttw"


def test_parse_channel_id():
    assert bt.parse_channel_id(f'..."externalId":"{CID}",...') == CID
    assert bt.parse_channel_id(f'<link rel="canonical" href="https://www.youtube.com/channel/{CID}">') == CID
    assert bt.parse_channel_id(f'{{"channelId":"{CID}"}}') == CID
    assert bt.parse_channel_id("<html>nothing</html>") is None


def test_parse_feed_and_select_new():
    channel, videos = bt.parse_feed(FEED)
    assert channel == "Some Channel"
    assert [v["id"] for v in videos] == ["AAA", "BBB"]
    assert videos[0]["published"] == "2026-10-03"
    assert videos[0]["url"].endswith("v=AAA")
    assert videos[1]["description"] == "desc B"
    assert [v["id"] for v in bt.select_new(videos, {"AAA"}, 3)] == ["BBB"]
    assert [v["id"] for v in bt.select_new(videos, set(), 1)] == ["AAA"]


def test_group_segments():
    segs = [(0, "a"), (10, "b"), (31, "c"), (3700, "d"), (3701, " ")]
    assert bt.group_segments(segs) == "[0:00] a b\n[0:31] c\n[1:01:40] d"
    assert bt.group_segments([(0, "はい。"), (1, "はい。"), (2, "はい。"), (3, "x")]) == "[0:00] はい。 x"


def test_run_engines_falls_through():
    def boom(v, c):
        raise RuntimeError("HTTP 429: quota")

    engines = {
        "gemini": (lambda: None, boom),
        "groq": (lambda: "GROQ_API_KEY not set", None),
        "whisper": (lambda: None, lambda v, c: ""),
        "captions": (lambda: None, lambda v, c: "[0:00] hello"),
    }
    name, text, errors = bt.run_engines({}, {}, engines, ["gemini", "groq", "whisper", "captions"])
    assert (name, text) == ("captions", "[0:00] hello")
    assert len(errors) == 3 and "429" in errors[0] and "skipped" in errors[1]

    name, _, errors = bt.run_engines({}, {}, engines, ["gemini", "groq"])
    assert name is None and len(errors) == 2


if __name__ == "__main__":
    for fn in [v for k, v in dict(globals()).items() if k.startswith("test_")]:
        fn()
        print("ok", fn.__name__)
