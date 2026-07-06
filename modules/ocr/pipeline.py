from typing import Any, Dict

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vision import Narration, Panel, SoundEffect, SpeechBubble
from modules.ocr.agents.ocr_agent import OCRAgent, SoundEffectAgent


class OCRPipeline:
    def __init__(self) -> None:
        self.ocr_agent = OCRAgent()
        self.sound_effect_agent = SoundEffectAgent()

    async def execute(self, page_id: int, job_id: int, session: AsyncSession) -> Dict[str, Any]:
        """Runs the OCR pipeline for a page"""
        payload = {"page_id": page_id}

        # We need panel IDs to attach OCR results
        stmt = select(Panel).where(Panel.page_id == page_id)
        result = await session.execute(stmt)
        panels = result.scalars().all()

        if not panels:
            return {"status": "error", "message": "No panels found for page. Run vision pipeline first."}

        panel_id = panels[0].id  # Just use the first one for mocking purposes

        ocr_res = await self.ocr_agent.execute(payload)
        sfx_res = await self.sound_effect_agent.execute(payload)

        for dialogue_data in ocr_res.get("dialogue", []):
            stmt_sb = insert(SpeechBubble).values(
                panel_id=panel_id,
                speaker=dialogue_data["speaker"],
                text=dialogue_data["text"],
                confidence=dialogue_data["confidence"],
                language=dialogue_data["language"],
                bubble_type=dialogue_data["bubble_type"],
            )
            await session.execute(stmt_sb)

        for nar_data in ocr_res.get("narration", []):
            stmt_nar = insert(Narration).values(panel_id=panel_id, text=nar_data["text"], type=nar_data["type"])
            await session.execute(stmt_nar)

        for sfx_data in sfx_res.get("sound_effects", []):
            stmt_sfx = insert(SoundEffect).values(
                panel_id=panel_id,
                text=sfx_data["text"],
                category=sfx_data["category"],
                ignore_for_summary=sfx_data["ignore_for_summary"],
            )
            await session.execute(stmt_sfx)

        await session.commit()

        return {"status": "success", "page_id": page_id, "ocr": ocr_res, "sfx": sfx_res}
