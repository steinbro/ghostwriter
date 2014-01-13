#!/usr/bin/env python

import curses
import curses.ascii
import os
import sys

from audio_app import AudioApp


class TextEditor(AudioApp):
    def __init__(self, args):
        self.buffer = ''
        self.cursor = 0

        if len(args) > 1:
            path = args[1]
            if os.path.exists(path):
                f = open(path)
                self.buffer = f.read()
                f.close()
            self.fd = open(path, 'w')

        super(TextEditor, self).__init__(args)

    def move_left(self):
        if self.cursor > 0:
            self.cursor -= 1
            self.speak_char(self.buffer[self.cursor])
            return True
        else:
            self.play_interval(1, 0.1)
            return False

    def move_right(self):
        if self.cursor < len(self.buffer):
            self.speak_char(self.buffer[self.cursor])
            self.cursor += 1
            return True
        else:
            self.play_interval(1, 0.1)
            return False

    def insert_char(self, char):
        self.buffer = self.buffer[:self.cursor] + char + self.buffer[self.cursor:]
        self.cursor += 1

    def remove_char(self):
        if self.cursor == 0:
            self.play_interval(1, 0.1)
            return False

        old_char = self.buffer[self.cursor - 1]
        self.buffer = self.buffer[:self.cursor - 1] + self.buffer[self.cursor:]
        self.cursor -= 1
        return old_char

    def backspace(self):
        deleted = self.remove_char()
        if deleted:
            self.speak_char(deleted)

    def last_word(self, ending_at=None):
        if ending_at is None:
            ending_at = self.cursor - 1

        if self.cursor < 2:
            return self.buffer[0]

        start = ending_at - 1
        while self.buffer[start].isalpha() and start > 0:
            start -= 1

        return self.buffer[start:ending_at + 1].strip()

    def last_sentence(self, ending_at=None):
        if ending_at is None:
            ending_at = self.cursor - 1

        if self.cursor < 2:
            return self.buffer[0]

        start = ending_at - 1
        while self.buffer[start] != '.' and start > 0:
            start -= 1

        return self.buffer[start:ending_at + 1].strip('. ')

    def close(self):
        if hasattr(self, 'fd'):
            self.fd.write(self.buffer)  # write changes to disk
            self.fd.close()

    def handle_key(self, key):
        #sys.stderr.write(str(key))

        if key == curses.ascii.ESC:
            self.close()
            return False  # exit

        elif key == curses.KEY_LEFT:
            self.move_left()

        elif key == curses.KEY_RIGHT:
            self.move_right()

        elif key == curses.ascii.DEL:  #curses.KEY_BACKSPACE:
            self.backspace()
                
        elif curses.ascii.isalpha(key):
            self.insert_char(chr(key))

        elif curses.ascii.isprint(key) or curses.ascii.isspace(key):
            self.insert_char(chr(key))
            if chr(key) == '.':
                self.speak(self.last_sentence())
            else:
                self.speak(self.last_word())
            #sys.stderr.write(self.buffer + '\r')

        return True  # keep reading keystrokes


if __name__ == '__main__':
    app = TextEditor(sys.argv)
    app.run()
