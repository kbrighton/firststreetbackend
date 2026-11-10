from config import (
    DevelopmentConfig,
    ProductionConfig,
    StagingConfig,
    TestingConfig,
)


def test_query_recording_is_enabled_only_for_development_and_tests():
    assert DevelopmentConfig.SQLALCHEMY_RECORD_QUERIES is True
    assert TestingConfig.SQLALCHEMY_RECORD_QUERIES is True
    assert ProductionConfig.SQLALCHEMY_RECORD_QUERIES is False
    assert StagingConfig.SQLALCHEMY_RECORD_QUERIES is False
