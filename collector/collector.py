import os
import ipdb

from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from playwright._impl._api_structures import ProxySettings

proxy_settings = ProxySettings(server='http://127.0.0.1:7890')

cur_env = os.environ.copy()
cur_env["https_proxy"] = "http://127.0.0.1:7890"
cur_env["http_proxy"] = "http://127.0.0.1:7890"
cur_env["all_proxy"] = "socks5://127.0.0.1:7890"


def main():
    with sync_playwright() as p:
        # for browser_type in [p.firefox]:
        for browser_type in [p.chromium]:
            browser = browser_type.launch_persistent_context(headless=False,
                                                             proxy=proxy_settings,
                                                             geolocation={"latitude": 35.6258, "longitude": 139.3415},
                                                             permissions=["geolocation"],
                                                             no_viewport=True,
                                                             user_data_dir="/Users/whitelok/Downloads/virtual-browser/binance_cache")
            page = browser.pages[0]
            page.goto('https://www.binance.com/zh-CN/my/dashboard?callback=', timeout=22896000,)
            ipdb.set_trace()
            browser.close()


if __name__ == "__main__":
    main()
