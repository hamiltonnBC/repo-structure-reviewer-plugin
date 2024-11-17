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