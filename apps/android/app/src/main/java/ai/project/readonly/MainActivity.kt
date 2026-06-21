package ai.project.readonly

import android.app.Activity
import android.graphics.Color
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView

class MainActivity : Activity() {
    private val client by lazy { ReadOnlyProjectAiClient(HttpGetTransport(BuildConfig.API_BASE_URL)) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val output = TextView(this).apply {
            setTextColor(Color.rgb(218, 225, 234))
            textSize = 16f
            text = "Select a read-only Project-AI surface."
            setPadding(24, 24, 24, 24)
        }
        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.rgb(11, 13, 18))
            addView(title("Project-AI Read Only"))
            addView(button("DOI Registry") { load(output) { renderDois(client.fetchDois()) } })
            addView(
                button("Canonical Replay Status") {
                    load(output) { renderReplay(client.fetchReplayStatus()) }
                },
            )
            addView(ScrollView(this@MainActivity).apply { addView(output) })
        }
        setContentView(layout)
    }

    private fun title(value: String): TextView = TextView(this).apply {
        text = value
        textSize = 24f
        setTextColor(Color.WHITE)
        setPadding(24, 32, 24, 16)
    }

    private fun button(label: String, action: () -> Unit): View = Button(this).apply {
        text = label
        isAllCaps = false
        setOnClickListener { action() }
    }

    private fun load(output: TextView, operation: () -> String) {
        output.text = "Loading..."
        Thread {
            val rendered = runCatching(operation).getOrElse { "Read failed: ${it.message}" }
            runOnUiThread { output.text = rendered }
        }.start()
    }

    private fun renderDois(records: List<DoiRecord>): String = records.joinToString("\n\n") {
        "${it.title}\n${it.doi}\n${it.url}"
    }

    private fun renderReplay(status: ReplayStatus): String =
        "${status.status}\n${status.invariantsPassed}/${status.invariantsTotal} invariants passed\n${status.updatedAt}"
}
