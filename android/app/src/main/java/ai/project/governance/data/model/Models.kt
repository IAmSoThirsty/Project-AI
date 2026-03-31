package ai.project.governance.data.model

import com.google.gson.annotations.SerializedName

// Actor Types
enum class ActorType {
    @SerializedName("human") HUMAN,
    @SerializedName("agent") AGENT,
    @SerializedName("system") SYSTEM
}

// Action Types
enum class ActionType {
    @SerializedName("read") READ,
    @SerializedName("write") WRITE,
    @SerializedName("execute") EXECUTE,
    @SerializedName("mutate") MUTATE
}

// Verdict Types
enum class Verdict {
    @SerializedName("allow") ALLOW,
    @SerializedName("deny") DENY,
    @SerializedName("degrade") DEGRADE
}

// Intent Request
data class Intent(
    val actor: ActorType,
    val action: ActionType,
    val target: String,
    val context: Map<String, Any> = emptyMap(),
    val origin: String = "android_app"
)

// Pillar Vote
data class PillarVote(
    val pillar: String,
    val verdict: Verdict,
    val reason: String
)

// Governance Result
data class GovernanceResult(
    @SerializedName("intent_hash") val intentHash: String,
    @SerializedName("tarl_version") val tarlVersion: String,
    val votes: List<PillarVote>,
    @SerializedName("final_verdict") val finalVerdict: Verdict,
    val timestamp: Double
)

// Intent Response
data class IntentResponse(
    val message: String,
    val governance: GovernanceResult
)

// Execute Response
data class ExecuteResponse(
    val message: String,
    val governance: GovernanceResult,
    val execution: ExecutionResult
)

data class ExecutionResult(
    val status: String,
    val note: String,
    val target: String
)

// TARL Rule
data class TarlRule(
    val action: String,
    @SerializedName("allowed_actors") val allowedActors: List<String>,
    val risk: String,
    val default: String
)

// TARL Response
data class TarlResponse(
    val version: String,
    val rules: List<TarlRule>
)

// Audit Record
data class AuditRecord(
    @SerializedName("intent_hash") val intentHash: String,
    @SerializedName("tarl_version") val tarlVersion: String,
    val votes: List<Map<String, String>>,
    @SerializedName("final_verdict") val finalVerdict: String,
    val timestamp: Double
)

// Audit Response
data class AuditResponse(
    @SerializedName("tarl_version") val tarlVersion: String,
    @SerializedName("tarl_signature") val tarlSignature: String,
    val records: List<AuditRecord>
)

// Health Response
data class HealthResponse(
    val status: String,
    val tarl: String
)
