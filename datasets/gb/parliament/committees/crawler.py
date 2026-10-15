from ..util import iter_api_items, make_committee


def crawl(dataset):

    BASE_URL = "https://committees-api.parliament.uk/api/Committees"

    PARAMS = {"skip": 0, "take": 30, "CommitteeStatus": "All"}

    for item in iter_api_items(dataset, BASE_URL, PARAMS):
        make_committee(dataset, item)


if __name__ == "__main__":
    pass
