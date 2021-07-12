import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import skopeoTransfer
import re
import unittest
import argparse

pep440 = re.compile('^([a-zA-Z0-9-_]*:v?[0-9.]+-?(r(c|ev)|a(lpha)?|b(eta)?|c|pre(view)?)?[0-9]*(\\.?(post|dev)[0-9])?)$')
pep440_latest = re.compile('^(?:v?[0-9.-]+(r(c|ev)|a(lpha)?|b(eta)?|c|pre(view)?)?[0-9]*(\\.?(post|dev)[0-9])?|latest)$')

class MyTest(unittest.TestCase):
    credentials = {
        "creds1" : {
            "name": "ixxel-repo",
            "api": "",
            "registry": "docker.io",
            "sa": "ixxel",
            "token": "d452509d-acee-4d3a-8fc2-a15735fb43a1",
            "ns": "ixxel"
        },
        "creds2" : {
            "name": "ixxel-repo",
            "api": "",
            "registry": "docker.io",
            "sa": "ixxel",
            "token": "d452509d-acee-4d3a-8fc2-a15735fb43a1",
            "ns": "ixxel"
        },
        "public" : {
            "name": "docker-hub",
            "registry": "",
            "ns": ""
        }
    }

    def create_parser(self):
        parser = argparse.ArgumentParser(description='Transfer docker image(s) from one repository to another with skopeo')
        exlusive = parser.add_mutually_exclusive_group(required=True)
        exlusive.add_argument('--image', type=str, help='Name of the docker image to transfer')
        exlusive.add_argument('--file', type=argparse.FileType('r'), help='List of docker images to transfer. Must be a file.')
        exlusive.add_argument('--update', nargs="*", type=str, help='Update latest img releases from one registry to another')
        parser.add_argument('--release', type=str, help='Release of the images to update. Exemple : 3.2 will download all 3.2.x')
        parser.add_argument('--public', default=False, action='store_true', help='download from a public registry')
        parser.add_argument('--daemon', default=False, action='store_true', help='use local docker daemon registry')
        parser.add_argument('--creds', type=str, help='Path of the json file for registries credentials')
        return parser

    def test_full_single_public_transfer(self):
        # Context
        parser = self.create_parser()
        args = parser.parse_args(['--image', 'alpine:latest', '--public'])
        credentials = self.credentials
        os.environ['TARGET'] = 'creds2'
        os.environ['DST_NAMESPACE'] = 'ixxel'
        os.environ['SOURCE'] = 'public'
        # Test
        try:
            MANDATORY_ENV_VARS = skopeoTransfer.define_mandatory_vars(args)
            source, target = skopeoTransfer.prepare_execution(MANDATORY_ENV_VARS, credentials)
            skopeoTransfer.process_options(source, target, args)
        except Exception as exc:
            assert False, f"Skopeo test_full_single_public_transfer failed : {exc}"

    def test_full_single_private_transfer(self):
        # Context
        parser = self.create_parser()
        args = parser.parse_args(['--image', 'alpine:latest'])
        credentials = self.credentials
        os.environ['SOURCE'] = 'creds1'
        os.environ['SRC_NAMESPACE'] = 'ixxel'
        os.environ['TARGET'] = 'creds2'
        os.environ['DST_NAMESPACE'] = 'ixxel'
        # Test
        try:
            MANDATORY_ENV_VARS = skopeoTransfer.define_mandatory_vars(args)
            source, target = skopeoTransfer.prepare_execution(MANDATORY_ENV_VARS, credentials)
            skopeoTransfer.process_options(source, target, args)
        except Exception as exc:
            assert False, f"Skopeo test_full_single_private_transfer failed : {exc}"

    def test_full_single_get_latest(self):
        # Context
        parser = self.create_parser()
        args = parser.parse_args(['--update', 'alpine', '--public'])
        credentials = self.credentials
        os.environ['SOURCE'] = 'public'
        os.environ['TARGET'] = 'creds2'
        os.environ['DST_NAMESPACE'] = 'ixxel'
        # Test
        try:
            MANDATORY_ENV_VARS = skopeoTransfer.define_mandatory_vars(args)
            source, target = skopeoTransfer.prepare_execution(MANDATORY_ENV_VARS, credentials)
            skopeoTransfer.process_options(source, target, args)
        except Exception as exc:
            assert False, f"Skopeo test_full_single_get_latest failed : {exc}"

    def test_full_single_get_latest_specific(self):
        # Context
        parser = self.create_parser()
        args = parser.parse_args(['--update', 'alpine', '--release', '3.12', '--public'])
        credentials = self.credentials
        os.environ['SOURCE'] = 'public'
        os.environ['TARGET'] = 'creds2'
        os.environ['DST_NAMESPACE'] = 'ixxel'
        # Test
        try:
            MANDATORY_ENV_VARS = skopeoTransfer.define_mandatory_vars(args)
            source, target = skopeoTransfer.prepare_execution(MANDATORY_ENV_VARS, credentials)
            skopeoTransfer.process_options(source, target, args)
        except Exception as exc:
            assert False, f"Skopeo test_full_single_get_latest_specific failed : {exc}"

    def test_full_multiple_private_transfer(self):
        # Context
        f = open("test.txt", "a")
        f.write("alpine:latest"+"\n")
        f.write("alpine:3.12")
        f.close()
        parser = self.create_parser()
        args = parser.parse_args(['--file', 'test.txt', '--public'])
        credentials = self.credentials
        os.environ['SOURCE'] = 'public'
        os.environ['TARGET'] = 'creds2'
        os.environ['DST_NAMESPACE'] = 'ixxel'
        # Test
        try:
            MANDATORY_ENV_VARS = skopeoTransfer.define_mandatory_vars(args)
            source, target = skopeoTransfer.prepare_execution(MANDATORY_ENV_VARS, credentials)
            skopeoTransfer.process_options(source, target, args)
        except Exception as exc:
            assert False, f"Skopeo test_full_multiple_private_transfer failed : {exc}"
        os.remove("test.txt")

    # def test_get_latest_release(self):
        # source = {
        # "name": "docker-hub",
        # "registry": "",
        # "ns": ""
        # }
    #     self.assertTrue(skopeoTransfer.check_regex(skopeoTransfer.get_latest_release("vault", source, None), pep440))

    # def test_get_latest_release_latest(self):
    #     os.environ["TAG_POLICY"] = "pep440_latest"
    #     global_params = ["TAG_POLICY"]
    #     skopeoTransfer.set_global_parameters(global_params)
    #     source = {
    #     "name": "docker-hub",
    #     "registry": "",
    #     "ns": ""
    #     }
    #     assert(skopeoTransfer.get_latest_release("vault", source, None) == "vault:latest")

    # def test_single_public_transfer(self):
    #     source = {
    #     "name": "docker-hub",
    #     "registry": "",
    #     "ns": ""
    #     }
    #     target = {
        # "name": "ixxel-repo",
        # "api": "",
        # "registry": "docker.io",
        # "sa": "ixxel",
        # "token": "d452509d-acee-4d3a-8fc2-a15735fb43a1",
        # "ns": "ixxel"
    #     }
    #     image = "alpine"
    #     try:
    #         skopeoTransfer.skopeo_single_transfer(source, target, image)
    #     except Exception as exc:
    #         assert False, f"Skopeo single transfer failed : {exc}"

    # def test_single_private_transfer(self):
    #     source = {
    #     "name": "ixxel-repo",
    #     "api": "",
    #     "registry": "docker.io",
    #     "sa": "ixxel",
    #     "token": "d452509d-acee-4d3a-8fc2-a15735fb43a1",
    #     "ns": "ixxel"
    #     }
    #     target = {
    #     "name": "ixxel-repo",
    #     "api": "",
    #     "registry": "docker.io",
    #     "sa": "ixxel",
    #     "token": "d452509d-acee-4d3a-8fc2-a15735fb43a1",
    #     "ns": "ixxel"
    #     }
    #     image = "alpine"
    #     try:
    #         skopeoTransfer.skopeo_single_transfer(source, target, image)
    #     except Exception as exc:
    #         assert False, f"Skopeo single transfer failed : {exc}"

    # def test_single_get_latest(self):
    #     source = {
    #     "name": "docker-hub",
    #     "registry": "",
    #     "ns": ""
    #     }
    #     target = {
    #     "name": "ixxel-repo",
    #     "api": "",
    #     "registry": "docker.io",
    #     "sa": "ixxel",
    #     "token": "d452509d-acee-4d3a-8fc2-a15735fb43a1",
    #     "ns": "ixxel"
    #     }
    #     images = ["alpine"]
    #     try:
    #         skopeoTransfer.update_releases(source, target, images)
    #     except Exception as exc:
    #         assert False, f"Skopeo single transfer failed : {exc}"

    # def test_single_get_latest_specific(self):
    #     source = {
    #     "name": "docker-hub",
    #     "registry": "",
    #     "ns": ""
    #     }
    #     target = {
    #     "name": "ixxel-repo",
    #     "api": "",
    #     "registry": "docker.io",
    #     "sa": "ixxel",
    #     "token": "d452509d-acee-4d3a-8fc2-a15735fb43a1",
    #     "ns": "ixxel"
    #     }
    #     images = ["alpine"]
    #     version = "3.12"
    #     try:
    #         skopeoTransfer.update_releases(source, target, images, version)
    #     except Exception as exc:
    #         assert False, f"Skopeo single transfer failed : {exc}"

# def test_convert_bytes_to_string():
#     str_test = "Something"
#     arr = bytearray(str_test, 'utf-8')
#     assert(isinstance(skopeoTransfer.convert_bytes_to_string(arr), str))

# def test_convert_bytes_list_to_clean_str_list():
#     array = []
#     str_test1 = "Something"
#     str_test2 = "Another thing"
#     array.append(bytes(str_test1, 'utf-8'))
#     array.append(bytes(str_test2, 'utf-8'))
#     assert(isinstance(skopeoTransfer.convert_bytes_list_to_clean_str_list(array), list))
#     for elem in skopeoTransfer.convert_bytes_list_to_clean_str_list(array):
#         assert(isinstance(elem, str))

# class MyTest(unittest.TestCase):
#     def test_check_regex(self):
#         latest_img = re.compile('^(latest)$')
#         pep440 = re.compile('^(v?[0-9.]+-?(r(c|ev)|a(lpha)?|b(eta)?|c|pre(view)?)?[0-9]*(\\.?(post|dev)[0-9])?)$')
#         self.assertTrue(skopeoTransfer.check_regex("latest", latest_img))
#         self.assertTrue(skopeoTransfer.check_regex("3.0.0-45", pep440))

#     def test_check_env_vars(self):
#         os.environ["TEST1"] = "set"
#         os.environ["TEST2"] = "set"
#         MANDATORY_ENV_VARS1 = ["TEST1", "TEST2"]
#         MANDATORY_ENV_VARS2 = ["TEST1", "TEST2", "TEST3"]

#         try:
#             skopeoTransfer.check_env_vars(MANDATORY_ENV_VARS1)
#         except Exception as exc:
#             assert False, f"'check_env_vars' raised an exception {exc}"
#         try:
#             skopeoTransfer.check_env_vars(MANDATORY_ENV_VARS2)
#         except Exception as exc:
#             assert True