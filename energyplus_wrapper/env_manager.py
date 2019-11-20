#!/usr/bin/env python
# coding=utf-8


import re
import sys

import pexpect
import requests
from path import Path, tempdir
import fasteners

eplus_filename_pattern = r".*?(?P<filename>EnergyPlus-(?P<version>\d+.\d+.\d+)-(?P<revision>\w+)-(?P<platform>.*?).sh)$"


def is_downloadable(url):
    content_type = (
        requests.head(url, allow_redirects=True).headers.get("content-type").lower()
    )
    if "text" in content_type:
        return False
    if "html" in content_type:
        return False
    return True


def extract_filename_info(url):
    filename_match = re.match(pattern=eplus_filename_pattern, string=url)
    return filename_match.groupdict()


def check_installer_name(installer_name):
    re.match("EnergyPlus-[]")


def download_eplus_version(url, path):
    if not is_downloadable(url):
        raise ValueError("URL is not a downloadable file.")
    response = requests.get(url, allow_redirects=True)
    with open(path, "wb") as f:
        f.write(response.content)


def extract_and_install(setup_script, eplus_folder):
    with pexpect.spawn(f"bash {setup_script}") as child:
        # child.logfile = sys.stderr
        child.expect("\r\n")
        # child.expect(r"Do you accept the license\? \[yN\]:")
        child.sendline("y")
        # child.expect(r"EnergyPlus install directory \[.*\]:")
        child.sendline(eplus_folder)
        child.expect("\r\n")
        # child.expect(r'Symbolic link location \(enter "n" for no links\) \[.*\]:')
        child.sendline("n")
        child.expect(pexpect.EOF)


def ensure_eplus_root(url, eplus_folder, installer_cache=None):
    eplus_folder = Path(eplus_folder)
    eplus_folder.mkdir_p()
    with fasteners.InterProcessLock(eplus_folder / '.lock'):

        def url_to_installed(url, eplus_folder, script_path):
            if not script_path.exists():
                download_eplus_version(url, script_path)
            extract_and_install(script_path, eplus_folder)

        finfo = extract_filename_info(url)
        filename = finfo["filename"]
        version = finfo["version"]
        expected_eplus_folder = eplus_folder / f"EnergyPlus-{version.replace('.', '-')}"
        if expected_eplus_folder.exists() and expected_eplus_folder.files():
            return expected_eplus_folder.abspath()
        expected_eplus_folder.rmtree_p()
        if installer_cache is None:
            with tempdir() as d:
                url_to_installed(url, eplus_folder, d / filename)
        else:
            installer_cache = Path(installer_cache)
            installer_cache.mkdir_p()
            url_to_installed(url, eplus_folder, installer_cache / filename)
        return expected_eplus_folder.abspath()
