
from pathlib import Path

class KotlinBuilder:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.plugin_path = base_path / "repo-structure-plugin"
        self.template_dir = base_path / "setup/templates/kotlin"
        self.kotlin_dir = self.plugin_path / "src/main/kotlin/com/your/plugin"

    def build(self):
        """Creates all Kotlin source files."""
        kotlin_files = [
            "RepoStructurePlugin.kt",
            "FileChangeListener.kt",
            "RepoStructureDocumenter.kt",
            "UpdateStructureAction.kt"
        ]

        for file in kotlin_files:
            with open(self.template_dir / f"{file}.template", 'r') as f:
                content = f.read()
            with open(self.kotlin_dir / file, 'w') as f:
                f.write(content)

        self._create_plugin_xml()

    def _create_plugin_xml(self):
        plugin_template_dir = self.base_path / "setup/templates/plugin"
        with open(plugin_template_dir / "plugin.xml.template", 'r') as f:
            content = f.read()
        with open(self.plugin_path / "src/main/resources/META-INF/plugin.xml", 'w') as f:
            f.write(content)
