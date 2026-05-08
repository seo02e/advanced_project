import json
import logging
import re
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from app.services.policy_service import save_policy_crawling
logger = logging.getLogger(__name__)

BASE_URL = "https://www.lh.or.kr"
START_URL = "https://www.lh.or.kr/menu.es?mid=a10401020100"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"
CRAWLING_OUTPUT_DIR = DATA_DIR / "crawling_chunks"

DATA_DIR.mkdir(parents=True, exist_ok=True)
CRAWLING_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


SECTION_TITLES = [
    "입주대상",
    "소득 기준",
    "소득 자산 기준",
    "임대조건",
    "거주기간",
    "공급시기",
    "신청방법",
    "문의처",
]


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def fetch_html(url: str) -> str:
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=15
    )
    response.raise_for_status()
    return response.text


def get_depth4_menu_links(url: str) -> list[str]:
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    menu_area = soup.find("ul", id="depth4_menu_ul")

    if not menu_area:
        raise ValueError("depth4_menu_ul 영역을 찾지 못했습니다.")

    links = []
    seen = set()

    for tag in menu_area.select("a[href]"):
        href = tag.get("href", "").strip()

        if "menu.es?mid" not in href:
            continue

        full_url = urljoin(BASE_URL, href)

        if full_url in seen:
            continue

        seen.add(full_url)
        links.append(full_url)

    return links


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_title(soup: BeautifulSoup) -> str:
    heading = soup.find(["h1", "h2", "h3"])

    if heading:
        return clean_text(heading.get_text(" "))

    if soup.title:
        return clean_text(soup.title.get_text(" "))

    return "LH 정책"


def extract_main_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    candidates = [
        soup.find("main"),
        soup.find(id="contents"),
        soup.find(id="content"),
        soup.find(class_="contents"),
        soup.find(class_="content"),
        soup.body,
    ]

    target = next(
        (candidate for candidate in candidates if candidate),
        soup
    )

    return target.get_text("\n")


def split_lines(text: str) -> list[str]:
    return [
        clean_text(line)
        for line in text.splitlines()
        if clean_text(line)
    ]


def find_section_title(line: str) -> str | None:
    normalized = line.replace(" ", "")

    for title in SECTION_TITLES:
        if title.replace(" ", "") in normalized:
            return title

    return None


def build_chunks(lines: list[str]) -> list[dict]:
    chunks = []
    current_title = "본문"
    current_lines = []

    for line in lines:
        detected_title = find_section_title(line)

        if detected_title:
            if current_lines:
                chunks.append({
                    "section_title": current_title,
                    "chunk_text": "\n".join(current_lines)
                })

            current_title = detected_title
            current_lines = [line]
            continue

        current_lines.append(line)

    if current_lines:
        chunks.append({
            "section_title": current_title,
            "chunk_text": "\n".join(current_lines)
        })

    return chunks


def build_chunk_schema(
    *,
    policy_id: str,
    policy_name: str,
    source_url: str,
    chunks: list[dict]
) -> list[dict]:
    result = []

    for index, chunk in enumerate(chunks, start=1):
        chunk_text = clean_text(chunk["chunk_text"])

        if not chunk_text:
            continue

        result.append({
            "chunk_id": f"{policy_id}_{index}",
            "policy_id": policy_id,
            "policy_name": policy_name,
            "issuing_org": "LH",
            "source_doc_name": policy_name,
            "source_url": source_url,
            "section_title": chunk["section_title"],
            "chunk_text": chunk_text,
            "chunk_order": index,
            "has_table": False,
            "doc_type": "web_page",
            "created_from": "section_chunking",
            "source_layer": "B",
        })

    return result


def process_page(url: str) -> list[dict]:
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    policy_id = url.split("mid=")[-1] if "mid=" in url else None

    if not policy_id:
        raise ValueError(f"policy_id 추출 실패: {url}")

    policy_name = extract_title(soup)
    main_text = extract_main_text(soup)
    lines = split_lines(main_text)
    chunks = build_chunks(lines)

    return build_chunk_schema(
        policy_id=policy_id,
        policy_name=policy_name,
        source_url=url,
        chunks=chunks
    )

def save_policy_crawling_chunks() -> int:
    urls = get_depth4_menu_links(START_URL)
    logger.info(f"LH 크롤링 대상 URL 수: {len(urls)}")

    all_chunks = []

    # 문서 저장
    for url in urls:
        logger.info(f"LH 정책 페이지 크롤링 시작: {url}")

        chunk_rows = process_page(url)
        all_chunks.extend(chunk_rows)

        page_id = url.split("mid=")[-1]

        save_json(
            CRAWLING_OUTPUT_DIR / f"{page_id}_chunks.json",
            {
                "chunks": chunk_rows
            }
        )

    save_json(
        CRAWLING_OUTPUT_DIR / "policy_chunks_all.json",
        {
            "chunks": all_chunks
        }
    )

    # DB 저장
    saved_count = save_policy_crawling(chunk_rows=all_chunks)

    logger.info(f"policy_chunks 저장 완료: {saved_count}건")

    return saved_count


if __name__ == "__main__":
    count = save_policy_crawling_chunks()
    print(f"policy_chunks 저장 완료: {count}건")