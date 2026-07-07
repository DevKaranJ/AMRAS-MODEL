from app.core.exceptions import AmrasException, ConfigurationError, DatabaseError


def test_base_exception_to_dict() -> None:
    exc = AmrasException(
        message="A base error",
        error_code="TEST_CODE",
        retryable=True,
        recovery_suggestion="Try again",
        debug_details={"info": "debug"},
    )
    exc_dict = exc.to_dict()
    assert exc_dict["error_code"] == "TEST_CODE"
    assert exc_dict["message"] == "A base error"
    assert exc_dict["retryable"] is True
    assert exc_dict["recovery_suggestion"] == "Try again"
    # Debug details are intentionally omitted from to_dict for user safety


def test_specific_exceptions() -> None:
    db_exc = DatabaseError("DB failed")
    assert db_exc.error_code == "DATABASE_ERROR"
    assert db_exc.retryable is True

    cfg_exc = ConfigurationError("Config invalid")
    assert cfg_exc.error_code == "CONFIG_ERROR"
    assert cfg_exc.retryable is False
