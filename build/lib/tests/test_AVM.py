from Vendors import AVMScraper


def test_init():
    AVM = AVMScraper(logger=None)
    assert AVM.url == "https://download.avm.de"
    assert AVM.name == "AVM"
    assert AVM.driver
