#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=unused-variable, anomalous-backslash-in-string

import re
import subprocess
import sys
import json
from colorama import init, Fore, Back, Style

init(autoreset=True)

def convert_bytes_to_string(bytes):
    string = ''.join(map(chr, bytes))
    return string

def convert_bytes_list_to_clean_str_list(bytes_list):
    clean_str_list = []
    for bytes_elem in bytes_list:
        str_elem = convert_bytes_to_string(bytes_elem)
        purged_tag = re.sub('[\\s\",\\n]', '', str_elem)
        clean_str_list.append(purged_tag)
    return clean_str_list

def check_regex(string, pattern):
    if pattern.search(string):
        return True
    else:
        return False

def load_json(json_file_path):
    try:
        json_file = open(json_file_path, 'r')
        try:
            python_dict = json.load(json_file)
        except json.decoder.JSONDecodeError:
            print(f' {Fore.RED}{Style.BRIGHT}[ ERROR ] >> File {json_file_path} could not be converted to json.{bcolors.ENDC}')
            sys.exit(1)
    except IOError:
        print(f' {Fore.RED}{Style.BRIGHT}[ ERROR ] >> Failed to open file {json_file_path}.{bcolors.ENDC}')
        sys.exit(1)
    return python_dict

def run_cmd(cmd, error_string=None, debug=False ):
    if debug:
        print(cmd)
    try:
        subprocess.run([cmd], shell=True, check=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        if error_string is None:
            print(f' {Fore.RED}{Style.BRIGHT}[ ERROR ] >> FAILED to execute cmd {cmd}.{bcolors.ENDC}')
        else:
            print(f'{error_string}')
        print(convert_bytes_to_string(e.stderr))
        sys.exit(1)

def popen_cmd(cmd, error_string=None, debug=False):
    if debug:
        print(cmd)
    sub = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = sub.stdout.readlines()
    output, errors = sub.communicate()
    if errors:
        if error_string is None:
            print(f' {Fore.RED}{Style.BRIGHT}[ ERROR ] >> FAILED to execute cmd {cmd}.{bcolors.ENDC}')
        else:
            print(f'{error_string}')
        print(f'{convert_bytes_to_string(errors)}')
        sys.exit(1)
    else:
        return result