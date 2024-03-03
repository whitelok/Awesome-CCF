import argparse
import logging
import playwright

from playwright.sync_api import expect
from playwright.sync_api import sync_playwright
from playwright._impl._api_structures import ProxySettings


def fetch_content(args: argparse.Namespace,
                  page: playwright.sync_api._generated.Page,
                  publish_meta: dict) -> None:
    url = publish_meta.get("url", None)
    page.goto(
        url,
        timeout=args.default_timeout,
    )
    content_locator = page.locator("#main > ul")
    content = []
    for item in content_locator.get_by_role('listitem').all():
        url = item.get_by_role("link").get_attribute('href')
        volume = item.text_content()
        content.append({"volume": volume, "url": url, "papers": []})
    publish_meta['content'] = content
    for volume_content in publish_meta['content']:
        page.goto(
            volume_content['url'],
            timeout=args.default_timeout,
        )
        paper_list_locator = page.locator(
            '.publ-list:not(.publ-list--disabled)')
        volume_count = paper_list_locator.count()

        papers = []
        for volume_idx in range(volume_count):
            for paper_meta in paper_list_locator.nth(volume_idx).get_by_role(
                    'listitem').all():
                total_content = paper_meta.inner_text()
                items = total_content.splitlines()
                if len(items) != 2:
                    continue
                author, title = [item.strip("\t").strip(":") for item in items]
                papers.append({"author": author.split(","), "title": title})
        volume_content["papers"] = papers


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--proxy_url',
                        type=str,
                        default="127.0.0.1:7890",
                        help="proxy url with format host:port")
    parser.add_argument('--is_use_proxy',
                        type=bool,
                        default=False,
                        help="is use proxy")
    parser.add_argument(
        '--log_level',
        default="INFO",
        choices=['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="log level")
    parser.add_argument('--default_timeout',
                        type=int,
                        default=60000,
                        help="data fetch timeout")
    parser.add_argument(
        '--main_page_url',
        type=str,
        default="https://www.ccf.org.cn/Academic_Evaluation/By_category/",
        help="default data source main page url")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(encoding='utf-8',
                        level=logging._nameToLevel.get(args.log_level))
    proxy_settings = None
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False,
                                             proxy=proxy_settings)
        page = browser.new_page()
        publish_meta = {
            "sname": "TC",
            "full_name": "IEEE Transactions on Computers",
            "publisher": "IEEE",
            "url": "http://dblp.uni-trier.de/db/journals/tc/index.html"
        }
        fetch_content(args, page, publish_meta)
