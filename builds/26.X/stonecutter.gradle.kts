import java.util.Properties

plugins {
    id("dev.kikugie.stonecutter")
}

val targetConfiguration = Properties().apply {
    rootProject.file("targets.properties").inputStream().use { load(it) }
}

stonecutter active "26.3-neoforge" /* [SC] DO NOT EDIT */

stonecutter {
    parameters {
        val target = node.metadata.project
        val loader = target.substringAfterLast('-')
        constants += listOf(
            "forge" to (loader == "forge"),
            "neoforge" to (loader == "neoforge"),
            "fabric" to (loader == "fabric"),
            "legacy" to false,
            "modern" to false,
            "mc_26_x" to true,
        )
    }
}

val targets = targetConfiguration.getProperty("targets")
    ?.split(',')?.map(String::trim)?.filter(String::isNotEmpty)
    ?: error("Missing non-empty targets in targets.properties")

// Every 26.X target is a release target, including the Fabric 26.3 addon.
tasks.register("buildAndCollect") {
    group = "build"
    description = "Build all 26.X NeoForge and Fabric release targets and collect jars"
    dependsOn(targets.map { target -> ":$target:buildAndCollect" })
}

// Preserve the existing developer command as a backward-compatible alias.
tasks.register("buildAllIncludingFabric") {
    group = "build"
    description = "Alias for buildAndCollect (all four 26.X release targets)"
    dependsOn("buildAndCollect")
}

val activeProject = stonecutter.current!!.project
fun activeTask(name: String) = ":$activeProject:$name"

tasks.register("runActiveClient") {
    group = "stonecutter"
    dependsOn(activeTask("runClient"))
}

tasks.register("runActiveServer") {
    group = "stonecutter"
    dependsOn(activeTask("runServer"))
}
