"""Data collector module for .NET (NuGet) dependencies."""

import json
import os
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from typing import Dict, List, Set

EMPTY_LEN = 0
FIRST_INDEX = 0
LAST_INDEX = -1
TIMEOUT_SECONDS = 15
USER_AGENT = "DepVisualizer/1.0"


def fetch_json(url: str) -> dict:
    """Fetch and decode JSON data from remote URL."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as response:
        content = response.read().decode("utf-8")
        return json.loads(content)


def extract_deps_from_groups(dependency_groups: list) -> List[str]:
    """Extract unique dependency package names from NuGet dependency groups."""
    dependencies: Set[str] = set()
    for group in dependency_groups:
        group_deps = group.get("dependencies", [])
        for item in group_deps:
            dep_id = item.get("id")
            if dep_id:
                dependencies.add(dep_id)
    return sorted(dependencies)


def fetch_nuget_dependencies(repo_url: str, package_name: str) -> List[str]:
    """Retrieve direct dependencies for a package from NuGet v3 API."""
    clean_repo = repo_url.rstrip("/")
    package_key = package_name.strip().lower()
    index_url = f"{clean_repo}/{package_key}/index.json"

    try:
        index_data = fetch_json(index_url)
    except urllib.error.HTTPError as error:
        raise RuntimeError(
            f"Failed to fetch package '{package_name}': HTTP {error.code}"
        ) from error

    pages = index_data.get("items", [])
    if len(pages) == EMPTY_LEN:
        return []

    target_page = pages[LAST_INDEX]
    if "items" not in target_page:
        page_url = target_page.get("@id")
        if not page_url:
            return []
        target_page = fetch_json(page_url)

    catalog_items = target_page.get("items", [])
    if len(catalog_items) == EMPTY_LEN:
        return []

    latest_entry = catalog_items[LAST_INDEX].get("catalogEntry", {})
    dep_groups = latest_entry.get("dependencyGroups", [])
    return extract_deps_from_groups(dep_groups)


def parse_nuspec_content(content: str) -> List[str]:
    """Parse nuspec XML string and extract dependency IDs."""
    root = ET.fromstring(content)
    dependencies: Set[str] = set()
    for elem in root.iter():
        tag = elem.tag.split("}")[LAST_INDEX]
        if tag == "dependency":
            dep_id = elem.attrib.get("id")
            if dep_id:
                dependencies.add(dep_id)
    return sorted(dependencies)


def parse_test_repo_json(raw_text: str) -> Dict[str, List[str]]:
    """Parse test repository content in JSON format."""
    parsed = json.loads(raw_text)
    return {
        str(k).strip(): [str(item).strip() for item in v]
        for k, v in parsed.items()
    }


def parse_test_repo_text(raw_text: str) -> Dict[str, List[str]]:
    """Parse test repository content in line-based text format."""
    graph: Dict[str, List[str]] = {}
    for line in raw_text.splitlines():
        line = line.strip()
        if len(line) == EMPTY_LEN:
            continue
        cleaned = line.replace("->", ":")
        parts = cleaned.split(":")
        node = parts[FIRST_INDEX].strip()
        targets: List[str] = []
        if len(parts) > 1 and len(parts[1].strip()) > EMPTY_LEN:
            for item in re.split(r"[,; ]+", parts[1].strip()):
                if len(item.strip()) > EMPTY_LEN:
                    targets.append(item.strip())
        graph[node] = targets
    return graph


def parse_test_repo_file(file_path: str) -> Dict[str, List[str]]:
    """Parse test repository file in JSON or text adjacency list format."""
    with open(file_path, "r", encoding="utf-8") as file_handle:
        raw_text = file_handle.read().strip()

    if len(raw_text) == EMPTY_LEN:
        return {}

    if raw_text.startswith("{"):
        return parse_test_repo_json(raw_text)

    return parse_test_repo_text(raw_text)


def get_direct_dependencies(
    package: str, repo: str, test_mode: bool
) -> List[str]:
    """Get direct dependencies for package from real or test repository."""
    if test_mode:
        repo_data = parse_test_repo_file(repo)
        return repo_data.get(package, [])
    if repo.endswith(".nuspec") or repo.endswith(".xml"):
        with open(repo, "r", encoding="utf-8") as file_handle:
            return parse_nuspec_content(file_handle.read())
    return fetch_nuget_dependencies(repo, package)
