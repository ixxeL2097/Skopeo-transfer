[Main menu](../README.md)

## 01 - Script usage
### skopeoTransfer.py - Transfer images from one registry to another

In order to make uses of skopeo easier, this script automates transfer of images between registries.

### What it does

Script simply pull a single image or multiple images from the source registry to the local `/tmp` directory and then push from `/tmp` to target registry.

### Usage

Script is written in python and is wrapped inside a Docker container. You can obviously use script as is, but it's highly recommended to use it within the docker container to be fully environment agnostic.

Script require at least one of these 3 sub-commands to work properly :

- `img` : usage `img <image-name:tag>` allow to transfer a single image from one registry to another.
- `file` : usage `file <file-path>` allow to transfer multiple images according to the file passed as argument from one registry to another.
- `update` : usage `update <img1> <img2> ... <imgn>` allow to transfer multiple images according to latest release located on the source repository.

Update can be combined with the following flag to pick a specific release version :
- `--release` : usage `update <img1> <img2> --release 3.3` allow to transfer multiple images according latest version of the specific release mentioned.

You can also specify a unique flag in combination with all other flags :
- `--public` : usage `--public` Boolean flag which activated the public registry pulling mode. Pulled image are from public registry and do not require credentials.

You can pass a credentials file to provide skopeo your private registries information in order to transfer with the following flag :
- `--creds` : usage `--creds <path-to-the-credential-file>` (must be a JSON formatted file) just as following ==>
```json
{
    "creds1": {
        "name": "my-private-registry",
        "registry": "example.com:5000",
        "sa": "user",
        "token": "secret",
        "ns": ""
    },
    "creds2": {
        "name": "second-registry",
        "registry": "another-registry.io:5000",
        "sa": "user",
        "token": "secret",
        "ns": ""
    }
}
```
By default, the script will look for a file named `credentials.json` in the working directory.

However, it's recommended to use Docker wrapped script commands are described below.

<!-- markdownlint-disable MD038 -->
| Sub-commands               | Description                                                                              |
| :------------------------- | :--------------------------------------------------------------------------------------- |
| `img`                      | [mutually-exclusive] Single named image transfer mode                                    |
| `file`                     | [mutually-exclusive] Multiple transfer mode from file                                    | 
| `update`                   | [mutually-exclusive] Update transfer mode                                                |

| General parameters         | Description                                                                              |
| :------------------------- | :--------------------------------------------------------------------------------------- |
| `--creds`                  | [optional] Path of the json file for registries credentials                              |
| `--safe`                   | [optional] Using safe mode will download and upload image instead of direct transfer     |
| `--debug`                  | [optional] Print out information to debug commands                                       |
| `--format`                 | [optional] Manifest type (oci, v2s1, or v2s2) to use in the destination                  |

| Sub parameters             | Description                                                                              |
| :------------------------- | :--------------------------------------------------------------------------------------- |
| `--public`                 | [optional] download from a public registry                                               |
| `--src`                    | [optional] source name                                                                   |
| `--dst`                    | [optional] destination name                                                              |
| `--src-ns`                 | [optional] source namespace name                                                         |
| `--dst-ns`                 | [optional] destination namespace name                                                    |
| `--src-mode`               | [optional] transport type for source                                                     |
| `--dst-mode`               | [optional] transport type for destination                                                |
<!-- markdownlint-enable MD038 -->


### Interesting links

- https://github.com/containers/skopeo
- https://github.com/nmasse-itix/OpenShift-Examples/tree/master/Using-Skopeo
- https://www.mankier.com/1/skopeo-login

---------------------------------------------------------------------------------------------------------------------------------

[Main menu](../README.md)

