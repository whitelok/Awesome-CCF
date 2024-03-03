import ipdb
import argparse
import logging
import playwright

from playwright.sync_api import expect


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
        paper_list_locator = page.locator("#main > ul")

        for paper_meta in paper_list_locator.get_by_role('listitem').all():
            paper_cite = paper_meta.locator("cite")
            paper_title = ""
            paper_authors = []
            for author in paper_cite.locator("span").all():
                if author.get_attribute("itemprop") == "author":
                    paper_authors.append(author.text_content())
                if author.get_attribute("itemprop") == "name":
                    paper_title = author.text_content()
            volume_content['papers'].append({
                "title": paper_title,
                "authors": paper_authors
            })


if __name__ == "__main__":
    pass
