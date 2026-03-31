package ai.project.legion.mini

import android.os.Bundle
import android.webkit.WebView
import android.webkit.WebViewClient
import android.webkit.WebSettings
import android.webkit.WebChromeClient
import androidx.appcompat.app.AppCompatActivity
import android.view.View
import android.widget.progressBar
import android.widget.ProgressBar

class MainActivity : AppCompatActivity() {
    
    private lateinit var webView: WebView
    private lateinit var progressBar: ProgressBar
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Create layout programmatically since we don't have a layout XML yet
        val layout = android.widget.FrameLayout(this)
        
        // Create WebView
        webView = WebView(this).apply {
            layoutParams = android.widget.FrameLayout.LayoutParams(
                android.widget.FrameLayout.LayoutParams.MATCH_PARENT,
                android.widget.FrameLayout.LayoutParams.MATCH_PARENT
            )
        }
        
        // Create ProgressBar
        progressBar = ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal).apply {
            layoutParams = android.widget.FrameLayout.LayoutParams(
                android.widget.FrameLayout.LayoutParams.MATCH_PARENT,
                8
            )
            max = 100
        }
        
        layout.addView(webView)
        layout.addView(progressBar)
        setContentView(layout)
        
        // Configure WebView
        configureWebView()
        
        // Load Legion interface
        // For testing, we'll load the local Legion interface embedded as HTML
        // In production, this would connect to the Legion API server
        loadLegionInterface()
    }
    
    private fun configureWebView() {
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            cacheMode = WebSettings.LOAD_DEFAULT
            mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
        }
        
        webView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                progressBar.visibility = View.GONE
            }
        }
        
        webView.webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView?, newProgress: Int) {
                progressBar.progress = newProgress
                if (newProgress == 100) {
                    progressBar.visibility = View.GONE
                } else {
                    progressBar.visibility = View.VISIBLE
                }
            }
        }
    }
    
    private fun loadLegionInterface() {
        // Option 1: Load from assets (for embedded interface)
        // webView.loadUrl("file:///android_asset/legion_interface.html")
        
        // Option 2: Load from local server (for development)
        val legionUrl = BuildConfig.LEGION_API_URL.replace("10.0.2.2", "localhost")
        
        // For now, load embedded HTML with Legion interface
        val legionHtml = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Legion Mini</title>
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body {
                        font-family: 'Segoe UI', sans-serif;
                        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
                        color: #e0e0e0;
                        height: 100vh;
                        display: flex;
                        flex-direction: column;
                    }
                    .header {
                        background: rgba(26, 26, 46, 0.95);
                        border-bottom: 2px solid #00ff88;
                        padding: 1rem;
                    }
                    .header h1 {
                        font-size: 1.5rem;
                        background: linear-gradient(135deg, #00ff88, #00d4ff);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                    }
                    .container {
                        flex: 1;
                        display: flex;
                        flex-direction: column;
                        padding: 1rem;
                        overflow: hidden;
                    }
                    .chat-box {
                        flex: 1;
                        background: rgba(26, 26, 46, 0.8);
                        border-radius: 12px;
                        padding: 1rem;
                        overflow-y: auto;
                        margin-bottom: 1rem;
                    }
                    .message {
                        margin-bottom: 1rem;
                    }
                    .message .label {
                        font-weight: 600;
                        margin-bottom: 0.5rem;
                        font-size: 0.85rem;
                    }
                    .message.user .label { color: #00d4ff; }
                    .message.legion .label { color: #00ff88; }
                    .message .content {
                        background: rgba(255, 255, 255, 0.05);
                        padding: 0.75rem;
                        border-radius: 8px;
                        border-left: 3px solid;
                    }
                    .message.user .content { border-left-color: #00d4ff; }
                    .message.legion .content { border-left-color: #00ff88; }
                    .input-area {
                        display: flex;
                        gap: 0.5rem;
                        background: rgba(26, 26, 46, 0.8);
                        padding: 1rem;
                        border-radius: 12px;
                    }
                    #messageInput {
                        flex: 1;
                        background: rgba(255, 255, 255, 0.05);
                        border: 1px solid rgba(255, 255, 255, 0.2);
                        color: #e0e0e0;
                        padding: 0.75rem;
                        border-radius: 8px;
                        font-size: 1rem;
                    }
                    #sendButton {
                        background: linear-gradient(135deg, #00ff88, #00d4ff);
                        border: none;
                        color: #0a0a0a;
                        padding: 0.75rem 1.5rem;
                        border-radius: 8px;
                        font-weight: 600;
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>LEGION MINI</h1>
                </div>
                <div class="container">
                    <div class="chat-box" id="chatBox">
                        <div class="message legion">
                            <div class="label">Legion</div>
                            <div class="content">Welcome to Legion Mini. I am your interface to Project-AI.</div>
                        </div>
                    </div>
                    <div class="input-area">
                        <input type="text" id="messageInput" placeholder="Message Legion...">
                        <button id="sendButton" onclick="sendMessage()">Send</button>
                    </div>
                </div>
                <script>
                    const API_URL = '${BuildConfig.LEGION_API_URL}';
                    
                    function addMessage(sender, content) {
                        const chatBox = document.getElementById('chatBox');
                        const messageDiv = document.createElement('div');
                        messageDiv.className = 'message ' + sender;
                        messageDiv.innerHTML =  '<div class="label">' + (sender === 'user' ? 'You' : 'Legion') + '</div>' +
                                                '<div class="content">' + content + '</div>';
                        chatBox.appendChild(messageDiv);
                        chatBox.scrollTop = chatBox.scrollHeight;
                    }
                    
                    async function sendMessage() {
                        const input = document.getElementById('messageInput');
                        const message = input.value.trim();
                        if (!message) return;
                        
                        addMessage('user', message);
                        input.value = '';
                        
                        try {
                            const response = await fetch(API_URL + '/chat', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    message: message,
                                    user_id: 'android_user',
                                    platform: 'android'
                                })
                            });
                            
                            if (response.ok) {
                                const data = await response.json();
                                addMessage('legion', data.response);
                            } else {
                                addMessage('legion', 'Error: Unable to connect to Legion API');
                            }
                        } catch (error) {
                            addMessage('legion', 'Error: ' + error.message);
                        }
                    }
                    
                    document.getElementById('messageInput').addEventListener('keypress', (e) => {
                        if (e.key === 'Enter') sendMessage();
                    });
                </script>
            </body>
            </html>
        """.trimIndent()
        
        webView.loadDataWithBaseURL(null, legionHtml, "text/html", "UTF-8", null)
    }
    
    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}
