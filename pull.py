
from subprocess import check_output
import requests
import hashlib
import json


def download_file(url, path, dohash):
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        sha = hashlib.sha256()
        with open(f'{path}{local_filename}', 'wb+') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    sha.update(chunk)
        if dohash:
            print(sha.hexdigest())
    
    return local_filename


def download_package(url, name, dohash): 
    print(f"Downloading {name} from {url}")
    download_file(f"{url}{name}.tar.gz", "/tmp/", True)
    print(f"Done downloading {name}")


def download_list(url): 
    print(f"Downloading list from {url}")
    download_file(f"{url}list.json", "/home/jake/.local/share/impulse/", False)
    print("Done downloading list")


def search_list(term):
    with open("/home/jake/.local/share/impulse/list.json") as json_file:
        data = json.load(json_file)
        if term in data:
            print(data[term]["name"])
            print(f'-- {data[term]["desc"]}')


download_package("https://jr0.org/impulse/", "rushnote", True)
download_list("https://jr0.org/impulse/")
search_list("test")
