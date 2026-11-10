"""Unit tests for Stage 4: Dependency loading order computation."""

import unittest
from src.graph import GraphResult
from src.order import compute_load_order, format_load_order

LAST_INDEX = -1
EMPTY_COUNT = 0


class TestStage4Order(unittest.TestCase):
    """Test suite for dependency load order algorithm."""

    def test_load_order_linear(self) -> None:
        """Test load order for simple linear dependency chain."""
        graph = GraphResult(
            root="A",
            adj={"A": ["B"], "B": ["C"], "C": ["D"], "D": []},
            cycles=[],
            depths={"A": 0, "B": 1, "C": 2, "D": 3},
        )
        order = compute_load_order(graph)
        self.assertEqual(order, ["D", "C", "B", "A"])

    def test_load_order_diamond(self) -> None:
        """Test load order for diamond dependency graph."""
        graph = GraphResult(
            root="A",
            adj={"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []},
            cycles=[],
            depths={"A": 0, "B": 1, "C": 1, "D": 2},
        )
        order = compute_load_order(graph)
        self.assertEqual(order[0], "D")
        self.assertEqual(order[LAST_INDEX], "A")
        self.assertIn("B", order[1:3])
        self.assertIn("C", order[1:3])

    def test_load_order_with_cycle(self) -> None:
        """Test load order resolves all nodes even when cycles exist."""
        graph = GraphResult(
            root="A",
            adj={"A": ["B"], "B": ["C"], "C": ["A"]},
            cycles=[("C", "A")],
            depths={"A": 0, "B": 1, "C": 2},
        )
        order = compute_load_order(graph)
        self.assertEqual(len(order), 3)
        self.assertEqual(set(order), {"A", "B", "C"})

    def test_format_load_order(self) -> None:
        """Test text formatting of dependency load order."""
        formatted = format_load_order(["D", "B", "A"], cycles=[("C", "A")])
        self.assertIn("Warning: Cyclic dependencies detected:", formatted)
        self.assertIn("1. D", formatted)
        self.assertIn("2. B", formatted)
        self.assertIn("3. A", formatted)


if __name__ == "__main__":
    unittest.main()
