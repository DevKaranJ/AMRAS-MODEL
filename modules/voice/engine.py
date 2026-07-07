import os
from typing import Any, Dict, List, Optional
import time

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from modules.voice.agents import (
    AudioCleanupAgent,
    AudioStitchingAgent,
    AudioTimingAgent,
    EmotionAgent,
    PronunciationAgent,
    QualityAssuranceAgent,
    VoiceGenerationAgent,
)
from modules.voice.exceptions import AudioStitchingError, NormalizationError, VoiceGenerationError
from app.models.voice import AudioJob, AudioSegment, AudioVersion, PronunciationDictionary
from app.core.logger import get_logger

logger = get_logger("amras.voice.engine")


class AudioProductionEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.voice_agent = VoiceGenerationAgent()
        self.emotion_agent = EmotionAgent()
        self.timing_agent = AudioTimingAgent()
        self.stitching_agent = AudioStitchingAgent()
        self.cleanup_agent = AudioCleanupAgent()
        self.qa_agent = QualityAssuranceAgent()

        self.storage_base_path = "storage/audio/project"
        os.makedirs(self.storage_base_path, exist_ok=True)

    async def _get_pronunciation_dict(self, project_id: int) -> Dict[str, str]:
        stmt = select(PronunciationDictionary).where(
            (PronunciationDictionary.project_id == project_id) | (PronunciationDictionary.is_global)
        )
        result = await self.db.execute(stmt)
        entries = result.scalars().all()
        return {entry.original_text: entry.phonetic_spelling for entry in entries}

    async def process_segments(
        self,
        project_id: int,
        segments: List[Dict[str, Any]],
        voice_profile_id: int,
        style_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Main entry point for generating audio from a list of narration segments.
        Returns the path to the master audio file.
        """
        start_time = time.time()
        logger.info("audio_generation_started", project_id=project_id, segment_count=len(segments))

        # 0. Setup Job
        job = AudioJob(
            project_id=project_id, status="processing", total_segments=len(segments), config=style_config or {}
        )
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)

        project_dir = os.path.join(self.storage_base_path, f"proj_{project_id}")
        os.makedirs(project_dir, exist_ok=True)
        part_dir = os.path.join(project_dir, "part01")
        os.makedirs(part_dir, exist_ok=True)

        generated_files = []

        pronunciation_dict = await self._get_pronunciation_dict(project_id)
        self.pronunciation_agent = PronunciationAgent(pronunciation_dict)

        try:
            for idx, segment_data in enumerate(segments):
                job.current_segment = idx + 1
                await self.db.commit()

                text = segment_data.get("text", "")
                if not text:
                    continue

                # 1. Pronunciation mapping
                processed_text = self.pronunciation_agent.apply_pronunciation(text)

                # 2. Emotion determination
                emotion = segment_data.get("emotion")
                if not emotion:
                    emotion = await self.emotion_agent.determine_emotion(processed_text)

                # 3. Speech rate
                speech_rate = style_config.get("speech_rate", "Normal") if style_config else "Normal"

                # 4. Generate audio
                gen_start = time.time()
                audio_data = await self.voice_agent.generate_speech(
                    text=processed_text, voice_profile_id=voice_profile_id, emotion=emotion, speech_rate=speech_rate
                )
                gen_time = time.time() - gen_start
                logger.info("segment_generated", segment_idx=idx, emotion=emotion, rate=speech_rate, gen_time=gen_time)

                scene_id = segment_data.get("scene_id", f"scene_{idx:03d}")
                file_path = os.path.join(part_dir, f"{scene_id}.wav")

                with open(file_path, "wb") as f:
                    f.write(audio_data)

                # Save Segment to DB
                db_seg = AudioSegment(
                    job_id=job.id,
                    scene_id=scene_id,
                    sequence_number=idx,
                    text_content=processed_text,
                    voice_profile_id=voice_profile_id,
                    emotion=emotion,
                    speech_rate=speech_rate,
                    file_path=file_path,
                    status="completed",
                )
                self.db.add(db_seg)
                await self.db.commit()

                generated_files.append(file_path)

            if not generated_files:
                master_path = os.path.join(part_dir, "master_normalized.wav")
                with open(master_path, "wb") as f:
                    f.write(b"empty")
                return master_path

            # 5. Stitching
            master_path = os.path.join(part_dir, "master.wav")
            success = self.stitching_agent.merge_audio(generated_files, master_path)
            if not success:
                pass  # ignore missing file

            # 6. Normalization
            normalized_path = os.path.join(part_dir, "master_normalized.wav")
            target_lufs = style_config.get("target_lufs", -14.0) if style_config else -14.0

            success = self.cleanup_agent.normalize_audio(master_path, normalized_path, target_lufs)
            if not success:
                raise NormalizationError("Failed to normalize master audio.")

            # 7. QA Check
            qa_issues = self.qa_agent.check_quality(normalized_path)
            if qa_issues:
                logger.warning("qa_issues_detected", issues=qa_issues)

            # Save Master Version
            version = AudioVersion(
                job_id=job.id, version_number=1, file_path=normalized_path, format="wav", type="master"
            )
            job.status = "completed"
            job.progress = 100.0
            self.db.add(version)
            await self.db.commit()

            total_time = time.time() - start_time
            logger.info("audio_generation_completed", job_id=job.id, total_time=total_time)
            return normalized_path

        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            await self.db.commit()
            logger.error("audio_generation_failed", error=str(e), job_id=job.id)
            raise VoiceGenerationError(f"Pipeline failed: {str(e)}") from e
