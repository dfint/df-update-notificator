import json
from pathlib import Path
from typing import Any
import requests

from rss import write_rss

# Docs: https://developer.valvesoftware.com/wiki/Steam_Web_API#GetNewsForApp_(v0002)
news_request_url = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/"
df_app_id = 975370

root_dir = Path(__file__).parent
latest_update_file = root_dir / "latest_update.json"
full_update_info_file = root_dir / "full_update_info.json"


def get_last_posts(*, count) -> list[dict[str, Any]]:
    response = requests.get(
        news_request_url,
        params=dict(appid=df_app_id, count=count, maxlength=1000, format="json"),
    )
    response.raise_for_status()
    return response.json()["appnews"]["newsitems"]


def main():
    posts = [post for post in get_last_posts(count=10) if "steam_community_announcements" in post["url"]]

    post = posts[0]

    if latest_update_file.exists():
        prev_update = json.loads(latest_update_file.read_text(encoding="utf-8"))

    if not latest_update_file.exists() or prev_update["date"] < post["date"]:
        prev_update = dict(
            gid=post["gid"],
            date=post["date"],
            title=post["title"],
            appid=post["appid"],
        )
        latest_update_file.write_text(json.dumps(prev_update), encoding="utf-8")
        full_update_info_file.write_text(json.dumps(post), encoding="utf-8")
        write_rss(post)
        print("yes")
    else:
        print("no")


if __name__ == "__main__":
    main()
