from lxml import html
import requests
import re
import settings

BASE_URL = 'http://www.emuparadise.me'
LIST_URL = settings.settings['listUrl']

EU_REGEX = re.compile('\((?i)(eu)\)|\((?i)(e)\)')
DS_REGEX = re.compile('\b([ds|DS])\w+')
TAG_REGEX = re.compile(r'(\(.+?\))')
SPECIAL_REGEX = re.compile('[^A-Za-z0-9]+')
RELEASE_NO_REGEX = re.compile(r'(?<=Nintendo DS Release #)\d+')

IMG_BASE_URL = 'http://s.emuparadise.org/ndsbox1/'
IMG_ICON_SUFFIX = 'i.gif'
IMG_BOX_SUFFIX = 'a.jpg'
IMG_SCREEN_SUFFIX = 'b.jpg'

WEIGHTED_RATING_LIMIT = 5


def get_games():
    page = requests.Session().get(BASE_URL + LIST_URL)

    tree = html.fromstring(page.text)
    bucket_elems = tree.find_class('gamelist')

    game_list = []
    count = 0
    duplicate_count = 0

    # prints count also
    full_count = count_all(bucket_elems)

    for elem in bucket_elems:
        if re.search(EU_REGEX, elem.text_content()):

            name_detagged = re.sub(TAG_REGEX, '', elem.text_content())
            name_stripped = strip_special_lower(name_detagged)

            # only adds if the game isn't already matching another
            # Have NOT yet tested this on full list - could be VERY slow TODO
            # But then again the time used on searching the list is probably saved in NOT getting the game ID
            if not any(game['stripped_name'] == name_stripped for game in game_list):
                game_details = {
                    'id': count,
                    'name': name_detagged,
                    'stripped_name': name_stripped,
                    'link': BASE_URL + elem.attrib['href'] + '-download'
                }

                game_page = requests.Session().get(BASE_URL + elem.attrib['href'])

                king_dict = add_dict({}, game_details)
                king_dict = add_dict(king_dict, get_ratings(game_page))
                king_dict = add_dict(king_dict, get_pictures(game_page))

                count += 1

                game_list.append(king_dict)
                print('Added Game ' + str(count) + '/' + str(full_count) + ': ' + king_dict['name'])
                # print(game_details)
            else:
                duplicate_count += 1

        #  if count >= 50:  # Just to limit the amount of time between test runs - instead of getting all 2000+ links
        #      break

    print '\nTOTAL DUPLICATES: ' + str(duplicate_count)

    return game_list


def count_all(bucket_elems):
    full_count = 0
    for elem in bucket_elems:
        if re.search(EU_REGEX, elem.text_content()):
            full_count += 1
    print('Total of ' + str(full_count) + ' games')
    return full_count


def add_dict(initial, add):
    for key, value in add.items():
        initial[key] = value

    return initial


def strip_special_lower(string):
    stripped_string = re.sub(DS_REGEX, '', string)
    stripped_string = re.sub(SPECIAL_REGEX, '', stripped_string)
    stripped_string = stripped_string.lower()

    return stripped_string


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
            'screenshot': screenshot_url,
            'id': game_no.group(0)
        }
    else:
        images_urls = {
            'icon': '',
            'boxart': '',
            'screenshot': '',
            'emu_id': ''
        }

    return images_urls


if __name__ == "__main__":
    get_games()