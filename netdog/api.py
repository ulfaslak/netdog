from typing import Optional
import requests as rq
from tqdm import tqdm

from netdog.local_types import Tweet

BEARER_TOKEN = os.getenv("BEARER_TOKEN")
BASE_URL = "https://api.twitter.com/2"


def bearer_oauth(r):
    """Method required by bearer token authentication."""
    r.headers["Authorization"] = f"Bearer {BEARER_TOKEN}"

    return r


def poll_tweets(
    tags: list[str],
    languages: list[str],
    since_id: Optional[int] = None,
    verbose: bool = False,
) -> tuple[list[Tweet], int]:
    """Search for tweets containing `tags` in `languages`."""
    if verbose:
        print(f"Searching for tweets with tags {tags} in languages {languages}")
        t = tqdm(total=None)

    tags = " OR ".join(tags)
    languages = " OR ".join(["lang:" + lang for lang in languages])
    query_params = {
        "query": f"({tags}) ({languages}) -is:retweet",
        "since_id": since_id,
        "max_results": 100,
        "tweet.fields": "author_id,public_metrics",
    }

    tweets = []
    while True:
        response = rq.get(
            BASE_URL + "/tweets/search/recent",
            params=query_params,
            auth=bearer_oauth,
        )

        if response.status_code != 200:
            raise Exception(response.status_code, response.text)

        data = response.json()
        tweets.extend(data["data"])

        if "next_token" in data["meta"]:
            query_params["next_token"] = data["meta"]["next_token"]

            if verbose:
                t.update(len(data["data"]))

        else:
            break

    return tweets, data["meta"]["newest_id"]


def get_tweet_likers(
    tweet_id: int, total: int = None, verbose: bool = False
) -> list[int]:
    """Get the list of user IDs who liked a tweet."""
    query_params = {
        "max_results": 100,
    }

    if verbose:
        print(f"Getting likes for tweet {tweet_id}")

    likers = []
    while True:

        response = rq.get(
            BASE_URL + f"/tweets/{tweet_id}/liking_users",
            params=query_params,
            auth=bearer_oauth,
        )

        if response.status_code != 200:
            raise Exception(response.status_code, response.text)

        if verbose and len(likers) == 0:
            t = tqdm(total=total)

        data = response.json()

        if data["meta"]["result_count"] > 0:
            likers.extend([user["id"] for user in data["data"]])
            if verbose:
                t.update(len(data["data"]))
        else:
            t.close()
            break

        if "next_token" in data["meta"]:
            query_params["pagination_token"] = data["meta"]["next_token"]

    return likers


def get_tweet_retweeters(
    tweet_id: int, total: int = None, verbose: bool = False
) -> list[int]:
    """Get the list of user IDs who retweeted a tweet."""
    query_params = {
        "max_results": 100,
    }

    if verbose:
        print(f"Getting retweets for tweet {tweet_id}")

    retweeters = []
    while True:

        response = rq.get(
            BASE_URL + f"/tweets/{tweet_id}/retweeted_by",
            params=query_params,
            auth=bearer_oauth,
        )

        if response.status_code != 200:
            raise Exception(response.status_code, response.text)

        if verbose and len(retweeters) == 0:
            t = tqdm(total=total)

        data = response.json()

        if data["meta"]["result_count"] > 0:
            retweeters.extend([user["id"] for user in data["data"]])
            if verbose:
                t.update(len(data["data"]))
        else:
            t.close()
            break

        if "next_token" in data["meta"]:
            query_params["pagination_token"] = data["meta"]["next_token"]

    return retweeters


def get_user_likes(user_id: int) -> list[int]:
    """Get the list of user IDs whose tweets a user liked."""
    query_params = {
        "max_results": 100,
        "tweet.fields": "author_id",
    }
    response = rq.get(
        BASE_URL + f"/users/{user_id}/liked_tweets",
        params=query_params,
        auth=bearer_oauth,
    )

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

    data = response.json()
    return [tweet["author_id"] for tweet in data["data"]]
