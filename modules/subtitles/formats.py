from typing import List

from app.models.subtitles import CaptionStyle, SubtitleSegment


def ms_to_srt_time(ms: int) -> str:
    """Converts milliseconds to SRT time format: HH:MM:SS,mmm"""
    seconds, milliseconds = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def ms_to_vtt_time(ms: int) -> str:
    """Converts milliseconds to VTT time format: HH:MM:SS.mmm"""
    seconds, milliseconds = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


def ms_to_ass_time(ms: int) -> str:
    """Converts milliseconds to ASS time format: H:MM:SS.cc"""
    seconds, milliseconds = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    centiseconds = milliseconds // 10
    return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"


def export_to_srt(segments: List[SubtitleSegment]) -> str:
    """Exports subtitle segments to SRT format."""
    lines = []
    for seg in sorted(segments, key=lambda x: x.start_time_ms):
        start = ms_to_srt_time(seg.start_time_ms)
        end = ms_to_srt_time(seg.end_time_ms)
        lines.append(str(seg.sequence_number))
        lines.append(f"{start} --> {end}")
        lines.append(seg.text)
        lines.append("")
    return "\n".join(lines)


def export_to_vtt(segments: List[SubtitleSegment]) -> str:
    """Exports subtitle segments to VTT format."""
    lines = ["WEBVTT", ""]
    for seg in sorted(segments, key=lambda x: x.start_time_ms):
        start = ms_to_vtt_time(seg.start_time_ms)
        end = ms_to_vtt_time(seg.end_time_ms)
        lines.append(str(seg.sequence_number))
        lines.append(f"{start} --> {end}")
        if seg.speaker:
            lines.append(f"<v {seg.speaker}>{seg.text}")
        else:
            lines.append(seg.text)
        lines.append("")
    return "\n".join(lines)


def export_to_ass(segments: List[SubtitleSegment], style: CaptionStyle | None = None) -> str:
    """Exports subtitle segments to ASS format with optional styling."""
    font_name = style.font_family if style else "Arial"
    font_size = style.font_size if style else 42

    # basic header
    lines = [
        "[Script Info]",
        "Title: AMRAS Generated Subtitles",
        "ScriptType: v4.00+",
        "WrapStyle: 0",
        "ScaledBorderAndShadow: yes",
        "YCbCr Matrix: None",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Default,{font_name},{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    for seg in sorted(segments, key=lambda x: x.start_time_ms):
        start = ms_to_ass_time(seg.start_time_ms)
        end = ms_to_ass_time(seg.end_time_ms)
        # Handle line breaks in ASS
        text = seg.text.replace("\n", "\\N")
        lines.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")

    return "\n".join(lines)
