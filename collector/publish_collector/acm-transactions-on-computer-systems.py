import os
import ipdb
import urllib
import argparse
import logging
import typing
import playwright

from playwright.sync_api import sync_playwright
from playwright._impl._api_structures import ProxySettings


def fetch_content(page: playwright.sync_api._generated.Page, url: str):
    
