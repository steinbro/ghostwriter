#!/usr/bin/env python

import curses
import curses.ascii
import random
import string
import tempfile
import unittest

from text_editor import TextEditor


class TextEditorTest(unittest.TestCase):
    def setUp(self):
        self.outfile = tempfile.NamedTemporaryFile()
        self.args = ['text_editor.py', self.outfile.name]
        self.app = TextEditor(self.args)

        # Override the sound-generating methods with silent recordkeeping.
        self.utterances = []
        def instead_of_sounds(phrase, a=0, b=0, c=0, d=0, e=0):
            if type(phrase) is str:
                self.utterances.append(phrase)
            else:
                self.utterances.append('[tone]')
        self.app.speak = instead_of_sounds
        self.app.play_interval = instead_of_sounds

    def tearDown(self):
        #print repr(self.utterances)
        pass

    def test_simple(self):
        # should speak previous word after non-alpha character
        self.app.simulate_typing('hello world ')
        self.assertEqual(self.utterances[-1], 'world')

        # should speak character just deleted
        self.app.simulate_keystroke(curses.ascii.DEL)
        self.assertEqual(self.utterances[-1], 'space')

        # should play tone when attempting to move cursor beyond bounds
        self.app.simulate_keystroke(curses.KEY_RIGHT)
        self.assertEqual(self.utterances[-1], '[tone]')

        for i in range(5):  # move cursor five characters left
            self.app.simulate_keystroke(curses.KEY_LEFT)
        self.app.simulate_typing('awesome ')

        self.app.simulate_keystroke(curses.ascii.ESC)  # quit
        self.outfile.seek(0)

        # check that contents were properly saved
        self.assertEqual(self.outfile.read(), "hello awesome world")

    def test_symbols(self):
        self.app.simulate_typing('foo')
        self.app.simulate_keystroke(curses.ascii.ESC)  # quit

        self.app = TextEditor(self.args)  # re-open
        self.app.simulate_typing('~ ~')
        self.app.simulate_keystroke(curses.ascii.ESC)  # quit

        self.outfile.seek(0)
        self.assertEqual(self.outfile.read(), "~ ~foo")

    def test_gibberish(self):
        # type n random printable characters
        n = 100
        self.app.simulate_typing(
            random.choice(string.printable) for i in range(n))
        self.app.simulate_keystroke(curses.ascii.ESC)  # quit
        self.outfile.seek(0)

        self.assertEqual(n, len(self.outfile.read()))

if __name__ == '__main__':
    unittest.main()
