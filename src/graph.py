"""Dependency graph builder using non-recursive BFS."""

from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Set, Tuple

INITIAL_DEPTH = 0
DEPTH_INCREMENT = 1
EMPTY_COUNT = 0


@dataclass
class GraphResult:
    """Result of dependency graph traversal."""

    root: str
    adj: Dict[str, List[str]] = field(default_factory=dict)
    cycles: List[Tuple[str, str]] = field(default_factory=list)
    depths: Dict[str, int] = field(default_factory=dict)


def is_filtered_out(package_name: str, filter_substring: str) -> bool:
    """Check if package should be excluded by substring filter."""
    if len(filter_substring.strip()) == EMPTY_COUNT:
        return False
    return filter_substring.lower() in package_name.lower()


def enqueue_child(
    parent: str,
    child: str,
    depth: int,
    path: Set[str],
    visited: Set[str],
    result: GraphResult,
) -> Optional[Tuple[str, int, Set[str]]]:
    """Check child for cycles and return queue item if unvisited."""
    if child not in result.adj[parent]:
        result.adj[parent].append(child)

    if child in path:
        result.cycles.append((parent, child))
        return None

    if child not in visited:
        visited.add(child)
        next_depth = depth + DEPTH_INCREMENT
        result.depths[child] = next_depth
        return (child, next_depth, path | {child})

    return None


def build_dependency_graph(
    root_package: str,
    fetch_deps_fn: Callable[[str], List[str]],
    max_depth: int,
    filter_substring: str = "",
) -> GraphResult:
    """Build dependency graph using non-recursive BFS with cycle detection."""
    result = GraphResult(root=root_package)
    result.adj[root_package] = []
    result.depths[root_package] = INITIAL_DEPTH

    queue: deque = deque([(root_package, INITIAL_DEPTH, {root_package})])
    visited: Set[str] = {root_package}

    while len(queue) > EMPTY_COUNT:
        node, depth, path = queue.popleft()
        if node not in result.adj:
            result.adj[node] = []
        if depth >= max_depth:
            continue

        for dep in fetch_deps_fn(node):
            if is_filtered_out(dep, filter_substring):
                continue
            item = enqueue_child(node, dep, depth, path, visited, result)
            if item is not None:
                queue.append(item)

    return result
