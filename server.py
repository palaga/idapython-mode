#! /usr/bin/env python

import asynchat
import asyncore
import socket
import code
import threading
import sys
import cStringIO


class Handler(asynchat.async_chat):
    def __init__(self, sock, terminator="\n"):
        asynchat.async_chat.__init__(self, sock)
        self.set_terminator("\n")
        self.data = ""

        self.interp = code.InteractiveInterpreter()
        self._prompt()

    def collect_incoming_data(self, data):
        self.data += data

    def found_terminator(self):
        try:
            more = self.interp.runsource(self.data)
        except SyntaxError:
            self.interp.showsyntaxerror()
        except OverflowError:
            self.interp.showtraceback()
        self.data = ""

        self._push_buffer(sys.stdout)
        self._push_buffer(sys.stderr)

        self._prompt(more)

    def _prompt(self, more=False):
        self.push("... " if more else ">>> ")

    def _push_buffer(self, channel):
        if channel.tell() > 0:
            channel.seek(0)
            buf = channel.read()
            channel.truncate(0)
            if buf:
                self.push(buf)


class Server(asyncore.dispatcher):
    def __init__(self, host="127.0.0.1", port=8008, backlog=5):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(backlog)
        self.stdout = None
        self.stderr = None

    def handle_accept(self):
        pair = self.accept()
        if pair:
            sock, addr = pair
            print "Incomming connection from %s:%d" % addr
            print "Starting interpreter..."
            self._redirect_output()
            Handler(sock)
            self.close()

    def _redirect_output(self):
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.stdout = cStringIO.StringIO()
        sys.stderr = cStringIO.StringIO()

    def _restore_output(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr


def server_runner():
    s = Server()
    asyncore.loop()
    s._restore_output()


if __name__ == '__main__':
    print "Starting server"
    t = threading.Thread(target=server_runner)
    t.start()
    print "Running server in background"
