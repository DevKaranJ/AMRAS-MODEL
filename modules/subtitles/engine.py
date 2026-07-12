from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import async_session_maker
from app.models.subtitles import LocalizationProfile, SubtitleJob, SubtitleLanguage, SubtitleSegment, TranslationJob
from modules.subtitles.exceptions import SubtitleEngineError


class SubtitleEngine:
    """Orchestrates Subtitle Generation, Translation, and QA processes."""

    def __init__(self, db_session: AsyncSession | None = None):
        self._db_session = db_session

    async def get_db(self) -> AsyncSession:
        if self._db_session:
            return self._db_session
        return async_session_maker()

    async def get_subtitle_job(self, job_id: int) -> SubtitleJob | None:
        db = await self.get_db()
        try:
            result = await db.execute(select(SubtitleJob).where(SubtitleJob.id == job_id))
            return result.scalar_one_or_none()
        finally:
            if not self._db_session:
                await db.close()

    async def get_translation_job(self, job_id: int) -> TranslationJob | None:
        db = await self.get_db()
        try:
            result = await db.execute(select(TranslationJob).where(TranslationJob.id == job_id))
            return result.scalar_one_or_none()
        finally:
            if not self._db_session:
                await db.close()

    async def create_subtitle_job(
        self, project_id: int, timeline_id: int, language_id: int, settings: Dict[str, Any]
    ) -> SubtitleJob:
        db = await self.get_db()
        job = SubtitleJob(
            project_id=project_id,
            timeline_id=timeline_id,
            language_id=language_id,
            status="pending",
            settings=settings,
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        if not self._db_session:
            await db.close()
        return job

    async def generate_subtitles(
        self, job_id: int, narration_script: str, audio_timestamps: List[Dict[str, Any]]
    ) -> None:
        from modules.subtitles.agents import QAAgent, SubtitleGenerationAgent, SynchronizationAgent

        db = await self.get_db()
        result = await db.execute(select(SubtitleJob).where(SubtitleJob.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            if not self._db_session:
                await db.close()
            return

        job.status = "generating"
        await db.commit()

        try:
            gen_agent = SubtitleGenerationAgent()
            sync_agent = SynchronizationAgent()
            qa_agent = QAAgent()

            # Generate initial segments
            gen_payload = {"narration_script": narration_script, "settings": job.settings}
            gen_result = await gen_agent.execute(gen_payload)
            segments = gen_result.get("segments", [])

            # Synchronize segments with audio
            sync_payload = {"segments": segments, "audio_timestamps": audio_timestamps}
            sync_result = await sync_agent.execute(sync_payload)
            sync_segments = sync_result.get("synchronized_segments", [])

            # Run QA
            qa_payload = {"segments": sync_segments}
            qa_result = await qa_agent.execute(qa_payload)

            if not qa_result.get("passed"):
                issues = qa_result.get("issues", [])
                issues_summary = "; ".join(issues[:5])
                job.error_message = f"QA failed: {issues_summary}"
                job.status = "failed"
                await db.commit()
                if not self._db_session:
                    await db.close()
                return

            # Save segments to database
            db_segments = []
            for i, seg in enumerate(qa_result.get("qa_segments", [])):
                db_seg = SubtitleSegment(
                    subtitle_job_id=job.id,
                    sequence_number=i + 1,
                    start_time_ms=seg.get("start_time_ms", 0),
                    end_time_ms=seg.get("end_time_ms", 0),
                    duration_ms=seg.get("duration_ms", 0),
                    text=seg.get("text", ""),
                    speaker=seg.get("speaker", None),
                    confidence=seg.get("confidence", 1.0),
                )
                db_segments.append(db_seg)

            db.add_all(db_segments)
            job.status = "completed"
            job.progress = 100.0
            await db.commit()

        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            await db.commit()
            raise e
        finally:
            if not self._db_session:
                await db.close()

    async def translate_subtitles(self, translation_job_id: int) -> None:
        db = await self.get_db()
        t_job = await self.get_translation_job(translation_job_id)
        if not t_job:
            if not self._db_session:
                await db.close()
            return

        t_job.status = "translating"
        await db.commit()

        try:
            source_segments = await self._fetch_source_segments(db, t_job.subtitle_job_id)
            target_lang = await self._fetch_target_language(db, t_job.target_language_id)

            translated_segs = await self._execute_translation_pipeline(db, t_job, source_segments, target_lang)

            await self._save_translated_segments(db, t_job, source_segments, translated_segs)

            t_job.status = "completed"
            t_job.progress = 100.0
            await db.commit()
        except Exception as e:
            t_job.status = "failed"
            t_job.error_message = str(e)
            await db.commit()
            raise e
        finally:
            if not self._db_session:
                await db.close()

    async def _fetch_source_segments(self, db: AsyncSession, subtitle_job_id: int) -> List[SubtitleSegment]:
        result = await db.execute(
            select(SubtitleSegment)
            .where(SubtitleSegment.subtitle_job_id == subtitle_job_id)
            .order_by(SubtitleSegment.sequence_number)
        )
        source_segments = result.scalars().all()
        if not source_segments:
            raise SubtitleEngineError("No source segments found for translation.")
        return list(source_segments)

    async def _fetch_target_language(self, db: AsyncSession, target_language_id: int) -> SubtitleLanguage:
        lang_result = await db.execute(select(SubtitleLanguage).where(SubtitleLanguage.id == target_language_id))
        target_lang = lang_result.scalar_one_or_none()
        if not target_lang:
            raise SubtitleEngineError("Target language not found.")
        return target_lang

    async def _execute_translation_pipeline(
        self,
        db: AsyncSession,
        t_job: TranslationJob,
        source_segments: List[SubtitleSegment],
        target_lang: SubtitleLanguage,
    ) -> List[Dict[str, Any]]:
        from modules.subtitles.agents import FormattingAgent, LocalizationAgent, TranslationAgent

        trans_agent = TranslationAgent()
        local_agent = LocalizationAgent()
        form_agent = FormattingAgent()

        segs_dict = [{"text": s.text} for s in source_segments]

        # Translation
        t_payload = {"segments": segs_dict, "target_language": target_lang.name}
        t_result = await trans_agent.execute(t_payload)
        translated_segs = t_result.get("translated_segments", [])

        # Localization
        translated_segs = await self._apply_localization(db, t_job, local_agent, translated_segs)

        # Formatting
        f_payload = {"segments": translated_segs, "settings": {"max_lines": 2, "max_characters_per_line": 42}}
        f_result = await form_agent.execute(f_payload)
        result: List[Dict[str, Any]] = f_result.get("formatted_segments", translated_segs)
        return result

    async def _apply_localization(
        self, db: AsyncSession, t_job: TranslationJob, local_agent: Any, translated_segs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        if not t_job.localization_profile_id:
            return translated_segs

        profile_result = await db.execute(
            select(LocalizationProfile).where(LocalizationProfile.id == t_job.localization_profile_id)
        )
        profile = profile_result.scalar_one_or_none()
        if profile:
            profile_dict = {
                "id": profile.id,
                "name": profile.name,
                "honorifics_strategy": profile.honorifics_strategy,
                "measurements_strategy": profile.measurements_strategy,
                "currency_strategy": profile.currency_strategy,
                "rules": profile.rules,
            }
            l_payload = {"segments": translated_segs, "profile": profile_dict}
            l_result = await local_agent.execute(l_payload)
            result: List[Dict[str, Any]] = l_result.get("localized_segments", translated_segs)
            return result
        return translated_segs

    async def _save_translated_segments(
        self,
        db: AsyncSession,
        t_job: TranslationJob,
        source_segments: List[SubtitleSegment],
        final_segs: List[Dict[str, Any]],
    ) -> None:
        if not t_job.subtitle_job:
            raise SubtitleEngineError("Translation job has no associated subtitle job")
        new_job = SubtitleJob(
            project_id=t_job.subtitle_job.project_id,
            timeline_id=t_job.subtitle_job.timeline_id,
            language_id=t_job.target_language_id,
            status="completed",
            progress=100.0,
        )
        db.add(new_job)
        await db.flush()

        db_segments = []
        for i, src_seg in enumerate(source_segments):
            text = final_segs[i].get("text", "") if i < len(final_segs) else src_seg.text
            db_seg = SubtitleSegment(
                subtitle_job_id=new_job.id,
                sequence_number=src_seg.sequence_number,
                start_time_ms=src_seg.start_time_ms,
                end_time_ms=src_seg.end_time_ms,
                duration_ms=src_seg.duration_ms,
                text=text,
                speaker=src_seg.speaker,
                confidence=1.0,
            )
            db_segments.append(db_seg)

        db.add_all(db_segments)
