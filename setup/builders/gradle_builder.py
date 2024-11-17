
from pathlib import Path
from string import Template

class GradleBuilder:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.plugin_path = base_path / "repo-structure-plugin"
        self.template_dir = base_path / "setup/templates/gradle"

    def build(self):
        """Creates all Gradle-related files."""
        self._create_build_gradle()
        self._create_settings_gradle()
        self._create_gradle_properties()

    def _create_build_gradle(self):
        with open(self.template_dir / "build.gradle.kts.template", 'r') as f:
            template = Template(f.read())
        content = template.substitute({})
        with open(self.plugin_path / "build.gradle.kts", 'w') as f:
            f.write(content)

    def _create_settings_gradle(self):
        with open(self.template_dir / "settings.gradle.kts.template", 'r') as f:
            content = f.read()
        with open(self.plugin_path / "settings.gradle.kts", 'w') as f:
            f.write(content)

    def _create_gradle_properties(self):
        with open(self.template_dir / "gradle.properties.template", 'r') as f:
            content = f.read()
        with open(self.plugin_path / "gradle.properties", 'w') as f:
            f.write(content)
