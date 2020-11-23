#!/usr/bin/python3
import argparse
import hashlib
from jakesutils.config import Config
import json
import os
from pathlib import Path
import requests
from subprocess import check_output, run
import sys
from termcolor import colored
from tqdm import tqdm


HOME_PATH = str(Path.home())
CONFIG = Config(f"{HOME_PATH}/.config/impulse/config.yaml", "yaml").config


def download_file(url: str, path: str, dohash: bool = True):
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


class PackageInstaller:
    def __init__(self, name: str):
        self.name = name

    def make_temp_dir(self):
        run(["sudo", "mkdir", f"/tmp/{self.name}"])

    def extract_tar(self):
        try:
            run(["sudo", "tar", "-xvf", f"/tmp/{self.name}.tar.gz", "-C", f"/tmp/{self.name}"])
            print(colored("Extracted!", "green"))
        except:
            print(colored("Error extracting archive!", "red"))

    def get_sub_temp_dir(self):
        self.sub_temp_dir = check_output(["ls", f"/tmp/{self.name}/"]).decode('ascii').strip()

    def show_diff(self):
        try:
            run(["less", f"/tmp/{self.name}/{self.sub_temp_dir}/impulse.build"])
        except:
            print(colored("Installation file doesn't exist!", "red"))

    def run_install(self):
        try:
            os.chdir(f"/tmp/{self.name}/{self.sub_temp_dir}/")
            print(colored("Installation complete!", "green"))
        except:
            print(colored("Installation failed!", "red"))

    def install_package(self):
        self.make_temp_dir()

        print("Extracting archive...")
        self.extract_tar()
        self.get_sub_temp_dir()

        if input("View impulse.build diff? [y/n] ").lower() == "y":
            self.show_diff()
        if input("Continue install? [y/n] ").lower() == "y":
            self.run_install()


def download_package(url: str, name: str):
    print(f"Downloading {name} from {url}")
    download_file(f"{url}{name}.tar.gz", "/tmp/")
    print(colored(f"Done downloading {name}!", "green"))
    if input(f"Do you want to install {name}? [y/n] ").lower() == "y":
        package_installer = PackageInstaller(name)
        package_installer.install_package()


def download_list(url: str):
    print(f"Downloading list from {url}")
    download_file(f"{url}list.json", f'{HOME_PATH}{CONFIG["local_path"]}', False)
    print(colored("Done downloading list", "green"))


def search_list(term: str):
    with open(f"{HOME_PATH}{CONFIG['local_path']}list.json") as json_file:
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


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-U", "--update", help="Update package database", action="store_true")
    parser.add_argument("-S", "--install", help="Install package")
    parser.add_argument("-Ss", "--search", help="Search package")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    if args.update:
        download_list(CONFIG["upstream"])

    elif args.install:
        download_package(CONFIG["upstream"], sys.argv[2])

    elif args.search:
        search_list(sys.argv[2])
