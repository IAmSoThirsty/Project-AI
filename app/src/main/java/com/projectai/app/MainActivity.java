package com.projectai.app;

import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.Gravity;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Main Activity for Project-AI Android App
 * Implements Triumvirate Dashboard, Intent Submission, and Audit Log Viewer.
 */
public class MainActivity extends AppCompatActivity {

    private static final String TAG = "ProjectAI";
    // Emulator loopback address; for physical device use actual IP
    private static final String API_BASE_URL = "http://10.0.2.2:8001";
    
    private TextView statusText;
    private Spinner actorTypeSpinner;
    private Spinner actionTypeSpinner;
    private EditText payloadInput;
    private TextView resultText;
    private TextView auditLogText;
    
    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private final Handler handler = new Handler(Looper.getMainLooper());

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // Build UI programmatically to ensure it works without layout XML dependencies
        ScrollView scrollView = new ScrollView(this);
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(32, 32, 32, 32);
        
        // Header
        TextView header = new TextView(this);
        header.setText("Project AI - Governance Kernel");
        header.setTextSize(24);
        header.setGravity(Gravity.CENTER);
        header.setPadding(0, 0, 0, 32);
        layout.addView(header);
        
        // Status Section
        TextView statusLabel = new TextView(this);
        statusLabel.setText("Kernel Status:");
        statusLabel.setTextSize(18);
        layout.addView(statusLabel);
        
        statusText = new TextView(this);
        statusText.setText("Connecting...");
        statusText.setPadding(0, 8, 0, 32);
        layout.addView(statusText);
        
        // Check Status Button
        Button checkStatusBtn = new Button(this);
        checkStatusBtn.setText("Refresh Status");
        checkStatusBtn.setOnClickListener(v -> checkKernelStatus());
        layout.addView(checkStatusBtn);
        
        // Intent Submission Section
        TextView intentLabel = new TextView(this);
        intentLabel.setText("\nSubmit Intent");
        intentLabel.setTextSize(18);
        intentLabel.setPadding(0, 32, 0, 16);
        layout.addView(intentLabel);
        
        // Actor Type Spinner
        String[] actorTypes = {"Human", "Agent", "System"};
        actorTypeSpinner = new Spinner(this);
        ArrayAdapter<String> actorAdapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, actorTypes);
        actorAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        actorTypeSpinner.setAdapter(actorAdapter);
        layout.addView(actorTypeSpinner);
        
        // Action Type Spinner
        String[] actionTypes = {"Read", "Write", "Execute", "Mutate"};
        actionTypeSpinner = new Spinner(this);
        ArrayAdapter<String> actionAdapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, actionTypes);
        actionAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        actionTypeSpinner.setAdapter(actionAdapter);
        layout.addView(actionTypeSpinner);
        
        // Payload Input
        payloadInput = new EditText(this);
        payloadInput.setHint("Payload (JSON or Text)");
        layout.addView(payloadInput);
        
        // Submit Button
        Button submitBtn = new Button(this);
        submitBtn.setText("Submit for Governance");
        submitBtn.setOnClickListener(v -> submitIntent());
        layout.addView(submitBtn);
        
        // Result Display
        resultText = new TextView(this);
        resultText.setText("Result: Ready");
        resultText.setPadding(0, 16, 0, 32);
        layout.addView(resultText);
        
        // Audit Log Section
        TextView auditLabel = new TextView(this);
        auditLabel.setText("Recent Audit Logs");
        auditLabel.setTextSize(18);
        layout.addView(auditLabel);
        
        Button refreshAuditBtn = new Button(this);
        refreshAuditBtn.setText("Fetch Logs");
        refreshAuditBtn.setOnClickListener(v -> fetchAuditLogs());
        layout.addView(refreshAuditBtn);
        
        auditLogText = new TextView(this);
        auditLogText.setText("No logs loaded.");
        layout.addView(auditLogText);
        
        scrollView.addView(layout);
        setContentView(scrollView);
        
        // Initial Check
        checkKernelStatus();
    }
    
    private void checkKernelStatus() {
        executor.execute(() -> {
            try {
                String response = makeGetRequest(API_BASE_URL + "/health");
                handler.post(() -> statusText.setText("Status: " + response));
            } catch (Exception e) {
                handler.post(() -> statusText.setText("Error: " + e.getMessage()));
            }
        });
    }
    
    private void submitIntent() {
        String actor = actorTypeSpinner.getSelectedItem().toString();
        String action = actionTypeSpinner.getSelectedItem().toString();
        String payload = payloadInput.getText().toString();
        
        executor.execute(() -> {
            try {
                JSONObject json = new JSONObject();
                json.put("actor_type", actor.toLowerCase());
                json.put("action_type", action.toLowerCase());
                json.put("payload", payload);
                
                String response = makePostRequest(API_BASE_URL + "/intent", json.toString());
                handler.post(() -> resultText.setText("Result: " + response));
                
                // Refresh audit logs after submission
                fetchAuditLogs();
            } catch (Exception e) {
                handler.post(() -> resultText.setText("Error: " + e.getMessage()));
            }
        });
    }
    
    private void fetchAuditLogs() {
        executor.execute(() -> {
            try {
                String response = makeGetRequest(API_BASE_URL + "/audit");
                // Pretty print if possible
                try {
                    JSONArray jsonArray = new JSONArray(response);
                    StringBuilder logs = new StringBuilder();
                    for (int i = 0; i < Math.min(jsonArray.length(), 5); i++) {
                        logs.append(jsonArray.getJSONObject(i).toString(2)).append("\n\n");
                    }
                    final String logText = logs.toString();
                    handler.post(() -> auditLogText.setText(logText));
                } catch (Exception e) {
                    handler.post(() -> auditLogText.setText(response));
                }
            } catch (Exception e) {
                handler.post(() -> auditLogText.setText("Failed to fetch logs: " + e.getMessage()));
            }
        });
    }
    
    // Minimal HTTP Client
    private String makeGetRequest(String urlString) throws Exception {
        URL url = new URL(urlString);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        conn.setConnectTimeout(5000);
        conn.setReadTimeout(5000);
        
        return readResponse(conn);
    }
    
    private String makePostRequest(String urlString, String jsonBody) throws Exception {
        URL url = new URL(urlString);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setDoOutput(true);
        
        try (OutputStream os = conn.getOutputStream()) {
            byte[] input = jsonBody.getBytes("utf-8");
            os.write(input, 0, input.length);
        }
        
        return readResponse(conn);
    }
    
    private String readResponse(HttpURLConnection conn) throws Exception {
        int responseCode = conn.getResponseCode();
        if (responseCode >= 200 && responseCode < 300) {
            try (BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream(), "utf-8"))) {
                StringBuilder response = new StringBuilder();
                String responseLine = null;
                while ((responseLine = br.readLine()) != null) {
                    response.append(responseLine.trim());
                }
                return response.toString();
            }
        } else {
            throw new Exception("HTTP Error: " + responseCode);
        }
    }
}
