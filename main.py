#!/usr/bin/env python
import sys
from services.scrap import WebScraper

movie_name_args = ' '.join(sys.argv[1:])
image_link = WebScraper().get_image(movie_name_args)

print(image_link)
