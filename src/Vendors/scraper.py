from abc import ABC, abstractmethod


class Scraper(ABC):
    """Defines public interface of vendor-specific scraper classes."""

    @abstractmethod
    def scrape_metadata(self) -> list[dict]:
        """
        Scrapes all firmware metadata of the respective vendor.

        Returns:
            A list of dicts, where every dict represents one firmware product.
            If there exist multiple up-to-date download links for the same firmware product,
            one dict per download link should be appended to the list.

            Every dict should have the following keys which are inserted into the DB as attributes:
                "manufacturer", "product_name", "product_type", "version", "release_date",
                "download_link", "checksum_scraped", "additional_data".

            All values must be of type str, except for "additional_data" which is a dict.
            "additional_data" serves as a vendor-specific field for data that does not fit
                the other keys but is still relevant for comparison of firmware entries or
                should be kept for other reasons.
            "release_date" should be a string formatted in this way: YYYY-MM-DD.
            If unknown at the time of scraping, values should be set to Null.
        """
        pass

    def get_attributes_to_compare(self) -> list[str]:
        """
        Defines keys (as defined by scrape_metadata()) to be used by the core when comparing
        existing metadata with newly scraped metadata.

        The keys correspond to identically named attributes of the DB.
        They are used to determine if a firmware product is new or has been updated.

        Returns:
            A list of strings where every string is a key as defined by scrape_metadata().
            Vendor-specific keys within "additional_data" can be expressed by returning
            the string "additional_data:<vendor-specific key>".
        """
        return ["manufacturer", "product_name", "version"]
