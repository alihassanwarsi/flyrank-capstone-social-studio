import httpx
from bs4 import BeautifulSoup


class UrlFetchError(Exception):
    pass

def fetch_url_content(url: str) -> tuple[str | None, str]:
    try:
        response = httpx.get(url, follow_redirects=True, timeout=10.0,)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise UrlFetchError("Could not fetch the URL.") from exc

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript", "nav", "footer"]):
        tag.decompose()

    article = soup.find("article") or soup.body or soup

    content = "\n".join(
        line.strip()
        for line in article.get_text("\n").splitlines()
        if line.strip()
    )

    if not content:
        raise UrlFetchError("No readable content found at the URL.")

    title = (
        soup.title.get_text(strip=True)
        if soup.title
        else None
    )

    return title, content