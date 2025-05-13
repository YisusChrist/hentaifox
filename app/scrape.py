import random
from typing import Any

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from app.config import BASE_URL, MAX_ID, MAX_RETRIES


def generate_random_id() -> int:
    return random.randint(1, MAX_ID)


def construct_url(id: int) -> str:
    return f"{BASE_URL}/{id}/"


def extract_id_from_url(url: str) -> str | None:
    matches: list[str] = url.split("gallery/")
    if len(matches) > 1:
        return matches[1].split("/")[0]
    return None


def scrape_content(url: str) -> dict[str, Any]:
    try:
        res: requests.Response = requests.get(url)
        res.raise_for_status()
        soup = BeautifulSoup(res.content, "html.parser")

        id_tag: Tag | None = soup.select_one("a.g_button")
        if not id_tag:
            raise ValueError("ID tag not found")

        # Extract the ID from the href attribute
        dj_id: int | None = int(id_tag["href"].split("/")[2])

        category: list[str] = [
            tag.text.replace("[0-9]", "").strip() for tag in soup.select("a.tag_btn")
        ]

        img_src = [
            img["data-src"] for img in soup.find_all("img") if img.get("data-src")
        ]
        if not img_src:
            raise ValueError("Content not found")

        parameter_img2: str = "/".join(img_src[0].split("/")[:5])
        extension_img: str = f".{img_src[0].split('.')[-1]}"

        info: list[str] = [span.text for span in soup.select("span.i_text.pages")]
        page_count: int = int("".join(filter(str.isdigit, info[0]))) if info else 0

        image_urls: list[str] = [
            f"{parameter_img2}/{i+1}{extension_img}" for i in range(page_count)
        ]

        info_header: Tag | None = soup.select_one("div.info h1")
        if not info_header:
            title_info: str = "No title"
        else:
            title_info = info_header.text

        object_data: dict[str, Any] = {
            "title": title_info,
            "id": dj_id,
            "tags": category,
            "type": extension_img,
            "total": page_count,
            "image": image_urls,
        }

        return {"success": True, "data": object_data, "source": f"{BASE_URL}/{dj_id}/"}

    except requests.HTTPError as http_err:
        if http_err.response.status_code == 404:
            raise ValueError("404")
        raise http_err
    except Exception as err:
        raise ValueError(f"Scraping error: {err}")


def scrape_with_retries(initial_id: int) -> dict[str, Any] | None:
    current_id: int = initial_id
    attempts = 0

    while attempts < MAX_RETRIES:
        try:
            print(f"Attempt {attempts + 1}/{MAX_RETRIES} with ID: {current_id}")
            url: str = construct_url(current_id)
            result: dict[str, Any] = scrape_content(url)
            return result
        except ValueError as e:
            if str(e) == "404":
                attempts += 1
                if attempts < MAX_RETRIES:
                    current_id = generate_random_id()
                    continue
            raise e

    return None
