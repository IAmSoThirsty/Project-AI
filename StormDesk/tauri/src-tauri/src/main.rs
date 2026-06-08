#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::Manager;

#[tauri::command]
fn notify(title: String, body: String, app: tauri::AppHandle) -> Result<(), String> {
    app.notification()
        .builder()
        .title(&title)
        .body(&body)
        .show()
        .map_err(|e| e.to_string())
}

#[tauri::command]
fn get_env(key: String) -> Result<String, String> {
    std::env::var(&key).map_err(|_| format!("Environment variable '{}' not set", key))
}

#[tauri::command]
fn set_window_fullscreen(
    fullscreen: bool,
    window: tauri::Window,
) -> Result<(), String> {
    window
        .set_fullscreen(fullscreen)
        .map_err(|e| e.to_string())
}

#[tauri::command]
fn set_window_always_on_top(
    on_top: bool,
    window: tauri::Window,
) -> Result<(), String> {
    window
        .set_always_on_top(on_top)
        .map_err(|e| e.to_string())
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_notification::init())
        .invoke_handler(tauri::generate_handler![
            notify,
            get_env,
            set_window_fullscreen,
            set_window_always_on_top,
        ])
        .setup(|app| {
            let window = app.get_webview_window("main")
                .expect("Failed to get main window");

            // Start maximized in production
            #[cfg(not(debug_assertions))]
            {
                let _ = window.maximize();
            }

            // Set window title
            let _ = window.set_title("Storm Desk — Breaking News Command Center");

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
