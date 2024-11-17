
from pathlib import Path

class DirectoryBuilder:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.plugin_path = base_path / "repo-structure-plugin"

    def build(self):
        """Creates the basic directory structure for the plugin."""
        directories = [
            "src/main/kotlin/com/your/plugin",
            "src/main/resources/META-INF",
            "src/test/kotlin/com/your/plugin",
            "gradle/wrapper"
        ]

        for directory in directories:
            (self.plugin_path / directory).mkdir(parents=True, exist_ok=True)
