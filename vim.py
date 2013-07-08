#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

from flask import Flask, request
from flask import json
from reast import *

ws = unnamed(" ")
def may_be(*xs):
    return Option(OneOrMore(ws), Option(*xs))

an_id = named('an_id', r'\d+')
keyword = named('keyword', r'\w+')

ranking = named('ranking', '#ranking', may_be(an_id))
me = named('me', '#me')
user = named('usr', 'ranking')


builder = Cat(Or(
    named("VimAdv", "", 
        Or(unnamed(r"\!VimAdv"), unnamed(r"\:vimadv"), unnamed(r"\!VAC")),
        may_be(Or(an_id, ranking, me, user)),
        ),
    named("help", ":h(elp)?"),
    named("vimhacks", ":vimhacks?", Or(
        may_be(an_id),
        may_be(keyword),
        )),
    named("MacVim", r"^またMacVimか"),
    named("SEGV", r".*SEGV.*"),
    ), unnamed("$"))

ast = builder.build()
rx = ast.compile()

app = Flask(__name__)


@app.route('/vim', methods=['GET', 'POST'])
def vim():
    if request.method == 'POST':
        array = json.loads(request.data)
        return ''.join([handle(event) for event in array['events']])
    else:
        return "VimAdvClone & :help"

def handle(event):
    text = event['message']['text']
    room = event['message']['room']
    who = event['message']['speaker_id']



def help():
    pass

def VimAdv():
    pass


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        app.debug = True

    if app.debug:
        app.run()
    else:
        app.run(host='0.0.0.0', port=11002)


