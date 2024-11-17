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