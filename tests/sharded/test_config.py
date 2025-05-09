from sharded.config import Environment


def test_environment_vital_static(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", "test_token")
    monkeypatch.setenv("GUILD_ID", "123456789")

    assert Environment().vital("DISCORD_TOKEN", provider="static") == "test_token"
    assert int(Environment().vital("GUILD_ID", provider="static")) == 123456789


def test_environment_vital_dynamic(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", "test_token")
    monkeypatch.setenv("GUILD_ID", "123456789")

    database = Environment().vital(provider="dynamic")
    assert database["DISCORD_TOKEN"] == "test_token"
    assert int(database["GUILD_ID"]) == 123456789
