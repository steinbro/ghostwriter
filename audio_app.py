#!/usr/bin/env python

import curses
import time

import fluidsynth
import pyttsx


class AudioApp(object):
    '''Base class for auditory UI.'''
    def __init__(self, args):
        # initialize text-to-speech
        self.narrator = pyttsx.init()
        #self.narrator.setProperty('voice', 'english-us')  # espeak
        self.narrator.setProperty('rate', 500)

        # initialize audio synthesizer
        self.synth = fluidsynth.Synth()
        self.synth.start()

        example = self.synth.sfload('example.sf2')
        self.synth.program_select(0, example, 0, 0)

    def speak(self, phrase):
        self.narrator.say(phrase)
        self.narrator.runAndWait()

    def speak_char(self, char):
        # TTS engine might not know how to pronounce these characters
        mapping = {
            'y': 'why',
            '.': 'dot',
            ' ': 'space',
            ',': 'comma',
            ';': 'semicolon',
            '-': 'dash',
            ':': 'colon',
            '/': 'slash',
            '\\': 'backslash',
            '?': 'question mark',
            '!': 'bang',
            '@': 'at',
            '#': 'pound',
            '$': 'dollar',
            '%': 'percent',
            '*': 'star',
            '^': 'caret',
            '~': 'squiggle'
        }
        speakable = char.lower()

        if speakable in mapping:
            speakable = mapping[speakable]
        elif char.isalpha():
            speakable = char
        else:
            speakable = 'splork'  # say something better

        return self.speak(speakable) 

    def play_interval(self, size, duration, root=80, delay=0, intensity=30, channel=0):
        self.synth.noteon(channel, root, intensity)
        time.sleep(delay)
        self.synth.noteon(channel, root + size, intensity)
        time.sleep(duration)
        self.synth.noteoff(channel, root)
        self.synth.noteoff(channel, root + size)

    def handle_key(self, key):
        '''Individual apps (subclasses) must override this method.'''
        raise NotImplementedError

    def run(self):
        '''Loop indefinitely, passing keystrokes to handle_key until that
        method returns false.'''
        try:
            stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            stdscr.keypad(1)

            while True:
                c = stdscr.getch()
                if not self.handle_key(c): break

        finally:
            curses.nocbreak()
            stdscr.keypad(0)
            curses.echo()
            curses.endwin()

    # for debugging
    def simulate_keystroke(self, key):
        #time.sleep(random.uniform(0.01, 0.05))
        self.handle_key(key)

    def simulate_typing(self, string):
        for char in string:
            self.simulate_keystroke(ord(char))
