import os
import ipdb
import urllib
import argparse
import logging
import typing
import playwright

from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from playwright._impl._api_structures import ProxySettings


def check_proxy(args: argparse.Namespace) -> bool:
    if not args.is_use_proxy:
        return False
    try:
        proxy_handler = urllib.request.ProxyHandler(
            {'http': f"http://{args.proxy_url}"})
        opener = urllib.request.build_opener(proxy_handler)
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        req = urllib.request.Request('http://www.google.com')
        # change the URL to test here
        urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        if args.is_use_proxy:
            raise e
        else:
            logging.warning(f"proxy connet error code: {e.code}")
            return False
    except Exception as e:
        logging.error(f"proxy check error code: {e.code}")
        raise e
    logging.info(f"proxy {args.proxy_url} is health")
    return True


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


def prepare_proxy_settings(args: argparse.Namespace) -> dict:
    proxy_settings = ProxySettings(server=f'http://{args.proxy_url}')
    cur_env = os.environ.copy()
    cur_env["https_proxy"] = f"http://{args.proxy_url}"
    cur_env["http_proxy"] = f"http://{args.proxy_url}"
    cur_env["all_proxy"] = f"socks5://{args.proxy_url}"
    return proxy_settings


def get_domain_url(url):
    return '{uri.scheme}://{uri.netloc}/'.format(
        uri=urllib.parse.urlparse(url))


def get_category_list(page: playwright.sync_api._generated.Page) -> dict:
    category_dict = {}
    # goto the category bar
    category_bar_locator = page.locator(
        "body > div.main.m-b-md > div.container > div.row-box > div > div.col-md-2 > div > ul:nth-child(2)"
    )
    domain_url = get_domain_url(page.main_frame.url)
    # from [1:-1] to skip the introduction and skip contact us
    for category_bar_li in category_bar_locator.get_by_role(
            'listitem').all()[1:-1]:
        category_bar_hyper_link = category_bar_li.first.get_by_role(
            "link").get_attribute('href')
        category_bar_content_text = category_bar_li.first.get_by_role(
            "link").text_content()
        category_bar_key = category_bar_hyper_link.strip('/').split('/')[-1]
        category_dict[category_bar_key] = {
            'desc': category_bar_content_text,
            'link': f"{domain_url}{category_bar_hyper_link}",
            'journals': {
                'a': [],
                'b': [],
                'c': []
            },
            'conferences': {
                'a': [],
                'b': [],
                'c': []
            }
        }
    return category_dict


def fetch_sub_grade_content(
        content_locator: playwright.sync_api._generated.Locator,
        grade_content_data: list):
    # [1:] skip form header
    for item in content_locator.get_by_role('listitem').all()[1:]:
        sname = item.locator(".sname").text_content()
        full_name = item.locator("div").nth(2).text_content()
        if sname == '\u00a0':
            sname = full_name
        publisher = item.locator("div").nth(3).text_content()
        url = item.locator("div").nth(4).text_content()
        grade_content_data.append({
            'sname': sname,
            'full_name': full_name,
            'publisher': publisher,
            'url': url,
        })


def fetch_journals(page: playwright.sync_api._generated.Page,
                   category_content: dict) -> None:
    journals_data = category_content['journals']
    # fetch class A
    class_a_content = page.locator(
        'body > div.main.m-b-md > div.container > div.row-box > div > div.col-md-10 > div > div > ul:nth-child(4)'
    )
    fetch_sub_grade_content(class_a_content, journals_data['a'])
    # fetch class B
    class_b_content = page.locator(
        'body > div.main.m-b-md > div.container > div.row-box > div > div.col-md-10 > div > div > ul:nth-child(6)'
    )
    fetch_sub_grade_content(class_b_content, journals_data['b'])
    # fetch class C
    class_c_content = page.locator(
        'body > div.main.m-b-md > div.container > div.row-box > div > div.col-md-10 > div > div > ul:nth-child(8)'
    )
    fetch_sub_grade_content(class_c_content, journals_data['c'])


def fetch_conferences(page: playwright.sync_api._generated.Page,
                      category_content: dict) -> None:
    conferences_data = category_content['conferences']
    # fetch class A
    class_a_content = page.locator(
        'body > div.main.m-b-md > div.container > div.row-box > div > div.col-md-10 > div > div > ul:nth-child(12)'
    )
    fetch_sub_grade_content(class_a_content, conferences_data['a'])
    # fetch class B
    class_b_content = page.locator(
        'body > div.main.m-b-md > div.container > div.row-box > div > div.col-md-10 > div > div > ul:nth-child(14)'
    )
    fetch_sub_grade_content(class_b_content, conferences_data['b'])
    # fetch class C
    class_c_content = page.locator(
        'body > div.main.m-b-md > div.container > div.row-box > div > div.col-md-10 > div > div > ul:nth-child(16)'
    )
    fetch_sub_grade_content(class_c_content, conferences_data['c'])


def fetch_category_data(args: argparse.Namespace,
                        page: playwright.sync_api._generated.Page,
                        category_dict: dict) -> None:
    for category_key in category_dict:
        category_content = category_dict[category_key]
        category_desc = category_content['desc']
        category_link = category_content['link']
        logging.info(f"Go to fetch {category_desc} data at {category_link}")
        page.goto(
            category_link,
            timeout=args.default_timeout,
        )
        # fetch journals
        fetch_journals(page, category_content)
        # fetch conferences
        fetch_conferences(page, category_content)


def fetch_ccf_data(args: argparse.Namespace,
                   playwright: playwright.sync_api._generated.Playwright,
                   proxy_settings: typing.Optional[dict] = None):
    browser = playwright.chromium.launch(headless=False, proxy=proxy_settings)
    page = browser.new_page()
    # go to main page at
    logging.info("Go to main page")
    page.goto(
        args.main_page_url,
        timeout=args.default_timeout,
    )
    logging.info("Get to main page")
    # category_data is a dict
    category_data = get_category_list(page)
    # go to each category and fetch content data
    fetch_category_data(args, page, category_data)
    ipdb.set_trace()
    browser.close()


def main():
    # get args
    args = parse_args()

    logging.basicConfig(encoding='utf-8',
                        level=logging._nameToLevel.get(args.log_level))

    # prepare proxy
    proxy_settings = None
    if check_proxy(args):
        proxy_settings = prepare_proxy_settings(args)

    # fetch ccf data
    with sync_playwright() as playwright:
        fetch_ccf_data(args, playwright, proxy_settings)


if __name__ == "__main__":
    main()
