#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=unused-variable, anomalous-backslash-in-string

# Owned
__author__ = "Frederic Spiers"
__credits__ = ["Frederic Spiers", "-", "-"]
__license__ = "----"
__version__ = "4.4.3"
__date__ = "19/02/2021"
__maintainers__ = ["Frederic Spiers"]
__email1__ = "fredspiers@gmail.com"
__status__ = "Released"

# EXAMPLE OF SOURCE/TARGET structure :
# example =	{
#     "name": "example",
#     "api": "api.example.local:5000",
#     "registry": "example.io",
#     "user": "admin",
#     "pwd": "password",
#     "sa": "default_sa",
#     "token": "oaUtbGciOiJSUzI1NiIefjoiHGda",
#     "ns": ""
# }

import re
import subprocess
import sys

invisible_char = '[\\s\\t\\n]+'
manifest_version = 'v2s2'

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    INFO = '\033[93m'
    WARNING = '\033[43m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    LOGIN = '\033[96m'

def convert_bytes_to_string(bytes):
    string = ''.join(map(chr, bytes))
    return string

def fetch_credentials(sa, token):
    if not sa or not token:
        print(f'{bcolors.HEADER}[ WARNING ] > Using empty credentials.{bcolors.ENDC}')
        credentials = 'null'
    else:
        credentials = f"{sa}:{token}"
    return credentials

def run_cmd(cmd, error_string=None):
    try:
        subprocess.run([cmd], shell=True, check=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        if error_string is None:
            print(f'{bcolors.FAIL}[ ERROR ] >> FAILED to execute cmd {cmd}.{bcolors.ENDC}')
        else:
            print(f'{error_string}')
        print(convert_bytes_to_string(e.stderr))
        sys.exit(1)

def popen_cmd(cmd, error_string=None):
    sub = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = sub.stdout.readlines()
    output, errors = sub.communicate()
    if errors:
        if error_string is None:
            print(f'{bcolors.FAIL}[ ERROR ] >> FAILED to execute cmd {cmd}.{bcolors.ENDC}')
        else:
            print(f'{error_string}')
        print(f'{convert_bytes_to_string(errors)}')
        sys.exit(1)
    else:
        return result

def skopeo_version():
    print(f'{bcolors.LOGIN}[ SKOPEO VERSION ] >> Displaying skopeo version...{bcolors.ENDC}')
    cmd = 'skopeo --version'
    error_str = f'{bcolors.FAIL}[ ERROR ] >> Skopeo FAILED to display version.{bcolors.ENDC}'
    run_cmd(cmd, error_str)

def skopeo_login(creds):
    print(f'{bcolors.LOGIN}[ SKOPEO LOGIN ] >> login to {creds.get("name")} registry : https://{creds.get("registry")}...{bcolors.ENDC}')
    cmd = f'skopeo login --tls-verify=false {creds.get("registry")} -u {creds.get("sa")} -p {creds.get("token")}'
    error_str = f'{bcolors.FAIL}[ ERROR ] >> Skopeo FAILED to login {creds.get("name")}.{bcolors.ENDC}'
    run_cmd(cmd, error_str)

def skopeo_copy(src_img, dst_img, src_mode, dst_mode, source, target):
    src_cred = fetch_credentials(source.get("sa"), source.get("token"))
    dst_cred = fetch_credentials(target.get("sa"), target.get("token"))
    cmd = f'skopeo copy --insecure-policy \
                        --format {manifest_version} \
                        --src-tls-verify=false \
                        --src-creds={src_cred} \
                        --dest-tls-verify=false \
                        --dest-creds={dst_cred} \
                        {src_mode}{src_img} \
                        {dst_mode}{dst_img}'
    print(cmd)
    error_str = f'{bcolors.FAIL}[ ERROR ] >> FAILED to download image {src_img}.{bcolors.ENDC}'
    print(f'{bcolors.INFO}[ SKOPEO COPY ] >> transfer from {src_mode}{src_img} to {dst_mode}{dst_img}{bcolors.ENDC}')
    run_cmd(cmd, error_str)

def skopeo_multiple_copy(data, src_mode, dst_mode, source, target):
    if source.get('name') == 'docker-hub':
        print(f'{bcolors.INFO}[ INFO ] >> Multiple transfer from PUBLIC registry{bcolors.ENDC}')
        for line, value in enumerate(data):
            value = re.sub(invisible_char, '', value)
            img_split = value.split('/')
            img_only = f'{img_split[-1]}'
            src_img = f'{value}'
            dst_img = f'{target.get("registry")}/{target.get("ns")}/{img_only}'
            skopeo_copy(src_img, dst_img, src_mode, dst_mode, source, target)
    else:
        print(f'{bcolors.INFO}[ INFO ] >> Multiple transfer from PRIVATE registry{bcolors.ENDC}')
        for line, value in enumerate(data):
            value = re.sub(invisible_char, '', value)
            img_split = value.split('/')
            img_only = f'{img_split[-1]}'
            src_img = f'{source.get("registry")}/{source.get("ns")}/{img_only}'
            dst_img = f'{target.get("registry")}/{target.get("ns")}/{img_only}'
            skopeo_copy(src_img, dst_img, src_mode, dst_mode, source, target)

def skopeo_list_img_tags(img, source=None, release=None):
    if source is None:
        if release is not None:
            print(f'{bcolors.OKBLUE}[ SKOPEO ] >> Fetching all image version of release {release} on repository {img} {bcolors.ENDC}')
            #cmd = f"skopeo list-tags --tls-verify=false docker://{img} | jq '.Tags' | grep -e '^\\s*\"{release}'"
            cmd = f"skopeo list-tags --tls-verify=false docker://{img} | jq '.Tags' | jq '.[]' | jq 'select(test(\"{release}\"))'"
        else:
            print(f'{bcolors.OKBLUE}[ SKOPEO ] >> Fetching all images on repository {img} {bcolors.ENDC}')
            cmd = f"skopeo list-tags --tls-verify=false docker://{img} | jq '.Tags' | jq '.[]'"
    else:
        if release is not None:
            print(f'{bcolors.OKBLUE}[ SKOPEO ] >> Fetching all images version of release {release} on repository {img} {bcolors.ENDC}')
            #cmd = f"skopeo list-tags --tls-verify=false docker://{img} --creds {source.get('sa')}:{source.get('token')} | jq '.Tags' | grep '^\\s*\"{release}'"
            cmd = f"skopeo list-tags --tls-verify=false docker://{img} --creds {source.get('sa')}:{source.get('token')} | jq '.Tags' | jq '.[]' | jq 'select(test(\"{release}\"))'"
        else:
            print(f'{bcolors.OKBLUE}[ SKOPEO ] >> Fetching all images on repository {img} {bcolors.ENDC}')
            cmd = f"skopeo list-tags --tls-verify=false docker://{img} --creds {source.get('sa')}:{source.get('token')} | jq '.Tags' | jq '.[]'"
    error_str = f'{bcolors.FAIL}[ ERROR ] >> FAILED to catch {img} tags.'
    print(cmd)
    result = popen_cmd(cmd, error_str)
    return result
