"""Main entry point for NuGet dependency graph visualizer."""

import sys
from typing import List, Optional
from src.cli import create_parser, parse_arguments
from src.collector import get_direct_dependencies
from src.config import Config, format_config_kv
from src.graph import GraphResult, build_dependency_graph
from src.order import compute_load_order, format_load_order
from src.visualizer import (
    display_image_on_screen,
    generate_plantuml_text,
    render_plantuml_to_png,
)

STAGE_1 = 1
STAGE_2 = 2
STAGE_3 = 3
STAGE_4 = 4
STAGE_5 = 5
EMPTY_COUNT = 0
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
DEFAULT_OUTPUT_IMAGE = "dependency_graph.png"


def run_stage1(cfg: Config) -> None:
    """Execute Stage 1: display configurable parameters in key-value form."""
    print("=== Stage 1: Configuration ===")
    print(format_config_kv(cfg))


def run_stage2(cfg: Config) -> List[str]:
    """Execute Stage 2: display direct dependencies of target package."""
    deps = get_direct_dependencies(
        cfg.package_name, cfg.repo, test_mode=cfg.test_mode
    )
    print(f"=== Stage 2: Direct Dependencies for {cfg.package_name} ===")
    if len(deps) == EMPTY_COUNT:
        print("(No direct dependencies found)")
    else:
        for dep in deps:
            print(f"- {dep}")
    return deps


def run_stage3(cfg: Config) -> GraphResult:
    """Execute Stage 3: construct graph via non-recursive BFS."""
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
    return result


def run_stage4(cfg: Config, graph: Optional[GraphResult] = None) -> List[str]:
    """Execute Stage 4: compute and display package loading order."""
    if graph is None:
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
    return order


def run_stage5(
    cfg: Config,
    no_gui: bool = False,
    graph: Optional[GraphResult] = None,
) -> None:
    """Execute Stage 5: generate PlantUML diagram and display image."""
    if graph is None:
        graph = build_dependency_graph(
            root_package=cfg.package_name,
            fetch_deps_fn=lambda pkg: get_direct_dependencies(
                pkg, cfg.repo, test_mode=cfg.test_mode
            ),
            max_depth=cfg.max_depth,
            filter_substring=cfg.filter_substring,
        )
    puml = generate_plantuml_text(graph)
    print("=== Stage 5: PlantUML Text ===")
    print(puml)

    success = render_plantuml_to_png(puml, DEFAULT_OUTPUT_IMAGE)
    if success:
        print(f"\nGraph image saved to: {DEFAULT_OUTPUT_IMAGE}")
        display_image_on_screen(DEFAULT_OUTPUT_IMAGE, no_gui=no_gui)
    else:
        print("\nPlantUML online rendering unavailable (offline fallback).")


def execute_stage(cfg: Config) -> None:
    """Dispatch pipeline execution based on configured stage."""
    stage = cfg.stage
    if stage == STAGE_1:
        run_stage1(cfg)
    elif stage == STAGE_2:
        run_stage2(cfg)
    elif stage == STAGE_3:
        run_stage3(cfg)
    elif stage == STAGE_4:
        run_stage4(cfg)
    else:
        run_stage1(cfg)
        print()
        graph = run_stage3(cfg)
        print()
        run_stage4(cfg, graph=graph)
        print()
        run_stage5(cfg, no_gui=cfg.no_gui, graph=graph)


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point coordinating stage executions."""
    try:
        cfg = parse_arguments(argv)
    except ValueError as err:
        print(f"Configuration Error: {err}", file=sys.stderr)
        return EXIT_FAILURE

    try:
        execute_stage(cfg)
    except RuntimeError as err:
        print(f"Runtime Error: {err}", file=sys.stderr)
        return EXIT_FAILURE

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
