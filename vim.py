#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

import urllib 
import re

from flask import Flask, request
from flask import json
from reast import *


def bitly_shorten(url):
    query = ['version=2.0.1&longUrl=', '&login=raaniconama&apiKey=R_446879b310c0e904023fdda3e0b97998']
    u = "http://api.bit.ly/shorten?{query[0]}{url}{query[1]}".format(query=query, url=url)
    with urllib.request.urlopen(u) as f:
        data = f.read()
    return json.loads(data)["results"][url]['shortUrl']



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

class Dispatch(object):
    def __init__(self):
        self.mapping = {}

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

dispatch = Dispatch()

def handle(event):
    text = event['message']['text']
    room = event['message']['room']
    who = event['message']['speaker_id']


    m = rx.match(text)

    if m is None:
        return ''
    d = m.groupdict()
    assoc = cap.associate(d)
    
    f, name = dispatch.resolve(assoc)

    if f is None:
        return 'Command not implemented "{0}".'.format(text)

    b = bindable(assoc, d, (name,))
    missing, toomany = findbind(f, b)

    if missing:
        return 'No enough args {0}'.format(missing)
    if toomany:
        return 'Unknown argment {0}'.format(toomany)
    return f(**b)


@dispatch.bind('help')
def help(keyword=None):
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


@dispatch.bind('VimAdv')
def VimAdv(anId=None, ranking=None, me=None, user=None):
    atnd.populate()

    if not any((anId, ranking, me, user)):
        short = bitly_shorten(atnd.last['url'])
        return prn(atnd.last, short)

    if anId is not None:
        entry = atnd[int(anId)]
        short = bitly_shorten(entry['url'])
        return prn(entry, short)

    if me is not None:
        return '\n'.join([prn(entry, bitly_shorten(entry['url']))
            for entry in atnd.filter_by(author='@raa0121')])



@dispatch.bind('vimhacks')
def vimhacks():
    pass

@dispatch.bind('MacVim')
def MacVim():
    return 'http://bit.ly/f2fjvZ#.png'

@dispatch.bind('SEGV')
def SEGV():
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
        print(VimAdv())
        sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == '#me':
        print(VimAdv(me=True))
        sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        app.debug = True

    if app.debug:
        app.run()
    else:
        app.run(host='0.0.0.0', port=11002)




