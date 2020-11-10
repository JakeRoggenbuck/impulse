#!/usr/bin/python3
import hashlib
import json
import os
from pathlib import Path
import requests
from subprocess import check_output, run
import sys
from termcolor import colored
from tqdm import tqdm
import yaml


with open(f"{str(Path.home())}/.config/impulse/config.yaml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


def download_file(url, path, dohash):
    local_filename = url.split("/")[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        sha = hashlib.sha256()
        with open(f"{path}{local_filename}", "wb+") as f:
            for chunk in tqdm(r.iter_content(chunk_size=8192)):
                if chunk:
                    f.write(chunk)
                    sha.update(chunk)
        if dohash:
            print(f"sha256sum: {sha.hexdigest()}")
    return local_filename


def install_package(name):
    run(["sudo", "mkdir", f"/tmp/{name}"])
    print("Extracting archive...")
    if run(
        ["sudo", "tar", "-xvf", f"/tmp/{name}.tar.gz", "-C", f"/tmp/{name}"]
    ).returncode:
        print(colored("Error extracting archive!", "red"))
        exit()
    else:
        print(colored("Extracted!", "green"))

    dir_ = check_output(["ls", f"/tmp/{name}/"])
    if input("View impulse.build diff? [y/n] ") == "y":
        if run(
            ["less", f"/tmp/{name}/{dir_.decode('ascii').strip()}/impulse.build"]
        ).returncode:
            print(colored("Installation file doesn't exist!", "red"))
            exit()
        else:
            pass

    if input("Continue install? [y/n] ") == "y":
        os.chdir(f"/tmp/{name}/{dir_.decode('ascii').strip()}/")
        if run(["sudo", "sh", "impulse.build"]).returncode:
            print(colored("Installation failed!", "red"))
        else:
            print(colored("Installation complete!", "green"))


def download_package(url, name, dohash):
    print(f"Downloading {name} from {url}")
    download_file(f"{url}{name}.tar.gz", "/tmp/", True)
    print(colored(f"Done downloading {name}!", "green"))
    install_prompt = input(f"Do you want to install {name}? [y/n] ")
    if install_prompt == "y":
        install_package(name)


def download_list(url):
    print(f"Downloading list from {url}")
    download_file(f"{url}list.json", f'{str(Path.home())}{config["local_path"]}', False)
    print(colored("Done downloading list", "green"))


def search_list(term):
    with open(f"{str(Path.home())}{config['local_path']}list.json") as json_file:
        data = json.load(json_file)
        if term == "a":
            print(
                "Here are the packages that can be installed.",
                "\nUse -Ss <package-name> to learn more about a package\n",
            )
            for entry in data:
                print(f"* {entry}")
        if term in data:
            print(data[term]["name"])
            print(f'-- {data[term]["desc"]}')


if sys.argv[1] == "-U":
    download_list(config["upstream"])

elif sys.argv[1] == "-S":
    download_package(config["upstream"], sys.argv[2], True)

elif sys.argv[1] == "-Ss":
    search_list(sys.argv[2])

else:
    print("Not a command, use the man page")