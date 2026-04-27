package com.projectai.evolution

import org.gradle.api.DefaultTask
import org.gradle.api.GradleException
import org.gradle.api.file.ConfigurableFileCollection
import org.gradle.api.file.DirectoryProperty
import org.gradle.api.file.RegularFileProperty
import org.gradle.api.provider.ListProperty
import org.gradle.api.provider.Property
import org.gradle.api.tasks.CacheableTask
import org.gradle.api.tasks.Input
import org.gradle.api.tasks.InputFile
import org.gradle.api.tasks.InputFiles
import org.gradle.api.tasks.Internal
import org.gradle.api.tasks.Optional
import org.gradle.api.tasks.OutputDirectory
import org.gradle.api.tasks.OutputFile
import org.gradle.api.tasks.PathSensitive
import org.gradle.api.tasks.PathSensitivity
import org.gradle.api.tasks.TaskAction
import org.gradle.workers.WorkAction
import org.gradle.workers.WorkParameters
import org.gradle.workers.WorkerExecutor
import java.io.File
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import javax.inject.Inject

private fun String.escapeJson(): String =
    replace("\\", "\\\\")
        .replace("\"", "\\\"")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")

private fun sha256(text: String): String =
    MessageDigest
        .getInstance("SHA-256")
        .digest(text.toByteArray(StandardCharsets.UTF_8))
        .joinToString("") { "%02x".format(it) }

private val isoTimestampPattern = Regex("""\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z""")

private fun normalizeContent(content: String): String =
    content
        .replace("\r\n", "\n")
        .replace('\r', '\n')
        .replace(isoTimestampPattern, "<timestamp>")
        .trimEnd() + "\n"

private fun extractJsonField(content: String, field: String): String? {
    val regex = Regex("\"$field\"\\s*:\\s*\"([^\"]+)\"")
    return regex.find(content)?.groupValues?.getOrNull(1)
}

private fun extractArtifactHashes(content: String): Map<String, String> {
    val markerIndex = content.indexOf("\"artifactHashes\"")
    if (markerIndex < 0) {
        return emptyMap()
    }

    val objectStart = content.indexOf('{', markerIndex)
    if (objectStart < 0) {
        return emptyMap()
    }

    var depth = 0
    var objectEnd = -1
    loop@ for (index in objectStart until content.length) {
        when (content[index]) {
            '{' -> depth += 1
            '}' -> {
                depth -= 1
                if (depth == 0) {
                    objectEnd = index
                    break@loop
                }
            }
        }
    }

    if (objectEnd <= objectStart) {
        return emptyMap()
    }

    val body = content.substring(objectStart + 1, objectEnd)
    val entryRegex = Regex("\"([^\"]+)\"\\s*:\\s*\"([^\"]+)\"")
    return entryRegex
        .findAll(body)
        .associate { match ->
            match.groupValues[1] to match.groupValues[2]
        }
        .toSortedMap()
}

private fun resolveArtifactPath(key: String): String = key.substringAfter("::", key)

private fun canonicalizeCapsulePayload(
    buildId: String,
    snapshotHash: String,
    modelHash: String,
    policyMode: String,
    policyRules: List<String>,
    snapshotPayload: String,
    artifactHashes: Map<String, String>,
): String {
    val normalizedPolicyRules = policyRules.sorted()
    val normalizedSnapshotPayload = normalizeContent(snapshotPayload)
    val snapshotPayloadHash = sha256(normalizedSnapshotPayload)
    val aggregatedArtifactHash = sha256(
        artifactHashes.entries
            .sortedBy { it.key }
            .joinToString("|") { (path, digest) -> "$path:$digest" },
    )
    val policyHash = sha256("${policyMode.lowercase()}::${normalizedPolicyRules.joinToString("|")}")

    return buildString {
        appendLine("{")
        appendLine("  \"buildId\": \"${buildId.escapeJson()}\",")
        appendLine("  \"snapshotHash\": \"${snapshotHash.escapeJson()}\",")
        appendLine("  \"modelHash\": \"${modelHash.escapeJson()}\",")
        appendLine("  \"policyMode\": \"${policyMode.escapeJson()}\",")
        appendLine("  \"policyHash\": \"${policyHash.escapeJson()}\",")
        appendLine("  \"policyRules\": [${normalizedPolicyRules.joinToString(",") { "\"${it.escapeJson()}\"" }}],")
        appendLine("  \"snapshotPayloadHash\": \"${snapshotPayloadHash.escapeJson()}\",")
        appendLine("  \"aggregatedArtifactHash\": \"${aggregatedArtifactHash.escapeJson()}\",")
        appendLine("  \"artifactHashes\": {")
        artifactHashes.entries.sortedBy { it.key }.forEachIndexed { index, (path, digest) ->
            val suffix = if (index == artifactHashes.size - 1) "" else ","
            appendLine("    \"${path.escapeJson()}\": \"${digest.escapeJson()}\"$suffix")
        }
        appendLine("  }")
        appendLine("}")
    }
}

private fun canonicalizeAuditPayload(
    buildId: String,
    validationHash: String,
    modelHash: String,
    policyMode: String,
    policyRules: List<String>,
    payload: String,
    artifactHashes: Map<String, String>,
): String {
    val normalizedPolicyRules = policyRules.sorted()
    val payloadHash = sha256(normalizeContent(payload))
    val aggregatedArtifactHash = sha256(
        artifactHashes.entries
            .sortedBy { it.key }
            .joinToString("|") { (path, digest) -> "$path:$digest" },
    )

    return buildString {
        appendLine("{")
        appendLine("  \"buildId\": \"${buildId.escapeJson()}\",")
        appendLine("  \"validationHash\": \"${validationHash.escapeJson()}\",")
        appendLine("  \"modelHash\": \"${modelHash.escapeJson()}\",")
        appendLine("  \"policyMode\": \"${policyMode.escapeJson()}\",")
        appendLine("  \"policyRules\": [${normalizedPolicyRules.joinToString(",") { "\"${it.escapeJson()}\"" }}],")
        appendLine("  \"payloadHash\": \"${payloadHash.escapeJson()}\",")
        appendLine("  \"aggregatedArtifactHash\": \"${aggregatedArtifactHash.escapeJson()}\",")
        appendLine("  \"artifactCount\": ${artifactHashes.size},")
        appendLine("  \"artifactHashes\": {")
        artifactHashes.entries.sortedBy { it.key }.forEachIndexed { index, (path, digest) ->
            val suffix = if (index == artifactHashes.size - 1) "" else ","
            appendLine("    \"${path.escapeJson()}\": \"${digest.escapeJson()}\"$suffix")
        }
        appendLine("  }")
        appendLine("}")
    }
}

abstract class CapsuleSignatureWork : WorkAction<CapsuleSignatureWork.Parameters> {
    interface Parameters : WorkParameters {
        val capsuleFile: RegularFileProperty
        val signatureFile: RegularFileProperty

        @get:Optional
        val signingKeyFile: RegularFileProperty
    }

    override fun execute() {
        val capsulePath = parameters.capsuleFile.get().asFile
        val signaturePath = parameters.signatureFile.get().asFile
        val keyPath = parameters.signingKeyFile.orNull?.asFile

        val capsuleHash = sha256(capsulePath.readText(StandardCharsets.UTF_8))
        val keyHash = if (keyPath != null && keyPath.exists()) {
            sha256(keyPath.readText(StandardCharsets.UTF_8))
        } else {
            "unsigned"
        }

        signaturePath.parentFile.mkdirs()
        signaturePath.writeText(
            buildString {
                appendLine("{")
                appendLine("  \"capsule\": \"${capsulePath.invariantSeparatorsPath.escapeJson()}\",")
                appendLine("  \"capsuleHash\": \"$capsuleHash\",")
                appendLine("  \"keyHash\": \"$keyHash\"")
                appendLine("}")
            },
            StandardCharsets.UTF_8,
        )
    }
}

@CacheableTask
abstract class EvolutionValidateTask : DefaultTask() {
    @get:Input
    abstract val snapshotPayload: Property<String>

    @get:Input
    abstract val snapshotHash: Property<String>

    @get:Input
    abstract val policyMode: Property<String>

    @get:Input
    abstract val policyRules: ListProperty<String>

    @get:Input
    abstract val policyEvaluationResult: Property<Boolean>

    @get:OutputFile
    abstract val report: RegularFileProperty

    @get:Internal
    abstract val engine: Property<EvolutionEngineService>

    @TaskAction
    fun run() {
        if (!policyEvaluationResult.get()) {
            throw GradleException(
                "Evolution policy evaluation failed before validation " +
                    "(mode=${policyMode.get()}, rules=${policyRules.get().size})",
            )
        }

        val result = engine.get().validate(
            snapshotPayload = snapshotPayload.get(),
            snapshotHash = snapshotHash.get(),
        )

        val reportFile = report.get().asFile
        reportFile.parentFile.mkdirs()
        reportFile.writeText(result.serialize(), StandardCharsets.UTF_8)

        if (!result.valid) {
            throw GradleException("Evolution validation failed: ${result.violations.joinToString("; ")}")
        }
    }
}

@CacheableTask
abstract class EvolutionCapsuleTask : DefaultTask() {
    @get:Input
    abstract val snapshotPayload: Property<String>

    @get:Input
    abstract val buildId: Property<String>

    @get:Input
    abstract val snapshotHash: Property<String>

    @get:Input
    abstract val modelHash: Property<String>

    @get:Input
    abstract val policyMode: Property<String>

    @get:Input
    abstract val policyRules: ListProperty<String>

    @get:InputFiles
    @get:PathSensitive(PathSensitivity.RELATIVE)
    abstract val moduleInputs: ConfigurableFileCollection

    @get:OutputFile
    abstract val capsule: RegularFileProperty

    @get:OutputFile
    abstract val signature: RegularFileProperty

    @get:Optional
    @get:InputFile
    @get:PathSensitive(PathSensitivity.RELATIVE)
    abstract val signingKey: RegularFileProperty

    @get:Internal
    abstract val engine: Property<EvolutionEngineService>

    @get:Inject
    abstract val workerExecutor: WorkerExecutor

    @TaskAction
    fun run() {
        val service = engine.get()

        // Phase 1: deterministic artifact hashing (sorted, normalized, content-addressed)
        val artifactHashes = service.buildArtifactIndex(
            moduleInputs.files.sortedBy { it.invariantSeparatorsPath },
            project.projectDir,
        )

        // Phase 2: deterministic payload aggregation (UTF-8, LF line endings, timestamp scrub)
        val canonicalPayload = canonicalizeCapsulePayload(
            buildId = buildId.get(),
            snapshotHash = snapshotHash.get(),
            modelHash = modelHash.get(),
            policyMode = policyMode.get(),
            policyRules = policyRules.get(),
            snapshotPayload = snapshotPayload.get(),
            artifactHashes = artifactHashes,
        )

        val generated = service.createCapsule(
            buildId = buildId.get(),
            snapshotHash = snapshotHash.get(),
            payload = canonicalPayload,
        )

        val outputCapsule = capsule.get().asFile
        outputCapsule.parentFile.mkdirs()
        generated.copyTo(outputCapsule, overwrite = true)

        // Phase 3: signature generation (isolated worker process)
        workerExecutor
            .processIsolation {
                forkOptions.maxHeapSize = "2g"
            }
            .submit(CapsuleSignatureWork::class.java) {
                capsuleFile.set(capsule)
                signatureFile.set(signature)
                if (signingKey.isPresent) {
                    signingKeyFile.set(signingKey)
                }
            }
    }
}

@CacheableTask
abstract class EvolutionAuditTask : DefaultTask() {
    @get:Input
    abstract val payload: Property<String>

    @get:Input
    abstract val buildId: Property<String>

    @get:Input
    abstract val validationHash: Property<String>

    @get:Input
    abstract val modelHash: Property<String>

    @get:Input
    abstract val policyMode: Property<String>

    @get:Input
    abstract val policyRules: ListProperty<String>

    @get:InputFiles
    @get:PathSensitive(PathSensitivity.RELATIVE)
    abstract val artifacts: ConfigurableFileCollection

    @get:OutputDirectory
    abstract val reports: DirectoryProperty

    @get:Internal
    abstract val engine: Property<EvolutionEngineService>

    @TaskAction
    fun run() {
        val service = engine.get()

        // Phase 1: deterministic artifact hashing (sorted, normalized, content-addressed)
        val artifactHashes = service.buildArtifactIndex(
            artifacts.files.sortedBy { it.invariantSeparatorsPath },
            project.projectDir,
        )

        // Phase 2: canonical audit aggregation
        val canonicalPayload = canonicalizeAuditPayload(
            buildId = buildId.get(),
            validationHash = validationHash.get(),
            modelHash = modelHash.get(),
            policyMode = policyMode.get(),
            policyRules = policyRules.get(),
            payload = payload.get(),
            artifactHashes = artifactHashes,
        )

        // Phase 3: emit report artifact via shared service
        val generated = service.audit(
            buildId = buildId.get(),
            validationHash = validationHash.get(),
            payload = canonicalPayload,
        )

        val outDir = reports.get().asFile
        outDir.mkdirs()
        generated.copyTo(outDir.resolve("audit.json"), overwrite = true)
    }
}

@CacheableTask
abstract class EvolutionReplayTask : DefaultTask() {
    @get:InputFiles
    @get:PathSensitive(PathSensitivity.RELATIVE)
    abstract val capsule: ConfigurableFileCollection

    @get:Input
    abstract val replayId: Property<String>

    @get:Input
    abstract val expectedSnapshotHash: Property<String>

    @get:OutputFile
    abstract val resultFile: RegularFileProperty

    @get:Internal
    abstract val engine: Property<EvolutionEngineService>

    @TaskAction
    fun run() {
        val resolvedCapsules = capsule.files
            .filter { it.isFile }
            .sortedBy { it.invariantSeparatorsPath }

        if (resolvedCapsules.isEmpty()) {
            throw GradleException("No replay capsules were resolved for replay configuration '${replayId.get()}'")
        }

        val service = engine.get()
        val mismatches = mutableListOf<String>()
        val verification = sortedMapOf<String, String>()
        val expectedModelHash = expectedSnapshotHash.get()

        resolvedCapsules.forEachIndexed { index, capsuleFile ->
            val content = capsuleFile.readText(StandardCharsets.UTF_8)
            val capsuleSnapshotHash = extractJsonField(content, "snapshotHash")
                ?: throw GradleException("Replay capsule '${capsuleFile.name}' is missing 'snapshotHash'")

            if (capsuleSnapshotHash != expectedModelHash) {
                mismatches +=
                    "snapshot hash mismatch for ${capsuleFile.name}: expected=$expectedModelHash actual=$capsuleSnapshotHash"
            }

            val capsuleArtifactHashes = extractArtifactHashes(content)
            capsuleArtifactHashes.forEach { (artifactKey, expectedDigest) ->
                val resolvedPath = resolveArtifactPath(artifactKey)
                val actualDigest = service.digestArtifact(project.file(resolvedPath))
                if (actualDigest != expectedDigest) {
                    mismatches +=
                        "artifact digest mismatch for $resolvedPath: expected=$expectedDigest actual=$actualDigest"
                }
            }

            verification["capsule.$index.path"] = capsuleFile.invariantSeparatorsPath
            verification["capsule.$index.sha256"] = sha256(content)
            verification["capsule.$index.artifacts"] = capsuleArtifactHashes.size.toString()
        }

        if (mismatches.isNotEmpty()) {
            val excerpt = mismatches.take(20).joinToString("; ")
            throw GradleException("Replay integrity verification failed: $excerpt")
        }

        verification["snapshotHash.expected"] = expectedModelHash
        verification["snapshotHash.verified"] = "true"
        verification["artifactIndex.size"] = service.artifactIndexSnapshot().size.toString()

        val replay = service.replay(replayId.get(), verification)
        val out = resultFile.get().asFile
        out.parentFile.mkdirs()
        out.writeText(replay.serialize(), StandardCharsets.UTF_8)
    }
}

@CacheableTask
abstract class EvolutionDocsTask : DefaultTask() {
    @get:Input
    abstract val snapshotPayload: Property<String>

    @get:Input
    abstract val snapshotHash: Property<String>

    @get:OutputDirectory
    abstract val output: DirectoryProperty

    @TaskAction
    fun run() {
        val docsDir = output.get().asFile
        docsDir.mkdirs()
        docsDir.resolve("evolution-model.md").writeText(
            buildString {
                appendLine("# Evolution Build Snapshot")
                appendLine()
                appendLine("- Snapshot Hash: `${snapshotHash.get()}`")
                appendLine()
                appendLine("```text")
                appendLine(normalizeContent(snapshotPayload.get()))
                appendLine("```")
            },
            StandardCharsets.UTF_8,
        )
    }
}

abstract class EvolutionApiStatusTask : DefaultTask() {
    @get:Internal
    abstract val apiService: Property<EvolutionApiService>

    @get:OutputFile
    abstract val statusFile: RegularFileProperty

    @TaskAction
    fun run() {
        val service = apiService.get()
        service.start()

        val out = statusFile.get().asFile
        out.parentFile.mkdirs()
        out.writeText(
            buildString {
                appendLine("service=evolution-api")
                appendLine("status=${service.status()}")
            },
            StandardCharsets.UTF_8,
        )
    }
}
