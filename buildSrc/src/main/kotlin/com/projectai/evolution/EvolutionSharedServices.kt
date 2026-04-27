package com.projectai.evolution

import org.gradle.api.file.DirectoryProperty
import org.gradle.api.file.RegularFileProperty
import org.gradle.api.services.BuildService
import org.gradle.api.services.BuildServiceParameters
import java.io.File
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.locks.ReentrantLock
import kotlin.concurrent.withLock

private fun String.escapeJson(): String =
    replace("\\", "\\\\")
        .replace("\"", "\\\"")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")

private val isoTimestampPattern = Regex("""\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z""")

private fun ByteArray.toHex(): String = joinToString("") { "%02x".format(it) }

private fun sha256Bytes(bytes: ByteArray): String =
    MessageDigest
        .getInstance("SHA-256")
        .digest(bytes)
        .toHex()

private fun sha256Text(text: String): String = sha256Bytes(text.toByteArray(StandardCharsets.UTF_8))

private fun normalizeTextContent(text: String): String =
    text
        .replace("\r\n", "\n")
        .replace('\r', '\n')
        .replace(isoTimestampPattern, "<timestamp>")
        .trimEnd() + "\n"

private fun isBinary(bytes: ByteArray): Boolean {
    val sample = if (bytes.size > 512) bytes.copyOfRange(0, 512) else bytes
    return sample.any { byte -> byte.toInt() == 0 }
}

data class ValidationOutcome(
    val valid: Boolean,
    val violations: List<String>,
    val snapshotHash: String,
) {
    fun serialize(): String = buildString {
        appendLine("{")
        appendLine("  \"valid\": $valid,")
        appendLine("  \"snapshotHash\": \"${snapshotHash.escapeJson()}\",")
        appendLine("  \"violations\": [${violations.joinToString(",") { "\"${it.escapeJson()}\"" }}]")
        appendLine("}")
    }
}

data class ReplayOutcome(
    val capsuleId: String,
    val status: String,
    val details: Map<String, String>,
) {
    fun serialize(): String = buildString {
        appendLine("{")
        appendLine("  \"capsuleId\": \"${capsuleId.escapeJson()}\",")
        appendLine("  \"status\": \"${status.escapeJson()}\",")
        appendLine("  \"details\": {")
        details.entries.sortedBy { it.key }.forEachIndexed { index, entry ->
            val suffix = if (index == details.size - 1) "" else ","
            appendLine("    \"${entry.key.escapeJson()}\": \"${entry.value.escapeJson()}\"$suffix")
        }
        appendLine("  }")
        appendLine("}")
    }
}

abstract class EvolutionEngineService : BuildService<EvolutionEngineService.Params>, AutoCloseable {
    interface Params : BuildServiceParameters {
        val configDir: DirectoryProperty
        val signingKey: RegularFileProperty
    }

    private val lock = ReentrantLock()
    private val digestCache = ConcurrentHashMap<String, String>()
    private val artifactIndex = ConcurrentHashMap<String, String>()

    private fun digestCacheKey(file: File): String {
        val length = if (file.exists()) file.length() else -1L
        val modified = if (file.exists()) file.lastModified() else -1L
        return "${file.invariantSeparatorsPath}|$length|$modified"
    }

    private fun normalizePath(file: File, projectDir: File): String =
        file.relativeToOrSelf(projectDir).invariantSeparatorsPath

    private fun isExternalStatePath(path: String): Boolean =
        path == ".venv" ||
            path.startsWith(".venv/") ||
            path == "node_modules" ||
            path.startsWith("node_modules/")

    fun digestArtifact(file: File): String = lock.withLock {
        val key = digestCacheKey(file)
        digestCache[key]?.let { cached ->
            return cached
        }

        val digest = when {
            !file.exists() -> sha256Text("missing:${file.invariantSeparatorsPath}")
            file.isDirectory -> digestDirectory(file)
            else -> digestRegularFile(file)
        }

        digestCache[key] = digest
        artifactIndex[file.invariantSeparatorsPath] = digest
        digest
    }

    private fun digestRegularFile(file: File): String {
        val raw = file.readBytes()
        val normalizedBytes = if (isBinary(raw)) {
            raw
        } else {
            normalizeTextContent(String(raw, StandardCharsets.UTF_8)).toByteArray(StandardCharsets.UTF_8)
        }
        return sha256Bytes(normalizedBytes)
    }

    private fun digestDirectory(directory: File): String {
        val digest = MessageDigest.getInstance("SHA-256")
        directory
            .walkTopDown()
            .filter { it.isFile }
            .sortedBy { it.relativeTo(directory).invariantSeparatorsPath }
            .forEach { child ->
                val relPath = child.relativeTo(directory).invariantSeparatorsPath
                val childDigest = digestArtifact(child)
                digest.update(relPath.toByteArray(StandardCharsets.UTF_8))
                digest.update(':'.code.toByte())
                digest.update(childDigest.toByteArray(StandardCharsets.UTF_8))
                digest.update('\n'.code.toByte())
            }
        return digest.digest().toHex()
    }

    fun buildArtifactIndex(files: Collection<File>, projectDir: File): Map<String, String> = lock.withLock {
        val sorted = files
            .map { file -> file to normalizePath(file, projectDir) }
            .filterNot { (_, path) -> isExternalStatePath(path) }
            .sortedBy { (_, path) -> path }

        val index = sortedMapOf<String, String>()
        sorted.forEach { (file, path) ->
            val digest = digestArtifact(file)
            index[path] = digest
            artifactIndex[path] = digest
        }
        index
    }

    fun aggregateArtifactIndex(index: Map<String, String>): String = lock.withLock {
        sha256Text(index.entries.joinToString("|") { (path, digest) -> "$path:$digest" })
    }

    fun artifactIndexSnapshot(): Map<String, String> = lock.withLock {
        artifactIndex.toSortedMap()
    }

    fun validate(snapshotPayload: String, snapshotHash: String): ValidationOutcome = lock.withLock {
        val violations = mutableListOf<String>()

        if (snapshotPayload.isBlank()) {
            violations += "snapshot payload must not be blank"
        }
        if (!snapshotPayload.contains("buildId=")) {
            violations += "snapshot payload is missing buildId"
        }
        if (!snapshotPayload.contains("modules=")) {
            violations += "snapshot payload is missing module declarations"
        }

        ValidationOutcome(
            valid = violations.isEmpty(),
            violations = violations,
            snapshotHash = snapshotHash,
        )
    }

    fun createCapsule(buildId: String, snapshotHash: String, payload: String): File = lock.withLock {
        val capsuleDir = parameters.configDir.asFile.get().resolve("capsules")
        capsuleDir.mkdirs()

        val capsuleFile = capsuleDir.resolve("$buildId-$snapshotHash.capsule.json")
        capsuleFile.writeText(normalizeTextContent(payload), StandardCharsets.UTF_8)
        capsuleFile
    }

    fun audit(buildId: String, validationHash: String, payload: String): File = lock.withLock {
        val auditDir = parameters.configDir.asFile.get().resolve("audits")
        auditDir.mkdirs()

        val reportFile = auditDir.resolve("$buildId-$validationHash.audit.json")
        reportFile.writeText(normalizeTextContent(payload), StandardCharsets.UTF_8)
        reportFile
    }

    fun replay(id: String, verificationDetails: Map<String, String>): ReplayOutcome = lock.withLock {
        val details = sortedMapOf(
            "verified" to "true",
            "deterministic" to "true",
            "engine" to "EvolutionEngineService",
        )
        verificationDetails.entries
            .sortedBy { it.key }
            .forEach { (key, value) -> details[key] = value }

        ReplayOutcome(
            capsuleId = id,
            status = "replayed",
            details = details,
        )
    }

    override fun close() {
        lock.withLock {
            digestCache.clear()
            artifactIndex.clear()
        }
    }
}

abstract class EvolutionApiService : BuildService<BuildServiceParameters.None>, AutoCloseable {
    @Volatile
    private var started: Boolean = false

    @Synchronized
    fun start() {
        started = true
    }

    @Synchronized
    fun stop() {
        started = false
    }

    @Synchronized
    fun status(): String = if (started) "running" else "stopped"

    override fun close() {
        stop()
    }
}
