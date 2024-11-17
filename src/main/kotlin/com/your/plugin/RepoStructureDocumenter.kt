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
        content.append("# ${directory.name.uppercase()} Structure\n")
        content.append("Last updated: ${LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME)}\n\n")
        
        content.append("## Directory Structure\n```\n")
        content.append(generateTree(directory))
        content.append("\n```\n\n")
        
        content.append("## File Documentation\n")
        generateDocumentation(directory, content)
        
        return content.toString()
    }
    
    private fun generateTree(file: VirtualFile, prefix: String = ""): String {
        val content = StringBuilder()
        val children = file.children.sortedWith(compareBy({ !it.isDirectory }, { it.name }))
        
        children.forEachIndexed { index, child ->
            val isLast = index == children.lastIndex
            val connector = if (isLast) "└── " else "├── "
            
            content.append("$prefix$connector${child.name}\n")
            
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
                content.append("\n### $newPath\n")
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
        content.append("\n#### ${file.name}\n")
        
        if (psiFile is PsiJavaFile) {
            psiFile.classes.forEach { psiClass ->
                psiClass.docComment?.let {
                    content.append("\n${it.text}\n")
                }
            }
        }
    }
    
    private fun extractPythonDoc(file: VirtualFile, content: StringBuilder) {
        val text = String(file.contentsToByteArray())
        val docstring = extractPythonDocstring(text)
        if (docstring.isNotEmpty()) {
            content.append("\n#### ${file.name}\n")
            content.append("$docstring\n")
        }
    }
    
    private fun extractJavaScriptDoc(file: VirtualFile, content: StringBuilder) {
        val text = String(file.contentsToByteArray())
        val jsDoc = extractJSDoc(text)
        if (jsDoc.isNotEmpty()) {
            content.append("\n#### ${file.name}\n")
            content.append("$jsDoc\n")
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