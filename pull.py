import requests
from subprocess import check_output


def download_file(url, path):
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(f'{path}{local_filename}', 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    
    return local_filename

def download_check(name):
    sha_pub = check_output(["cat", f"/tmp/{name}.sha"])
    sha_check = check_output(["sha256sum", f"/tmp/{name}.tar.gz"])
    print(sha_pub)
    print(sha_check)


def download_package(url, name): 
    download_file(f"{url}{name}.tar.gz", "/tmp/")
    download_file(f"{url}{name}.sha", "/tmp/")
    download_check(name)


_url = "https://jr0.org/impulse/"
_name = "rushnote"

download_package(_url, _name)

