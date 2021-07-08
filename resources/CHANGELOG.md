# Changelog

## Remember:

### REV M.m.r, where:

- M: Mayor — Complete change of code resulting in major added feature or program functionnalities.
- m: Minor — This is an added feature.
- p: Patch — Programmer error. Bug. Optimization of code.

## Actual versions
- v5.0.0
- v4.5.6
- v4.5.5
- v4.5.4
- v4.5.3
- v4.5.2
- v4.5.1
- v4.5.0
- v4.4.2
- v4.4.1
- v4.4.0
- v4.3.4
- v4.3.3
- v4.3.2
- v4.3.1
- v4.3.0
- v4.2.0
- v4.1.0
- v4.0.0
- v3.0.0
- v2.2.3
- v2.2.2
- v2.2.1
- v2.2.0
- v2.1.0
- v2.0.0
- v1.1.0
- v1.0.0

## [v5.0.0] - New credentials feature approach
#### 8/07/2021
### Json file credentials
  * Skopeo script now generates credentials from a JSON file instead of hard coded dict credentials

## [v4.5.6] - Updated PROD credentials second edition
#### 27/04/2021
### Updated creds
  * Updated PROD skopeo SA credentials

## [v4.5.5] - Updated PROD credentials
#### 19/04/2021
### Updated creds
  * Updated PROD skopeo SA credentials

## [v4.5.4] - Updated DEV5 credentials
#### 19/04/2021
### Updated creds
  * Updated DEV5 skopeo SA credentials

## [v4.5.3] - Added DEV8 creds
#### 06/04/2021
### New creds
  * Added DEV8 ROKS credentials
  
## [v4.5.2] - Added RedHat private registry
#### 25/02/2021
### Script python
  * Added Red Hat private registry to list of credentials possibilities

## [v4.5.1] - Library upgrade
#### 12/01/2021
### Skopeolib
  * Updated skopeolib for 1.2.1 skopeo version adding --insecure-policy flag
  * Added skopeo version at script start

## [v4.5.0] - Optimization and new Feature
#### 12/01/2021
### Script python
  * Using PEP-440 standard for Image version regex
  * Ability to consider 'latest' tag as a valid option for update transfer
  * Improved various functions and code snippets

## [v4.4.2] - Optimization
#### 08/01/2021
### Dockerfile
  * Optimized dockerfile with latest packages and alpine latest

## [v4.4.1] - Hotfix and feature
#### 06/01/2021
### Docker daemon transfer & manifest format
  * Fixed problem when using full registry name for docker daemon registry transfer mode
  * Added modularity of the docker manifest version to be used for transfer
  * added information on list tag for skopeo

## [v4.4.0] - New Feature
#### 06/01/2021
### Docker daemon
  * Allow transfer from local docker daemon by sharing the docker socket
  * Fixed empty line bug in multiple transfer from file

## [v4.3.4] - Feature
#### 06/01/2021
### Identical source/target
  * Allowed identical source and target by using deepcopy module on target python variables

## [v4.3.3] - Feature
#### 05/01/2021
### Dev20
  * Added credentials for dev20

## [v4.3.2] - Hotfix
#### 18/12/2020
### Manifest version
  * Forcing docker manifest version to v2s2 on skopeo copy commands

## [v4.3.1] - Hotfix
#### 24/09/2020
### Public registry pull
  * Added 'v' to available images version tags
  * Reworker tags list
  * Added time calculation

## [v4.3.0] - New feature
#### 22/09/2020
### Public registry pull
  * Added public registry pulling feature
  * Updated skopeolib library
  * Removed some variables
  * Added colours to output

## [v4.2.0] - New feature
#### 16/09/2020
### Automatic image update release
  * Automatically detect latest specific releases of an image and transfer it

## [v4.1.0] - New feature
#### 15/09/2020
### Public registry download
  * Using library for skopeo functions

## [v4.0.0] - New feature
#### 09/09/2020
### Automatic img update
  * Automatically detect latest repository releases of an image and transfer it

## [v3.0.0] - New feature
#### 08/09/2020
### New OCP login method
  * Registry login to OCP using skopeo login instead of oc login
  * Generic pull&push functions
  * Removed OC binary
  * Lighter docker image
  * Using service account instead of kubeadmin to login OCP

## [v2.2.3] - Upgrade & optimizations
#### 05/09/2020
### Code optimization & client upgrade
  * Using fname concatenation instead of join (faster)
  * Variabilized OC client
  * Upgrade of OC client from 4.2 to 4.4

## [v2.2.2] - Various functions optimization
#### 05/09/2020
### Code optimization
  * Improved some functions

## [v2.2.1] - Exception handling
#### 04/09/2020
### Code optimization
  * Added exception handling
  * Using subprocess instead of os.system
  * Optimized environment variables checking

## [v2.2.0] - Multiple images transfer
#### 03/09/2020
### Code optimization & new features
  * Added possibility to transfer multiple images via single list
  * Decoupled transfer functions

## [v2.1.0] - code refactoring
#### 17/07/2020
### Code optimization & new features
  * Dynamic source and target environments variables
  * Transfer from OCP to OCP
  * added dev6 env
  * added int2 env

## [v2.0.0] - Complete algorithm reworking
#### 16/06/2020
### New Features
  * Python script uses argument parser
  * Python script load images from parser instead of file
  * Python script is able to move files to several registries
  * Python script uses environment variables as source and destination parameters
  * Dockerfile is based on alpine:edge instead of centos
  * Dockerfile now embed only necessary packages

## [v1.1.0] - code refactoring
#### 19/03/2020
### Code optimization
  * Rewriting python script with functions
  * Rewriting Dockerfile with less layers

## [v1.0.0] - Initial Version
#### date unknown
### All New Features
  *  Initial Release
