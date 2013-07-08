#!/usr/bin/python
# -*- coding: utf-8 -*-

from vim import rx, ast

import unittest

print(ast.make_pat())


class reastTestCase(unittest.TestCase):
    def test_vimadv_empty(self):
        self.assertIsNotNone(rx.match(':vimadv'))
        self.assertIsNotNone(rx.match('!VimAdv'))
        self.assertIsNotNone(rx.match('!VAC'))

    def test_vimadv_ws(self):
        self.assertIsNotNone(rx.match(':vimadv '))
        self.assertIsNotNone(rx.match('!VimAdv '))
        self.assertIsNotNone(rx.match('!VAC '))

    def test_vimadv_id(self):
        self.assertIsNotNone(rx.match(':vimadv 42'))
        self.assertIsNotNone(rx.match('!VimAdv 42'))
        self.assertIsNotNone(rx.match('!VAC 42'))

    def test_vimadv_ranking(self):
        self.assertIsNotNone(rx.match(':vimadv #ranking42'))
        self.assertIsNotNone(rx.match('!VimAdv #ranking42'))
        self.assertIsNotNone(rx.match('!VAC '))

    def test_vimadv_ranking(self):
        self.assertIsNotNone(rx.match(':vimadv #ranking 42'))
        self.assertIsNotNone(rx.match(':vimadv #ranking   42'))
        self.assertIsNotNone(rx.match('!VimAdv #ranking 42'))
        self.assertIsNotNone(rx.match('!VimAdv #ranking   42'))
        self.assertIsNotNone(rx.match('!VAC #ranking 42'))
        self.assertIsNotNone(rx.match('!VAC #ranking      42'))


    def test_help(self):
        self.assertIsNotNone(rx.match(':h'))
        self.assertIsNotNone(rx.match(':help'))
        self.assertIsNone(rx.match(':hel'))
        self.assertIsNone(rx.match(':he'))

    def test_vimhacks_empty(self):
        self.assertIsNotNone(rx.match(':vimhacks'))

    def test_vimhacks_empty(self):
        self.assertIsNotNone(rx.match(':vimhack'))

    def test_vimhacks_id(self):
        self.assertIsNotNone(rx.match(':vimhacks 42'))
        self.assertIsNotNone(rx.match(':vimhacks   42'))

    def test_vimhack_id(self):
        self.assertIsNotNone(rx.match(':vimhack 42'))
        self.assertIsNotNone(rx.match(':vimhack   42'))

    def test_vimhacks_keyword(self):
        self.assertIsNotNone(rx.match(':vimhacks foobar'))
        self.assertIsNotNone(rx.match(':vimhacks       foobar'))

    def test_vimhack_keyword(self):
        self.assertIsNotNone(rx.match(':vimhack foobar'))
        self.assertIsNotNone(rx.match(':vimhack       foobar'))

    def test_vimhacks_keyword_segv(self):
        self.assertIsNotNone(rx.match(':vimhacks SEGV'))

    def test_vimhack_keyword_segv(self):
        self.assertIsNotNone(rx.match(':vimhack SEGV'))

    def test_macvim(self):
        self.assertIsNotNone(rx.match('またMacVimか'))

    def test_segv(self):
        self.assertIsNotNone(rx.match('RubyたんがSEGVした'))
    
if __name__ == '__main__':
    unittest.main()
