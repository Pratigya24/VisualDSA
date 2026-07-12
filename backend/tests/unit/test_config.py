from app.core.config import Settings


class TestSettings:
    def test_cors_origins_parses_comma_separated_string(self):
        settings = Settings(cors_origins="http://a.com, http://b.com")
        assert settings.cors_origins == ["http://a.com", "http://b.com"]

    def test_cors_origins_accepts_list_directly(self):
        settings = Settings(cors_origins=["http://a.com"])
        assert settings.cors_origins == ["http://a.com"]

    def test_is_production_false_by_default(self):
        settings = Settings()
        assert settings.is_production is False

    def test_is_production_true_when_environment_production(self):
        settings = Settings(environment="production")
        assert settings.is_production is True
