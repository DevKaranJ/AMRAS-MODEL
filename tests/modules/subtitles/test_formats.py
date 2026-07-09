# type: ignore
from app.models.subtitles import CaptionStyle, SubtitleSegment
from modules.subtitles.formats import (
    export_to_ass,
    export_to_srt,
    export_to_vtt,
    ms_to_ass_time,
    ms_to_srt_time,
    ms_to_vtt_time,
)


def test_ms_to_srt_time() -> None:
    assert ms_to_srt_time(0) == "00:00:00,000"
    assert ms_to_srt_time(1000) == "00:00:01,000"
    assert ms_to_srt_time(3600000 + 60000 + 1000 + 500) == "01:01:01,500"


def test_ms_to_vtt_time() -> None:
    assert ms_to_vtt_time(0) == "00:00:00.000"
    assert ms_to_vtt_time(1000) == "00:00:01.000"
    assert ms_to_vtt_time(3600000 + 60000 + 1000 + 500) == "01:01:01.500"


def test_ms_to_ass_time() -> None:
    assert ms_to_ass_time(0) == "0:00:00.00"
    assert ms_to_ass_time(1000) == "0:00:01.00"
    assert ms_to_ass_time(3600000 + 60000 + 1000 + 500) == "1:01:01.50"


def test_export_to_srt() -> None:
    segments = [
        SubtitleSegment(sequence_number=1, start_time_ms=0, end_time_ms=1000, text="Hello"),
        SubtitleSegment(sequence_number=2, start_time_ms=1000, end_time_ms=2000, text="World"),
    ]
    srt_out = export_to_srt(segments)
    assert "1" in srt_out
    assert "00:00:00,000 --> 00:00:01,000" in srt_out
    assert "Hello" in srt_out
    assert "2" in srt_out
    assert "00:00:01,000 --> 00:00:02,000" in srt_out
    assert "World" in srt_out


def test_export_to_vtt() -> None:
    segments = [
        SubtitleSegment(sequence_number=1, start_time_ms=0, end_time_ms=1000, text="Hello", speaker="John"),
    ]
    vtt_out = export_to_vtt(segments)
    assert "WEBVTT" in vtt_out
    assert "00:00:00.000 --> 00:00:01.000" in vtt_out
    assert "<v John>Hello" in vtt_out


def test_export_to_ass() -> None:
    segments = [
        SubtitleSegment(sequence_number=1, start_time_ms=0, end_time_ms=1000, text="Hello\nWorld"),
    ]
    style = CaptionStyle(font_family="Arial", font_size=42)
    ass_out = export_to_ass(segments, style)
    assert "[Script Info]" in ass_out
    assert "Style: Default,Arial,42" in ass_out
    assert "Dialogue: 0,0:00:00.00,0:00:01.00,Default,,0,0,0,,Hello\\NWorld" in ass_out
