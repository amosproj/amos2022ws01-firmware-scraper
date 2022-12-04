import pytest


@pytest.fixture(scope="session")
def test_init(Synology):
    assert Synology.url == "https://www.synology.com/en-global/support/download/"
    assert Synology.driver
    return Synology


def test_create_product_catalog(Synology):
    Synology._create_product_catalog()
    assert type(Synology.product_catalog) == {}


def test_get_product_list(Synology):
    Synology._get_product_list()
    assert type(Synology.product_list) == []


def test_get_product_line_list(Synology):
    Synology._get_product_line_list()
    assert type(Synology.product_line_list) == []
