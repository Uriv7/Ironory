from backend.app.core.config import Settings


def test_default_settings():
    s = Settings()
    assert s.APP_NAME == "Ironory"
    assert s.API_V1_PREFIX == "/api/v1"
    assert s.STORAGE_BACKEND == "local"
    assert isinstance(s.CORS_ORIGINS, list)
    assert len(s.CORS_ORIGINS) > 0


def test_cors_origins_parsing():
    s = Settings(CORS_ORIGINS="http://example.com, https://app.example.com")
    assert s.CORS_ORIGINS == ["http://example.com", "https://app.example.com"]
