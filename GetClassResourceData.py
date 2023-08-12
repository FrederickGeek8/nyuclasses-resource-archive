import json
from pathlib import Path
from getpass import getpass

from src.webdav3.client import Client

from src.slugify import slugify

import argparse

parser = argparse.ArgumentParser(
    prog="NYU Class Resource Scraper",
    description="Tool for scraping NYU Classes data over WebDAV",
)
parser.add_argument("-j", "--json", type=str, default="classes.txt")
parser.add_argument("-u", "--user", type=str, default=None)
parser.add_argument("-p", "--pass", type=str, default=None)
parser.add_argument("-o", "--outdir", type=str, default=None)
args = vars(parser.parse_args())

print(
    "Run the following in your Javascript console in your web browser's development tools"
)
print(
    """
JSON.stringify(Object.fromEntries(Array.from(document.querySelectorAll("[headers=worksite]")).map(x => ([x.children[0]?.innerText, x.children[0]?.href]))))
"""
)

input(
    f"Put the result in a file called {args['json']} in this directory and press enter.")


data_path = Path(args["json"])

if not data_path.exists():
    raise FileNotFoundError(
        f"{data_path} does not exist. Please ensure you have populated the result of the javascript function there. Exiting."
    )

print("Trying to load data...")

with open(data_path, "r") as f:
    dir_json = json.load(f)

class_map = {}
print("You are looking to copy the following data:")
for name, url in dir_json.items():
    cls_id = url.split("/")[-1]
    print(f"\t Name: {name} \t ID: {cls_id}")
    class_map[name] = cls_id


print("===== AUTHENTICATION =====")
if args["user"] is not None and args["pass"] is not None:
    username = args["user"].strip()
    password = args["pass"].strip()
else:
    print("We need to get your NYU netid and password to log in.")
    username = input("NYU username: ").strip()
    password = getpass("NYU Password: ").strip()

options = {
    "webdav_hostname": "https://newclasses.nyu.edu/dav/",
    "webdav_login": username,
    "webdav_password": password,
}

client = Client(options)

print()
print("===== READY TO START DOWNLOAD =====")
if args["outdir"] is not None:
    root_dir = args["outdir"].strip()
else:
    root_dir = input(
        "Enter the path to the directory where you want to download all the class data: "
    ).strip()
root_dir = Path(root_dir)

for name, cls_id in class_map.items():
    safe_name = slugify(name)
    print(f"{safe_name} listing {cls_id}")
    print(client.list(cls_id))
    output_dir = root_dir / safe_name
    output_dir.mkdir(exist_ok=True, parents=True)
    print(f"Pulling {safe_name} to {output_dir}...")

    client.pull(remote_directory=cls_id, local_directory=str(output_dir))
