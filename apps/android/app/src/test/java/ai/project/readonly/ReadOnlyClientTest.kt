package ai.project.readonly

import org.junit.Assert.assertEquals
import org.junit.Test

class ReadOnlyClientTest {
    @Test
    fun clientUsesOnlyFixedReadEndpoints() {
        val paths = mutableListOf<String>()
        val client = ReadOnlyProjectAiClient { path ->
            paths += path
            when (path) {
                "/dois" -> """{"dois":[{"doi":"10.1/a","title":"A","url":"https://doi.org/10.1/a"}]}"""
                "/replay/status" -> """{"status":"pass","invariants_passed":5,"invariants_total":5,"updated_at":"2026-06-20T00:00:00Z"}"""
                else -> error("unexpected path")
            }
        }

        assertEquals("10.1/a", client.fetchDois().single().doi)
        assertEquals(5, client.fetchReplayStatus().invariantsPassed)
        assertEquals(listOf("/dois", "/replay/status"), paths)
    }

    @Test
    fun replayPayloadMapsCanonicalStatus() {
        val status = ReadOnlyPayloads.parseReplayStatus(
            """{"status":"pass","invariants_passed":5,"invariants_total":5,"updated_at":"now"}""",
        )
        assertEquals(ReplayStatus("pass", 5, 5, "now"), status)
    }
}
