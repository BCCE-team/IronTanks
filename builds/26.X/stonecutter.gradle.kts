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

// Keep the established release matrix unchanged until the Maven-backed
// Fabric preview passes a real compile and in-game smoke test.
val releasedTargets = targets.filterNot { it.endsWith("-fabric") }
tasks.register("buildAndCollect") {
    group = "build"
    description = "Build released 26.X NeoForge targets and collect jars"
    dependsOn(releasedTargets.map { target -> ":$target:buildAndCollect" })
}

tasks.register("buildAllIncludingFabric") {
    group = "build"
    description = "Build every 26.X target, including Maven-backed Fabric preview"
    dependsOn(targets.map { target -> ":$target:buildAndCollect" })
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
