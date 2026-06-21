package ai.project.readonly

import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URI
import java.net.URL

data class DoiRecord(val doi: String, val title: String, val url: String)

data class ReplayStatus(
    val status: String,
    val invariantsPassed: Int,
    val invariantsTotal: Int,
    val updatedAt: String,
)

fun interface GetTransport {
    fun get(path: String): String
}

class HttpGetTransport(baseUrl: String) : GetTransport {
    private val base = URI(baseUrl.trimEnd('/')).also {
        require(it.scheme == "http" || it.scheme == "https") { "API URL must use HTTP or HTTPS" }
        require(it.host != null) { "API URL must include a host" }
    }

    override fun get(path: String): String {
        require(path.startsWith('/') && ".." !in path) { "path must be absolute and normalized" }
        val connection = URL(base.toString() + path).openConnection() as HttpURLConnection
        connection.requestMethod = "GET"
        connection.connectTimeout = 5_000
        connection.readTimeout = 5_000
        connection.doOutput = false
        return try {
            val code = connection.responseCode
            require(code in 200..299) { "read-only API returned HTTP $code" }
            connection.inputStream.bufferedReader().use { it.readText() }
        } finally {
            connection.disconnect()
        }
    }
}

class ReadOnlyProjectAiClient(private val transport: GetTransport) {
    fun fetchDois(): List<DoiRecord> = ReadOnlyPayloads.parseDois(transport.get("/dois"))

    fun fetchReplayStatus(): ReplayStatus =
        ReadOnlyPayloads.parseReplayStatus(transport.get("/replay/status"))
}

object ReadOnlyPayloads {
    fun parseDois(payload: String): List<DoiRecord> {
        val records = JSONObject(payload).getJSONArray("dois")
        return List(records.length()) { index ->
            val item = records.getJSONObject(index)
            DoiRecord(
                doi = item.getString("doi"),
                title = item.getString("title"),
                url = item.getString("url"),
            )
        }
    }

    fun parseReplayStatus(payload: String): ReplayStatus {
        val item = JSONObject(payload)
        return ReplayStatus(
            status = item.getString("status"),
            invariantsPassed = item.getInt("invariants_passed"),
            invariantsTotal = item.getInt("invariants_total"),
            updatedAt = item.getString("updated_at"),
        )
    }
}
