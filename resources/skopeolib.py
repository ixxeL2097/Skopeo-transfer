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
#     "sa": "default_sa",
#     "token": "oaUtbGciOiJSUzI1NiIefjoiHGda",
#     "ns": "default"
# }

import re
import sys
import toolbox
from colorama import init, Fore, Back, Style

invisible_char = '[\\s\\t\\n]+'
manifest_version = 'v2s2'
debug = False
init(autoreset=True)

def fetch_credentials(sa, token):
    if not sa or not token:
        print(f'{Fore.MAGENTA}{Style.BRIGHT}[ WARNING ] >{Style.NORMAL} Using empty credentials.')
        credentials = 'null'
    else:
        credentials = f"{sa}:{token}"
    return credentials

def skopeo_version():
    print(f'{Fore.CYAN}{Style.BRIGHT}[ SKOPEO VERSION ] >> Displaying skopeo version...')
    cmd = 'skopeo --version'
    error_str = f' {Fore.RED}{Style.BRIGHT}[ ERROR ] >> Skopeo FAILED to display version.'
    toolbox.run_cmd(cmd, error_str)

def skopeo_login(creds):
    print(f'{Fore.CYAN}{Style.BRIGHT}[ SKOPEO LOGIN ] >> login to {creds.get("name")} registry : https://{creds.get("registry")}...')
    cmd = f'skopeo login --tls-verify=false {creds.get("registry")} -u {creds.get("sa")} -p {creds.get("token")}'
    error_str = f' {Fore.RED}{Style.BRIGHT}[ ERROR ] >> Skopeo FAILED to login {creds.get("name")}.'
    toolbox.run_cmd(cmd, error_str)

def skopeo_copy(src_img, dst_img, src_mode, dst_mode, source, target, safe=False):
    src_cred = fetch_credentials(source.get("sa"), source.get("token"))
    dst_cred = fetch_credentials(target.get("sa"), target.get("token"))
    if safe:
        print(f'{Fore.YELLOW}{Style.BRIGHT}[ INFO ] >>{Style.NORMAL} Skopeo using {Fore.RED}{Style.BRIGHT}SAFE TRANSFER MODE')
        img_only = f"{dst_img.split('/')[-1]}"
        cmd1 = f'skopeo copy --insecure-policy \
                             --format {manifest_version} \
                             --src-tls-verify=false \
                             --src-creds={src_cred} \
                             {src_mode}{src_img} \
                             dir:/tmp/{img_only}'

        cmd2 = f'skopeo copy --insecure-policy \
                             --format {manifest_version} \
                             --dest-tls-verify=false \
                             --dest-creds={dst_cred} \
                             dir:/tmp/{img_only} \
                            {dst_mode}{dst_img}'
        error_str = f'{Fore.RED}{Style.BRIGHT}[ ERROR ] >> FAILED to download image {src_img}.'
        print(f'{Fore.YELLOW}{Style.BRIGHT}[ SKOPEO PULL - STEP 1 ] >>{Style.NORMAL} transfer from {Style.BRIGHT}{src_mode}{src_img}{Style.NORMAL} to {Style.BRIGHT}dir:/tmp/{img_only}')
        toolbox.run_cmd(cmd1, error_str, debug)
        print(f'{Fore.YELLOW}{Style.BRIGHT}[ SKOPEO PUSH - STEP 2 ] >>{Style.NORMAL} transfer from {Style.BRIGHT}dir:/tmp/{img_only}{Style.NORMAL} to {Style.BRIGHT}{dst_mode}{dst_img}')
        toolbox.run_cmd(cmd2, error_str, debug)
    else:
        print(f'{Fore.YELLOW}{Style.BRIGHT}[ INFO ] >>{Style.NORMAL}  Skopeo using {Fore.RED}{Style.BRIGHT}DIRECT TRANSFER MODE')
        cmd = f'skopeo copy --insecure-policy \
                            --format {manifest_version} \
                            --src-tls-verify=false \
                            --src-creds={src_cred} \
                            --dest-tls-verify=false \
                            --dest-creds={dst_cred} \
                            {src_mode}{src_img} \
                            {dst_mode}{dst_img}'
        error_str = f'{Fore.RED}{Style.BRIGHT}[ ERROR ] >> FAILED to download image {src_img}. '
        print(f'{Fore.YELLOW}{Style.BRIGHT}[ SKOPEO COPY ] >>{Style.NORMAL} transfer from {Style.BRIGHT}{src_mode}{src_img}{Style.NORMAL} to {Style.BRIGHT}{dst_mode}{dst_img}')
        toolbox.run_cmd(cmd, error_str, debug)

def skopeo_multiple_copy(data, src_mode, dst_mode, source, target, safe=False):
    if source.get('name') == 'docker-hub':
        print(f'{Fore.YELLOW}{Style.BRIGHT}[ INFO ] >>{Style.NORMAL} Multiple transfer from PUBLIC registry')
        for line, value in enumerate(data):
            value = re.sub(invisible_char, '', value)
            img_only = f"{value.split('/')[-1]}"
            src_img = f'{value}'
            dst_img = f'{target.get("registry")}/{target.get("ns")}/{img_only}'
            skopeo_copy(src_img, dst_img, src_mode, dst_mode, source, target, safe)
    else:
        print(f'{Fore.YELLOW}{Style.BRIGHT}[ INFO ] >>{Style.NORMAL} Multiple transfer from PRIVATE registry')
        for line, value in enumerate(data):
            value = re.sub(invisible_char, '', value)
            img_only = f"{value.split('/')[-1]}"
            src_img = f'{source.get("registry")}/{source.get("ns")}/{img_only}'
            dst_img = f'{target.get("registry")}/{target.get("ns")}/{img_only}'
            skopeo_copy(src_img, dst_img, src_mode, dst_mode, source, target, safe)

def skopeo_list_img_tags(img, source=None, release=None):
    if source is None:
        if release is not None:
            print(f'{Fore.BLUE}{Style.BRIGHT}[ SKOPEO ] >>{Style.NORMAL} Fetching all image version of release {Fore.CYAN}{Style.BRIGHT}{release}{Fore.BLUE}{Style.NORMAL} on repository {Fore.CYAN}{Style.BRIGHT}{img}')
            cmd = f"skopeo list-tags --tls-verify=false docker://{img} | jq '.Tags' | jq '.[]' | jq 'select(test(\"^{release}\"))'"
        else:
            print(f'{Fore.BLUE}{Style.BRIGHT}[ SKOPEO ] >>{Style.NORMAL} Fetching all images on repository {Fore.CYAN}{Style.BRIGHT}{img}')
            cmd = f"skopeo list-tags --tls-verify=false docker://{img} | jq '.Tags' | jq '.[]'"
    else:
        if release is not None:
            print(f'{Fore.BLUE}{Style.BRIGHT}[ SKOPEO ] >>{Style.NORMAL} Fetching all images version of release {Fore.CYAN}{Style.BRIGHT}{release}{Fore.BLUE}{Style.NORMAL} on repository {Fore.CYAN}{Style.BRIGHT}{img}')
            cmd = f"skopeo list-tags --tls-verify=false docker://{img} --creds {source.get('sa')}:{source.get('token')} | jq '.Tags' | jq '.[]' | jq 'select(test(\"^{release}\"))'"
        else:
            print(f'{Fore.BLUE}{Style.BRIGHT}[ SKOPEO ] >>{Style.NORMAL} Fetching all images on repository {Fore.CYAN}{Style.BRIGHT}{img}')
            cmd = f"skopeo list-tags --tls-verify=false docker://{img} --creds {source.get('sa')}:{source.get('token')} | jq '.Tags' | jq '.[]'"
    error_str = f'{Fore.RED}{Style.BRIGHT}[ ERROR ] >> FAILED to catch {img} tags.'
    result = toolbox.popen_cmd(cmd, error_str, debug)
    return result
