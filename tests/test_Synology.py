def test_init(Synology):
    assert Synology.url == "https://www.synology.com/en-global/support/download/"
    assert Synology.driver
    return Synology
