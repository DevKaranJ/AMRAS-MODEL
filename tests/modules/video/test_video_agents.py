import pytest

from modules.video.agents.animation_agent import AnimationAgent, AnimationInput
from modules.video.agents.composition_agent import CompositionAgent, CompositionInput
from modules.video.agents.encoding_agent import EncodingAgent, EncodingInput
from modules.video.agents.qa_agent import QAAgent, QAInput
from modules.video.agents.render_manager import RenderManagerAgent, RenderManagerInput
from modules.video.agents.resource_manager import ResourceManagementAgent
from modules.video.agents.scene_renderer import SceneRendererAgent, SceneRendererInput
from modules.video.agents.transition_agent import TransitionAgent, TransitionInput


@pytest.mark.asyncio
async def test_render_manager_agent() -> None:
    agent = RenderManagerAgent()
    input_data = RenderManagerInput(job_id=1, action="start")
    result = await agent.execute(input_data)
    assert result.status == "queued"
    assert result.job_id == 1


@pytest.mark.asyncio
async def test_scene_renderer_agent() -> None:
    agent = SceneRendererAgent()
    input_data = SceneRendererInput(scene_id=1, timeline_data={})
    result = await agent.execute(input_data)
    assert result.status == "completed"
    assert result.scene_id == 1


@pytest.mark.asyncio
async def test_transition_agent() -> None:
    agent = TransitionAgent()
    input_data = TransitionInput(
        transition_type="crossfade", scene_a_path="a.mp4", scene_b_path="b.mp4", duration_ms=1000
    )
    result = await agent.execute(input_data)
    assert result.status == "completed"


@pytest.mark.asyncio
async def test_animation_agent() -> None:
    agent = AnimationAgent()
    input_data = AnimationInput(animation_type="pan", start_params={}, end_params={}, duration_ms=2000)
    result = await agent.execute(input_data)
    assert result.status == "success"


@pytest.mark.asyncio
async def test_composition_agent() -> None:
    agent = CompositionAgent()
    input_data = CompositionInput(panel_paths=["p1.png"], background_path=None, safe_margins={})
    result = await agent.execute(input_data)
    assert result.status == "success"


@pytest.mark.asyncio
async def test_encoding_agent() -> None:
    agent = EncodingAgent()
    input_data = EncodingInput(
        input_path="in.mp4", output_path="out.mp4", codec="H.264", format="mp4", resolution="1080p", fps=60
    )
    result = await agent.execute(input_data)
    assert result.status == "completed"


@pytest.mark.asyncio
async def test_resource_manager_agent() -> None:
    agent = ResourceManagementAgent()
    status = await agent.get_system_status()
    assert status.cpu_usage_percent >= 0.0


@pytest.mark.asyncio
async def test_qa_agent() -> None:
    agent = QAAgent()
    input_data = QAInput(video_path="test.mp4", expected_duration_ms=60000, expected_fps=60.0)
    result = await agent.execute(input_data)
    assert result.passed is True
