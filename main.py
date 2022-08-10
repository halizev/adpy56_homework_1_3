import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from string import punctuation
import pymorphy2
from tqdm import tqdm

DESIRED_HUBS = ['дизайн', 'фото', 'web', 'python']
STOPWORDS = stopwords.words('russian')


def get_habr_links(initial_link):
    ret = requests.get(initial_link)
    soup = BeautifulSoup(ret.text, 'html.parser')
    posts = soup.find_all('article', class_='tm-articles-list__item')
    post_links = []
    for post in posts:
        post_link = post.find('a', class_='tm-article-snippet__title-link').get('href')
        post_links.append(post_link)
    return post_links

def check_habr_links(post_links):
    for post_link in tqdm(post_links):
        ret = requests.get(f'https://habr.com{post_link}')
        soup = BeautifulSoup(ret.text, 'html.parser')

        post_hubs = soup.find_all(class_='tm-article-snippet__hubs-item')
        post_text = soup.find(id='post-content-body').get_text(' ')
        if (check_post_hubs(post_hubs) or check_post_text(post_text)) == 1:
            post_time = soup.find('time').get('title')
            post_h2 = soup.find('h1').find('span').text
            print(f'\n {post_time} - {post_h2} - https://habr.com{post_link}')


def check_post_hubs(post_hubs):
    for post_hub in post_hubs:
        post_hub_span = post_hub.find('span').text
        post_hub_lower = post_hub_span.lower()
        if any([post_hub_lower in desired for desired in DESIRED_HUBS]):
            return 1


def check_post_text(post_text):
    tokens_list = nltk.word_tokenize(post_text.lower(), 'russian')
    tokens_list_clear = [token for token in tokens_list if token not in STOPWORDS and token not in punctuation]
    morph = pymorphy2.MorphAnalyzer()
    lemms_list = [morph.parse(word)[0].normal_form for word in tokens_list_clear]
    if any([desired in lemms_list for desired in DESIRED_HUBS]):
        return 1


check_habr_links(get_habr_links('https://habr.com/ru/all/'))

