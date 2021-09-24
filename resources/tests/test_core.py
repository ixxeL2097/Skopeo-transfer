import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import skopeoTransfer
import re
import unittest
import argparse
import skopeolib

pep440 = re.compile('^([a-zA-Z0-9-_]*:v?[0-9.]+-?(r(c|ev)|a(lpha)?|b(eta)?|c|pre(view)?)?[0-9]*(\\.?(post|dev)[0-9])?)$')
pep440_latest = re.compile('^(?:v?[0-9.-]+(r(c|ev)|a(lpha)?|b(eta)?|c|pre(view)?)?[0-9]*(\\.?(post|dev)[0-9])?|latest)$')

class MyTest(unittest.TestCase):
    credentials = {
        "creds1" : {
            "name": "ixxel-repo",
            "api": "",
            "registry": "docker.io",
            "sa": "ixxel",
            "token": "2794d8ea-0fa5-4039-8036-9bc85f3765af",
            "ns": "ixxel"
        },
        "creds2" : {
            "name": "ixxel-repo",
            "api": "",
            "registry": "docker.io",
            "sa": "ixxel",
            "token": "2794d8ea-0fa5-4039-8036-9bc85f3765af",
            "ns": "ixxel"
        },
        "fail1" : {
            "name": "ixxel-repo",
            "api": "",
            "registry": "docker.io",
            "sa": "fail",
            "token": "2794d8ea-0fa5-4039-8036-9bc85f3765af",
            "ns": "ixxel"
        },
        'public' : {
            "name": "docker-hub",
            "registry": "",
            "ns": ""
        },
        'local' : {
            "name": "local",
            "registry": "localhost",
            "ns": "default"
        }
    }

    def create_parser(self):
        parser = argparse.ArgumentParser(prog='skopeoTransfer', description='Transfer docker image(s) from one repository to another with skopeo')
        subparsers = parser.add_subparsers(help='sub-command help', dest='command')
        sub_img = subparsers.add_parser('img', help='Single named image transfer mode')
        sub_file = subparsers.add_parser('file', help='Multiple transfer mode from file')
        sub_update = subparsers.add_parser('update', help='Update transfer mode')
        # GENERAL arguments
        parser.add_argument('--format', type=str, default='v2s2', choices=['v2s2','v2s1','oci'], help='Manifest type (oci, v2s1, or v2s2) to use in the destination (default is manifest type of source, with fallbacks)')
        parser.add_argument('--creds', type=str, default='credentials.json', help='Path of the json file for registries credentials')
        # IMG arguments
        sub_img.set_defaults(func=skopeoTransfer.img_transfer_process)
        sub_img.add_argument('image', type=str, help='Name of the docker image to transfer')
        sub_img.add_argument('--public', default=False, action='store_true', help='download from a public registry')
        sub_img.add_argument('--src', type=str, help='source name')
        sub_img.add_argument('--dst', type=str, help='destination name')
        sub_img.add_argument('--src-ns', type=str, help='namespace for source')
        sub_img.add_argument('--dst-ns', type=str, help='namespace for destination')
        sub_img.add_argument('--src-mode', type=str, default='docker', choices=['containers-storage','docker','docker-daemon','dir'], help='transport type for source')
        sub_img.add_argument('--dst-mode', type=str, default='docker', choices=['containers-storage','docker','docker-daemon','dir'], help='transport type for destination')
        # FILE arguments
        sub_file.set_defaults(func=skopeoTransfer.file_transfer_process)
        sub_file.add_argument('file', type=argparse.FileType('r'), help='List of docker images to transfer. Must be a file.')
        sub_file.add_argument('--public', default=False, action='store_true', help='download from a public registry')
        sub_file.add_argument('--src', type=str, help='source name')
        sub_file.add_argument('--dst', type=str, help='destination name')
        sub_file.add_argument('--src-ns', type=str, help='namespace for source')
        sub_file.add_argument('--dst-ns', type=str, help='namespace for destination')
        sub_file.add_argument('--src-mode', type=str, default='docker', choices=['containers-storage','docker','docker-daemon','dir'], help='transport type for source')
        sub_file.add_argument('--dst-mode', type=str, default='docker', choices=['containers-storage','docker','docker-daemon','dir'], help='transport type for destination')
        # UPDATE arguments
        sub_update.set_defaults(func=skopeoTransfer.file_update_process)
        sub_update.add_argument('update', nargs="+", type=str, help='Update latest img releases from one registry to another')
        sub_update.add_argument('--public', default=False, action='store_true', help='download from a public registry')
        sub_update.add_argument('--src', type=str, help='source name')
        sub_update.add_argument('--dst', type=str, help='destination name')
        sub_update.add_argument('--src-ns', type=str, help='namespace for source')
        sub_update.add_argument('--dst-ns', type=str, help='namespace for destination')
        sub_update.add_argument('--src-mode', type=str, default='docker', choices=['containers-storage','docker','docker-daemon','dir'], help='transport type for source')
        sub_update.add_argument('--dst-mode', type=str, default='docker', choices=['containers-storage','docker','docker-daemon','dir'], help='transport type for destination')
        sub_update.add_argument('--release', type=str, help='Release of the images to update. Exemple : 3.2 will download all 3.2.x')
        return parser

    def test_parser(self):
        skopeoTransfer.sys.argv[1:] = ['img','test','--public']
        args = skopeoTransfer.parse()
        self.assertEqual(getattr(args, 'image'),'test')
        self.assertTrue(getattr(args, 'public'))

    def test_full_single_public_transfer(self):
        # Context
        parser = self.create_parser()
        args = parser.parse_args(['img', 'alpine:latest', '--public', '--dst', 'creds2', '--dst-ns', 'ixxel'])
        credentials = self.credentials
        # Test
        try:
            source, target = skopeoTransfer.prepare_transfer(args, credentials)
            args.func(args, credentials, source, target)
        except Exception as exc:
            assert False, f"Skopeo test_full_single_public_transfer failed : {exc}"

    def test_full_single_private_transfer(self):
        # Context
        parser = self.create_parser()
        args = parser.parse_args(['img', 'alpine:latest', '--dst', 'creds2', '--dst-ns', 'ixxel', '--src', 'creds1', '--src-ns', 'ixxel'])
        credentials = self.credentials
        # Test
        try:
            source, target = skopeoTransfer.prepare_transfer(args, credentials)
            args.func(args, credentials, source, target)
        except Exception as exc:
            assert False, f"Skopeo test_full_single_private_transfer failed : {exc}"

    def test_full_single_get_latest(self):
        # Context
        os.mkdir('/localhost')
        os.mkdir('/localhost/default')
        parser = self.create_parser()
        args = parser.parse_args(['update', 'alpine', '--public', '--dst-mode', 'dir'])
        credentials = self.credentials
        # Test
        try:
            source, target = skopeoTransfer.prepare_transfer(args, credentials)
            args.func(args, credentials, source, target)
        except Exception as exc:
            assert False, f"Skopeo test_full_single_get_latest failed : {exc}"

    def test_full_single_get_latest_specific(self):
        # Context
        parser = self.create_parser()
        args = parser.parse_args(['update', 'alpine', '--release', '3.12', '--public', '--dst', 'creds2', '--dst-ns', 'ixxel'])
        credentials = self.credentials
        # Test
        try:
            source, target = skopeoTransfer.prepare_transfer(args, credentials)
            args.func(args, credentials, source, target)
        except Exception as exc:
            assert False, f"Skopeo test_full_single_get_latest_specific failed : {exc}"

    def test_full_multiple_public_transfer(self):
        # Context
        f = open("test.txt", "a")
        f.write("alpine:latest"+"\n")
        f.write("alpine:3.12"+"\n")
        f.close()
        parser = self.create_parser()
        args = parser.parse_args(['file', 'test.txt', '--public', '--dst', 'creds2', '--dst-ns', 'ixxel'])
        credentials = self.credentials
        # Test
        try:
            source, target = skopeoTransfer.prepare_transfer(args, credentials)
            args.func(args, credentials, source, target)
        except Exception as exc:
            assert False, f"Skopeo test_full_multiple_public_transfer failed : {exc}"
        os.remove("test.txt")

    def test_full_multiple_private_transfer(self):
        # Context
        f = open("test.txt", "a")
        f.write("alpine:latest"+"\n")
        f.write("alpine:3.12"+"\n")
        f.close()
        parser = self.create_parser()
        args = parser.parse_args(['file', 'test.txt', '--dst', 'creds2', '--dst-ns', 'ixxel', '--src', 'creds1', '--src-ns', 'ixxel'])
        credentials = self.credentials
        # Test
        try:
            source, target = skopeoTransfer.prepare_transfer(args, credentials)
            args.func(args, credentials, source, target)
        except Exception as exc:
            assert False, f"Skopeo test_full_multiple_private_transfer failed : {exc}"
        os.remove("test.txt")

    def test_full_fail_single_public_transfer(self):
        # Context
        parser = self.create_parser()
        args = parser.parse_args(['img', 'alpine:latest', '--dst', 'creds2', '--dst-ns', 'ixxel', '--src', 'fail1', '--src-ns', 'ixxel'])
        credentials = self.credentials
        # Test
        with self.assertRaises(SystemExit):
            source, target = skopeoTransfer.prepare_transfer(args, credentials)
            args.func(args, credentials, source, target)

    def test_full_fail_single_get_latest(self):
        # Context
        parser = self.create_parser()
        args = parser.parse_args(['update', 'failxyz', '--public', '--dst', 'creds2', '--dst-ns', 'ixxel'])
        credentials = self.credentials
        # Test
        with self.assertRaises(SystemExit):
            source, target = skopeoTransfer.prepare_transfer(args, credentials)
            args.func(args, credentials, source, target)
