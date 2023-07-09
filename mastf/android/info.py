import bs4

from google_play_scraper import app


def get_details(package_name: str) -> tuple[dict, str]:
    try:
        result = app(package_name)
        result.pop("descriptionHTML", None)
        result.pop("comments", None)

        desc = bs4.BeautifulSoup(result["description"], features="lxml")
        result["description"] = desc.get_text()
        return result, "PlayStore"
    except Exception as err:
        # log that
        return get_3p_details(package_name)


def get_3p_details(package_name: str) -> tuple:
    # TODO: check third-party app stores
    # raise NotImplementedError("Could not fetch data from GooglePlay")
    return {}, None
