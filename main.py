#!/usr/bin/env python
import logging
import json
import multiprocessing
import sys
import time
from services.scrap import WebScraper
from multiprocessing import Process


def get_json_object():
    with open('data/movies.json', 'r') as json_file:
        json_object = json.load(json_file)
        json_file.close()

    return json_object


def get_url_movies(list_movies: list[str]):

    for index, movie in enumerate(list_movies):
        len_movies = len(list_movies)
        logging.info(f"[{index+1}/{len_movies}] Scraping [{movie['name']}]")
        url = WebScraper().get_image(movie['name'])
        movie['url'] = url

    return list_movies


def refresh_file_with_processed_images(content):
    with open('data/procced-images.json', 'w') as json_file:
        json_file.write(content)
        json_file.close()


def config():
    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        encoding='utf-8',
        level=logging.DEBUG,
    )


def get_args():
    """
    Arguments definitions:

    -r | --range : define a range to scrap movies, by default the range is all movies
    ex: -r 0 100

    -a | --async : define quantity of asyncronous requests, by default is 5
    ex: -a 10

    -c | --change : change scrap already executed, by default this option is disabled, 0 is disabled and 1 is enabled
    ex: -c 0 | -c 1

    """
    args = sys.argv[1:]

    args_definition = {
        '--change': 0,
        '--async': 5,
    }

    for index, arg in enumerate(args):
        if arg == '-r' or arg == '--range':
            range = args[index+1:index+3]

            args_definition['--range'] = {
                "start": int(range[0]),
                "end": int(range[1]),
            }
        elif arg == '-c' or arg == '--change':
            args_definition['--change'] = int(args[index+1])
        elif arg == '-a' or arg == '--async':
            args_definition['--async'] = int(args[index+1])

    return args_definition


def get_movie_range(args, movies):
    if '--range' in args.keys():
        return movies[args['--range']['start']: args['--range']['end']]

    return movies


def filter_with_change_arg(args, movies):
    if args['--change'] == 0:
        return [movie for movie in movies if 'url' not in movie.keys()]

    return movies


def start_scraping(args):
    json_object = get_json_object()

    movies = get_movie_range(args, json_object['movies'])

    movies = filter_with_change_arg(args, movies)

    movies = perform_requests(args, movies)

    save_processed(movies)


def divide_chunks(args, movies):
    chunk_size = args['--async']
    chunks = []
    for i in range(0, len(movies), chunk_size):
        chunks.append(movies[i:i + chunk_size])
    return chunks


def worker(movie, return_dict):
    logging.info(f"Scraping {movie['name']}")
    movie['url'] = WebScraper().get_image(movie['name'])
    logging.info(f"Scraping {movie['name']} completed successfully")

    return_dict[movie['name']] = movie['url']


def execute_chunk(chunk, movies):
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    jobs = []
    for movie in chunk:
        p = multiprocessing.Process(target=worker, args=(movie, return_dict))
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()

    return return_dict


def perform_requests(args, movies):
    movie_chunks = divide_chunks(args, movies)

    results = []
    for chunk in movie_chunks:
        chunk_results = execute_chunk(chunk, movies)
        for result in chunk_results:
            movie = {
                "name": result,
                "url": chunk_results[result],
            }
            results.append(movie)

    return results


def save_processed(movies):
    movies_to_text = json.dumps(movies, ensure_ascii=False)
    refresh_file_with_processed_images(movies_to_text)
    logging.info(f"Scrapping completed.")


if __name__ == '__main__':
    try:
        args = get_args()
        config()
        start_scraping(args)

    except KeyboardInterrupt as exc:
        logging.info(f"Scrapping stoped.")

    except Exception as exc:
        logging.exception(f"Something goes wrong: %s" % exc)
