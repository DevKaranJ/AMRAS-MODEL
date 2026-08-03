"""Consolidated story analysis - 1 LLM call instead of 7."""

import json
from typing import Any, Dict, List, Optional

from app.core.logger import get_logger
from app.shared.providers.base import ai_provider_manager, ensure_providers_registered

logger = get_logger("amras.story.consolidated")

SYSTEM_PROMPT = """You are an expert manga analyst. Given OCR text and panel descriptions from a manga chapter, extract a complete story analysis as JSON.

Return ONLY valid JSON with this exact structure:
{
  "title": "chapter title or summary",
  "synopsis": "2-3 sentence summary",
  "scenes": [
    {
      "scene_number": 1,
      "panels": [1, 2, 3],
      "description": "what happens in this scene",
      "emotion": "tension|romance|action|humor|drama|mystery|calm",
      "characters_present": ["character names"],
      "location": "where this takes place",
      "dialogue_summary": "key dialogue or narration"
    }
  ],
  "characters": [
    {
      "name": "Character Name",
      "role": "protagonist|antagonist|supporting|background",
      "description": "appearance and personality",
      "first_appearance_panel": 1
    }
  ],
  "events": [
    {
      "event_number": 1,
      "description": "what happens",
      "panel_start": 1,
      "panel_end": 5,
      "importance": "major|minor|incidental",
      "emotional_impact": "high|medium|low"
    }
  ],
  "relationships": [
    {
      "character_a": "Name",
      "character_b": "Name",
      "type": "romantic|family|rivalry|friendship|authority|unknown",
      "description": "nature of relationship"
    }
  ],
  "timeline": [
    {
      "time_reference": "then|now|flashback|future",
      "events": ["event descriptions"]
    }
  ],
  "locations": [
    {
      "name": "Location Name",
      "description": "what it looks like",
      "significance": "plot relevance"
    }
  ],
  "world_building": {
    "time_period": "when this takes place",
    "setting": "type of world/setting",
    "tone": "overall tone",
    "themes": ["main themes"]
  },
  "narration_style": {
    "recommended_tone": "descriptive|dramatic|intimate|energetic",
    "pacing": "slow|medium|fast",
    "key_moments": ["moments worth emphasizing in narration"]
  }
}"""


async def analyze_story_consolidated(
    ocr_text: str,
    panels: List[Dict[str, Any]],
    chapter_number: int = 1,
) -> Dict[str, Any]:
    """Single LLM call that does story + character + event + relationship + timeline + world analysis."""

    ensure_providers_registered()

    # Build compact input
    panel_summaries = []
    for i, panel in enumerate(panels[:30], 1):  # Cap at 30 panels to save tokens
        bbox = panel.get("bounding_box", {})
        scene_type = panel.get("scene_type", "normal")
        speech = panel.get("speech_bubbles", [])
        dialogue = " ".join([s.get("text", "") for s in speech[:3]])  # Max 3 bubbles
        panel_summaries.append(
            f"Panel {i}: [{scene_type}] {dialogue[:200]}"
        )

    user_prompt = f"""Chapter {chapter_number} Analysis

OCR Text (may be noisy):
{ocr_text[:3000]}

Panel Descriptions ({len(panel_summaries)} panels):
{chr(10).join(panel_summaries)}

Analyze this manga chapter and return the complete JSON structure."""

    try:
        result_str = await ai_provider_manager.generate_text(
            prompt=user_prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=4000,
        )

        # Parse JSON from response
        try:
            result = _parse_json_response(result_str)
        except Exception as parse_err:
            logger.warning("json_parse_failed", error=str(parse_err), response_preview=result_str[:200])
            result = _fallback_analysis(ocr_text, panels, chapter_number)

        logger.info(
            "consolidated_analysis_complete",
            scenes=len(result.get("scenes", [])),
            characters=len(result.get("characters", [])),
        )
        return result

    except Exception as e:
        logger.error("consolidated_analysis_failed", error=str(e))
        return _fallback_analysis(ocr_text, panels, chapter_number)


async def generate_narration_consolidated(
    story_analysis: Dict[str, Any],
    style: str = "narration",
    max_duration_minutes: int = 8,
) -> Dict[str, Any]:
    """Single LLM call that generates full narration script from story analysis."""

    ensure_providers_registered()

    # Build compact input from story analysis
    scenes = story_analysis.get("scenes", [])
    characters = story_analysis.get("characters", [])
    synopsis = story_analysis.get("synopsis", "")

    scene_briefs = []
    for s in scenes[:15]:  # Cap scenes
        scene_briefs.append(
            f"Scene {s.get('scene_number', '?')}: {s.get('description', '')} "
            f"[{s.get('emotion', 'neutral')}] Characters: {', '.join(s.get('characters_present', []))}"
        )

    char_list = [f"{c['name']} ({c.get('role', 'unknown')})" for c in characters[:10]]

    system_prompt = """You are a professional manga recap narrator for YouTube. Your voice is engaging, dramatic, and makes viewers feel like they're experiencing the story live.

Create a narration script that would work for a YouTube manga recap video.

Return ONLY valid JSON:
{
  "title": "catchy YouTube video title",
  "opening_hook": "attention-grabbing first sentence that makes viewers stay",
  "segments": [
    {
      "segment_number": 1,
      "text": "narration text (2-3 short sentences, max 40 words per sentence)",
      "scene_reference": "which scene",
      "emotion": "tone of voice",
      "estimated_duration_seconds": 15,
      "visual_cue": "what manga panels to show"
    }
  ],
  "closing": "wrap-up that encourages likes/subscribes",
  "total_estimated_duration_seconds": 300,
  "word_count": 600
}

CRITICAL RULES:
- Write in PRESENT TENSE: "we see", "she walks", "he draws his sword"
- Each segment text must be 2-3 SHORT sentences (max 80 words total per segment)
- Make it DRAMATIC - use vivid descriptions, emotional language
- Hook viewers immediately - no boring introductions
- Reference specific visual moments from the panels
- Match the manga's emotion (romance, action, drama, etc.)
- Target {target_seconds} seconds total (roughly {target_words} words)
- End each segment at a natural pause point for TTS

    user_prompt = f"""Manga Recap Narration

Story Synopsis: {synopsis}

Characters: {', '.join(char_list)}

Scenes ({len(scene_briefs)} total):
{chr(10).join(scene_briefs)}

Style: {style}
Target duration: ~{max_duration_minutes * 60} seconds
Target word count: ~{max_duration_minutes * 130} words

Create the complete narration script. Make it dramatic and engaging for YouTube viewers."""

    try:
        result_str = await ai_provider_manager.generate_text(
            prompt=user_prompt,
            system_prompt=system_prompt.format(
                target_seconds=max_duration_minutes * 60,
                target_words=max_duration_minutes * 130,
            ),
            temperature=0.7,
            max_tokens=3000,
        )

        result = _parse_json_response(result_str)
        logger.info(
            "narration_generated",
            segments=len(result.get("segments", [])),
            duration=result.get("total_estimated_duration_seconds", 0),
        )
        return result

    except Exception as e:
        logger.error("narration_generation_failed", error=str(e))
        return _fallback_narration(story_analysis)


def _parse_json_response(text: str) -> Dict[str, Any]:
    """Extract JSON from LLM response, handling markdown code blocks and special chars."""
    import re

    text = text.strip()

    # Remove markdown code block
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)

    # Aggressively replace ALL non-ASCII chars
    text = text.encode("ascii", "ignore").decode("ascii")

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object in text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError as e:
                # Try to fix common issues
                json_str = text[start:end]
                # Remove any remaining non-printable chars
                json_str = re.sub(r'[^\x20-\x7E]', '', json_str)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
        raise ValueError(f"Could not parse JSON from LLM response: {text[:300]}")


def _fallback_analysis(
    ocr_text: str, panels: List[Dict[str, Any]], chapter_number: int
) -> Dict[str, Any]:
    """Fallback analysis without LLM - basic heuristics."""
    scenes = []
    panel_count = len(panels)

    # Split panels into groups of 5-8 for scenes
    scene_size = max(3, panel_count // max(1, panel_count // 6))
    for i in range(0, panel_count, scene_size):
        chunk = panels[i : i + scene_size]
        scenes.append({
            "scene_number": len(scenes) + 1,
            "panels": list(range(i + 1, min(i + scene_size + 1, panel_count + 1))),
            "description": f"Scene covering panels {i+1}-{min(i+scene_size, panel_count)}",
            "emotion": "neutral",
            "characters_present": [],
            "location": "unknown",
            "dialogue_summary": "",
        })

    return {
        "title": f"Chapter {chapter_number}",
        "synopsis": ocr_text[:300] if ocr_text else f"Manga chapter {chapter_number} with {panel_count} pages",
        "scenes": scenes,
        "characters": [],
        "events": [],
        "relationships": [],
        "timeline": [],
        "locations": [],
        "world_building": {"time_period": "unknown", "setting": "unknown", "tone": "neutral", "themes": []},
        "narration_style": {"recommended_tone": "descriptive", "pacing": "medium", "key_moments": []},
    }


def _fallback_narration(story_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback narration without LLM - template-based."""
    synopsis = story_analysis.get("synopsis", "This manga chapter tells an interesting story.")
    scenes = story_analysis.get("scenes", [])

    segments = []
    for i, scene in enumerate(scenes[:10], 1):
        desc = scene.get("description", "")
        emotion = scene.get("emotion", "neutral")
        segments.append({
            "segment_number": i,
            "text": f"In this scene, {desc.lower()}" if desc else f"Moving on to the next part of the story.",
            "scene_reference": f"Scene {i}",
            "emotion": emotion,
            "estimated_duration_seconds": 15,
            "visual_cue": f"Show panels for scene {i}",
        })

    if not segments:
        segments.append({
            "segment_number": 1,
            "text": synopsis,
            "scene_reference": "Overall",
            "emotion": "neutral",
            "estimated_duration_seconds": 20,
            "visual_cue": "Show chapter pages",
        })

    total_seconds = sum(s["estimated_duration_seconds"] for s in segments)

    return {
        "title": story_analysis.get("title", "Manga Recap"),
        "opening_hook": "Welcome back to another manga recap!",
        "segments": segments,
        "closing": "That's it for this chapter! Like and subscribe for more!",
        "total_estimated_duration_seconds": total_seconds,
        "word_count": sum(len(s["text"].split()) for s in segments),
    }
