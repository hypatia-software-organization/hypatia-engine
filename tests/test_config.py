from hypatia import config

def test_config():
    """Test the default configuration.
    """

    c = config.create_config()
    assert c.has_section("game")
    assert c["game"]["name"] == "Hypatia"
