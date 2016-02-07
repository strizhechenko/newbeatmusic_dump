#!/usr/bin/env python

# coding: utf-8
"""
Download all tracks from vk.com group wall to directory named by group id

How to set group id:
    ./download.py <group_id>
example:
    ./download.py 18312682
or by export environment variable VK_GROUP_ID:
    export VK_GROUP_ID=<group_id>
    ./download.py
example
    export VK_GROUP_ID=18312682
    ./download.py

By default group_id set to http://vk.com/newbeatmusic

You can known group id by viewing URL of some post on its wall.
"""

import os
import json
from sys import argv
from urllib import urlretrieve
from urllib2 import urlopen
from urlparse import urlparse
from HTMLParser import HTMLParser

HTML = HTMLParser()
API_URL = 'https://api.vk.com/method'
VK_GROUP_ID = os.environ.get('VK_GROUP_ID', '18312682')


def simplify(attach):
    """reduce dict and normalize url/title/performer values"""
    audio = attach.get('audio')
    url = audio.get('url')
    return {
        'url': url.replace('?' + urlparse(url).query, ''),
        'title': HTML.unescape(audio.get('title', 'Unknown song')),
        'performer': HTML.unescape(audio.get('performer', 'Unknown artist')),
    }


def download(track, group_id):
    """download and save tracks, skip if file already exist"""
    data = (track['performer'], track['title'])
    print ("Download: %s - %s" % data).encode('utf-8'), track.get('url')
    filename = ("%s - %s.mp3" % data).replace("/", "")
    filename = "%s/%s" % (group_id, filename)
    if os.path.isfile(filename):
        print "... already here, skip"
        return
    try:
        urlretrieve(track['url'], filename)
    except IOError:
        print '... hmmm, IOError :('


def download_all_response(url, group_id):
    """iterate tracks in current response, call download() for each of them"""
    response = json.load(urlopen(url)).get('response')[1:]
    posts = [post for post in response if post.get('attachments')]
    for post in posts:
        is_audio = lambda a: a['type'] == 'audio' and a.get('audio').get('url')
        attachments = filter(is_audio, post['attachments'])
        attachments = map(simplify, attachments)
        for attach in attachments:
            download(attach, group_id)


def __main__(group_id):
    if len(argv) > 1:
        group_id = argv[1].strip('/')
    if not os.path.isdir(group_id):
        os.mkdir(group_id)
    wall_url = '%s/wall.get?owner_id=-%s' % (API_URL, group_id)
    post_count = json.load(urlopen(wall_url + '&count=1')).get('response')[0]
    for offset in range(0, post_count, 100):
        url = "%s&count=100&offset=%d" % (wall_url, offset)
        download_all_response(url, group_id)

if __name__ == '__main__':
    if '--help' in argv:
        print __doc__
        exit()
    __main__(VK_GROUP_ID)
