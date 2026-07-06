from modules.vision.preprocessing import preprocess_pipeline


def test_preprocess_pipeline() -> None:
    res = preprocess_pipeline("test.png")
    assert res == "test.png"
