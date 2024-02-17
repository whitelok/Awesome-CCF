import os
import ipdb
import urllib
import argparse

from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from playwright._impl._api_structures import ProxySettings


def check_proxy(proxy_url):
    try:
        proxy_handler = urllib.request.ProxyHandler({'http': proxy_url})
        opener = urllib.request.build_opener(proxy_handler)
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        req = urllib.request.Request('http://www.google.com')
        # change the URL to test here
        urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        print('Proxy Error code: ', e.code)
        return e.code
    except Exception as detail:
        print("Proxy ERROR:", detail)
        return True
    return False


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--proxy_url',
                        type=str,
                        default="127.0.0.1:7890",
                        help="proxy url with format host:port")
    args = parser.parse_args()
    return args


def prepare_proxy_settings():
    proxy_settings = ProxySettings(server='http://127.0.0.1:7890')

    cur_env = os.environ.copy()
    cur_env["https_proxy"] = "http://127.0.0.1:7890"
    cur_env["http_proxy"] = "http://127.0.0.1:7890"
    cur_env["all_proxy"] = "socks5://127.0.0.1:7890"


def main():
    # get args
    args = parse_args()
    print(args)
    return

    # prepare proxy
    proxy_settings = prepare_proxy_settings()

    # check proxy

    # launch browser
    with sync_playwright() as p:
        for browser_type in [p.chromium]:
            browser = browser_type.launch_persistent_context(
                headless=False, proxy=proxy_settings, no_viewport=True)
            page = browser.pages[0]
            page.goto(
                'https://www.binance.com/zh-CN/my/dashboard?callback=',
                timeout=22896000,
            )
            ipdb.set_trace()
            browser.close()


if __name__ == "__main__":
    main()
