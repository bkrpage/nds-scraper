from lxml import html
from lxml.html import builder as E
from jinja2 import Environment
import requests
import re
import settings

BASE_URL = 'http://www.emuparadise.me'
LIST_URL = settings.settings['listUrl']

RELEASE_NO_REGEX = re.compile(r'(?<=Nintendo DS Release #)\d+')
TAG_REGEX = re.compile(r'(\(.+?\))')

IMG_BASE_URL = 'http://s.emuparadise.org/ndsbox1/'
IMG_ICON_SUFFIX = 'i.gif'
IMG_BOX_SUFFIX = 'a.jpg'
IMG_SCREEN_SUFFIX = 'b.jpg'


def get_games():
    page = requests.Session().get(BASE_URL + LIST_URL)

    tree = html.fromstring(page.text)
    bucket_elems = tree.find_class('gamelist')

    game_list = []
    full_count = 0
    count = 0

    for elem in bucket_elems:
        for pattern in settings.settings['patterns']:
            if re.search(pattern, elem.text_content()):
                full_count += 1

    print('Total of ' + str(full_count) + ' games')

    for elem in bucket_elems:
        for pattern in settings.settings['patterns']:
            if re.search(pattern, elem.text_content()):
                name_detagged = re.sub(TAG_REGEX, '', elem.text_content())
                game_page = requests.Session().get(BASE_URL + elem.attrib['href'])

                game_details = {'name': name_detagged, 'link': BASE_URL + elem.attrib['href'] + '-download'}

                king_dict = add_dict({}, game_details)
                king_dict = add_dict(king_dict, get_ratings(game_page))
                king_dict = add_dict(king_dict, get_pictures(game_page))

                count += 1

                game_list.append(king_dict)
                print('Added Game ' + str(count) + '/' + str(full_count) + ': ' + king_dict['name'])

    generate_html(game_list)


def add_dict(initial, add_dict):
    for key, value in add_dict.items():
        initial[key] = value

    return initial


def get_ratings(game_page):
    tree = html.fromstring(game_page.text)

    rating = tree.findall(".//span[@itemprop='ratingValue']")[0].text_content()
    rating_count = tree.findall(".//span[@itemprop='ratingCount']")[0].text_content()

    ratings = {
        'rating': rating,
        'rating_count': rating_count
    }

    return ratings


def get_pictures(game_page):
    tree = html.fromstring(game_page.text)

    img_div = tree.find_class('download-link')[0].text_content()

    game_no = re.search(RELEASE_NO_REGEX, img_div)
    if game_no:
        icon_url = IMG_BASE_URL + game_no.group(0) + IMG_ICON_SUFFIX
        boxart_url = IMG_BASE_URL + game_no.group(0) + IMG_BOX_SUFFIX
        screenshot_url = IMG_BASE_URL + game_no.group(0) + IMG_SCREEN_SUFFIX

        images_urls = {
            'icon': icon_url,
            'boxart': boxart_url,
            'screenshot': screenshot_url
        }

    else:
        images_urls = {
            'icon': '',
            'boxart': '',
            'screenshot': ''
        }

    return images_urls

def generate_html(game_list):

    HTML = """
    <html>
    <head>
    <title>Test</title>
    </head>
    <body>
    <table>
        <thead>
            <th> Name </th>
            <th> Rating </th>
            <th> Rating Count </th>
        </thead>
        {% for dict in game_list %}
        <tr>
            <td> {{ dict["name"] }} </td>
            <td> {{ dict["rating"] }} </td>
            <td> {{ dict["rating_count"] }} </td>
        </tr>
        {% endfor %}
    </table>
    </body>
    </html>
    """
    print Environment().from_string(HTML).render(game_list=game_list)

if __name__ == '__main__':
    get_games()