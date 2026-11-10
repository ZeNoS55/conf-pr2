"""Unit tests for Stage 3: BFS dependency graph construction."""

import unittest
from src.collector import parse_test_repo_file
from src.graph import build_dependency_graph, is_filtered_out

ZERO = 0
DEPTH_ZERO = 0
DEPTH_ONE = 1
DEPTH_TWO = 2
DEPTH_TEN = 10
CYCLE_COUNT_ONE = 1


class TestStage3Graph(unittest.TestCase):
    """Test suite for BFS dependency graph traversal."""

    def test_filter_matching(self) -> None:
        """Test substring filter matching logic."""
        self.assertTrue(is_filtered_out("Microsoft.Extensions", "microsoft"))
        self.assertTrue(is_filtered_out("CTEST", "TEST"))
        self.assertFalse(is_filtered_out("Serilog", "microsoft"))
        self.assertFalse(is_filtered_out("A", ""))

    def test_bfs_linear_graph(self) -> None:
        """Test non-recursive BFS on a linear dependency graph."""
        repo = {"A": ["B"], "B": ["C"], "C": ["D"], "D": []}
        res = build_dependency_graph(
            "A", lambda pkg: repo.get(pkg, []), DEPTH_TEN
        )
        self.assertEqual(res.adj.get("A"), ["B"])
        self.assertEqual(res.adj.get("B"), ["C"])
        self.assertEqual(res.adj.get("C"), ["D"])
        self.assertEqual(len(res.cycles), ZERO)

    def test_bfs_diamond_graph(self) -> None:
        """Test BFS on diamond graph with shared transitive dependency."""
        repo = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
        res = build_dependency_graph(
            "A", lambda pkg: repo.get(pkg, []), DEPTH_TEN
        )
        self.assertIn("B", res.adj["A"])
        self.assertIn("C", res.adj["A"])
        self.assertEqual(res.adj["B"], ["D"])
        self.assertEqual(res.adj["C"], ["D"])

    def test_bfs_max_depth_zero(self) -> None:
        """Test max depth 0 limits traversal to root only."""
        repo = {"A": ["B", "C"], "B": ["D"]}
        res = build_dependency_graph(
            "A", lambda pkg: repo.get(pkg, []), DEPTH_ZERO
        )
        self.assertEqual(len(res.adj["A"]), ZERO)

    def test_bfs_max_depth_one(self) -> None:
        """Test max depth 1 includes only direct dependencies."""
        repo = {"A": ["B", "C"], "B": ["D"], "C": ["E"]}
        res = build_dependency_graph(
            "A", lambda pkg: repo.get(pkg, []), DEPTH_ONE
        )
        self.assertEqual(res.adj["A"], ["B", "C"])
        self.assertEqual(len(res.adj.get("B", [])), ZERO)
        self.assertEqual(len(res.adj.get("C", [])), ZERO)

    def test_bfs_substring_filter(self) -> None:
        """Test that packages matching filter substring are excluded."""
        repo = parse_test_repo_file("test_repos/filtered.json")
        res = build_dependency_graph(
            "A",
            lambda pkg: repo.get(pkg, []),
            DEPTH_TEN,
            filter_substring="TEST",
        )
        self.assertEqual(res.adj["A"], ["B"])
        self.assertNotIn("CTEST", res.adj)

    def test_bfs_cycle_detection(self) -> None:
        """Test detecting cycle without entering infinite loop."""
        repo = parse_test_repo_file("test_repos/cycle.json")
        res = build_dependency_graph(
            "A", lambda pkg: repo.get(pkg, []), DEPTH_TEN
        )
        self.assertEqual(len(res.cycles), CYCLE_COUNT_ONE)
        self.assertEqual(res.cycles[ZERO], ("C", "A"))


if __name__ == "__main__":
    unittest.main()
