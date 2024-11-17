#!/usr/bin/env python3
import os
import shutil
from pathlib import Path
import subprocess
import sys

class PluginSetup:
    """Sets up the repository structure for the JetBrains plugin project."""

    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.plugin_path = self.base_path / "repo-structure-plugin"

    def create_directory_structure(self):
        """Creates the basic directory structure for the plugin."""
        directories = [
            "src/main/kotlin/com/your/plugin",
            "src/main/resources/META-INF",
            "src/test/kotlin/com/your/plugin",
            "gradle/wrapper"
        ]

        for directory in directories:
            (self.plugin_path / directory).mkdir(parents=True, exist_ok=True)

    def create_build_gradle(self):
        """Creates the build.gradle.kts file."""
        content = '''
plugins {
    id("java")
    id("org.jetbrains.kotlin.jvm") version "1.8.21"
    id("org.jetbrains.intellij") version "1.13.3"
}

group = "com.your.plugin"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
}

intellij {
    version.set("2023.1.3")
    type.set("IC") // IC for IntelliJ IDEA Community, IU for Ultimate
    plugins.set(listOf("com.intellij.java"))
}

tasks {
    withType<JavaCompile> {
        sourceCompatibility = "17"
        targetCompatibility = "17"
    }
    
    withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile> {
        kotlinOptions.jvmTarget = "17"
    }

    patchPluginXml {
        sinceBuild.set("231")
        untilBuild.set("241.*")
    }
}
        '''.strip()

        with open(self.plugin_path / "build.gradle.kts", "w") as f:
            f.write(content)

    def create_settings_gradle(self):
        """Creates the settings.gradle.kts file."""
        content = 'rootProject.name = "repo-structure-plugin"'
        with open(self.plugin_path / "settings.gradle.kts", "w") as f:
            f.write(content)

    def create_gradle_properties(self):
        """Creates the gradle.properties file."""
        content = '''
# Gradle properties
org.gradle.jvmargs=-Xmx2048M -Dkotlin.daemon.jvm.options\\="-Xmx2048M"
        '''.strip()

        with open(self.plugin_path / "gradle.properties", "w") as f:
            f.write(content)

    def create_gitignore(self):
        """Creates the .gitignore file."""
        content = '''
.gradle/
build/
.idea/
*.iml
out/
.DS_Store
        '''.strip()

        with open(self.plugin_path / ".gitignore", "w") as f:
            f.write(content)

    def create_plugin_xml(self):
        """Creates the plugin.xml file."""
        content = '''
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
        '''.strip()

        with open(self.plugin_path / "src/main/resources/META-INF/plugin.xml", "w") as f:
            f.write(content)

    def create_kotlin_files(self):
        """Creates the Kotlin source files."""
        files = {
            "RepoStructurePlugin.kt": '''
package com.your.plugin

import com.intellij.openapi.project.Project
import com.intellij.openapi.startup.StartupActivity
import com.intellij.openapi.vfs.VirtualFileManager

class RepoStructurePlugin : StartupActivity {
    override fun runActivity(project: Project) {
        val connection = project.messageBus.connect()
        connection.subscribe(VirtualFileManager.VFS_CHANGES, FileChangeListener(project))
    }
}
            '''.strip(),

            "FileChangeListener.kt": '''
package com.your.plugin

import com.intellij.openapi.project.Project
import com.intellij.openapi.vfs.newvfs.BulkFileListener
import com.intellij.openapi.vfs.newvfs.events.VFileEvent
import com.intellij.openapi.command.WriteCommandAction
import com.intellij.openapi.vfs.LocalFileSystem

class FileChangeListener(private val project: Project) : BulkFileListener {
    private val documenter = RepoStructureDocumenter(project)
    
    override fun after(events: List<VFileEvent>) {
        val shouldUpdate = events.any { 
            it.file?.extension in listOf("kt", "java", "py", "js", "jsx", "ts", "tsx") 
        }
        
        if (shouldUpdate) {
            project.basePath?.let { basePath ->
                val projectDir = LocalFileSystem.getInstance().findFileByPath(basePath) ?: return
                
                listOf("frontend", "backend").forEach { dirName ->
                    projectDir.findChild(dirName)?.let { dir ->
                        val content = documenter.generateStructure(dir)
                        WriteCommandAction.runWriteCommandAction(project) {
                            val structureFile = dir.findChild("REPOSITORY_STRUCTURE.md") 
                                ?: dir.createChildData(this, "REPOSITORY_STRUCTURE.md")
                            structureFile.setBinaryContent(content.toByteArray())
                        }
                    }
                }
            }
        }
    }
}
            '''.strip(),

            "RepoStructureDocumenter.kt": '''
package com.your.plugin

import com.intellij.openapi.project.Project
import com.intellij.openapi.vfs.VirtualFile
import com.intellij.psi.*
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

class RepoStructureDocumenter(private val project: Project) {
    private val psiManager = PsiManager.getInstance(project)
    
    fun generateStructure(directory: VirtualFile): String {
        val content = StringBuilder()
        content.append("# ${directory.name.uppercase()} Structure\\n")
        content.append("Last updated: ${LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME)}\\n\\n")
        
        content.append("## Directory Structure\\n```\\n")
        content.append(generateTree(directory))
        content.append("\\n```\\n\\n")
        
        content.append("## File Documentation\\n")
        generateDocumentation(directory, content)
        
        return content.toString()
    }
    
    private fun generateTree(file: VirtualFile, prefix: String = ""): String {
        val content = StringBuilder()
        val children = file.children.sortedWith(compareBy({ !it.isDirectory }, { it.name }))
        
        children.forEachIndexed { index, child ->
            val isLast = index == children.lastIndex
            val connector = if (isLast) "└── " else "├── "
            
            content.append("$prefix$connector${child.name}\\n")
            
            if (child.isDirectory) {
                val newPrefix = prefix + if (isLast) "    " else "│   "
                content.append(generateTree(child, newPrefix))
            }
        }
        
        return content.toString()
    }
    
    private fun generateDocumentation(directory: VirtualFile, content: StringBuilder, relativePath: String = "") {
        directory.children.sortedWith(compareBy({ !it.isDirectory }, { it.name })).forEach { file ->
            if (file.isDirectory) {
                val newPath = if (relativePath.isEmpty()) file.name else "$relativePath/${file.name}"
                content.append("\\n### $newPath\\n")
                generateDocumentation(file, content, newPath)
            } else {
                when (file.extension) {
                    "kt", "java" -> extractKotlinJavaDoc(file, content)
                    "py" -> extractPythonDoc(file, content)
                    "js", "jsx", "ts", "tsx" -> extractJavaScriptDoc(file, content)
                }
            }
        }
    }
    
    private fun extractKotlinJavaDoc(file: VirtualFile, content: StringBuilder) {
        val psiFile = psiManager.findFile(file) ?: return
        content.append("\\n#### ${file.name}\\n")
        
        if (psiFile is PsiJavaFile) {
            psiFile.classes.forEach { psiClass ->
                psiClass.docComment?.let {
                    content.append("\\n${it.text}\\n")
                }
            }
        }
    }
    
    private fun extractPythonDoc(file: VirtualFile, content: StringBuilder) {
        val text = String(file.contentsToByteArray())
        val docstring = extractPythonDocstring(text)
        if (docstring.isNotEmpty()) {
            content.append("\\n#### ${file.name}\\n")
            content.append("$docstring\\n")
        }
    }
    
    private fun extractJavaScriptDoc(file: VirtualFile, content: StringBuilder) {
        val text = String(file.contentsToByteArray())
        val jsDoc = extractJSDoc(text)
        if (jsDoc.isNotEmpty()) {
            content.append("\\n#### ${file.name}\\n")
            content.append("$jsDoc\\n")
        }
    }
    
    private fun extractPythonDocstring(content: String): String {
        val tripleQuotePattern = """^[\s]*(?:'{3}|"{3})(.*?)(?:'{3}|"{3})""".toRegex(RegexOption.DOT_MATCHES_ALL)
        return tripleQuotePattern.find(content)?.groupValues?.get(1)?.trim() ?: ""
    }
    
    private fun extractJSDoc(content: String): String {
        val jsDocPattern = """/\*\*(.*?)\*/""".toRegex(RegexOption.DOT_MATCHES_ALL)
        return jsDocPattern.find(content)?.groupValues?.get(1)?.trim() ?: ""
    }
}
            '''.strip(),

            "UpdateStructureAction.kt": '''
package com.your.plugin

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.command.WriteCommandAction
import com.intellij.openapi.vfs.LocalFileSystem

class UpdateStructureAction : AnAction() {
    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        
        val documenter = RepoStructureDocumenter(project)
        
        project.basePath?.let { basePath ->
            val projectDir = LocalFileSystem.getInstance().findFileByPath(basePath) ?: return
            
            listOf("frontend", "backend").forEach { dirName ->
                projectDir.findChild(dirName)?.let { dir ->
                    val content = documenter.generateStructure(dir)
                    WriteCommandAction.runWriteCommandAction(project) {
                        val structureFile = dir.findChild("REPOSITORY_STRUCTURE.md") 
                            ?: dir.createChildData(this, "REPOSITORY_STRUCTURE.md")
                        structureFile.setBinaryContent(content.toByteArray())
                    }
                }
            }
        }
    }
    
    override fun update(e: AnActionEvent) {
        val project = e.project
        e.presentation.isEnabledAndVisible = project != null
    }
}
            '''.strip()
        }

        kotlin_dir = self.plugin_path / "src/main/kotlin/com/your/plugin"
        for filename, content in files.items():
            with open(kotlin_dir / filename, "w") as f:
                f.write(content)

    def init_git(self):
        """Initializes git repository."""
        os.chdir(self.plugin_path)
        subprocess.run(["git", "init"])
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", "Initial plugin setup"])

    def setup(self):
        """Runs the complete setup process."""
        print("Setting up plugin project structure...")

        if self.plugin_path.exists():
            response = input(f"{self.plugin_path} already exists. Delete it? (y/N): ")
            if response.lower() == 'y':
                shutil.rmtree(self.plugin_path)
            else:
                print("Setup aborted.")
                return

        self.create_directory_structure()
        self.create_build_gradle()
        self.create_settings_gradle()
        self.create_gradle_properties()
        self.create_gitignore()
        self.create_plugin_xml()
        self.create_kotlin_files()
        self.init_git()

        print(f"""
Setup complete! Your plugin project has been created at:
{self.plugin_path}

Next steps:
1. Open the project in IntelliJ IDEA
2. Wait for Gradle sync to complete
3. Run the plugin using Gradle task:
   repo-structure-plugin > Tasks > intellij > runIde

For development:
- Source files are in: src/main/kotlin/com/your/plugin/
- Plugin configuration: src/main/resources/META-INF/plugin.xml
- Build configuration: build.gradle.kts
        """)

if __name__ == "__main__":
    setup = PluginSetup(os.getcwd())
    setup.setup()