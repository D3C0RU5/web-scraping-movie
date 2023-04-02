from bs4 import BeautifulSoup
import urllib
from urllib.request import Request, urlopen
from Levenshtein import distance

headers ={
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0",
    'content-type':'text/html; charset=utf-8',
    'server': 'server'
}

class WebScraper:
    def get_image(self, movie_name):
        url = urllib.parse.quote(movie_name)
        print(f"Iniciando scraping do filme: {movie_name}")

        req = Request(
            url=f'https://www.imdb.com/find/?q={url}', 
            headers=headers
        )
        print(f"Buscando resultados...")
        webpage = urlopen(req).read()
        soup = BeautifulSoup(webpage, "html.parser")

        # Obtendo lista de resultados
        print(f"Listando resultados...")
        movie_list = soup.find_all(class_="find-title-result")

        # Encontrando filme na lista
        print(f"Calculando distancia de items para o nome [{movie_name}]")

        selected_movie_index = 0
        less_distance_value = None

        for index, movie_item in enumerate(movie_list):
            movie_item_name = movie_item.find("a").text
            distance_value = distance(movie_name, movie_item_name)
            print(f"[{index}] -- {movie_item_name}")
            print(f"Result -> {distance_value}")

            if(less_distance_value == None or distance_value < less_distance_value):
                less_distance_value = distance_value
                selected_movie_index = index

        # Selecionando melhor resultado
        selected_movie = movie_list[selected_movie_index]
        selected_movie_name = selected_movie.find("a").text
        print(f"O melhor resultado foi: {selected_movie_name}")

        # Buscando página do filme
        print(f"Buscando página do filme...")
        movie_link = "https://www.imdb.com/" + selected_movie.find("a")["href"]
        req = Request(
            url=movie_link, 
            headers=headers
        )
        webpage = urlopen(req).read()
        soup = BeautifulSoup(webpage, "html.parser")

        image_poster_link = soup.find(class_="hero-media__watchlist").findNext('a')['href']

        # Buscando poster
        print(f"Buscando poster do filme...")
        req = Request(
            url="https://www.imdb.com/" + image_poster_link, 
            headers=headers
        )
        webpage = urlopen(req).read()
        soup = BeautifulSoup(webpage, "html.parser")

        image_poster_link = soup.findAll('img')[1]['src']

        print(f"Link encontrado!!")
        return image_poster_link
