"""Main entry point for stage 4: package loading order computation."""

import sys
from typing import List, Optional
from src.cli import parse_arguments
from src.collector import get_direct_dependencies
from src.graph import build_dependency_graph
from src.order import compute_load_order, format_load_order


def main(argv: Optional[List[str]] = None) -> int:
    """Compute and display bottom-up package load order."""
    cfg = parse_arguments(argv)
    graph = build_dependency_graph(
        root_package=cfg.package_name,
        fetch_deps_fn=lambda pkg: get_direct_dependencies(
            pkg, cfg.repo, test_mode=cfg.test_mode
        ),
        max_depth=cfg.max_depth,
        filter_substring=cfg.filter_substring,
    )
    order = compute_load_order(graph)
    print("=== Stage 4: Package Load Order ===")
    print(format_load_order(order, graph.cycles))
    return 0


if __name__ == "__main__":
    sys.exit(main())
