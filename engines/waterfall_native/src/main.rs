use std::env;
use std::io::{self, Read};
use std::process;

use waterfall_native_engine::{
    hit_test_internal_route, hit_test_markup_document, render_internal_route, render_markup_document,
    HitTarget, RenderBox, RenderedInternalRoute,
};

fn json_escape(value: &str) -> String {
    let mut escaped = String::with_capacity(value.len() + 8);

    for character in value.chars() {
        match character {
            '"' => escaped.push_str("\\\""),
            '\\' => escaped.push_str("\\\\"),
            '\n' => escaped.push_str("\\n"),
            '\r' => escaped.push_str("\\r"),
            '\t' => escaped.push_str("\\t"),
            control if control.is_control() => {
                escaped.push_str(&format!("\\u{:04x}", control as u32));
            }
            other => escaped.push(other),
        }
    }

    escaped
}

fn render_box_json(render_box: &RenderBox) -> String {
    let text_json = match &render_box.text {
        Some(text) => format!("\"{}\"", json_escape(text)),
        None => "null".to_string(),
    };
    let focus_index_json = match render_box.focus_index {
        Some(focus_index) => focus_index.to_string(),
        None => "null".to_string(),
    };
    let surface_json = match &render_box.surface {
        Some(surface) => format!("\"{}\"", json_escape(surface)),
        None => "null".to_string(),
    };
    let tone_json = match &render_box.tone {
        Some(tone) => format!("\"{}\"", json_escape(tone)),
        None => "null".to_string(),
    };
    let layout_json = match &render_box.layout {
        Some(layout) => format!("\"{}\"", json_escape(layout)),
        None => "null".to_string(),
    };
    let emphasis_json = match &render_box.emphasis {
        Some(emphasis) => format!("\"{}\"", json_escape(emphasis)),
        None => "null".to_string(),
    };
    let href_json = match &render_box.href {
        Some(href) => format!("\"{}\"", json_escape(href)),
        None => "null".to_string(),
    };
    let action_id_json = match &render_box.action_id {
        Some(action_id) => format!("\"{}\"", json_escape(action_id)),
        None => "null".to_string(),
    };
    let control_kind_json = match &render_box.control_kind {
        Some(control_kind) => format!("\"{}\"", json_escape(control_kind)),
        None => "null".to_string(),
    };
    let setting_path_json = match &render_box.setting_path {
        Some(setting_path) => format!("\"{}\"", json_escape(setting_path)),
        None => "null".to_string(),
    };
    let control_label_json = match &render_box.control_label {
        Some(control_label) => format!("\"{}\"", json_escape(control_label)),
        None => "null".to_string(),
    };
    let control_caption_json = match &render_box.control_caption {
        Some(control_caption) => format!("\"{}\"", json_escape(control_caption)),
        None => "null".to_string(),
    };
    let control_string_value_json = match &render_box.control_string_value {
        Some(control_string_value) => format!("\"{}\"", json_escape(control_string_value)),
        None => "null".to_string(),
    };
    let control_number_value_json = match render_box.control_number_value {
        Some(control_number_value) => control_number_value.to_string(),
        None => "null".to_string(),
    };
    let control_placeholder_json = match &render_box.control_placeholder {
        Some(control_placeholder) => format!("\"{}\"", json_escape(control_placeholder)),
        None => "null".to_string(),
    };
    let control_min_json = match render_box.control_min {
        Some(control_min) => control_min.to_string(),
        None => "null".to_string(),
    };
    let control_max_json = match render_box.control_max {
        Some(control_max) => control_max.to_string(),
        None => "null".to_string(),
    };
    let control_step_json = match render_box.control_step {
        Some(control_step) => control_step.to_string(),
        None => "null".to_string(),
    };
    let control_options_json = render_box
        .control_options
        .iter()
        .map(|option| {
            format!(
                "{{\"value\":\"{}\",\"label\":\"{}\"}}",
                json_escape(&option.value),
                json_escape(&option.label)
            )
        })
        .collect::<Vec<_>>()
        .join(",");

    format!(
        "{{\"nodePath\":\"{}\",\"role\":\"{}\",\"x\":{},\"y\":{},\"width\":{},\"height\":{},\"zIndex\":{},\"focusIndex\":{},\"text\":{},\"surface\":{},\"tone\":{},\"layout\":{},\"emphasis\":{},\"interactive\":{},\"href\":{},\"actionId\":{},\"controlKind\":{},\"settingPath\":{},\"controlLabel\":{},\"controlCaption\":{},\"controlStringValue\":{},\"controlNumberValue\":{},\"controlPlaceholder\":{},\"controlMin\":{},\"controlMax\":{},\"controlStep\":{},\"controlOptions\":[{}]}}",
        json_escape(&render_box.node_path),
        json_escape(&render_box.role),
        render_box.x,
        render_box.y,
        render_box.width,
        render_box.height,
        render_box.z_index,
        focus_index_json,
        text_json,
        surface_json,
        tone_json,
        layout_json,
        emphasis_json,
        if render_box.interactive { "true" } else { "false" },
        href_json,
        action_id_json,
        control_kind_json,
        setting_path_json,
        control_label_json,
        control_caption_json,
        control_string_value_json,
        control_number_value_json,
        control_placeholder_json,
        control_min_json,
        control_max_json,
        control_step_json,
        control_options_json
    )
}

fn hit_target_json(hit_target: &HitTarget) -> String {
    let text_json = match &hit_target.text {
        Some(text) => format!("\"{}\"", json_escape(text)),
        None => "null".to_string(),
    };
    let surface_json = match &hit_target.surface {
        Some(surface) => format!("\"{}\"", json_escape(surface)),
        None => "null".to_string(),
    };
    let tone_json = match &hit_target.tone {
        Some(tone) => format!("\"{}\"", json_escape(tone)),
        None => "null".to_string(),
    };
    let href_json = match &hit_target.href {
        Some(href) => format!("\"{}\"", json_escape(href)),
        None => "null".to_string(),
    };
    let action_id_json = match &hit_target.action_id {
        Some(action_id) => format!("\"{}\"", json_escape(action_id)),
        None => "null".to_string(),
    };
    let control_kind_json = match &hit_target.control_kind {
        Some(control_kind) => format!("\"{}\"", json_escape(control_kind)),
        None => "null".to_string(),
    };
    let setting_path_json = match &hit_target.setting_path {
        Some(setting_path) => format!("\"{}\"", json_escape(setting_path)),
        None => "null".to_string(),
    };
    let focus_index_json = match hit_target.focus_index {
        Some(focus_index) => focus_index.to_string(),
        None => "null".to_string(),
    };

    format!(
        "{{\"nodePath\":\"{}\",\"role\":\"{}\",\"x\":{},\"y\":{},\"width\":{},\"height\":{},\"zIndex\":{},\"focusIndex\":{},\"interactive\":{},\"href\":{},\"actionId\":{},\"controlKind\":{},\"settingPath\":{},\"text\":{},\"surface\":{},\"tone\":{}}}",
        json_escape(&hit_target.node_path),
        json_escape(&hit_target.role),
        hit_target.x,
        hit_target.y,
        hit_target.width,
        hit_target.height,
        hit_target.z_index,
        focus_index_json,
        if hit_target.interactive { "true" } else { "false" },
        href_json,
        action_id_json,
        control_kind_json,
        setting_path_json,
        text_json,
        surface_json,
        tone_json
    )
}

fn rendered_route_json(rendered_route: &RenderedInternalRoute) -> String {
    let boxes_json = rendered_route
        .boxes
        .iter()
        .map(render_box_json)
        .collect::<Vec<_>>()
        .join(",");

    let focus_json = rendered_route
        .engine
        .focus
        .iter()
        .map(|focus| format!("\"{}\"", json_escape(focus)))
        .collect::<Vec<_>>()
        .join(",");

    format!(
        "{{\"route\":\"{}\",\"title\":\"{}\",\"subtitle\":\"{}\",\"markup\":\"{}\",\"viewportWidth\":{},\"documentHeight\":{},\"boxes\":[{}],\"engine\":{{\"engineId\":\"{}\",\"integration\":\"{}\",\"focus\":[{}]}}}}",
        json_escape(&rendered_route.route),
        json_escape(&rendered_route.title),
        json_escape(&rendered_route.subtitle),
        json_escape(&rendered_route.markup),
        rendered_route.viewport_width,
        rendered_route.document_height,
        boxes_json,
        json_escape(rendered_route.engine.engine_id),
        json_escape(rendered_route.engine.integration),
        focus_json
    )
}

fn main() {
    let args = env::args().skip(1).collect::<Vec<_>>();

    match args.first().map(String::as_str) {
        Some("render-route") => {
            let route = args
                .get(1)
                .cloned()
                .unwrap_or_else(|| "waterfall://home".to_string());
            let viewport_width = args
                .get(2)
                .and_then(|value| value.parse::<u16>().ok())
                .unwrap_or(84);
            let rendered_route = render_internal_route(&route, viewport_width);

            println!("{}", rendered_route_json(&rendered_route));
        }
        Some("hit-test-route") => {
            let route = args
                .get(1)
                .cloned()
                .unwrap_or_else(|| "waterfall://home".to_string());
            let x = args.get(2).and_then(|value| value.parse::<u16>().ok()).unwrap_or(0);
            let y = args.get(3).and_then(|value| value.parse::<u16>().ok()).unwrap_or(0);
            let viewport_width = args
                .get(4)
                .and_then(|value| value.parse::<u16>().ok())
                .unwrap_or(84);
            let hit_target = hit_test_internal_route(&route, viewport_width, x, y);

            println!(
                "{}",
                hit_target
                    .as_ref()
                    .map(hit_target_json)
                    .unwrap_or_else(|| "null".to_string())
            );
        }
        Some("render-markup") => {
            let route = args
                .get(1)
                .cloned()
                .unwrap_or_else(|| "waterfall://document".to_string());
            let title = args
                .get(2)
                .cloned()
                .unwrap_or_else(|| "WaterFall Document".to_string());
            let subtitle = args
                .get(3)
                .cloned()
                .unwrap_or_else(|| "Rendered from a WaterFall document payload.".to_string());
            let viewport_width = args
                .get(4)
                .and_then(|value| value.parse::<u16>().ok())
                .unwrap_or(84);
            let mut markup = String::new();

            if let Err(error) = io::stdin().read_to_string(&mut markup) {
                eprintln!("failed to read markup from stdin: {}", error);
                process::exit(1);
            }

            let rendered_route =
                render_markup_document(&route, &title, &subtitle, &markup, viewport_width);

            println!("{}", rendered_route_json(&rendered_route));
        }
        Some("hit-test-markup") => {
            let route = args
                .get(1)
                .cloned()
                .unwrap_or_else(|| "waterfall://document".to_string());
            let title = args
                .get(2)
                .cloned()
                .unwrap_or_else(|| "WaterFall Document".to_string());
            let subtitle = args
                .get(3)
                .cloned()
                .unwrap_or_else(|| "Rendered from a WaterFall document payload.".to_string());
            let x = args.get(4).and_then(|value| value.parse::<u16>().ok()).unwrap_or(0);
            let y = args.get(5).and_then(|value| value.parse::<u16>().ok()).unwrap_or(0);
            let viewport_width = args
                .get(6)
                .and_then(|value| value.parse::<u16>().ok())
                .unwrap_or(84);
            let mut markup = String::new();

            if let Err(error) = io::stdin().read_to_string(&mut markup) {
                eprintln!("failed to read markup from stdin: {}", error);
                process::exit(1);
            }

            let hit_target =
                hit_test_markup_document(&route, &title, &subtitle, &markup, viewport_width, x, y);

            println!(
                "{}",
                hit_target
                    .as_ref()
                    .map(hit_target_json)
                    .unwrap_or_else(|| "null".to_string())
            );
        }
        _ => {
            eprintln!(
                "usage: waterfall-native-engine render-route <waterfall://route> [viewport_width] | hit-test-route <waterfall://route> <x> <y> [viewport_width] | render-markup <route> <title> <subtitle> [viewport_width] | hit-test-markup <route> <title> <subtitle> <x> <y> [viewport_width]"
            );
            process::exit(1);
        }
    }
}
