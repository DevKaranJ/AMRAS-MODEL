from modules.timeline.agents.audio_sync import AudioSynchronizationAgent
from modules.timeline.agents.camera_director import CameraDirectorAgent
from modules.timeline.agents.motion_planning import MotionPlanningAgent
from modules.timeline.agents.panel_selection import PanelSelectionAgent
from modules.timeline.agents.planning import TimelinePlanningAgent
from modules.timeline.agents.quality_assurance import QualityAssuranceAgent
from modules.timeline.agents.reading_flow import ReadingFlowAgent
from modules.timeline.agents.scene_composition import SceneCompositionAgent


class TestAgents:
    def test_planning_agent(self) -> None:
        agent = TimelinePlanningAgent()
        timeline = agent.create_initial_timeline(project_id=1, settings={})
        assert timeline.project_id == 1
        scenes = agent.plan_scenes(1, [{"id": 1}], [{"id": 10}])
        assert len(scenes) == 1

    def test_panel_selection_agent(self) -> None:
        agent = PanelSelectionAgent()
        panels = agent.select_panels(1, {"panels": [{"id": 1, "is_action": True}]}, 1000)
        assert len(panels) == 1
        assert panels[0].importance_score > 0.5
        assert agent.select_panels(1, {}, 1000) == []

    def test_camera_director_agent(self) -> None:
        agent = CameraDirectorAgent()
        path = agent.plan_camera_movement({"is_battle": True}, 1000)
        assert path.type == "aggressive_zoom"
        path = agent.plan_camera_movement({"emotion": "sad"}, 1000)
        assert path.type == "slow_zoom"
        path = agent.plan_camera_movement({}, 1000)
        assert path.type == "static"

    def test_scene_composition_agent(self) -> None:
        agent = SceneCompositionAgent()
        metadata = agent.analyze_scene({}, [])
        assert metadata.emotion == "neutral"
        crop = agent.calculate_safe_crop({})
        assert crop["w"] == 1.0

    def test_audio_sync_agent(self) -> None:
        agent = AudioSynchronizationAgent()
        syncs = agent.synchronize(
            [{"id": 1, "start_time_ms": 0, "end_time_ms": 500, "duration_ms": 500}], [{"id": 1, "duration_ms": 1000}]
        )
        assert len(syncs) == 1
        assert syncs[0].end_time_ms == 1000

        syncs = agent.synchronize([{"id": 1, "start_time_ms": 0, "end_time_ms": 500}], [])
        assert syncs == []

    def test_reading_flow_agent(self) -> None:
        agent = ReadingFlowAgent()
        panels = [{"id": 1, "x": 0, "y": 10}, {"id": 2, "x": 10, "y": 0}]
        r2l = agent.order_panels(panels, "right-to-left")
        assert r2l[0]["id"] == 2
        l2r = agent.order_panels(panels, "left-to-right")
        assert l2r[0]["id"] == 2
        assert agent.order_panels([], "right-to-left") == []

    def test_motion_planning_agent(self) -> None:
        agent = MotionPlanningAgent()
        t1 = agent.plan_transition({"metadata": {"emotion": "happy"}}, {"metadata": {"emotion": "sad"}})
        assert t1.type == "fade"
        t2 = agent.plan_transition({"metadata": {"emotion": "happy"}}, {"metadata": {"emotion": "happy"}})
        assert t2.type == "cut"

    def test_qa_agent(self) -> None:
        agent = QualityAssuranceAgent()
        issues = agent.audit_timeline({"scenes": [{"id": 1, "duration_ms": 100}]})
        assert len(issues) == 1
        assert issues[0]["issue_type"] == "fast_cut"

        issues = agent.audit_timeline({"scenes": [{"id": 1, "duration_ms": 40000}]})
        assert len(issues) == 1
        assert issues[0]["issue_type"] == "slow_scene"
