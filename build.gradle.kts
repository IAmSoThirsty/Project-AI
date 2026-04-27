import com.projectai.evolution.BuildTypeCompatibilityRule
import com.projectai.evolution.BuildTypeDisambiguationRule
import com.projectai.evolution.EvolutionApiService
import com.projectai.evolution.EvolutionApiStatusTask
import com.projectai.evolution.EvolutionAuditTask
import com.projectai.evolution.EvolutionCapsuleTask
import com.projectai.evolution.EvolutionDocsTask
import com.projectai.evolution.EvolutionEngineService
import com.projectai.evolution.EvolutionReplayTask
import com.projectai.evolution.EvolutionValidateTask
import com.projectai.evolution.PlatformCompatibilityRule
import com.projectai.evolution.PlatformDisambiguationRule
import org.gradle.api.Named
import org.gradle.api.NamedDomainObjectContainer
import org.gradle.api.attributes.Attribute
import org.gradle.api.file.ConfigurableFileCollection
import org.gradle.api.model.ObjectFactory
import org.gradle.api.provider.Property
import org.gradle.api.provider.Provider
import org.gradle.api.publish.maven.MavenPublication
import org.gradle.api.tasks.PathSensitivity
import org.gradle.kotlin.dsl.create
import org.gradle.kotlin.dsl.register
import org.gradle.kotlin.dsl.withType
import java.io.File
import java.io.Serializable
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import javax.inject.Inject

plugins {
    id("base")
    id("maven-publish")
}

group = "ai.project"
version = findProperty("projectVersion")?.toString() ?: "1.0.0"
description = "Project-AI Evolution governed build runtime"

/**
 * Target convention plugin IDs for composite build-logic architecture:
 *   - evolution.core
 *   - evolution.policy
 *   - evolution.capsule
 *   - evolution.audit
 *
 * If these plugins are unavailable in pluginManagement/includeBuild, this
 * script keeps the fully-typed fallback wiring active.
 */
val requestedEvolutionPlugins = listOf(
    "evolution.core",
    "evolution.policy",
    "evolution.capsule",
    "evolution.audit",
)

val appliedEvolutionPlugins = mutableListOf<String>()
requestedEvolutionPlugins.forEach { pluginId ->
    runCatching {
        pluginManager.apply(pluginId)
        appliedEvolutionPlugins += pluginId
    }.onFailure {
        logger.info("Evolution convention plugin '$pluginId' is not currently available; fallback typed wiring remains active.")
    }
}

logger.lifecycle(
    "Evolution convention plugins active: ${appliedEvolutionPlugins.ifEmpty { listOf("none") }.joinToString(", ")}",
)

enum class ModuleType {
    PYTHON,
    ANDROID,
    ELECTRON,
    DOCS,
    API,
    GENERIC,
}

abstract class EvolutionModule @Inject constructor(
    private val moduleName: String,
    objects: ObjectFactory,
) : Named {
    override fun getName(): String = moduleName
    abstract val type: Property<ModuleType>
    val inputs: ConfigurableFileCollection = objects.fileCollection()
    val outputs: ConfigurableFileCollection = objects.fileCollection()
}

abstract class Policy @Inject constructor(
    private val policyName: String,
) : Named {
    override fun getName(): String = policyName
    abstract val mode: Property<String>
    abstract val enabled: Property<Boolean>
}

abstract class Capsule @Inject constructor(
    private val capsuleName: String,
    objects: ObjectFactory,
) : Named {
    override fun getName(): String = capsuleName
    abstract val buildType: Property<String>
    abstract val platform: Property<String>
    val artifacts: ConfigurableFileCollection = objects.fileCollection()
}

abstract class EvolutionModel @Inject constructor(
    private val objects: ObjectFactory,
) {
    abstract val buildId: Property<String>
    abstract val timestamp: Property<String>
    abstract val ci: Property<Boolean>

    val modules: NamedDomainObjectContainer<EvolutionModule> =
        objects.domainObjectContainer(EvolutionModule::class.java) { name ->
            objects.newInstance(EvolutionModule::class.java, name)
        }

    val policies: NamedDomainObjectContainer<Policy> =
        objects.domainObjectContainer(Policy::class.java) { name ->
            objects.newInstance(Policy::class.java, name)
        }

    val capsules: NamedDomainObjectContainer<Capsule> =
        objects.domainObjectContainer(Capsule::class.java) { name ->
            objects.newInstance(Capsule::class.java, name)
        }
}

data class PolicyRule(
    val id: String,
    val enabled: Boolean = true,
    val predicate: String = "true",
) : Serializable

abstract class PolicyExtension {
    abstract val mode: Property<String>
    abstract val rules: org.gradle.api.provider.ListProperty<PolicyRule>
}

data class ModuleSnapshot(
    val name: String,
    val type: String,
    val inputs: List<String>,
    val outputs: List<String>,
) : Serializable

data class PolicySnapshot(
    val name: String,
    val mode: String,
    val enabled: Boolean,
) : Serializable

data class CapsuleModelSnapshot(
    val name: String,
    val buildType: String,
    val platform: String,
    val artifacts: List<String>,
) : Serializable

data class EvolutionModelSnapshot(
    val buildId: String,
    val timestamp: String,
    val ci: Boolean,
    val modules: List<ModuleSnapshot>,
    val policies: List<PolicySnapshot>,
    val capsules: List<CapsuleModelSnapshot>,
) : Serializable

data class FrozenPolicyState(
    val mode: String,
    val rules: List<PolicyRule>,
) : Serializable

data class AuditSnapshot(
    val buildId: String,
    val capsulePath: String,
    val validationHash: String,
    val artifactCount: Int,
    val reports: List<String>,
) : Serializable {
    fun serialize(): String = buildString {
        appendLine("{")
        appendLine("  \"buildId\": \"${buildId.escapeJson()}\",")
        appendLine("  \"capsulePath\": \"${capsulePath.escapeJson()}\",")
        appendLine("  \"validationHash\": \"${validationHash.escapeJson()}\",")
        appendLine("  \"artifactCount\": $artifactCount,")
        appendLine("  \"reports\": [${reports.joinToString(",") { "\"${it.escapeJson()}\"" }}]")
        appendLine("}")
    }
}

fun String.escapeJson(): String =
    replace("\\", "\\\\")
        .replace("\"", "\\\"")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")

fun ByteArray.toHex(): String = joinToString("") { "%02x".format(it) }

fun sha256(text: String): String =
    MessageDigest
        .getInstance("SHA-256")
        .digest(text.toByteArray(StandardCharsets.UTF_8))
        .toHex()

fun File.normalizedPath(projectDir: File): String =
    relativeToOrSelf(projectDir).invariantSeparatorsPath

fun String.isExternalStatePath(): Boolean =
    this == ".venv" ||
        startsWith(".venv/") ||
        this == "node_modules" ||
        startsWith("node_modules/")

fun EvolutionModel.toSnapshot(projectDir: File): EvolutionModelSnapshot = EvolutionModelSnapshot(
    buildId = buildId.orNull ?: "unset-build-id",
    timestamp = timestamp.orNull ?: "1970-01-01T00:00:00Z",
    ci = ci.orNull ?: false,
    modules = modules
        .map { module ->
            ModuleSnapshot(
                name = module.name,
                type = module.type.orNull?.name ?: ModuleType.GENERIC.name,
                inputs = module.inputs.files
                    .map { file -> file.normalizedPath(projectDir) }
                    .filterNot { it.isExternalStatePath() }
                    .sorted(),
                outputs = module.outputs.files
                    .map { file -> file.normalizedPath(projectDir) }
                    .sorted(),
            )
        }
        .sortedBy { it.name },
    policies = policies
        .map { policy ->
            PolicySnapshot(
                name = policy.name,
                mode = policy.mode.orNull ?: "strict",
                enabled = policy.enabled.orNull ?: true,
            )
        }
        .sortedBy { it.name },
    capsules = capsules
        .map { capsule ->
            CapsuleModelSnapshot(
                name = capsule.name,
                buildType = capsule.buildType.orNull ?: "release",
                platform = capsule.platform.orNull ?: "linux-x64",
                artifacts = capsule.artifacts.files
                    .map { file -> file.normalizedPath(projectDir) }
                    .sorted(),
            )
        }
        .sortedBy { it.name },
)

fun EvolutionModelSnapshot.canonicalString(): String = buildString {
    append("buildId=").append(buildId).append('\n')
    append("timestamp=").append(timestamp).append('\n')
    append("ci=").append(ci).append('\n')

    append("modules=")
    modules.forEach { module ->
        append(module.name)
            .append('|')
            .append(module.type)
            .append('|')
            .append(module.inputs.joinToString(";"))
            .append('|')
            .append(module.outputs.joinToString(";"))
            .append('\n')
    }

    append("policies=")
    policies.forEach { policy ->
        append(policy.name)
            .append('|')
            .append(policy.mode)
            .append('|')
            .append(policy.enabled)
            .append('\n')
    }

    append("capsules=")
    capsules.forEach { capsule ->
        append(capsule.name)
            .append('|')
            .append(capsule.buildType)
            .append('|')
            .append(capsule.platform)
            .append('|')
            .append(capsule.artifacts.joinToString(";"))
            .append('\n')
    }
}

fun EvolutionModelSnapshot.stableHash(): String = sha256(canonicalString())

fun evaluatePolicies(
    snapshot: EvolutionModelSnapshot,
    mode: String,
    rules: List<PolicyRule>,
): Boolean {
    val normalizedMode = mode.lowercase()
    val activeRules = rules.filter { it.enabled }

    if (normalizedMode == "off" || normalizedMode == "disabled") {
        return true
    }

    if (snapshot.modules.isEmpty()) {
        return false
    }

    return when (normalizedMode) {
        "permissive" -> activeRules.isNotEmpty()
        else -> activeRules.isNotEmpty() && snapshot.policies.any { it.enabled }
    }
}

val evolution = extensions.create<EvolutionModel>("evolution")
val evolutionPolicy = extensions.create<PolicyExtension>("evolutionPolicy")

evolution.buildId.convention(
    providers.gradleProperty("evolution.buildId").orElse("${rootProject.name}-${project.version}"),
)
evolution.timestamp.convention(
    providers.gradleProperty("evolution.timestamp").orElse("1970-01-01T00:00:00Z"),
)
evolution.ci.convention(
    providers.gradleProperty("ci").map { it.toBooleanStrictOrNull() ?: false }.orElse(false),
)

evolutionPolicy.mode.convention("strict")
evolutionPolicy.rules.convention(
    listOf(
        PolicyRule(id = "core-integrity", enabled = true, predicate = "modules.notEmpty"),
        PolicyRule(id = "policy-enabled", enabled = true, predicate = "policies.enabled"),
    ),
)

evolution.modules.register("python-app") {
    type.convention(ModuleType.PYTHON)
    inputs.from(layout.projectDirectory.dir("src"))
    inputs.from(layout.projectDirectory.file("pyproject.toml"))
    inputs.from(layout.projectDirectory.file("requirements.txt"))
    outputs.from(layout.buildDirectory.dir("python"))
}

evolution.modules.register("desktop-electron") {
    type.convention(ModuleType.ELECTRON)
    inputs.from(layout.projectDirectory.file("desktop/package.json"))
    inputs.from(layout.projectDirectory.file("desktop/package-lock.json"))
    outputs.from(layout.buildDirectory.dir("desktop"))
}

evolution.modules.register("documentation") {
    type.convention(ModuleType.DOCS)
    inputs.from(layout.projectDirectory.dir("docs"))
    outputs.from(layout.buildDirectory.dir("docs"))
}

evolution.policies.register("constitutional") {
    mode.convention("strict")
    enabled.convention(true)
}

evolution.policies.register("supply-chain") {
    mode.convention("strict")
    enabled.convention(true)
}

evolution.capsules.register("release-linux-x64") {
    buildType.convention("release")
    platform.convention("linux-x64")
    artifacts.from(layout.buildDirectory.dir("outputs"))
}

val evolutionBuildType = providers.gradleProperty("evolution.buildType").orElse("release")
val evolutionPlatform = providers.gradleProperty("evolution.platform").orElse("linux-x64")

val buildTypeAttribute = Attribute.of("buildType", String::class.java)
val platformAttribute = Attribute.of("platform", String::class.java)

val capsuleElements = configurations.findByName("capsuleElements")
    ?: configurations.create("capsuleElements") {
        isCanBeConsumed = true
        isCanBeResolved = false
    }

capsuleElements.attributes {
    attribute(buildTypeAttribute, evolutionBuildType.get())
    attribute(platformAttribute, evolutionPlatform.get())
}

val replayConfiguration = configurations.findByName("replay")
    ?: configurations.create("replay") {
        isCanBeConsumed = false
        isCanBeResolved = true
    }

replayConfiguration.attributes {
    attribute(buildTypeAttribute, evolutionBuildType.get())
    attribute(platformAttribute, evolutionPlatform.get())
}

dependencies {
    attributesSchema {
        attribute(buildTypeAttribute) {
            compatibilityRules.add(BuildTypeCompatibilityRule::class.java)
            disambiguationRules.add(BuildTypeDisambiguationRule::class.java)
        }
        attribute(platformAttribute) {
            compatibilityRules.add(PlatformCompatibilityRule::class.java)
            disambiguationRules.add(PlatformDisambiguationRule::class.java)
        }
    }
}

findProperty("evolutionReplayDependency")?.toString()?.trim()?.takeIf { it.isNotEmpty() }?.let { dep ->
    dependencies.add(replayConfiguration.name, dep)
}

val evolutionEngine = gradle.sharedServices.registerIfAbsent(
    "evolutionEngine",
    EvolutionEngineService::class.java,
) {
    parameters.configDir.set(layout.projectDirectory.dir("config/evolution"))
    parameters.signingKey.set(layout.projectDirectory.file("config/evolution/signing.key"))
}

val evolutionApiService = gradle.sharedServices.registerIfAbsent(
    "evolutionApiService",
    EvolutionApiService::class.java,
) {}

val frozenSnapshot: EvolutionModelSnapshot by lazy(LazyThreadSafetyMode.NONE) {
    evolution.toSnapshot(project.projectDir)
}

val frozenPolicyState: FrozenPolicyState by lazy(LazyThreadSafetyMode.NONE) {
    FrozenPolicyState(
        mode = evolutionPolicy.mode.orNull ?: "strict",
        rules = (evolutionPolicy.rules.orNull ?: emptyList())
            .map { rule ->
                PolicyRule(
                    id = rule.id,
                    enabled = rule.enabled,
                    predicate = rule.predicate,
                )
            }
            .sortedBy { it.id },
    )
}

val modelSnapshotProvider: Provider<EvolutionModelSnapshot> = providers.provider { frozenSnapshot }
val policyModeProvider: Provider<String> = providers.provider { frozenPolicyState.mode }
val policyRulesProvider: Provider<List<String>> = providers.provider {
    frozenPolicyState.rules.map { rule -> "${rule.id}:${rule.enabled}:${rule.predicate}" }.sorted()
}

val modelPayloadProvider: Provider<String> = modelSnapshotProvider.map { it.canonicalString() }
val modelHashProvider: Provider<String> = modelSnapshotProvider.map { it.stableHash() }
val modelBuildIdProvider: Provider<String> = modelSnapshotProvider.map { it.buildId }
val policyHashProvider: Provider<String> = policyModeProvider.zip(policyRulesProvider) { mode, rules ->
    sha256("${mode.lowercase()}::${rules.joinToString("|")}")
}
val policyEvaluationResultProvider: Provider<Boolean> = providers.provider {
    evaluatePolicies(frozenSnapshot, frozenPolicyState.mode, frozenPolicyState.rules)
}
val venvPresentProvider: Provider<Boolean> = providers.provider {
    layout.projectDirectory.dir(".venv").asFile.exists()
}
val nodeModulesPresentProvider: Provider<Boolean> = providers.provider {
    layout.projectDirectory.dir("node_modules").asFile.exists()
}

val moduleInputFiles: Provider<Set<File>> = modelSnapshotProvider.map { snapshot ->
    snapshot.modules
        .flatMap { module -> module.inputs.map { path -> project.file(path) } }
        .toSet()
}

val moduleOutputFiles: Provider<Set<File>> = modelSnapshotProvider.map { snapshot ->
    snapshot.modules
        .flatMap { module -> module.outputs.map { path -> project.file(path) } }
        .toSet()
}

val capsuleFileProvider = layout.buildDirectory.file("capsules/${project.name}-${project.version}.capsule.json")
val signatureFileProvider = layout.buildDirectory.file("capsules/${project.name}-${project.version}.capsule.sig")

val auditPayloadProvider: Provider<String> = providers.provider {
    val snapshot = frozenSnapshot
    AuditSnapshot(
        buildId = snapshot.buildId,
        capsulePath = capsuleFileProvider.get().asFile.invariantSeparatorsPath,
        validationHash = snapshot.stableHash(),
        artifactCount = snapshot.modules.sumOf { module -> module.inputs.size + module.outputs.size },
        reports = listOf("validation", "capsule", "policy", "replay"),
    ).serialize()
}

val evolutionValidate = tasks.register<EvolutionValidateTask>("evolutionValidate") {
    group = "evolution"
    description = "Validate immutable evolution snapshot against policy model"

    snapshotPayload.set(modelPayloadProvider)
    snapshotHash.set(modelHashProvider)
    policyMode.set(policyModeProvider)
    policyRules.set(policyRulesProvider)
    policyEvaluationResult.set(policyEvaluationResultProvider)
    report.convention(layout.buildDirectory.file("reports/evolution/validation.json"))
    engine.set(evolutionEngine)

    inputs.property("modelHash", modelHashProvider)
    inputs.property("policyMode", policyModeProvider)
    inputs.property("policyRules", policyRulesProvider)
    inputs.property("policyEvaluationResult", policyEvaluationResultProvider)
    inputs.files(moduleInputFiles).withPathSensitivity(PathSensitivity.RELATIVE)
    inputs.property("externalState.venv.present", venvPresentProvider)
    inputs.property("externalState.node_modules.present", nodeModulesPresentProvider)
}

val evolutionCapsule = tasks.register<EvolutionCapsuleTask>("evolutionCapsule") {
    group = "evolution"
    description = "Create deterministic, signed build capsule from immutable snapshot"

    dependsOn(evolutionValidate)

    snapshotPayload.set(modelPayloadProvider)
    buildId.set(modelBuildIdProvider)
    snapshotHash.set(modelHashProvider)
    modelHash.set(modelHashProvider)
    policyMode.set(policyModeProvider)
    policyRules.set(policyRulesProvider)
    moduleInputs.from(moduleInputFiles)
    capsule.convention(capsuleFileProvider)
    signature.convention(signatureFileProvider)

    val signingKeyFile = layout.projectDirectory.file("config/evolution/signing.key").asFile
    if (signingKeyFile.exists()) {
        signingKey.set(layout.projectDirectory.file("config/evolution/signing.key"))
    }

    engine.set(evolutionEngine)

    inputs.property("modelHash", modelHashProvider)
    inputs.property("policyMode", policyModeProvider)
    inputs.property("policyRules", policyRulesProvider)
    inputs.property("policyHash", policyHashProvider)
    inputs.files(moduleInputFiles).withPathSensitivity(PathSensitivity.RELATIVE)
    inputs.property("externalState.venv.present", venvPresentProvider)
    inputs.property("externalState.node_modules.present", nodeModulesPresentProvider)
}

val evolutionAudit = tasks.register<EvolutionAuditTask>("evolutionAudit") {
    group = "evolution"
    description = "Generate deterministic audit artifacts from model/capsule state"

    dependsOn(evolutionCapsule)
    dependsOn(evolutionDocs)

    payload.set(auditPayloadProvider)
    buildId.set(modelBuildIdProvider)
    validationHash.set(modelHashProvider)
    modelHash.set(modelHashProvider)
    policyMode.set(policyModeProvider)
    policyRules.set(policyRulesProvider)
    artifacts.from(moduleOutputFiles)
    artifacts.from(evolutionCapsule.flatMap { it.capsule })
    reports.convention(layout.buildDirectory.dir("reports/evolution"))
    engine.set(evolutionEngine)

    inputs.property("modelHash", modelHashProvider)
    inputs.property("policyMode", policyModeProvider)
    inputs.property("policyRules", policyRulesProvider)
    inputs.property("policyHash", policyHashProvider)
    inputs.files(moduleInputFiles).withPathSensitivity(PathSensitivity.RELATIVE)
    inputs.property("externalState.venv.present", venvPresentProvider)
    inputs.property("externalState.node_modules.present", nodeModulesPresentProvider)
}

val evolutionReplay = tasks.register<EvolutionReplayTask>("evolutionReplay") {
    group = "evolution"
    description = "Replay capsule provenance from resolvable replay configuration with integrity checks"

    capsule.from(replayConfiguration)
    replayId.convention(providers.gradleProperty("evolution.replayId").orElse("latest"))
    expectedSnapshotHash.set(modelHashProvider)
    resultFile.convention(layout.buildDirectory.file("reports/evolution/replay.json"))
    engine.set(evolutionEngine)
}

val evolutionDocs = tasks.register<EvolutionDocsTask>("evolutionDocs") {
    group = "evolution"
    description = "Derive trace-linked documentation artifacts from immutable model snapshot"

    snapshotPayload.set(modelPayloadProvider)
    snapshotHash.set(modelHashProvider)
    output.convention(layout.buildDirectory.dir("docs/evolution"))

    inputs.property("snapshotHash", modelHashProvider)
}

val evolutionApiStatus = tasks.register<EvolutionApiStatusTask>("evolutionApiStatus") {
    group = "evolution"
    description = "Manage and materialize external Evolution API service status"

    apiService.set(evolutionApiService)
    statusFile.convention(layout.buildDirectory.file("reports/evolution/api-status.txt"))
}

gradle.buildFinished {
    evolutionApiService.get().close()
}

val evolutionVerify = tasks.register("evolutionVerify") {
    group = "verification"
    description = "Run independent Evolution verification boundaries"
    dependsOn(evolutionValidate)
    dependsOn(evolutionAudit)
}

val evolutionPackage = tasks.register("evolutionPackage") {
    group = "build"
    description = "Run independent Evolution packaging boundary"
    dependsOn(evolutionCapsule)
}

artifacts {
    add(capsuleElements.name, evolutionCapsule.flatMap { it.capsule }) {
        type = "json"
        classifier = "capsule"
        builtBy(evolutionCapsule)
    }
}

publishing {
    publications {
        create<MavenPublication>("capsule") {
            groupId = project.group.toString()
            artifactId = "${project.name}-capsule"
            version = project.version.toString()

            artifact(evolutionCapsule.flatMap { it.capsule }) {
                extension = "json"
                classifier = "capsule"
                builtBy(evolutionCapsule)
            }
        }
    }
    repositories {
        maven {
            name = "localCapsuleRepo"
            url = uri(layout.buildDirectory.dir("repo"))
        }
    }
}

tasks.named("check") {
    dependsOn(evolutionVerify)
}

tasks.named("assemble") {
    dependsOn(evolutionPackage)
}

tasks.named("build") {
    dependsOn(evolutionVerify)
    dependsOn(evolutionPackage)
    dependsOn(evolutionDocs)
    dependsOn(evolutionApiStatus)
}

logger.lifecycle(
    "Evolution runtime wired: verify=${evolutionVerify.name}, package=${evolutionPackage.name}, " +
        "validate=${evolutionValidate.name}, capsule=${evolutionCapsule.name}, audit=${evolutionAudit.name}, " +
        "replay=${evolutionReplay.name}, docs=${evolutionDocs.name}",
)
