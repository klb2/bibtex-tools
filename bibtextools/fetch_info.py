import feedparser
import requests

from .const import KEY_AUTHOR, KEY_TITLE
from .util import getnames


def get_arxiv_category(eprint):
    base_url = "http://export.arxiv.org/api/query?"
    search_query = {
        "id_list": eprint,
    }
    query = "&".join(["{}={}".format(k, v) for k, v in search_query.items()])
    feed = feedparser.parse(base_url + query)
    entries = feed["entries"]
    if len(entries) != 1:
        return None
    # a_id = entries[0]["id"].split('/abs/')[-1]
    try:
        primary_class = entries[0]["arxiv_primary_category"]["term"]
    except KeyError:
        return None
    if primary_class == "":
        return None
    else:
        return primary_class


def get_doi(entry):
    doi = _get_doi_from_crossref(entry)
    return doi


def _get_doi_from_crossref(entry):
    API_CROSSREF = "https://api.crossref.org/works"
    KEY_CROSSREF_SCORE = "score"
    KEY_CROSSREF_AUTHOR = "author"
    KEY_CROSSREF_TITLE = "title"
    KEY_CROSSREF_DOI = "DOI"

    request_return_fields = [
        KEY_CROSSREF_SCORE,
        KEY_CROSSREF_TITLE,
        KEY_CROSSREF_DOI,
        KEY_CROSSREF_AUTHOR,
    ]
    params = {"select": ",".join(request_return_fields), "rows": 1, "sort": "score"}
    params["query.title"] = entry.get(KEY_TITLE)
    author_string = entry.get(KEY_AUTHOR, "")
    params["query.author"] = getnames(
        [i.strip() for i in author_string.replace("\n", " ").split(" and ")]
    )[0]
    print(params)
    try:
        resp = requests.get(API_CROSSREF, params=params)
        resp.raise_for_status()
        _json = resp.json()
        matched_entry = _json["message"]["items"][0]
        match_score = float(matched_entry.get(KEY_CROSSREF_SCORE, 0))
        if match_score < 50:
            raise ValueError("No suitable match found when fetching DOI")
    except requests.HTTPError as ex:
        raise ex
    except requests.Timeout as ex:
        raise ex
    except ValueError as ex:
        raise ex
    print(_json)
    doi = matched_entry["DOI"]
    print(f"Found DOI: {doi}")
    return doi
