package ai.project.readonly

import android.app.Activity
import android.graphics.Color
import android.os.Build
import android.os.Bundle
import android.text.method.LinkMovementMethod
import android.text.util.Linkify
import android.util.TypedValue
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import java.util.concurrent.Executors

class MainActivity : Activity() {
    private val client by lazy { ReadOnlyProjectAiClient(HttpGetTransport(BuildConfig.API_BASE_URL)) }
    private val executor = Executors.newSingleThreadExecutor()
    private val actionButtons = mutableListOf<Button>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val output = resultView()
        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.rgb(11, 13, 18))
            setPadding(dp(16), dp(12), dp(16), dp(16))
            addView(title())
            addView(introduction())
            addView(actionButton(R.string.doi_registry, output) { renderDois(client.fetchDois()) })
            addView(
                actionButton(R.string.canonical_replay_status, output) {
                    renderReplay(client.fetchReplayStatus())
                },
            )
            addView(ScrollView(this@MainActivity).apply {
                isFillViewport = true
                addView(output)
                layoutParams = LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    0,
                    1f,
                ).apply { topMargin = dp(12) }
            })
        }
        setContentView(layout)
    }

    override fun onDestroy() {
        executor.shutdownNow()
        super.onDestroy()
    }

    private fun title(): TextView = TextView(this).apply {
        setText(R.string.screen_title)
        textSize = 24f
        setTextColor(Color.WHITE)
        setPadding(dp(8), dp(20), dp(8), dp(8))
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) isAccessibilityHeading = true
    }

    private fun introduction(): TextView = TextView(this).apply {
        setText(R.string.select_surface)
        setTextColor(Color.rgb(174, 190, 207))
        textSize = 16f
        setPadding(dp(8), 0, dp(8), dp(12))
    }

    private fun resultView(): TextView = TextView(this).apply {
        setText(R.string.select_surface)
        setTextColor(Color.rgb(218, 225, 234))
        textSize = 16f
        setPadding(dp(12), dp(16), dp(12), dp(24))
        setTextIsSelectable(true)
        autoLinkMask = Linkify.WEB_URLS
        movementMethod = LinkMovementMethod.getInstance()
        isFocusable = true
        accessibilityLiveRegion = View.ACCESSIBILITY_LIVE_REGION_POLITE
    }

    private fun actionButton(labelResource: Int, output: TextView, action: () -> String): Button =
        Button(this).apply {
            setText(labelResource)
            isAllCaps = false
            minimumHeight = dp(48)
            layoutParams = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT,
            ).apply { topMargin = dp(8) }
            setOnClickListener { load(output, text.toString(), action) }
            actionButtons += this
        }

    private fun load(output: TextView, operationLabel: String, operation: () -> String) {
        actionButtons.forEach { it.isEnabled = false }
        output.text = getString(R.string.loading_announcement, operationLabel)
        executor.execute {
            val result = runCatching(operation)
            val rendered = result.getOrElse {
                getString(R.string.read_failed, it.message ?: getString(R.string.unknown_error))
            }
            runOnUiThread {
                if (isDestroyed || isFinishing) return@runOnUiThread
                output.text = rendered
                actionButtons.forEach { it.isEnabled = true }
            }
        }
    }

    private fun renderDois(records: List<DoiRecord>): String =
        if (records.isEmpty()) {
            getString(R.string.no_doi_records)
        } else {
            records.joinToString("\n\n") {
                getString(R.string.doi_record, it.title, it.doi, it.url)
            }
        }

    private fun renderReplay(status: ReplayStatus): String = getString(
        R.string.replay_result,
        status.status,
        status.invariantsPassed,
        status.invariantsTotal,
        status.updatedAt,
    )

    private fun dp(value: Int): Int = TypedValue.applyDimension(
        TypedValue.COMPLEX_UNIT_DIP,
        value.toFloat(),
        resources.displayMetrics,
    ).toInt()
}
