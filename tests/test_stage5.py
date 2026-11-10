"""Unit tests for Stage 5: PlantUML generation and visualization."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from src.graph import GraphResult
from src.visualizer import (
    PLANTUML_CHARS,
    display_image_on_screen,
    encode_plantuml,
    generate_plantuml_text,
    render_plantuml_to_png,
)

EMPTY_LEN = 0


class TestStage5Visualizer(unittest.TestCase):
    """Test suite for PlantUML generator and visualization."""

    def test_generate_plantuml_text_simple(self) -> None:
        """Test generating PlantUML syntax for a directed graph."""
        graph = GraphResult(
            root="A",
            adj={"A": ["B", "C"], "B": ["D"], "C": [], "D": []},
            cycles=[],
            depths={"A": 0, "B": 1, "C": 1, "D": 2},
        )
        puml = generate_plantuml_text(graph)
        self.assertIn("@startuml", puml)
        self.assertIn("@enduml", puml)
        self.assertIn("[A] #LightBlue", puml)
        self.assertIn("[A] --> [B]", puml)
        self.assertIn("[A] --> [C]", puml)
        self.assertIn("[B] --> [D]", puml)

    def test_generate_plantuml_with_cycle(self) -> None:
        """Test formatting cycle edges as dashed lines."""
        graph = GraphResult(
            root="A",
            adj={"A": ["B"], "B": ["A"]},
            cycles=[("B", "A")],
            depths={"A": 0, "B": 1},
        )
        puml = generate_plantuml_text(graph)
        self.assertIn("[B] ..> [A] : cycle", puml)

    def test_encode_plantuml(self) -> None:
        """Test PlantUML URL string encoding."""
        sample = "@startuml\nA -> B\n@enduml"
        encoded = encode_plantuml(sample)
        self.assertGreater(len(encoded), EMPTY_LEN)
        for char in encoded:
            self.assertIn(char, PLANTUML_CHARS)

    @patch("src.visualizer.urllib.request.urlopen")
    def test_render_plantuml_to_png_mocked(
        self, mock_urlopen: MagicMock
    ) -> None:
        """Test rendering PlantUML diagram to PNG file with mocked HTTP."""
        fake_response = MagicMock()
        fake_response.read.return_value = b"\x89PNG\r\n\x1a\nfakeimagebytes"
        mock_urlopen.return_value.__enter__.return_value = fake_response

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".png"
        ) as file_handle:
            tmp_path = file_handle.name

        try:
            success = render_plantuml_to_png("@startuml\n@enduml", tmp_path)
            self.assertTrue(success)
            self.assertTrue(os.path.isfile(tmp_path))
            with open(tmp_path, "rb") as reader:
                data = reader.read()
                self.assertTrue(data.startswith(b"\x89PNG"))
        finally:
            if os.path.isfile(tmp_path):
                os.remove(tmp_path)

    def test_display_image_no_gui(self) -> None:
        """Test that display does not fail when no_gui flag is set."""
        display_image_on_screen("non_existent_image.png", no_gui=True)


if __name__ == "__main__":
    unittest.main()
