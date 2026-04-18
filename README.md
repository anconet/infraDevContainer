# infraDevContainer

This is a repo for setup dev containers on various projects in VSCode. 

## Files
| File | Description | Notes |
| --- | --- | --- |
| README.md | Project overview and usage notes |
| devcontainer.json | Dev container configuration | - Add VSCode extensions<br> - Name the container |
| Dockerfile | Container image definition | Shouldn't have to touch this very much |
| post-create.sh | Post-creation setup script | - Add things to install <br> - Aliases|

## How to use

The main branch contains a generic dev container file set for use with dev containers in VSCode.

### Git submodule directly to .devcontainer
Create this as a git submodule in your project.

```bash

## You have to clone to .devcontainer if you want VSCode to find it.
git clone https://github.com/anconet/infraDevContainer.git .devcontainer
```

### Git submodule with an install.py script

### Git submodule with file links


## Use specific containers
Create a branch on the project for dev containers that are project type specific.

Current branches
```bash
verilog
python
```