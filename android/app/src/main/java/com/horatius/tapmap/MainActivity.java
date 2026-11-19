package com.horatius.tapmap;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.database.Cursor;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.graphics.Color;
import android.provider.OpenableColumns;
import android.view.Gravity;
import android.view.View;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends Activity {
    private static final int REQUEST_GEODB_FILES = 4107;
    private static final int REQUEST_PCAPDROID_START = 4108;
    private static final int REQUEST_PCAPDROID_STOP = 4109;
    private static final String PCAPDROID_PACKAGE = "com.emanuelef.remote_capture";
    private static final String PCAPDROID_CONTROL = "com.emanuelef.remote_capture.activities.CaptureCtrl";

    private final Handler mainHandler = new Handler(Looper.getMainLooper());
    private final ExecutorService worker = Executors.newSingleThreadExecutor();

    private FrameLayout root;
    private WebView webView;
    private LinearLayout loadingPanel;
    private ProgressBar spinner;
    private TextView statusText;
    private Button retryButton;

    private volatile boolean destroyed = false;
    private boolean pageLoaded = false;
    private boolean loadFailed = false;
    private boolean capturePromptShown = false;
    private boolean captureRunning = false;
    private String appUrl = "http://127.0.0.1:8765/";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(Color.rgb(16, 19, 26));
        getWindow().setNavigationBarColor(Color.rgb(16, 19, 26));
        buildInterface();
        startTapMap();
    }

    private void buildInterface() {
        root = new FrameLayout(this);
        root.setBackgroundColor(Color.rgb(16, 19, 26));

        webView = new WebView(this);
        webView.setBackgroundColor(Color.rgb(16, 19, 26));
        webView.getSettings().setJavaScriptEnabled(true);
        webView.getSettings().setDomStorageEnabled(true);
        webView.getSettings().setDatabaseEnabled(true);
        webView.getSettings().setJavaScriptCanOpenWindowsAutomatically(false);
        webView.addJavascriptInterface(new AndroidBridge(), "TapMapAndroid");
        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageStarted(WebView view, String url, android.graphics.Bitmap favicon) {
                if (!pageLoaded) showLoading("Loading TapMap interface...");
                loadFailed = false;
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                if (!loadFailed) {
                    pageLoaded = true;
                    loadingPanel.setVisibility(View.GONE);
                    installAndroidPickerHandler();
                    showPcapdroidPromptOnce();
                }
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request,
                                        android.webkit.WebResourceError error) {
                if (request.isForMainFrame()) {
                    showError("TapMap could not load. Check that its local service is running, then retry.");
                }
            }
        });

        root.addView(webView, new FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT));

        loadingPanel = new LinearLayout(this);
        loadingPanel.setOrientation(LinearLayout.VERTICAL);
        loadingPanel.setGravity(Gravity.CENTER);
        loadingPanel.setPadding(36, 36, 36, 36);
        loadingPanel.setBackgroundColor(Color.rgb(16, 19, 26));

        spinner = new ProgressBar(this);
        loadingPanel.addView(spinner);

        statusText = new TextView(this);
        statusText.setTextColor(Color.rgb(228, 215, 186));
        statusText.setTextSize(16);
        statusText.setGravity(Gravity.CENTER);
        statusText.setPadding(0, 22, 0, 18);
        statusText.setText("Starting TapMap Android...");
        loadingPanel.addView(statusText);

        retryButton = new Button(this);
        retryButton.setText("Retry");
        retryButton.setVisibility(View.GONE);
        retryButton.setOnClickListener(v -> {
            loadFailed = false;
            showLoading("Connecting to TapMap...");
            webView.loadUrl(appUrl);
        });
        loadingPanel.addView(retryButton);

        root.addView(loadingPanel, new FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT));
        setContentView(root);
    }

    private void installAndroidPickerHandler() {
        String script =
                "(function(){"
                + "if(window.__tapMapPickerBound)return;"
                + "window.__tapMapPickerBound=true;"
                + "document.addEventListener('click',function(e){"
                + "var b=e.target.closest('#btn_open_data');"
                + "if(b){e.preventDefault();e.stopPropagation();"
                + "if(window.TapMapAndroid)window.TapMapAndroid.openGeoDbPicker();}"
                + "},true);"
                + "})();";
        webView.evaluateJavascript(script, null);
    }

    private class AndroidBridge {
        @JavascriptInterface
        public void openGeoDbPicker() {
            mainHandler.post(() -> {
                Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.setType("*/*");
                intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
                intent.putExtra(Intent.EXTRA_MIME_TYPES, new String[] {
                        "application/octet-stream", "application/gzip", "application/x-gzip"
                });
                startActivityForResult(intent, REQUEST_GEODB_FILES);
            });
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == REQUEST_PCAPDROID_START) {
            if (resultCode == RESULT_OK) {
                captureRunning = true;
                Toast.makeText(this, "PCAPdroid capture started. TapMap is receiving traffic.", Toast.LENGTH_LONG).show();
            } else {
                Toast.makeText(this, "PCAPdroid capture was not started. TapMap will remain idle until capture is enabled.", Toast.LENGTH_LONG).show();
            }
            return;
        }

        if (requestCode == REQUEST_PCAPDROID_STOP) {
            captureRunning = false;
            if (resultCode != RESULT_OK) {
                Toast.makeText(this, "PCAPdroid did not confirm that capture stopped.", Toast.LENGTH_LONG).show();
            }
            finish();
            return;
        }

        if (requestCode != REQUEST_GEODB_FILES || resultCode != RESULT_OK || data == null) return;

        File targetDir = new File(getFilesDir(), "tapmap");
        if (!targetDir.exists() && !targetDir.mkdirs()) {
            Toast.makeText(this, "Could not open TapMap's database folder.", Toast.LENGTH_LONG).show();
            return;
        }

        int copied = 0;
        StringBuilder failures = new StringBuilder();
        if (data.getClipData() != null) {
            for (int i = 0; i < data.getClipData().getItemCount(); i++) {
                Uri uri = data.getClipData().getItemAt(i).getUri();
                if (copyGeoDbFile(uri, targetDir, failures)) copied++;
            }
        } else if (data.getData() != null) {
            if (copyGeoDbFile(data.getData(), targetDir, failures)) copied++;
        }

        final int copiedCount = copied;
        final String errorText = failures.toString();
        String message = copiedCount == 2
                ? "Two database files imported. Checking them now..."
                : copiedCount == 1
                ? "One database imported. Checking database status..."
                : "No City/ASN database file was imported.";
        if (errorText.length() > 0) message += " " + errorText;
        Toast.makeText(this, message, Toast.LENGTH_LONG).show();

        if (copiedCount > 0 && webView != null) {
            webView.postDelayed(() -> webView.evaluateJavascript(
                    "(function(){var b=document.getElementById('btn_check_databases');"
                    + "if(b){b.click();return 'recheck-started';}return 'recheck-button-not-found';})()",
                    result -> {
                        if (result != null && result.contains("not-found")) {
                            Toast.makeText(this, "Files were copied, but TapMap's Recheck button was not found.", Toast.LENGTH_LONG).show();
                        }
                    }), 300);
        }
    }

    private void showPcapdroidPromptOnce() {
        if (capturePromptShown || destroyed) return;
        capturePromptShown = true;
        new AlertDialog.Builder(this)
                .setTitle("Enable network monitoring")
                .setMessage("TapMap uses PCAPdroid as its capture engine. Tap Start to send captured traffic to TapMap locally on this device. Android will ask you to approve the capture.")
                .setPositiveButton("Start capture", (dialog, which) -> startPcapdroidCapture())
                .setNegativeButton("Not now", (dialog, which) ->
                        Toast.makeText(this, "TapMap is open, but no network traffic will appear until capture is started.", Toast.LENGTH_LONG).show())
                .show();
    }

    private void startPcapdroidCapture() {
        Intent intent = new Intent(Intent.ACTION_VIEW);
        intent.setClassName(PCAPDROID_PACKAGE, PCAPDROID_CONTROL);
        intent.putExtra("action", "start");
        intent.putExtra("pcap_dump_mode", "udp_exporter");
        intent.putExtra("collector_host", "127.0.0.1");
        intent.putExtra("collector_port", "5123");
        intent.putExtra("dump_extensions", true);

        try {
            startActivityForResult(intent, REQUEST_PCAPDROID_START);
        } catch (android.content.ActivityNotFoundException error) {
            Toast.makeText(this, "PCAPdroid is not installed. Install PCAPdroid, then reopen TapMap.", Toast.LENGTH_LONG).show();
        } catch (Exception error) {
            Toast.makeText(this, "Could not start PCAPdroid: " + error.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void stopPcapdroidCapture() {
        Intent intent = new Intent(Intent.ACTION_VIEW);
        intent.setClassName(PCAPDROID_PACKAGE, PCAPDROID_CONTROL);
        intent.putExtra("action", "stop");
        try {
            startActivityForResult(intent, REQUEST_PCAPDROID_STOP);
        } catch (Exception error) {
            captureRunning = false;
            Toast.makeText(this, "Could not stop PCAPdroid: " + error.getMessage(), Toast.LENGTH_LONG).show();
            finish();
        }
    }

    private boolean copyGeoDbFile(Uri uri, File targetDir, StringBuilder failures) {
        String displayName = queryDisplayName(uri);
        String lower = displayName.toLowerCase();
        String destinationName;

        if (lower.contains("city") && lower.endsWith(".mmdb")) {
            destinationName = lower.contains("geolite")
                    ? "GeoLite2-City.mmdb" : "DBIP-City.mmdb";
        } else if (lower.contains("asn") && lower.endsWith(".mmdb")) {
            destinationName = lower.contains("geolite")
                    ? "GeoLite2-ASN.mmdb" : "DBIP-ASN.mmdb";
        } else {
            appendFailure(failures, "Skipped unsupported file: " + displayName);
            return false;
        }

        File destination = new File(targetDir, destinationName);
        File temporary = new File(targetDir, destinationName + ".importing");
        try (InputStream input = getContentResolver().openInputStream(uri);
             FileOutputStream output = new FileOutputStream(temporary)) {
            if (input == null) throw new java.io.IOException("Could not read selected file.");
            byte[] buffer = new byte[64 * 1024];
            int count;
            while ((count = input.read(buffer)) != -1) {
                output.write(buffer, 0, count);
            }
            output.getFD().sync();
            if (destination.exists() && !destination.delete()) {
                throw new java.io.IOException("Could not replace the existing database.");
            }
            if (!temporary.renameTo(destination)) {
                throw new java.io.IOException("Could not move imported database into place.");
            }
            return true;
        } catch (Exception error) {
            temporary.delete();
            appendFailure(failures, displayName + ": " + error.getMessage());
            return false;
        }
    }

    private String queryDisplayName(Uri uri) {
        try (Cursor cursor = getContentResolver().query(
                uri, new String[] { OpenableColumns.DISPLAY_NAME }, null, null, null)) {
            if (cursor != null && cursor.moveToFirst()) {
                int index = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME);
                if (index >= 0) return cursor.getString(index);
            }
        } catch (Exception ignored) { }
        String segment = uri.getLastPathSegment();
        return segment == null ? "selected-file" : segment;
    }

    private void appendFailure(StringBuilder failures, String message) {
        if (failures.length() > 0) failures.append(" ");
        failures.append(message);
    }

    private void showLoading(String message) {
        if (destroyed) return;
        statusText.setText(message);
        spinner.setVisibility(View.VISIBLE);
        retryButton.setVisibility(View.GONE);
        loadingPanel.setVisibility(View.VISIBLE);
    }

    private void showError(String message) {
        if (destroyed) return;
        loadFailed = true;
        spinner.setVisibility(View.GONE);
        statusText.setText(message);
        retryButton.setVisibility(View.VISIBLE);
        loadingPanel.setVisibility(View.VISIBLE);
    }

    private void startTapMap() {
        showLoading("Starting Python runtime and TapMap service...");
        worker.execute(() -> {
            try {
                if (!Python.isStarted()) {
                    Python.start(new AndroidPlatform(this));
                }

                appUrl = Python.getInstance()
                        .getModule("tapmap_android")
                        .callAttr("start", getFilesDir().getAbsolutePath(), 8765)
                        .toString();

                mainHandler.post(() -> {
                    if (destroyed) return;
                    showLoading("TapMap service started. Loading map...");
                    webView.loadUrl(appUrl);
                });
            } catch (Throwable error) {
                mainHandler.post(() -> showError("TapMap could not start:\n" + error.toString()));
            }
        });
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else if (captureRunning) {
            stopPcapdroidCapture();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        destroyed = true;
        worker.execute(() -> {
            try {
                if (Python.isStarted()) {
                    Python.getInstance().getModule("tapmap_android").callAttr("stop");
                }
            } catch (Throwable ignored) { }
        });
        worker.shutdown();
        if (webView != null) {
            webView.stopLoading();
            webView.destroy();
        }
        super.onDestroy();
    }
}
