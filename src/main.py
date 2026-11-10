"""Main entry point for stage 3: BFS dependency graph construction."""

import sys
from typing import List, Optional
from src.cli import parse_arguments
from src.collector import get_direct_dependencies
from src.graph import build_dependency_graph

EMPTY_COUNT = 0


def main(argv: Optional[List[str]] = None) -> int:
    """Build dependency graph using non-recursive BFS and print edges."""
    cfg = parse_arguments(argv)
    result = build_dependency_graph(
        root_package=cfg.package_name,
        fetch_deps_fn=lambda pkg: get_direct_dependencies(
            pkg, cfg.repo, test_mode=cfg.test_mode
        ),
        max_depth=cfg.max_depth,
        filter_substring=cfg.filter_substring,
    )
    print(f"=== Stage 3: BFS Graph (Root: {cfg.package_name}) ===")
    for src in sorted(result.adj.keys()):
        print(f"{src} -> {result.adj[src]}")
    if len(result.cycles) > EMPTY_COUNT:
        print(f"Detected cycles: {result.cycles}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
