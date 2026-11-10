"""Module for computing dependency loading order."""

from collections import deque
from typing import Dict, List, Set, Tuple
from src.graph import GraphResult

EMPTY_COUNT = 0


def collect_graph_nodes(graph: GraphResult) -> Set[str]:
    """Collect all unique nodes present in graph result."""
    all_nodes: Set[str] = {graph.root}
    for node, targets in graph.adj.items():
        all_nodes.add(node)
        for target in targets:
            all_nodes.add(target)
    return all_nodes


def build_dependency_maps(
    graph: GraphResult, all_nodes: Set[str]
) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
    """Build prerequisite sets and reverse dependent sets for each node."""
    prereqs: Dict[str, Set[str]] = {node: set() for node in all_nodes}
    dependents: Dict[str, Set[str]] = {node: set() for node in all_nodes}

    cycle_edges = set(graph.cycles)

    for node, targets in graph.adj.items():
        for target in targets:
            if target not in all_nodes:
                continue
            if (node, target) in cycle_edges:
                continue
            prereqs[node].add(target)
            dependents[target].add(node)

    return prereqs, dependents


def compute_load_order(graph: GraphResult) -> List[str]:
    """Compute bottom-up load order ensuring dependencies load first."""
    all_nodes = collect_graph_nodes(graph)
    prereqs, dependents = build_dependency_maps(graph, all_nodes)

    ready: deque = deque(
        sorted(
            [node for node in all_nodes if len(prereqs[node]) == EMPTY_COUNT]
        )
    )
    load_order: List[str] = []
    visited: Set[str] = set()

    while len(ready) > EMPTY_COUNT:
        node = ready.popleft()
        if node in visited:
            continue
        visited.add(node)
        load_order.append(node)

        for dep in sorted(dependents[node]):
            if dep in visited:
                continue
            prereqs[dep].discard(node)
            if len(prereqs[dep]) == EMPTY_COUNT:
                ready.append(dep)

    remaining = sorted(all_nodes - visited)
    while len(remaining) > EMPTY_COUNT:
        next_node = remaining.pop(EMPTY_COUNT)
        load_order.append(next_node)
        visited.add(next_node)

    return load_order


def format_load_order(
    load_order: List[str], cycles: List[Tuple[str, str]]
) -> str:
    """Format package load order with cycle diagnostics."""
    lines: List[str] = []
    if len(cycles) > EMPTY_COUNT:
        lines.append("Warning: Cyclic dependencies detected:")
        for src, dst in cycles:
            lines.append(f"  {src} -> {dst}")
        lines.append("")

    lines.append("Package load order (bottom-up / prerequisites first):")
    for step, pkg in enumerate(load_order, start=1):
        lines.append(f"{step}. {pkg}")
    return "\n".join(lines)
