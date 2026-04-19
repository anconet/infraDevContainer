# install.spec.md
This is a specification for the install.py script.

## The project
This repo contains 3 files that support VSCode Dev Containers. Those files are
* Dockerfile
* devconainer.json
* post-create.sh

The repo is intended to help setup a project to support VSCode Dev Containers.

To setup project for dev containers, the three VSCode Dev Container files need to be in some way connected to the .devcontainer directory in the root of the project.

Since this project is a repo that will be installed as a git submodule, the root project directory should default to one directory above.

There are two ways the dev container files are connected to the .devcontainer directory.

### Option 1: Copy 

The .devcontainer directory is create in the root of the project, assuming the .devcontainer directory doesn't already exist.

The files are then copied from this directory to the .devcontainer directory.

For the copy option there should also be an uninstall that removes the copied files from .devcontainer and removes the .devcontainer directory. The user should be asked if they are sure.

### Option 2: Softlink option
The .devcontainer directory is created in the root of the project, assuming the .dev container direcotry doesn't already exist.

The script then creates linux symbolic links from .devcontainer to the files in this directory.

Like option 1 the script should provide an uninstall that removes the sybolic links and removes the .devcontainer directory.

## General

- Name the file you create install.py.
- The file should be written in python.
