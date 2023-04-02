#!/usr/bin/env python
import sys

from services.scrap import WebScraper

image_link =WebScraper().get_image(sys.argv[1])

print(image_link)
