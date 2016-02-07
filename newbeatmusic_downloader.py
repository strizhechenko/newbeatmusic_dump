#coding: utf-8
""" Выкачивает все трэки со стены группы вконтакте """
import json
import os
import urllib
import urllib2
from urlparse import urlparse
from sys import argv
import HTMLParser

HTML = HTMLParser.HTMLParser()
API_URL = 'https://api.vk.com/method'

def get_group_id():
    """ сперва проверяем аргументы, затем env, затем берём дефолтное """
    return len(argv) > 1 and argv[1] or (os.environ.get('ID') or '18312682')


def wall_post_count_get(url):
    """ узнаём число постов на стене """
    return json.load(urllib2.urlopen(url + '&count=1')).get('response')[0]


def simplify(attach):
    """ отдаём упрощённое описание трэка """
    audio = attach.get('audio')
    url = audio.get('url')
    return {
        'url': url.replace('?' + urlparse('url').query, ''),
        'title': HTML.unescape(audio['title']),
        'performer': HTML.unescape(audio['performer']),
    }


def download(track):
    """ скачиваем и сохраняем трэк """
    data = (track['performer'], track['title'])
    print ("Download: %s - %s" % data).encode('utf-8')
    # в два захода, чтобы не сделать download/x в downloadx
    filename = ("%s - %s.mp3" % data).replace("/", "")
    filename = "download/%s" % (filename,)
    if os.path.isfile(filename):
        print "... already here, skip"
        return
    if not track['url']:
        print '... no url, skip'
        return
    urllib.urlretrieve(track['url'], filename)


def download_all_response(url):
    """ выкачиваем все аудио из полученного ответа """
    response = json.load(urllib2.urlopen(url)).get('response')
    response.remove(response[0])
    posts = [post for post in response if post.get('attachments')]
    for post in posts:
        attachments = [a for a in post['attachments'] if a['type'] == 'audio']
        attachments = map(simplify, attachments)
        for attach in attachments:
            download(attach)


def main():
    group_id = get_group_id()
    wall_get_url = '%s/wall.get?owner_id=-%s' % (API_URL, group_id,)
    wall_post_count = wall_post_count_get(wall_get_url)
    if not os.path.isdir('download'):
        os.mkdir('download')
    for offset in range(0, wall_post_count, 100):
        url = "%s&count=100&offset=%d" % (wall_get_url, offset)
        download_all_response(url)

if __name__ == '__main__':
    main()
