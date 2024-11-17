plugins {
    id("java")
    id("org.jetbrains.kotlin.jvm") version "1.9.22"  // Updated Kotlin version
    id("org.jetbrains.intellij") version "1.17.2"    // Updated IntelliJ plugin version
}

group = "com.your.plugin"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
}

// Explicitly specify Kotlin API version and language version
kotlin {
    jvmToolchain(17)
}

intellij {
    version.set("2023.3.3")  // Updated to latest stable version
    type.set("IC") // IC for IntelliJ IDEA Community, IU for Ultimate
    plugins.set(listOf("com.intellij.java"))
}

tasks {
    withType<JavaCompile> {
        sourceCompatibility = "17"
        targetCompatibility = "17"
    }

    patchPluginXml {
        sinceBuild.set("233")    // Updated to match the IntelliJ version
        untilBuild.set("241.*")
    }

    // Disable specific lint checks if needed
    withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile> {
        kotlinOptions {
            jvmTarget = "17"
            freeCompilerArgs = listOf("-Xjvm-default=all")
        }
    }
}