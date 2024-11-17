
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
