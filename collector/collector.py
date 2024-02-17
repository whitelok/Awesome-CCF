import os
import ipdb
import urllib
import argparse
import logging
import typing

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


def parse_args():
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
    args = parser.parse_args()
    return args


def prepare_proxy_settings(args: argparse.Namespace):
    proxy_settings = ProxySettings(server=f'http://{args.proxy_url}')
    cur_env = os.environ.copy()
    cur_env["https_proxy"] = f"http://{args.proxy_url}"
    cur_env["http_proxy"] = f"http://{args.proxy_url}"
    cur_env["all_proxy"] = f"socks5://{args.proxy_url}"
    return proxy_settings


def fetch_ccf_data(args: argparse.Namespace,
                   proxy_settings: typing.Optional[dict] = None):
    pass


def main():
    # get args
    args = parse_args()

    logging.basicConfig(encoding='utf-8',
                        level=logging._nameToLevel.get(args.log_level))

    # prepare proxy
    proxy_settings = None
    if check_proxy(args):
        proxy_settings = prepare_proxy_settings(args)

    print(type(proxy_settings))

    # # launch browser
    # with sync_playwright() as p:
    #     for browser_type in [p.chromium]:
    #         browser = browser_type.launch_persistent_context(
    #             headless=False, proxy=proxy_settings, no_viewport=True)
    #         page = browser.pages[0]
    #         page.goto(
    #             'https://www.binance.com/zh-CN/my/dashboard?callback=',
    #             timeout=22896000,
    #         )
    #         ipdb.set_trace()
    #         browser.close()


if __name__ == "__main__":
    main()
