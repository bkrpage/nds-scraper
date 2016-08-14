from lxml import html
import requests
import re

BASE_URL = 'http://www.emuparadise.me'

LIST_URL = "/Nintendo_DS_ROMs/List-All-Titles/32"

patterns = [ '\(e\)', '\(E\)', '\(eu\)', '\(EU\)', '\(Eu\)' ]

RELEASE_NO_REGEX = re.compile(r'(?<=Nintendo DS Release #)\d+')

IMG_BASE_URL       = 'http://s.emuparadise.org/ndsbox1/'
IMG_ICON_SUFFIX    = 'i.gif'
IMG_BOX_SUFFIX     = 'a.jpg'
IMG_SCREEN_SUFFIX  = 'b.jpg'

def getGames():
    page = requests.Session().get(BASE_URL + LIST_URL)

    tree = html.fromstring(page.text)
    bucket_elems = tree.find_class('gamelist')

    for elem in bucket_elems:
        for pattern in patterns:
            if re.search(pattern, elem.text_content()):
                game_page = requests.Session().get(BASE_URL + elem.attrib['href'])
                doc_line  = '\'=HYPERLINK("' + BASE_URL + elem.attrib['href'] + '-download","' + elem.text_content() + '") ; '
                doc_line += getRatings(game_page)
                doc_line += getPictures(game_page)
                print(doc_line)


def getRatings(game_page):
    tree = html.fromstring(game_page.text)

    rating = tree.findall(".//span[@itemprop='ratingValue']")[0].text_content()
    rating_count = tree.findall(".//span[@itemprop='ratingCount']")[0].text_content()

    return '\'' + rating + ';\'' + rating_count + ';'


def getPictures(game_page):
    tree = html.fromstring(game_page.text)

    img_div = tree.find_class('download-link')[0].text_content()

    img_string = ''
    game_no = re.search(RELEASE_NO_REGEX, img_div)
    if game_no:
        icon_url       = IMG_BASE_URL + game_no.group(0) + IMG_ICON_SUFFIX
        boxart_url     = IMG_BASE_URL + game_no.group(0)  + IMG_BOX_SUFFIX
        screenshot_url = IMG_BASE_URL + game_no.group(0)  + IMG_SCREEN_SUFFIX

        img_string  = '\'=HYPERLINK("' + icon_url + '", "Icon") ; '
        img_string += '\'=HYPERLINK("' + boxart_url + '", "Box Art") ; '
        img_string += '\'=HYPERLINK("' + screenshot_url + '", "Screenshot") ; '
    else:
        img_string = '\';\';\';'

    return img_string


if __name__ == '__main__':
    getGames()