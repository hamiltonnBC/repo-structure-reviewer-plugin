#!/usr/bin/env python3
import os
from pathlib import Path
import shutil
from textwrap import dedent

class ProjectStructureCreator:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.setup_dir = base_path / "setup"
        self.existing_code = self._get_existing_code()

    def _get_existing_code(self):
        """Extract the existing code from your current setup_plugin.py"""
        kotlin_files = {
            "RepoStructurePlugin.kt": None,
            "FileChangeListener.kt": None,
            "RepoStructureDocumenter.kt": None,
            "UpdateStructureAction.kt": None
        }

        try:
            with open(self.base_path / "setup_plugin.py", 'r') as f:
                content = f.read()

            # Extract Kotlin code blocks
            for file in kotlin_files.keys():
                start = content.find(f'"{file}": \'\'\'')
                if start != -1:
                    end = content.find("'''", start + len(file) + 7)
                    kotlin_files[file] = content[start + len(file) + 7:end].strip()
        except FileNotFoundError:
            print("Warning: setup_plugin.py not found. Creating new templates.")

        return kotlin_files

    def create_directory_structure(self):
        """Create the basic directory structure"""
        directories = [
            "setup/builders",
            "setup/templates/gradle",
            "setup/templates/kotlin",
            "setup/templates/plugin"
        ]

        for directory in directories:
            (self.base_path / directory).mkdir(parents=True, exist_ok=True)

    def create_init_files(self):
        """Create __init__.py files"""
        init_locations = [
            "setup",
            "setup/builders"
        ]

        for location in init_locations:
            (self.base_path / location / "__init__.py").touch()

    def create_main_setup(self):
        """Create the main setup.py file"""
        content = '''
        #!/usr/bin/env python3
        from pathlib import Path
        from setup.builders.directory_builder import DirectoryBuilder
        from setup.builders.gradle_builder import GradleBuilder
        from setup.builders.kotlin_builder import KotlinBuilder

        def main():
            base_path = Path.cwd()
            builders = [
                DirectoryBuilder(base_path),
                GradleBuilder(base_path),
                KotlinBuilder(base_path)
            ]
            
            for builder in builders:
                builder.build()

        if __name__ == "__main__":
            main()
        '''

        with open(self.base_path / "setup.py", 'w') as f:
            f.write(dedent(content))

        # Make executable
        os.chmod(self.base_path / "setup.py", 0o755)

    def create_builders(self):
        """Create builder class files"""
        # Directory Builder
        directory_builder = '''
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
        '''

        # Gradle Builder
        gradle_builder = '''
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
        '''

        # Kotlin Builder
        kotlin_builder = '''
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
        '''

        builders = {
            "directory_builder.py": directory_builder,
            "gradle_builder.py": gradle_builder,
            "kotlin_builder.py": kotlin_builder
        }

        for filename, content in builders.items():
            with open(self.base_path / "setup/builders" / filename, 'w') as f:
                f.write(dedent(content))

    def create_templates(self):
        """Create template files"""
        # Gradle templates
        gradle_templates = {
            "build.gradle.kts.template": '''
            plugins {
                id("java")
                id("org.jetbrains.kotlin.jvm") version "1.9.22"
                id("org.jetbrains.intellij") version "1.17.2"
            }
            
            group = "com.your.plugin"
            version = "1.0-SNAPSHOT"
            
            repositories {
                mavenCentral()
            }
            
            kotlin {
                jvmToolchain(17)
            }
            
            intellij {
                version.set("2023.3.3")
                type.set("IC")
                plugins.set(listOf(
                    "com.intellij.java",
                    "org.jetbrains.kotlin"
                ))
            }
            
            dependencies {
                implementation("org.jetbrains.kotlin:kotlin-stdlib-jdk8")
            }
            
            tasks {
                buildSearchableOptions {
                    enabled = false
                }
            
                patchPluginXml {
                    sinceBuild.set("233")
                    untilBuild.set("241.*")
                }
            
                runIde {
                    jvmArgs = listOf("-Xmx1024m", "-Xms256m")
                }
            }
            ''',
            "settings.gradle.kts.template": 'rootProject.name = "repo-structure-plugin"',
            "gradle.properties.template": '''
            # Gradle properties
            org.gradle.jvmargs=-Xmx2048M -Dkotlin.daemon.jvm.options\\="-Xmx2048M"
            '''
        }

        # Create Gradle templates
        for filename, content in gradle_templates.items():
            with open(self.base_path / "setup/templates/gradle" / filename, 'w') as f:
                f.write(dedent(content))

        # Create Kotlin templates
        for filename, content in self.existing_code.items():
            if content:
                with open(self.base_path / "setup/templates/kotlin" / f"{filename}.template", 'w') as f:
                    f.write(content)

        # Create plugin.xml template
        plugin_xml = '''
        <idea-plugin>
            <id>com.your.plugin.repo-structure</id>
            <name>Repository Structure Documenter</name>
            <vendor>Your Name</vendor>
            <description>Automatically generates and updates repository structure documentation</description>
            
            <depends>com.intellij.modules.platform</depends>
            <depends>com.intellij.modules.java</depends>
            
            <extensions defaultExtensionNs="com.intellij">
                <postStartupActivity implementation="com.your.plugin.RepoStructurePlugin"/>
            </extensions>
            
            <actions>
                <action id="UpdateStructureAction" 
                        class="com.your.plugin.UpdateStructureAction" 
                        text="Update Repository Structure" 
                        description="Update repository structure documentation">
                    <add-to-group group-id="ProjectViewPopupMenu" anchor="last"/>
                </action>
            </actions>
        </idea-plugin>
        '''

        with open(self.base_path / "setup/templates/plugin/plugin.xml.template", 'w') as f:
            f.write(dedent(plugin_xml))

    def create_gitignore(self):
        """Create .gitignore file"""
        content = '''
        .gradle/
        build/
        .idea/
        *.iml
        out/
        .DS_Store
        __pycache__/
        venv/
        '''

        with open(self.base_path / ".gitignore", 'w') as f:
            f.write(dedent(content))

    def setup(self):
        """Run the complete setup process"""
        print("Creating project structure...")
        self.create_directory_structure()
        self.create_init_files()
        self.create_main_setup()
        self.create_builders()
        self.create_templates()
        self.create_gitignore()
        print("Project structure created successfully!")

def main():
    creator = ProjectStructureCreator(Path.cwd())
    creator.setup()
    print("""
Setup complete! Your project structure has been created.

To build the plugin:
1. Run the setup script:
   python setup.py

2. Open the generated plugin project in IntelliJ IDEA:
   - Open the repo-structure-plugin directory
   - Wait for Gradle sync
   - Run using Gradle task: runIde
    """)

if __name__ == "__main__":
    main()