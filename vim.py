#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

import urllib 
import re

import itertools
import functools

from flask import Flask, request
from flask import json
from reast import *


def bitly_shorten(url):
    query = ['version=2.0.1&longUrl=', '&login=raaniconama&apiKey=R_446879b310c0e904023fdda3e0b97998']
    u = "http://api.bit.ly/shorten?{query[0]}{url}{query[1]}".format(query=query, url=url)
    with urllib.request.urlopen(u) as f:
        data = f.read()
    return json.loads(data)["results"][url]['shortUrl']


def ranknumbering(f, xs):
    last_v = None
    last_i = None
    for i, x in enumerate(xs):
        if last_v is not None and f(x, last_v):
            yield last_i, x
        else:
            yield i, x
            last_i = i
            last_v = x


class Atnd(object):
    r = re.compile(r"""\|(.*)\|(.*)\|(.*)\|"(.*)":(.*)\|""")

    def __init__(self):
        self.d = {}

    @property
    def last(self):
        return self.d[len(self.d)]

    def __getitem__(self, key):
        return self.d[key]

    def filter_by(self, **kw):
        return [v for v in self.d.values() if all([v[k] == kw[k] for k in kw])]

    def group_by(self, k):
        xs = list(self.d.values())
        xs.sort(key=lambda v: v[k])
        return [(k, list(g)) for k, g in itertools.groupby(xs,  lambda v:v[k])]
    
    def populate(self):
        s = self.get()
        for line in s.splitlines():
            d = self.parse(line)
            if d is not None:
                self.d[int(d['count'])] = d
        return len(self.d)

    def get(self): 
        with urllib.request.urlopen("http://api.atnd.org/events/?event_id=33746&format=json") as f:
            atnd = json.loads(f.read())
        return atnd['events'][0]['description']

    def parse(self, line):
        m = self.r.match(line)
        if m is None:
            return None
        g = m.groups()
        return dict(zip(('count','date', 'author', 'title', 'url'), (int(g[0]),)+g[1:]))



atnd = Atnd()



ws = unnamed(" ")
def may_be(*xs):
    return Option(OneOrMore(ws), Option(*xs))

an_id = named('anId', r'\d+')
keyword = named('keyword', r'\w+')

ranking = named('ranking', '#ranking', may_be(an_id))
me = named('me', '#me')
user = named('user', '\w+')

builder = Cat(Or(
    named("VimAdv", "", 
        Or(unnamed(r"\!VimAdv"), unnamed(r"\:vimadv"), unnamed(r"\!VAC")),
        may_be(Or(an_id, ranking, me, user)),
        ),
    named("help", ":h(elp)?", may_be(keyword)),
    named("vimhacks", ":vimhacks?", Or(
        may_be(an_id),
        may_be(keyword),
        )),
    named("MacVim", r"^またMacVimか"),
    named("SEGV", r".*SEGV.*"),
    ), unnamed("$"))

ast = builder.build()
rx = ast.compile()
cap = ast.make_capture()

app = Flask(__name__)


@app.route('/vim', methods=['GET', 'POST'])
def vim():
    if request.method == 'POST':
        array = json.loads(request.data)
        return ''.join([handle(event) for event in array['events']])
    else:
        return "VimAdvClone & :help"

class Dispatcher(object):
    def __init__(self, ast, on_no_match=None, on_missing=None, on_toomany=None, on_not_implemetned=None):
        self.mapping = {}
        self.on_no_match = on_no_match
        self.on_missing = on_missing
        self.on_toomany = on_toomany
        self.on_not_implemetned = on_not_implemetned
        self.ast = ast
        self.rx = ast.compile()
        self.cap = ast.make_capture()

    def bind(self, name):
        def foo(f):
            assert name not in self.mapping
            self.mapping[name] = f
            return f
        return foo

    def resolve(self, assoc):
        for k, c in assoc.items():
            if c.name in self.mapping:
                return self.mapping[c.name], c.name
        return None, None

    def dispatch(self, text, **kw):
        m = self.rx.match(text)
        if m is None:
            return self.on_no_match(text)

        d = m.groupdict()
        assoc = self.cap.associate(d)

        f, name = self.resolve(assoc)

        if f is None:
            return self.on_not_implemetned(text)

        f = functools.partial(f, **kw)

        b = bindable(assoc, d, (name,))
        missing, toomany = findbind(f, b)

        if missing:
            return self.on_missing(missing)
        if toomany:
            return self.on_toomany(missing)
        return f(**b)


dispatcher = Dispatcher(
        ast,
        on_no_match=lambda x : '',
        on_not_implemetned=lambda text: 'Command not implemented "{0}"'.format(text),
        on_missing=lambda missing : 'No enough args {0}'.format(missing),
        on_toomany=lambda toomany : 'Unknown argment {0}'.format(toomany),
        )

def handle(event):
    text = event['message']['text']
    room = event['message']['room']
    who = event['message']['speaker_id']
    return dispatcher.dispatch(text, room=room, who=who)


@dispatcher.bind('help')
def help(who, room, keyword=None):
    '''generate vim help from file

    a) using tag file to locate file
        tags = File.read("#{docroot}/tags").lines.map {|l| l.chomp.split("\t", 3) }
        t = tags.detect {|t| t[0] == help[1].sub(/@ja/,"").sub("+","\\+")}

    b) help in japanese
        if help[1] =~ /@ja/
        docroot = jadocroot
        t[1].sub! /.txt$/, '.jax'

    c) then scrape help file text
        text = File.read("#{docroot}/#{t[1]}")
    '''

    if keyword is None:
        return ''
    return 'http://gyazo.com/f71ba83245a2f0d41031033de1c57109.png'




def prn(entry, url):
    s = """{entry[count]} {entry[date]} {entry[author]} {entry[title]} - {url}"""
    return s.format(entry=entry, url=url)


@dispatcher.bind('VimAdv')
def VimAdv(room, who, anId=None, ranking=None, me=None, user=None):
    atnd.populate()

    if not any((anId, ranking, me, user)):
        short = bitly_shorten(atnd.last['url'])
        return prn(atnd.last, short)

    if anId is not None:
        entry = atnd[int(anId)]
        short = bitly_shorten(entry['url'])
        return prn(entry, short)

    if ranking is not None:
        if anId is None:
            rank = 10
        else:
            rank = int(anId)
        xs = list(map(lambda x : (x[0], len(x[1])), atnd.group_by('author')))
        xs.sort(key=lambda x: x[1], reverse=True)

        return '\n'.join(["{0} {1} {2}".format(i+1, name, count)
            for i, (name, count) in ranknumbering(lambda x, y: x[1] == y[1], xs[:rank])])


    if me is not None:
        return '\n'.join([prn(entry, bitly_shorten(entry['url']))
            for entry in atnd.filter_by(author=who)])



@dispatcher.bind('vimhacks')
def vimhacks(room, who):
    pass

@dispatcher.bind('MacVim')
def MacVim(room, who):
    return 'http://bit.ly/f2fjvZ#.png'

@dispatcher.bind('SEGV')
def SEGV(room, who):
    return "キャッシュ(笑)"


if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            n = 0
        if n > 0:
            print(VimAdv(n))
            sys.exit()

    if len(sys.argv) > 1 and sys.argv[1] == 'atnd':
        print(atnd.get())
        sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == 'pplt':
        print(atnd.populate())
        sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == 'VimAdv':
        print(VimAdv(who='@raa0121', room='computer_science'))
        sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == '#me':
        print(VimAdv(who='@raa0121', room='computer_science', me=True))
        sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == 'rank':
        print(VimAdv(who='@raa0121', room='computer_science', ranking=True))
        sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        app.debug = True

    if app.debug:
        app.run()
    else:
        app.run(host='0.0.0.0', port=11002)



