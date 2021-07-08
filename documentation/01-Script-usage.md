[Main menu](../README.md)

## 01 - Script usage
### getImage.py - Transfer images from one registry to another

In order to make uses of skopeo easier, this script automates transfer of images between registries.

### What it does

Script simply pull a single image or multiple images from the source registry to the local `/tmp` directory and then push from `/tmp` to target registry.

### Usage

Script is written in python and is wrapped inside a Docker container. You can obviously use script as is, but it's highly recommended to use it within the docker container to be fully environment agnostic.

Script require at least one of these 3 flags to work properly :

- `--image` : usage `--image <image-name:tag>` allow to transfer a single image from one registry to another.
- `--file` : usage `--file <file-path>` allow to transfer multiple images according to the file passed as argument from one registry to another.
- `--update` : usage `--update <img1> <img2> ... <imgn>` allow to transfer multiple images according to latest release located on the source repository.

Update can be combined with the following flag to pick a specific release version :
- `--release` : usage `--update <img1> <img2> --release 3.3` allow to transfer multiple images according latest version of the specific release mentioned.

You can also specify a unique flag in combination with all other flags :
- `--public` : usage `--public` Boolean flag which activated the public registry pulling mode. Pulled image are from public registry and do not require credentials.

If you want to upload a docker image on your local machine (local docker daemon) you can specify the following flag :
- `--daemon` : usage `--daemon` Boolean flag which activate the docker daemon transfer, pulling images from your local machine and sending to target.

Additionally, some environment variables are mandatory as well :

- `SOURCE` : source registry name. **Has to match inside script structure variable name.**
- `TARGET` : target registry name. **Has to match inside script structure variable name.**
- `SRC_NAMESPACE` : source namespace. Namespace of the image located in the source registry.
- `DST_NAMESPACE` : destination namespace. Namespace of the destination registry you want to push your image in.

For a classic usage of the script, you need to set first the above environment variables, then you can execute command as follow :

```shell
python3 getImage.py --image <image-name-to-transfer>
```

```shell
python3 getImage.py --file <path-to-list-images-file>
```

However, it's recommended to use Docker wrapped script commands are described below.

<!-- markdownlint-disable MD038 -->
| Arguments                  | Description                                                                              |
| :------------------------- | :--------------------------------------------------------------------------------------- |
| `--rm`                     | [optional] remove the docker image after it finishes running.                            |
| `--name`                   | [optional] gives a custom name to container.                                             |
| `-it`                      | [recommended] run in an interactive terminal and display output.                         |
| `--network=host`           | [optional] use host network settings.                                                    |
| `--dns=<DNS-IP>`           | [optional] use specific DNS for the container.                                           |
| `-e SRC_NAMESPACE`         | [mandatory] source namespace in classic mode. (not needed in public mode)                |
| `-e DST_NAMESPACE`         | [mandatory] target namespace.                                                            |
| `-e SOURCE`                | [mandatory] source registry name in classic mode. (not needed in public mode)            |
| `-e TARGET`                | [mandatory] target registry name.                                                        |
| `-e https_proxy`           | [optional] use specific https proxy for container.                                       |
| `-e http_proxy`            | [optional] use specific http proxy for container.                                        |
| `-e no_proxy`              | [optional] use specific no proxy configuration for container.                            |
| `-e MANIFEST_FORMAT`       | [optional] configure manifest format version of docker images.                           |
| `-e TAG_POLICY`            | [optional] configure allowed tag policy.                                                 |
| `-v <path>:/app/list:ro`   | [conditionally-required] mount "path" to /app/list dir to read `--image` list.           |
| `--image`                  | [required/exclusive] image name to transfer.                                             |
| `--list`                   | [required/exclusive] list images name to transfer.                                       |
| `--update`                 | [required/exclusive] list of image to transfer, according to latest release on repo.     |
| `--release`                | [optional] specific release to use with `--update` (ex: 3.1, 4.0, 7.9...)                |
| `--public`                 | [optional] boolean specifying that pulled image(s) are from public registry              |
| `--daemon`                 | [optional] boolean specifying that transfered image(s) are from local docker daemon      |
<!-- markdownlint-enable MD038 -->


**Single image transfer**

```shell
docker run --rm -it --name skopeo --network=host \
           -e SRC_NAMESPACE=<source-namespace> \
           -e DST_NAMESPACE=<destination-namespace> \
           -e SOURCE=<source-registry> \
           -e TARGET=<target-registry> \
           <SKOPEO-IMAGE-NAME> \
           --image <IMAGE-TO-TRANSFER>
```

**Single image transfer from public registry**

```shell
docker run --rm -it --name skopeo --network=host \
           -e DST_NAMESPACE=<destination-namespace> \
           -e TARGET=<target-registry> \
           <SKOPEO-IMAGE-NAME> \
           --image <IMAGE-TO-TRANSFER> \
           --public
```

**Single image transfer from local docker daemon registry**

```shell
docker run --rm -it --name skopeo --network=host \
           -v /var/run/docker.sock:/var/run/docker.sock \
           -e DST_NAMESPACE=<destination-namespace> \
           -e TARGET=<target-registry> \
           <SKOPEO-IMAGE-NAME> \
           --image <IMAGE-TO-TRANSFER> \
           --daemon
```

**Multiple image transfer**

Your image file list must be formated like below :
```
bpm-standalone:7.11.0-ee-10
cmdb:3.2.0-70
vault:1.5.0
alpine:edge
```

```shell
docker run --rm -it --name skopeo --network=host \
           -v <host-path-to-image-file-list>:/app/list:ro \
           -e SRC_NAMESPACE=<source-namespace> \
           -e DST_NAMESPACE=<destination-namespace> \
           -e SOURCE=<source-registry> \
           -e TARGET=<target-registry> \
           <SKOPEO-IMAGE-NAME> \
           --file /app/list/<file-name>
```

**Updating latest images versions**

```shell
docker run --rm -it --name skopeo --network=host \
           -e SRC_NAMESPACE=<source-namespace> \
           -e DST_NAMESPACE=<destination-namespace> \
           -e SOURCE=<source-registry> \
           -e TARGET=<target-registry> \
           <SKOPEO-IMAGE-NAME> \
           --update <img1> <img2> <imgn>
```

**Updating latest images versions of a specific release**

```shell
docker run --rm -it --name skopeo --network=host \
           -e SRC_NAMESPACE=<source-namespace> \
           -e DST_NAMESPACE=<destination-namespace> \
           -e SOURCE=<source-registry> \
           -e TARGET=<target-registry> \
           <SKOPEO-IMAGE-NAME> \
           --update <img1> <img2> <imgn>
           --release 4.0
```

You can also use other flags rather than `--network=host` like `--dns` or `--add-host`. You can also specify manually environment proxy variable with `-e http_proxy=http://user:password@ip:port/ -e no_proxy="localhost"` for example.

examples :

**Single image transfer**

```console
[root@workstation ~ ]$ docker run --rm -it --name skopeo -e SOURCE=ibm -e SRC_NAMESPACE=argo-int -e DST_NAMESPACE=cmp-core -e TARGET=dev6 --network=host skopeo-script-py:2.2.0-1 --image dispatcher:3.1.10-30
```

**Multiple image transfer**

```console
[root@workstation ~ ]$ docker run --rm -it --name skopeo -e SOURCE=ibm -e SRC_NAMESPACE=argo-int -e DST_NAMESPACE=cmp-core -e TARGET=dev6 --network=host -v /home/fred/Documents:/app/list:ro skopeo-script-py:2.2.0-1 --file /app/list/images.list
```

**Updating latest images versions**

```console
[root@workstation ~ ]$ docker run --rm -it --name skopeo -e SOURCE=ibm -e SRC_NAMESPACE=argo-dev -e DST_NAMESPACE=cmp-core -e TARGET=dev6 --network=host skopeo-script-py:2.2.0-1 --update cmdb bpm dispatcher connector
```

**Updating latest images versions of release 3.2**

```console
[root@workstation ~ ]$ docker run --rm -it --name skopeo -e SOURCE=ibm -e SRC_NAMESPACE=argo-dev -e DST_NAMESPACE=cmp-core -e TARGET=dev6 --network=host skopeo-script-py:2.2.0-1 --update cmdb bpm dispatcher connector --release 3.2
```

**Using public registry transfer mode**

```console
[root@workstation ~ ]$ docker run --rm -it --name skopeo -e DST_NAMESPACE=cmp-core -e TARGET=dev6 --network=host skopeo-script-py:2.2.0-1 --update cmdb bpm dispatcher connector --release 3.2 --public
```

**Using docker daemon registry transfer mode**

```console
[root@workstation ~ ]$ docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock -e DST_NAMESPACE=cmp-core -e TARGET=dev6 --network=host skopeo-script-py:4.4.0-1 --image dispatcher:4.0.0-9 --daemon
```

### Tweaking

You can add your own registry setup by adding or modifying inside script structure variable as follow :

```python
<name> =	{
    "name": "<NAME>",
    "api": "<API-URL>",
    "registry": "<REGISTRY-URL>",
    "user": "<USER>",
    "token": "<PASSWORD>"
}
```

This kind of modification allows you to call a new `SOURCE` or `TARGET` registry as parameter (`-e SOURCE=<new-registry>`/`-e TARGET=<new-registry>`).

### Output

**Single image transfer**

```console
[root@workstation ~]$ docker run --rm -it -e SOURCE=dev5 -e SRC_NAMESPACE=cmp-core -e DST_NAMESPACE=cmp-core -e TARGET=dev6 --network=host skopeo-script-py:2.2.0-1 --image ipam-mock:3.2.0
all ENV vars supplied. Processing transfer now...
OC login : https://api.ocp4-dev5.devibm.local:6443
Login successful.

You have access to 66 projects, the list has been suppressed. You can list all projects with 'oc projects'

Using project "default".
Welcome! See 'oc help' to get started.
[ SKOPEO ] > COPYING SINGLE IMAGE FROM [[ default-route-openshift-image-registry.apps.ocp4-dev5.devibm.local/cmp-core/ipam-mock:3.2.0 ]] to [[ default-route-openshift-image-registry.apps.devibm.local/cmp-core/ipam-mock:3.2.0 ]]
[ STEP 1 ] >> transfer from remote default-route-openshift-image-registry.apps.ocp4-dev5.devibm.local/cmp-core/ipam-mock:3.2.0 to local /tmp/ipam-mock:3.2.0
Getting image source signatures 
Copying blob 8db9b749023b done   
Copying blob b8e7bf085d0d done  
Copying config a06bf1e579 done  
Writing manifest to image destination
Storing signatures
OC login : https://api.devibm.local:6443
Login successful.

You have access to 65 projects, the list has been suppressed. You can list all projects with 'oc projects'

Using project "default".
[ STEP 2 ] >> transfer from local /tmp/ipam-mock:3.2.0 to default-route-openshift-image-registry.apps.devibm.local/cmp-core/ipam-mock:3.2.0
Getting image source signatures
Copying blob 8db9b749023b skipped: already exists  
Copying blob b8e7bf085d0d done  
Copying config a06bf1e579 done  
Writing manifest to image destination
Storing signatures
```

**Multiple image transfer** 

```console
[root@workstation ~]$ docker run --rm -it -e SOURCE=dev5 -e SRC_NAMESPACE=cmp-core -e DST_NAMESPACE=cmp-core -e TARGET=dev6 --network=host -v /home/fred/Documents:/app/test:ro skopeo-script-py:2.2.0-1 --file /app/test/list-images
all ENV vars supplied. Processing transfer now...
OC login : https://api.ocp4-dev5.devibm.local:6443
Login successful.

You have access to 66 projects, the list has been suppressed. You can list all projects with 'oc projects'

Using project "default".
Welcome! See 'oc help' to get started.
[ SKOPEO ] > COPYING MULTIPLE IMAGES FROM [[ default-route-openshift-image-registry.apps.ocp4-dev5.devibm.local/ ]] to [[ default-route-openshift-image-registry.apps.devibm.local/ ]]
[ STEP 1 ] >> transfer from remote default-route-openshift-image-registry.apps.ocp4-dev5.devibm.local/cmp-core/bpm-standalone:7.11.0-ee-10 to local /tmp/bpm-standalone:7.11.0-ee-10
Getting image source signatures
Copying blob e7c96db7181b done  
Copying blob f910a506b6cb done 
Copying config b7818ae79a done  
Writing manifest to image destination
Storing signatures
[ STEP 1 ] >> transfer from remote default-route-openshift-image-registry.apps.ocp4-dev5.devibm.local/cmp-core/cmdb:3.2.0-70 to local /tmp/cmdb:3.2.0-70
Getting image source signatures  
Copying blob 3bd1f242066c done  
Copying blob aa7f2750e41e done  
Copying blob e4390dbaf0c1 done  
Copying config 5a2157d390 done  
Writing manifest to image destination
Storing signatures
OC login : https://api.devibm.local:6443
Login successful.

You have access to 65 projects, the list has been suppressed. You can list all projects with 'oc projects'

Using project "default".
[ STEP 2 ] >> transfer from local /tmp/bpm-standalone:7.11.0-ee-10 to default-route-openshift-image-registry.apps.devibm.local/cmp-core/bpm-standalone:7.11.0-ee-10
Getting image source signatures
Copying blob e7c96db7181b skipped: already exists  
Copying blob f910a506b6cb skipped: already exists  
Copying config b7818ae79a [--------------------------------------] 0.0b / 4.6KiB
Writing manifest to image destination
Storing signatures
[ STEP 2 ] >> transfer from local /tmp/cmdb:3.2.0-70 to default-route-openshift-image-registry.apps.devibm.local/cmp-core/cmdb:3.2.0-70
Getting image source signatures 
Copying blob 3bd1f242066c skipped: already exists  
Copying blob aa7f2750e41e skipped: already exists  
Copying blob e4390dbaf0c1 [--------------------------------------] 0.0b / 0.0b
Copying config 5a2157d390 [--------------------------------------] 0.0b / 9.0KiB
Writing manifest to image destination
Storing signatures
```

**Updating latest images versions** 

```console
[root@workstation ~]$ docker run --rm -it -e SOURCE=ibm -e SRC_NAMESPACE=argo-dev -e DST_NAMESPACE=cmp-core -e TARGET=dev6 --network=host skopeo-script-py:3.1.0-test --update cmdb bpm dispatcher connector
[ CHECK SUCCESS ] >> all ENV vars provided. Processing transfer now...
[ LISTING ] >> cmdb latest tag is cmdb:3.2.0-77
[ LISTING ] >> bpm latest tag is bpm:3.2.0-112
[ LISTING ] >> dispatcher latest tag is dispatcher:3.2.7-83
[ LISTING ] >> connector latest tag is connector:3.2.1-42
[ SKOPEO ] > LATEST RELEASES TO TRANSFER ARE ['cmdb:3.2.0-77', 'bpm:3.2.0-112', 'dispatcher:3.2.7-83', 'connector:3.2.1-42']
[ SKOPEO ] > COPYING MULTIPLE IMAGES FROM [[ de.icr.io/argo-dev ]] to [[ default-route-openshift-image-registry.apps.devibm.local/cmp-core ]]
[ LOGIN ] >> login to IBM registry : https://de.icr.io...
Login Succeeded!
[ STEP 1 ] >> transfer from remote de.icr.io/argo-dev/cmdb:3.2.0-77  to local /tmp/cmdb:3.2.0-77
Getting image source signatures
Copying blob 419e7ae5bb1e done
[...]
```

### Wrapped docker run

To ease docker launching, it can be useful to wrap `docker run` execution within a bash script. You can use [this script](../resources/getImage-hostnet.sh) (network host version) or [this script](../resources/getImage-proxy.sh) (proxy and dns version) to manage execution of the skopeo python script wrapped in a container. These both scripts are also embeded inside the container and can be extracted from it with following commands :

Run the container with `/bin/sh` entrypoint :

```shell
docker run -it --rm --name skopeo --entrypoint=/bin/sh skopeo-script-py:4.2.0-1
```

Then copy the file from another prompt command :

```shell
docker cp skopeo:/app/getImage-proxy.sh .
```

Here is the nethost wrapper script:

```bash
#!/bin/bash

#########################################################################
#########################################################################
######################## SKOPEO WRAPPER SCRIPT ##########################
######################### NETWORK HOST VERSION ##########################
#########################################################################
#########################################################################

# v4.4.3

# SKOPEO VERSION IMAGE EXECUTED
SKOPEO_IMG=skopeo-script-py:4.4.3

# PROGRAM PARAMETERS
SRC=$1
SRC_NS=$2
DST=$3
DST_NS=$4
IMAGE=$5
RELEASE=$6
PUBLIC=""               # Public transfer option
SOCKET=""               # Docker daemon socket
MANIFEST_FORMAT=""      # valid are : v2s2 (default), v2s1 or oci
TAG_POLICY=""           # Valid are : pep440 (default) or pep440_latest

# FILE TRANSFER PARAMETERS
HOST_LIST_PATH=/home/fred/Documents
LIST_FILE=list.images2

if [[ ${!#} = "public" ]] && [[ $# -gt 2 ]]
then
    if [[ ! -z $6  ]]
    then
        echo "[ ERROR ] >> Too many arguments for 'Public' transfer mode. Please execute script without SOURCE (SRC) and SOURCE_NAMESPACE (SRC_NS) variables."
        exit 1
    else
        echo "[ INFO ] >> Processing transfer from a PUBLIC registry."
        MODE="--public"
        DST=$1
        DST_NS=$2
        IMAGE=$3
        RELEASE=$4
    fi
elif [[ ${!#} = "daemon" ]] && [[ $# -gt 2 ]]
then
    if [[ ! -z $6  ]]
    then
        echo "[ ERROR ] >> Too many arguments for 'Daemon' transfer mode. Please execute script without SOURCE (SRC) and SOURCE_NAMESPACE (SRC_NS) variables."
        exit 1
    else
        echo "[ INFO ] >> Processing transfer from local DOCKER DAEMON registry."
        MODE="--daemon"
        SOCKET="-v /var/run/docker.sock:/var/run/docker.sock"
        DST=$1
        DST_NS=$2
        IMAGE=$3
        RELEASE=$4
    fi
elif [[ ${!#} = "public" ]] || [[ ${!#} = "daemon" ]] && [[ $# -lt 3 ]]
then
    echo "[ ERROR ] >> Not enough arguments for 'Public' or 'Daemon' transfer mode."
    exit 1
elif [[ $# -lt 4 ]]
then
    echo "[ ERROR ] >> Not enough arguments for 'Private' transfer mode."
    exit 1
else
    echo "[ INFO ] >> Processing transfer from a PRIVATE registry."
fi

if [[ ! -z $IMAGE ]] && [[ $IMAGE != "public" ]] && [[ $IMAGE != "daemon" ]]
then
    if [[ ! $IMAGE =~ "," ]]
    then
        docker run --rm -it --name skopeo --network=host \
                $SOCKET \
                -e SOURCE=$SRC \
                -e SRC_NAMESPACE=$SRC_NS \
                -e DST_NAMESPACE=$DST_NS \
                -e TARGET=$DST \
                -e MANIFEST_FORMAT=$MANIFEST_FORMAT \
                -e TAG_POLICY=$TAG_POLICY \
                $SKOPEO_IMG \
                --image $IMAGE \
                $MODE
    elif [[ $IMAGE =~ "," ]]
    then
        if [[ ! -z $RELEASE ]] && [[ $RELEASE != "public" ]] && [[ $RELEASE != "daemon" ]]
        then
            IMAGES=${IMAGE//,/ }
            docker run --rm -it --name skopeo --network=host \
                    $SOCKET \
                    -e SOURCE=$SRC \
                    -e SRC_NAMESPACE=$SRC_NS \
                    -e DST_NAMESPACE=$DST_NS \
                    -e TARGET=$DST \
                    -e MANIFEST_FORMAT=$MANIFEST_FORMAT \
                    -e TAG_POLICY=$TAG_POLICY \
                    $SKOPEO_IMG \
                    --update $IMAGES \
                    --release $RELEASE \
                    $MODE
        else
            IMAGES=${IMAGE//,/ }
            docker run --rm -it --name skopeo --network=host \
                    $SOCKET \
                    -e SOURCE=$SRC \
                    -e SRC_NAMESPACE=$SRC_NS \
                    -e DST_NAMESPACE=$DST_NS \
                    -e TARGET=$DST \
                    -e MANIFEST_FORMAT=$MANIFEST_FORMAT \
                    -e TAG_POLICY=$TAG_POLICY \
                    $SKOPEO_IMG \
                    --update $IMAGES \
                    $MODE
        fi
    fi
elif [ -f "$HOST_LIST_PATH/$LIST_FILE" ]
then
    docker run --rm -it --name skopeo --network=host \
               $SOCKET \
               -e SOURCE=$SRC \
               -e SRC_NAMESPACE=$SRC_NS \
               -e DST_NAMESPACE=$DST_NS \
               -e TARGET=$DST \
               -v $HOST_LIST_PATH:/app/list:ro \
               -e MANIFEST_FORMAT=$MANIFEST_FORMAT \
               -e TAG_POLICY=$TAG_POLICY \
               $SKOPEO_IMG \
               --file /app/list/$LIST_FILE \
               $MODE
else
    echo "[ ERROR ] >> either image parameter $IMAGE is null, or no such file or directory $HOST_LIST_PATH/$LIST_FILE provided"
fi
```

For example to transfer a **single image** `dispatcher:3.2.7-80` to `DEV5` OpenShift cluster registry, execute following command :

```shell
./getImage.sh ibm argo-dev dev5 cmp-core dispatcher:3.2.7-80
```

If you want to transfer **multiple images**, you need to ensure that the following parameters in the `getImage.sh` script are correct :

- `HOST_LIST_PATH` : set this variable to the directory where your images list file is located (for example : `/home/fred/Documents`).
- `LIST_FILE` : set this variable to the name of your image file name (for example : `images.list`)

Create your images file list, for example like below :
```
dispatcher:3.2.7-80
connector:3.2.1-42
bpm:3.2.0-111
```

Then execute following command :

```shell
./getImage.sh ibm argo-dev dev5 cmp-core
```

If you want to **Update latest images versions**, you just have to provide a list of images **separated by commas** :

```shell
./execute-getImage.sh ibm argo-dev dev6 cmp-core dispatcher,bpm,cmdb
```

Finally, if you want to **Update latest images versions of a specific release**, you just have to provide a list of images **separated by commas** and a release number :

```shell
./execute-getImage.sh ibm argo-dev dev6 cmp-core dispatcher,bpm,cmdb 3.4
```

### Warning


### Interesting links

- https://github.com/containers/skopeo
- https://github.com/nmasse-itix/OpenShift-Examples/tree/master/Using-Skopeo
- https://www.mankier.com/1/skopeo-login

---------------------------------------------------------------------------------------------------------------------------------

[Main menu](../README.md)

