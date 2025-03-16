from sharded.API.config import Environment

def test_environment_vital_static(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", "test_token")
    monkeypatch.setenv("DISCORD_PREFIX", "!")
    monkeypatch.setenv("GUILD_ID", int(123456789))

    assert Environment.vital("DISCORD_TOKEN", "static") == "test_token"
    assert Environment.vital("DISCORD_PREFIX", "static") == "!"
    assert Environment.vital("GUILD_ID", "static").id == 123456789
    assert Environment.vital("NON_EXISTENT_KEY", "static") is None


def test_environment_vital_dynamic(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", "test_token")
    monkeypatch.setenv("DISCORD_PREFIX", "!")
    monkeypatch.setenv("GUILD_ID", int(123456789))

    database = Environment.vital(provider="dynamic")
    assert database["DISCORD_TOKEN"] == "test_token"
    assert database["DISCORD_PREFIX"] == "!"
    assert database["GUILD_ID"].id == 123456789
