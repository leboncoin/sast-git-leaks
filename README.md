# SAST GIT LEAKS
[![Python 3.4|3.8](https://img.shields.io/badge/python-3.6|3.7|3.8-green.svg)](https://www.python.org/) [![License](https://img.shields.io/github/license/leboncoin/sast-git-leaks?color=blue)](https://github.com/leboncoin/sast-git-leaks/blob/master/LICENSE)

SAST tool used to check leaks from your repositories

## Prerequisites

### Tools

You must install the tools:
- [gitleaks](https://github.com/zricethezav/gitleaks) 
- [shhgit](https://github.com/eth0izzle/shhgit)

### Dependencies

#### Debian / Ubuntu

```bash
$> apt install python3-pip
$> cd sast-git-leaks
$> pip3 install -r requirements.txt
```

#### MacOS

```bash
$> brew install python3
$> cd sast-git-leaks
$> pip3 install -r requirements.txt
```

## Get started

```bash
$> git clone https://github.com/orgs/leboncoin/sast-git-leaks --branch master --depth 1
$> cd sast-git-leaks
$> pip3 install -r requirements.txt
$> python3 sast_git_leaks.py -r <repo_name> -o <report_path.json> -t <tools,to,use,default,all>
$> cat <report_path.json> | jq
```

## Usage

```bash
$> python3 sast_git_leaks.py --help
usage: sast_git_leaks.py [-h] -r REPO -o OUTPUT [-t TOOLS]

optional arguments:
  -h, --help            show this help message and exit
  -r REPO, --repo REPO  name of the repo to scan
  -o OUTPUT, --output OUTPUT
                        name of the json report
  -t TOOLS, --tools TOOLS
                        tools to use (gitleaks,shhgit)
```

## Tools

### Gitleaks

Link: https://github.com/zricethezav/gitleaks

### Shhgit

Link: https://github.com/eth0izzle/shhgit

# LICENSE

Licensed under the [Apache License](https://github.com/leboncoin/sast-git-leaks/blob/master/LICENSE), Version 2.0 (the "License").

# COPYRIGHT

Copyright 2020 Ankirama; ([ankirama](https://github.com/ankirama/))