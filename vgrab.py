#!/usr/bin/env python
import os
import re
import requests
from urlparse import urlparse, parse_qs
import urllib

import feedparser
from slugify import slugify

ATOM_FEED = "http://gdata.youtube.com/feeds/base/users/redecentralize/uploads?alt=rss&v=2"
INFO_LIST ="https://www.youtube.com/get_video_info?eurl=https://youtube.googleapis.com/v/{id}&video_id={id}"
YTDL_GET  = "youtube-dl --no-progress -f {0} -o {1} {2}"
FOLDER = "/var/www/redecentralise.net/video"


def info_for_video(link):
    info = {}

    obj = urlparse(link).query[2:]
    r = requests.get(INFO_LIST.format(id=obj))
    qs = parse_qs(r.content)
    info['poster_large'] = qs['iurlmaxres'][0]
    # Should parse this from qs['fmt_list']
    info['formats'] = {'webm': 43, 'mp4': 18}
    return info

# Get the feed
feed = feedparser.parse(ATOM_FEED)
for item in feed.entries:
    title, link = item.title, item.link
    # Tiny bit of cleanup
    title = slugify(title)
    if title.startswith("redecentralize-interviews-"):
        title = title[len("redecentralize-interviews-"):]
    link = link[0:link.find('&')]

    info = info_for_video(link)
    poster = os.path.join(FOLDER, title + ".jpg")
    urllib.urlretrieve(info['poster_large'], poster)

    for ext, fmt in info['formats'].iteritems():
        out = os.path.join(FOLDER, title + "." + ext)
        if os.path.exists(out):
            print "Skipping fmt:{0} for {1}".format(ext, title)
            continue
        else:
            print "Fetching {0} as {1}".format(title, ext)

            get_cmd = YTDL_GET.format(fmt, out, link)
            # Run the command and just wait
            f = os.popen(get_cmd)
            # We have to consume the data otherwise it will blow up.
            while True:
                data = f.read(2048)
                if not data:
                    break
