import requests
import argparse
import json
import time
import re
from html.parser import HTMLParser

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
}


# ─── Utility ──────────────────────────────────────────────────────────────────

def get_pin_id(pin_input: str) -> str:
    match = re.search(r"pinterest\.[^/]+/pin/(\d+)", pin_input)
    if match:
        return match.group(1)
    if pin_input.strip().isdigit():
        return pin_input.strip()
    raise ValueError(f"Impossibile estrarre il pin ID da: {pin_input}")


# ─── Metodo 1: API interna Pinterest ──────────────────────────────────────────

def _build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(HEADERS)
    resp = session.get("https://www.pinterest.com/", timeout=15)
    resp.raise_for_status()
    csrftoken = session.cookies.get("csrftoken")
    if csrftoken:
        session.headers.update({"X-CSRFToken": csrftoken})
    return session


def fetch_via_internal_api(pin_id: str) -> dict | None:
    try:
        session = _build_session()
        timestamp = int(time.time() * 1000)
        options = json.dumps({"options": {"id": pin_id, "field_set_key": "detailed"}})
        url = (
            f"https://www.pinterest.com/resource/PinResource/get/"
            f"?source_url=/pin/{pin_id}/"
            f"&data={options}"
            f"&_{timestamp}"
        )
        session.headers.update({
            "Accept": "application/json, text/javascript, */*, q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"https://www.pinterest.com/pin/{pin_id}/",
        })
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        pin_data = data.get("resource_response", {}).get("data", {})
        for key in ("title", "grid_title", "description"):
            val = pin_data.get(key)
            if val and str(val).strip():
                return {"title": str(val).strip(), "source": "internal_api", "raw": data}
        return {"title": None, "source": "internal_api", "raw": data}
    except Exception as e:
        return {"error": str(e), "source": "internal_api"}


# ─── Metodo 2: OEmbed (endpoint pubblico, non richiede login) ─────────────────

def fetch_via_oembed(pin_id: str) -> dict | None:
    url = f"https://www.pinterest.com/oembed/?url=https://www.pinterest.com/pin/{pin_id}/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        title = data.get("title", "").strip()
        return {"title": title or None, "source": "oembed", "raw": data}
    except Exception as e:
        return {"error": str(e), "source": "oembed"}


# ─── Metodo 3: Scraping HTML (meta og:title) ──────────────────────────────────

class _MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title: str | None = None
        self._in_title = False
        self._title_text = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "meta":
            prop = attrs_dict.get("property", "") or attrs_dict.get("name", "")
            if prop in ("og:title", "twitter:title"):
                content = attrs_dict.get("content", "").strip()
                if content:
                    self.title = content
        elif tag == "title":
            self._in_title = True

    def handle_data(self, data):
        if self._in_title:
            self._title_text.append(data)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
            if not self.title:
                raw = "".join(self._title_text).strip()
                if raw:
                    self.title = raw


def fetch_via_html_scraping(pin_id: str) -> dict:
    url = f"https://www.pinterest.com/pin/{pin_id}/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        resp.raise_for_status()
        parser = _MetaParser()
        parser.feed(resp.text)
        return {"title": parser.title, "source": "html_scraping"}
    except Exception as e:
        return {"error": str(e), "source": "html_scraping"}


# ─── Orchestratore ────────────────────────────────────────────────────────────

def get_pin_title(pin_id: str, verbose: bool = False) -> dict:
    methods = [
        ("API interna",     fetch_via_internal_api),
        ("OEmbed",          fetch_via_oembed),
        ("HTML scraping",   fetch_via_html_scraping),
    ]
    for label, fn in methods:
        if verbose:
            print(f"  Provo con {label}...", end=" ", flush=True)
        result = fn(pin_id)
        if result and not result.get("error") and result.get("title"):
            if verbose:
                print("OK")
            return {**result, "method": label}
        if verbose:
            reason = result.get("error", "nessun titolo trovato")
            print(f"fallito ({reason})")
    return {"title": None, "method": None}


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="pinterest",
        description="Legge un pin di Pinterest ed estrae il titolo (API interna, OEmbed, HTML)"
    )
    parser.add_argument(
        "-p", "--pin",
        required=True,
        help="ID numerico del pin (es. 123456789) oppure URL completo"
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Mostra la risposta grezza dell'API (solo metodo 1 o 2)"
    )
    parser.add_argument(
        "--method",
        choices=["api", "oembed", "html"],
        default=None,
        help="Forza un metodo specifico: api | oembed | html"
    )
    args = parser.parse_args()

    try:
        pin_id = get_pin_id(args.pin)
    except ValueError as e:
        print(f"\nErrore: {e}")
        return

    print(f"\nPin ID: {pin_id}")

    if args.method:
        fn_map = {
            "api":    fetch_via_internal_api,
            "oembed": fetch_via_oembed,
            "html":   fetch_via_html_scraping,
        }
        result = fn_map[args.method](pin_id)
        if args.raw and "raw" in result:
            print(json.dumps(result["raw"], indent=2, ensure_ascii=False))
            return
        if result.get("error"):
            print(f"\nErrore [{args.method}]: {result['error']}")
        elif result.get("title"):
            print(f"\nTitolo: {result['title']}")
        else:
            print("\nTitolo non trovato con il metodo scelto.")
        return

    print("Tentativo di recupero titolo (3 metodi)...")
    result = get_pin_title(pin_id, verbose=True)

    if result.get("title"):
        print(f"\nTitolo: {result['title']}")
        print(f"(estratto via: {result['method']})")
    else:
        print("\nImpossibile recuperare il titolo del pin.")
        print("Possibili cause: pin privato, ID inesistente, o Pinterest ha bloccato le richieste.")


if __name__ == "__main__":
    main()
