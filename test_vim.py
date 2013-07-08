#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import json

import unittest

from vim import rx, ast, cap, handle, atnd
from reast import bindable


#print(ast.make_pat())


class reastTestCase(unittest.TestCase):
    def test_vimadv_empty(self):
        self.assertIsNotNone(rx.match(':vimadv'))
        self.assertIsNotNone(rx.match('!VimAdv'))
        self.assertIsNotNone(rx.match('!VAC'))

        assoc = cap.associate(rx.match(':vimadv').groupdict())
        self.assertIn('_VimAdv', assoc)
        assoc = cap.associate(rx.match('!VimAdv').groupdict())
        self.assertIn('_VimAdv', assoc)
        assoc = cap.associate(rx.match('!VAC').groupdict())
        self.assertIn('_VimAdv', assoc)


    def test_vimadv_ws(self):
        self.assertIsNotNone(rx.match(':vimadv '))
        self.assertIsNotNone(rx.match('!VimAdv '))
        self.assertIsNotNone(rx.match('!VAC '))

    def test_vimadv_id(self):
        self.assertIsNotNone(rx.match(':vimadv 42'))
        self.assertIsNotNone(rx.match('!VimAdv 42'))
        self.assertIsNotNone(rx.match('!VAC 42'))

        d = rx.match(':vimadv 42').groupdict()
        assoc = cap.associate(d)
        self.assertIn('_VimAdv', assoc)
        self.assertIn('_VimAdv_anId', assoc)
        b = bindable(assoc, d, ('VimAdv',))
        self.assertEqual('42', b['anId'])

        d = rx.match('!VimAdv 42').groupdict()
        assoc = cap.associate(d)
        self.assertIn('_VimAdv', assoc)
        self.assertIn('_VimAdv_anId', assoc)
        b = bindable(assoc, d, ('VimAdv',))
        self.assertEqual('42', b['anId'])

        d = rx.match('!VAC 42').groupdict()
        assoc = cap.associate(d)
        self.assertIn('_VimAdv', assoc)
        self.assertIn('_VimAdv_anId', assoc)
        b = bindable(assoc, d, ('VimAdv',))
        self.assertEqual('42', b['anId'])

    def test_vimadv_ranking(self):
        self.assertIsNotNone(rx.match(':vimadv #ranking42'))
        self.assertIsNotNone(rx.match('!VimAdv #ranking42'))
        self.assertIsNotNone(rx.match('!VAC #ranking42'))

        d = rx.match('!VAC #ranking42').groupdict()
        assoc = cap.associate(d)
        self.assertIn('_VimAdv', assoc)
        self.assertIn('_VimAdv_anId', assoc)
        b = bindable(assoc, d, ('VimAdv',))
        self.assertEqual('42', b['anId'])
        self.assertEqual('ranking', b['ranking'])

        d = rx.match('!VAC #ranking').groupdict()
        assoc = cap.associate(d)
        self.assertIn('_VimAdv', assoc)
        self.assertNotIn('_VimAdv_anId', assoc)
        b = bindable(assoc, d, ('VimAdv',))
        self.assertNotIn('anId', b)
        self.assertEqual('ranking', b['ranking'])


    def test_vimadv_ranking(self):
        self.assertIsNotNone(rx.match(':vimadv #ranking 42'))
        self.assertIsNotNone(rx.match(':vimadv #ranking   42'))
        self.assertIsNotNone(rx.match('!VimAdv #ranking 42'))
        self.assertIsNotNone(rx.match('!VimAdv #ranking   42'))
        self.assertIsNotNone(rx.match('!VAC #ranking 42'))
        self.assertIsNotNone(rx.match('!VAC #ranking      42'))


        d = rx.match('!VAC #ranking              42').groupdict()
        assoc = cap.associate(d)
        self.assertIn('_VimAdv', assoc)
        self.assertIn('_VimAdv_ranking_anId', assoc)
        b = bindable(assoc, d, ('VimAdv',))
        self.assertEqual('42', b['anId'])
        self.assertEqual('#ranking              42', b['ranking'])


    def test_help(self):
        self.assertIsNotNone(rx.match(':h'))
        self.assertIsNotNone(rx.match(':help'))
        self.assertIsNone(rx.match(':hel'))
        self.assertIsNone(rx.match(':he'))

    def test_vimhacks_empty(self):
        self.assertIsNotNone(rx.match(':vimhacks'))

        d = rx.match(':vimhacks').groupdict()
        assoc = cap.associate(d)
        self.assertIn('_vimhacks', assoc)
        self.assertNotIn('_vimhacks_anId', assoc)
        self.assertNotIn('_vimhacks_keyword', assoc)
        b = bindable(assoc, d, ('vimhacks',))
        self.assertNotIn('anId', b)
        self.assertNotIn('keyword', b)

    def test_vimhacks_empty(self):
        self.assertIsNotNone(rx.match(':vimhack'))

    def test_vimhacks_id(self):
        self.assertIsNotNone(rx.match(':vimhacks 42'))
        self.assertIsNotNone(rx.match(':vimhacks   42'))

        d = rx.match(':vimhacks 42').groupdict()
        assoc = cap.associate(d)
        self.assertIn('_vimhacks', assoc)
        self.assertIn('_vimhacks_anId', assoc)
        self.assertNotIn('_vimhacks_keyword', assoc)
        b = bindable(assoc, d, ('vimhacks',))
        self.assertIn('anId', b)
        self.assertIn('42', b['anId'])
        self.assertNotIn('keyword', b)

    def test_vimhack_id(self):
        self.assertIsNotNone(rx.match(':vimhack 42'))
        self.assertIsNotNone(rx.match(':vimhack   42'))

    def test_vimhacks_keyword(self):
        self.assertIsNotNone(rx.match(':vimhacks foobar'))
        self.assertIsNotNone(rx.match(':vimhacks       foobar'))

        d = rx.match(':vimhacks foobar').groupdict()
        assoc = cap.associate(d)
        self.assertIn('_vimhacks', assoc)
        self.assertNotIn('_vimhacks_anId', assoc)
        self.assertIn('_vimhacks_keyword', assoc)
        b = bindable(assoc, d, ('vimhacks',))
        self.assertNotIn('anId', b)
        self.assertIn('keyword', b)
        self.assertIn('foobar', b['keyword'])

    def test_vimhack_keyword(self):
        self.assertIsNotNone(rx.match(':vimhack foobar'))
        self.assertIsNotNone(rx.match(':vimhack       foobar'))

    def test_vimhacks_keyword_segv(self):
        self.assertIsNotNone(rx.match(':vimhacks SEGV'))

        d = rx.match(':vimhacks SEGV').groupdict()
        assoc = cap.associate(d)
        self.assertIn('_vimhacks', assoc)
        self.assertNotIn('_vimhacks_anId', assoc)
        self.assertIn('_vimhacks_keyword', assoc)
        b = bindable(assoc, d, ('vimhacks',))
        self.assertNotIn('anId', b)
        self.assertIn('keyword', b)
        self.assertIn('SEGV', b['keyword'])

    def test_vimhack_keyword_segv(self):
        self.assertIsNotNone(rx.match(':vimhack SEGV'))

    def test_macvim(self):
        self.assertIsNotNone(rx.match('またMacVimか'))

    def test_segv(self):
        self.assertIsNotNone(rx.match('RubyたんがSEGVした'))
    


class HandleTestCase(unittest.TestCase):
    def say(self, user, text):
        return json.dumps(dict(events=[dict(message=dict(
            text=text, speaker_id=user, room="computer_science"))]))

    def test_say(self):
        j = self.say('raa0121', 'test')
        req = json.loads(j)
        event = req['events'][0]
        self.assertIn('message', event)
        self.assertIn('text', event['message'])
        self.assertIn('test', event['message']['text'])
        self.assertIn('speaker_id', event['message'])
        self.assertIn('raa0121', event['message']['speaker_id'])


    def test_macvim(self):
        req = json.loads(self.say('raa0121', 'またMacVimか'))
        response = handle(req['events'][0])
        self.assertEqual('http://bit.ly/f2fjvZ#.png', response)

    def test_help_empty(self):
        req = json.loads(self.say('raa0121', ':h'))
        response = handle(req['events'][0])
        self.assertEqual('', response)

    def test_help_not_found(self):
        req = json.loads(self.say('raa0121', ':help hoge'))
        response = handle(req['events'][0])
        self.assertEqual('http://gyazo.com/f71ba83245a2f0d41031033de1c57109.png', response)

class AtndTestCase(unittest.TestCase):
    def test_get(self):
        pass
    def test_parseline(self):
        line = """|213|07/01(月)|@manga_osyo|"Vim で Web ページを :source する":http://d.hatena.ne.jp/osyo-manga/20130701/1372680621|"""
        d = atnd.parse(line)
        self.assertEqual(dict(
            count='213',
            date='07/01(月)',
            author='@manga_osyo',
            title='Vim で Web ページを :source する', 
            url='http://d.hatena.ne.jp/osyo-manga/20130701/1372680621'),
            d)


if __name__ == '__main__':
    unittest.main()
