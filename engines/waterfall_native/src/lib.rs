//! WaterFall Native Engine
//!
//! This crate is the first native rendering foothold for Thirsty's WaterFall.
//! It deliberately starts small: parsing a narrow HTML subset into a DOM-like
//! tree and turning that tree into a paint-friendly block layout blueprint.

use std::collections::BTreeMap;

const BLOCK_TAGS: &[&str] = &[
    "article", "aside", "body", "div", "footer", "h1", "h2", "h3", "header", "html", "li",
    "main", "nav", "ol", "p", "section", "ul", "wf-control",
];

type Attributes = BTreeMap<String, String>;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EngineIdentity {
    pub engine_id: &'static str,
    pub integration: &'static str,
    pub focus: &'static [&'static str],
}

pub fn engine_identity() -> EngineIdentity {
    EngineIdentity {
        engine_id: "thirstys-waterfall-native",
        integration: "utf-sidecar",
        focus: &[
            "html-tokenizer",
            "dom-graph",
            "block-layout",
            "paint-blueprint",
            "route-interactions",
            "region-layout",
            "semantic-surfaces",
            "focus-graph",
            "hit-testing",
        ],
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Document {
    pub children: Vec<Node>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Node {
    Element(ElementNode),
    Text(TextNode),
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ElementNode {
    pub tag_name: String,
    pub attributes: Attributes,
    pub children: Vec<Node>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TextNode {
    pub text: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RenderBlueprint {
    pub viewport_width: u16,
    pub document_height: u16,
    pub boxes: Vec<RenderBox>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RenderBox {
    pub node_path: String,
    pub role: String,
    pub x: u16,
    pub y: u16,
    pub width: u16,
    pub height: u16,
    pub z_index: u16,
    pub focus_index: Option<u16>,
    pub text: Option<String>,
    pub surface: Option<String>,
    pub tone: Option<String>,
    pub layout: Option<String>,
    pub emphasis: Option<String>,
    pub interactive: bool,
    pub href: Option<String>,
    pub action_id: Option<String>,
    pub control_kind: Option<String>,
    pub setting_path: Option<String>,
    pub control_label: Option<String>,
    pub control_caption: Option<String>,
    pub control_string_value: Option<String>,
    pub control_number_value: Option<u16>,
    pub control_placeholder: Option<String>,
    pub control_min: Option<u16>,
    pub control_max: Option<u16>,
    pub control_step: Option<u16>,
    pub control_options: Vec<ControlOption>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ControlOption {
    pub value: String,
    pub label: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct InternalRoutePage {
    pub route: String,
    pub title: String,
    pub subtitle: String,
    pub markup: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RenderedInternalRoute {
    pub route: String,
    pub title: String,
    pub subtitle: String,
    pub markup: String,
    pub viewport_width: u16,
    pub document_height: u16,
    pub boxes: Vec<RenderBox>,
    pub engine: EngineIdentity,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct HitTarget {
    pub node_path: String,
    pub role: String,
    pub x: u16,
    pub y: u16,
    pub width: u16,
    pub height: u16,
    pub z_index: u16,
    pub focus_index: Option<u16>,
    pub interactive: bool,
    pub href: Option<String>,
    pub action_id: Option<String>,
    pub control_kind: Option<String>,
    pub setting_path: Option<String>,
    pub text: Option<String>,
    pub surface: Option<String>,
    pub tone: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct ElementBuilder {
    tag_name: String,
    attributes: Attributes,
    children: Vec<Node>,
}

#[derive(Debug, Clone, Default, PartialEq, Eq)]
struct InteractionState {
    href: Option<String>,
    action_id: Option<String>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum LayoutKind {
    Stack,
    Grid,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
struct LayoutFrame {
    left: u16,
    width: u16,
}

#[derive(Debug, Clone, Default, PartialEq, Eq)]
struct ControlMetadata {
    control_kind: Option<String>,
    setting_path: Option<String>,
    control_label: Option<String>,
    control_caption: Option<String>,
    control_string_value: Option<String>,
    control_number_value: Option<u16>,
    control_placeholder: Option<String>,
    control_min: Option<u16>,
    control_max: Option<u16>,
    control_step: Option<u16>,
    control_options: Vec<ControlOption>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct LayoutMetadata {
    kind: LayoutKind,
    columns: u16,
    span: u16,
    gap: u16,
    padding_x: u16,
    padding_y: u16,
}

pub fn parse_html_fragment(markup: &str) -> Document {
    let mut stack = vec![ElementBuilder {
        tag_name: "document".to_string(),
        attributes: Attributes::new(),
        children: Vec::new(),
    }];
    let mut index = 0usize;

    while index < markup.len() {
        let rest = &markup[index..];
        if let Some(stripped) = rest.strip_prefix('<') {
            if let Some(tag_end) = stripped.find('>') {
                let raw_tag = stripped[..tag_end].trim();
                index += tag_end + 2;

                if raw_tag.starts_with('!') || raw_tag.starts_with('?') {
                    continue;
                }

                if let Some(tag_name) = raw_tag.strip_prefix('/') {
                    close_element(&mut stack, tag_name.trim().to_lowercase());
                    continue;
                }

                let trimmed_tag = raw_tag.trim();
                let self_closing = trimmed_tag.ends_with('/');
                let (tag_name, attributes) = parse_tag_definition(trimmed_tag);

                if tag_name.is_empty() {
                    continue;
                }

                if self_closing {
                    push_node(
                        &mut stack,
                        Node::Element(ElementNode {
                            tag_name,
                            attributes,
                            children: Vec::new(),
                        }),
                    );
                } else {
                    stack.push(ElementBuilder {
                        tag_name,
                        attributes,
                        children: Vec::new(),
                    });
                }

                continue;
            }
        }

        let next_tag = rest.find('<').unwrap_or(rest.len());
        let text = &rest[..next_tag];
        push_text(&mut stack, text);
        index += next_tag;
    }

    while stack.len() > 1 {
        finalize_top_element(&mut stack);
    }

    let root = stack.pop().unwrap_or(ElementBuilder {
        tag_name: "document".to_string(),
        attributes: Attributes::new(),
        children: Vec::new(),
    });

    Document {
        children: root.children,
    }
}

pub fn build_render_blueprint(markup: &str, viewport_width: u16) -> RenderBlueprint {
    let document = parse_html_fragment(markup);
    build_blueprint_from_document(&document, viewport_width)
}

pub fn resolve_internal_route(route: &str) -> InternalRoutePage {
    let normalized_route = route.trim().trim_end_matches('/').to_lowercase();

    match normalized_route.as_str() {
        "waterfall://home" | "waterfall://welcome" | "waterfall://launch" => InternalRoutePage {
            route: "waterfall://home".to_string(),
            title: "WaterFall Native Home".to_string(),
            subtitle: "This page is being rendered through WaterFall's own native route lane instead of the guest webview.".to_string(),
            markup: "<main data-wf-surface=\"hero\" data-wf-tone=\"lagoon\"><h1>WaterFall Native Home</h1><p>waterfall:// is alive inside Thirsty's WaterFall, and these blueprint boxes can now route you deeper into the first-party browser deck.</p><div data-wf-surface=\"cluster\" data-wf-layout=\"grid\" data-wf-columns=\"3\"><section data-wf-surface=\"card\" data-wf-span=\"2\" href=\"waterfall://engine-lab\"><h2>Engine Lab</h2><p>Inspect the native renderer spine and the path toward deeper layout, paint, and interaction work.</p></section><section data-wf-surface=\"card\" href=\"waterfall://routes\"><h2>Route Atlas</h2><p>See the native route index and branch into first-party WaterFall pages.</p></section><section data-wf-surface=\"card\" href=\"waterfall://mesh\"><h2>Mesh Deck</h2><p>Inspect node identity, trust posture, and collective direction.</p></section></div></main>".to_string(),
        },
        "waterfall://engine-lab" => InternalRoutePage {
            route: "waterfall://engine-lab".to_string(),
            title: "Engine Lab".to_string(),
            subtitle: "WaterFall's rendering core is starting with parser, DOM graph, layout, paint-blueprint work, and direct route interactions in Rust.".to_string(),
            markup: "<main data-wf-surface=\"hero\" data-wf-tone=\"ember\"><h1>Engine Lab</h1><p>The native lane now preserves href and action metadata, which means painted blueprint boxes can become usable browser controls.</p><div data-wf-surface=\"cluster\" data-wf-layout=\"grid\" data-wf-columns=\"3\"><section data-wf-surface=\"card\" href=\"waterfall://home\"><h2>Return Home</h2><p>Jump back to the WaterFall dashboard.</p></section><section data-wf-surface=\"card\" href=\"waterfall://routes\"><h2>Route Atlas</h2><p>Open the route index and survey the live native pages.</p></section><section data-wf-surface=\"card\" href=\"waterfall://mesh\"><h2>Mesh Deck</h2><p>Check how native routing connects to the future collective layer.</p></section></div></main>".to_string(),
        },
        "waterfall://mesh" => InternalRoutePage {
            route: "waterfall://mesh".to_string(),
            title: "Mesh Deck".to_string(),
            subtitle: "A placeholder native page for future shared-compute and peer route orchestration.".to_string(),
            markup: "<main data-wf-surface=\"hero\" data-wf-tone=\"signal\"><h1>Mesh Deck</h1><p>The compute mesh remains voluntary, explicit, and bounded while the peer protocol grows underneath it.</p><div data-wf-surface=\"cluster\" data-wf-layout=\"grid\" data-wf-columns=\"3\"><section data-wf-surface=\"card\" href=\"waterfall://collective\"><h2>Collective Deck</h2><p>Inspect current pledge posture and contribution limits.</p></section><section data-wf-surface=\"card\" href=\"waterfall://routes\"><h2>Route Atlas</h2><p>Return to the native route index.</p></section><section data-wf-surface=\"card\" href=\"waterfall://home\"><h2>Native Home</h2><p>Jump back to the main WaterFall dashboard.</p></section></div></main>".to_string(),
        },
        _ => InternalRoutePage {
            route: route.trim().to_string(),
            title: "Route Not Found".to_string(),
            subtitle: "WaterFall caught the route, but this native page has not been authored yet.".to_string(),
            markup: format!(
                "<main data-wf-surface=\"hero\" data-wf-tone=\"ember\"><h1>Route Not Found</h1><p>{}</p><section data-wf-surface=\"card\" href=\"waterfall://routes\"><h2>Open Route Atlas</h2><p>Browse the currently authored WaterFall native routes.</p></section><section data-wf-surface=\"card\" href=\"waterfall://home\"><h2>Return Home</h2><p>Go back to WaterFall native home.</p></section></main>",
                route.trim()
            ),
        },
    }
}

pub fn render_internal_route(route: &str, viewport_width: u16) -> RenderedInternalRoute {
    let page = resolve_internal_route(route);
    render_markup_document(&page.route, &page.title, &page.subtitle, &page.markup, viewport_width)
}

pub fn render_markup_document(
    route: &str,
    title: &str,
    subtitle: &str,
    markup: &str,
    viewport_width: u16,
) -> RenderedInternalRoute {
    let blueprint = build_render_blueprint(markup, viewport_width);

    RenderedInternalRoute {
        route: route.to_string(),
        title: title.to_string(),
        subtitle: subtitle.to_string(),
        markup: markup.to_string(),
        viewport_width: blueprint.viewport_width,
        document_height: blueprint.document_height,
        boxes: blueprint.boxes,
        engine: engine_identity(),
    }
}

pub fn hit_test_blueprint(blueprint: &RenderBlueprint, x: u16, y: u16) -> Option<HitTarget> {
    hit_test_render_boxes(&blueprint.boxes, x, y)
}

pub fn hit_test_markup_document(
    route: &str,
    title: &str,
    subtitle: &str,
    markup: &str,
    viewport_width: u16,
    x: u16,
    y: u16,
) -> Option<HitTarget> {
    let rendered = render_markup_document(route, title, subtitle, markup, viewport_width);
    hit_test_render_boxes(&rendered.boxes, x, y)
}

pub fn hit_test_internal_route(
    route: &str,
    viewport_width: u16,
    x: u16,
    y: u16,
) -> Option<HitTarget> {
    let rendered = render_internal_route(route, viewport_width);
    hit_test_render_boxes(&rendered.boxes, x, y)
}

pub fn build_blueprint_from_document(document: &Document, viewport_width: u16) -> RenderBlueprint {
    let viewport_width = viewport_width.max(24);
    let mut cursor = 0u16;
    let mut boxes = Vec::new();
    let interaction = InteractionState::default();
    let mut next_focus_index = 0u16;
    let root_frame = LayoutFrame {
        left: 0,
        width: viewport_width,
    };

    for (index, node) in document.children.iter().enumerate() {
        let path = format!("/document[{index}]");
        layout_node(
            node,
            root_frame,
            0,
            &path,
            &mut cursor,
            &mut boxes,
            &interaction,
            &mut next_focus_index,
        );
    }

    RenderBlueprint {
        viewport_width,
        document_height: cursor.max(1),
        boxes,
    }
}

fn parse_tag_definition(raw_tag: &str) -> (String, Attributes) {
    let trimmed = raw_tag.trim().trim_end_matches('/').trim();
    let mut attributes = Attributes::new();

    if trimmed.is_empty() {
        return (String::new(), attributes);
    }

    let bytes = trimmed.as_bytes();
    let mut index = 0usize;

    while index < bytes.len() && !bytes[index].is_ascii_whitespace() {
        index += 1;
    }

    let tag_name = trimmed[..index].to_lowercase();

    while index < bytes.len() {
        while index < bytes.len() && bytes[index].is_ascii_whitespace() {
            index += 1;
        }

        if index >= bytes.len() {
            break;
        }

        let name_start = index;
        while index < bytes.len()
            && !bytes[index].is_ascii_whitespace()
            && bytes[index] != b'='
        {
            index += 1;
        }

        let name = trimmed[name_start..index].trim().to_lowercase();

        while index < bytes.len() && bytes[index].is_ascii_whitespace() {
            index += 1;
        }

        let mut value = "true".to_string();
        if index < bytes.len() && bytes[index] == b'=' {
            index += 1;

            while index < bytes.len() && bytes[index].is_ascii_whitespace() {
                index += 1;
            }

            if index < bytes.len() && (bytes[index] == b'"' || bytes[index] == b'\'') {
                let quote = bytes[index];
                index += 1;
                let value_start = index;

                while index < bytes.len() && bytes[index] != quote {
                    index += 1;
                }

                value = trimmed[value_start..index].to_string();

                if index < bytes.len() {
                    index += 1;
                }
            } else {
                let value_start = index;
                while index < bytes.len() && !bytes[index].is_ascii_whitespace() {
                    index += 1;
                }
                value = trimmed[value_start..index].to_string();
            }
        }

        if !name.is_empty() {
            attributes.insert(name, value);
        }
    }

    (tag_name, attributes)
}

fn push_node(stack: &mut [ElementBuilder], node: Node) {
    if let Some(parent) = stack.last_mut() {
        parent.children.push(node);
    }
}

fn push_text(stack: &mut [ElementBuilder], text: &str) {
    let normalized = normalize_text(text);
    if normalized.is_empty() {
        return;
    }

    push_node(
        stack,
        Node::Text(TextNode { text: normalized }),
    );
}

fn normalize_text(text: &str) -> String {
    text.split_whitespace().collect::<Vec<_>>().join(" ")
}

fn close_element(stack: &mut Vec<ElementBuilder>, tag_name: String) {
    if stack.len() <= 1 {
        return;
    }

    while stack.len() > 1 {
        let matches = stack
            .last()
            .map(|element| element.tag_name == tag_name)
            .unwrap_or(false);
        finalize_top_element(stack);
        if matches {
            break;
        }
    }
}

fn finalize_top_element(stack: &mut Vec<ElementBuilder>) {
    if stack.len() <= 1 {
        return;
    }

    let element = stack.pop().unwrap_or(ElementBuilder {
        tag_name: "document".to_string(),
        attributes: Attributes::new(),
        children: Vec::new(),
    });

    if let Some(parent) = stack.last_mut() {
        parent.children.push(Node::Element(ElementNode {
            tag_name: element.tag_name,
            attributes: element.attributes,
            children: element.children,
        }));
    }
}

fn layout_node(
    node: &Node,
    frame: LayoutFrame,
    depth: u16,
    node_path: &str,
    cursor: &mut u16,
    boxes: &mut Vec<RenderBox>,
    inherited_interaction: &InteractionState,
    next_focus_index: &mut u16,
) {
    match node {
        Node::Text(text) => {
            let available_width = frame.width.max(8);
            let interactive = inherited_interaction.href.is_some() || inherited_interaction.action_id.is_some();
            let height = required_lines(&text.text, available_width).max(1);
            let focus_index = if interactive {
                let assigned = *next_focus_index;
                *next_focus_index = next_focus_index.saturating_add(1);
                Some(assigned)
            } else {
                None
            };
            boxes.push(RenderBox {
                node_path: node_path.to_string(),
                role: "text".to_string(),
                x: frame.left,
                y: *cursor,
                width: available_width,
                height,
                z_index: depth,
                focus_index,
                text: Some(text.text.clone()),
                surface: None,
                tone: None,
                layout: None,
                emphasis: None,
                interactive,
                href: inherited_interaction.href.clone(),
                action_id: inherited_interaction.action_id.clone(),
                control_kind: None,
                setting_path: None,
                control_label: None,
                control_caption: None,
                control_string_value: None,
                control_number_value: None,
                control_placeholder: None,
                control_min: None,
                control_max: None,
                control_step: None,
                control_options: Vec::new(),
            });
            *cursor = cursor.saturating_add(height.max(1));
        }
        Node::Element(element) => {
            let control_metadata = extract_control_metadata(&element.attributes);
            let layout_metadata = extract_layout_metadata(element, &control_metadata);
            let minimum_height = minimum_box_height(element, &control_metadata, &layout_metadata);
            let x = frame.left;
            let width = frame.width.max(10);
            let start_y = *cursor;
            let next_interaction = merge_interaction(inherited_interaction, &element.attributes);
            let surface = surface_token(&element.attributes);
            let tone = tone_token(&element.attributes);
            let layout = layout_token(&element.attributes);
            let emphasis = emphasis_token(&element.attributes);
            let interactive = next_interaction.href.is_some()
                || next_interaction.action_id.is_some()
                || control_metadata.control_kind.is_some();
            let focus_index = if interactive {
                let assigned = *next_focus_index;
                *next_focus_index = next_focus_index.saturating_add(1);
                Some(assigned)
            } else {
                None
            };
            let box_index = boxes.len();

            boxes.push(RenderBox {
                node_path: node_path.to_string(),
                role: build_render_role(element),
                x,
                y: start_y,
                width,
                height: minimum_height,
                z_index: depth,
                focus_index,
                text: None,
                surface,
                tone,
                layout,
                emphasis,
                interactive,
                href: next_interaction.href.clone(),
                action_id: next_interaction.action_id.clone(),
                control_kind: control_metadata.control_kind.clone(),
                setting_path: control_metadata.setting_path.clone(),
                control_label: control_metadata.control_label.clone(),
                control_caption: control_metadata.control_caption.clone(),
                control_string_value: control_metadata.control_string_value.clone(),
                control_number_value: control_metadata.control_number_value,
                control_placeholder: control_metadata.control_placeholder.clone(),
                control_min: control_metadata.control_min,
                control_max: control_metadata.control_max,
                control_step: control_metadata.control_step,
                control_options: control_metadata.control_options.clone(),
            });

            let top_padding = layout_metadata.padding_y;
            let bottom_padding = layout_metadata.padding_y;
            *cursor = start_y.saturating_add(top_padding);

            let content_frame = LayoutFrame {
                left: x.saturating_add(layout_metadata.padding_x),
                width: width
                    .saturating_sub(layout_metadata.padding_x.saturating_mul(2))
                    .max(8),
            };

            if layout_metadata.kind == LayoutKind::Grid {
                layout_children_in_grid(
                    &element.children,
                    content_frame,
                    depth + 1,
                    node_path,
                    cursor,
                    boxes,
                    &next_interaction,
                    &layout_metadata,
                    next_focus_index,
                );
            } else {
                layout_children_in_stack(
                    &element.children,
                    content_frame,
                    depth + 1,
                    node_path,
                    cursor,
                    boxes,
                    &next_interaction,
                    next_focus_index,
                );
            }

            let content_end = (*cursor).max(start_y.saturating_add(top_padding));
            *cursor = content_end.saturating_add(bottom_padding);
            let height = cursor.saturating_sub(start_y).max(minimum_height);

            if let Some(render_box) = boxes.get_mut(box_index) {
                render_box.height = height;
            }

            let desired_cursor = start_y.saturating_add(height);
            if *cursor < desired_cursor {
                *cursor = desired_cursor;
            }
        }
    }
}

fn layout_children_in_stack(
    children: &[Node],
    frame: LayoutFrame,
    depth: u16,
    node_path: &str,
    cursor: &mut u16,
    boxes: &mut Vec<RenderBox>,
    inherited_interaction: &InteractionState,
    next_focus_index: &mut u16,
) {
    for (index, child) in children.iter().enumerate() {
        let child_path = format!("{node_path}/stack[{index}]");
        layout_node(
            child,
            frame,
            depth + 1,
            &child_path,
            cursor,
            boxes,
            inherited_interaction,
            next_focus_index,
        );
    }
}

fn layout_children_in_grid(
    children: &[Node],
    frame: LayoutFrame,
    depth: u16,
    node_path: &str,
    cursor: &mut u16,
    boxes: &mut Vec<RenderBox>,
    inherited_interaction: &InteractionState,
    layout_metadata: &LayoutMetadata,
    next_focus_index: &mut u16,
) {
    let columns = layout_metadata.columns.max(1);
    if columns == 1 || children.is_empty() {
        layout_children_in_stack(
            children,
            frame,
            depth,
            node_path,
            cursor,
            boxes,
            inherited_interaction,
            next_focus_index,
        );
        return;
    }

    let gap = layout_metadata.gap;
    let total_gap = gap.saturating_mul(columns.saturating_sub(1));
    let column_width = frame.width.saturating_sub(total_gap).max(columns) / columns;

    if column_width < 10 {
        layout_children_in_stack(
            children,
            frame,
            depth,
            node_path,
            cursor,
            boxes,
            inherited_interaction,
            next_focus_index,
        );
        return;
    }

    let mut row_start = *cursor;
    let mut row_height = 0u16;
    let mut column_index = 0u16;

    for (index, child) in children.iter().enumerate() {
        let span = grid_span_for_node(child, columns);

        if column_index > 0 && column_index.saturating_add(span) > columns {
            row_start = row_start.saturating_add(row_height.max(1));
            row_height = 0;
            column_index = 0;
        }

        let child_left = frame.left.saturating_add(
            column_index.saturating_mul(column_width.saturating_add(gap)),
        );
        let child_width = if span >= columns {
            frame.width
        } else {
            column_width
                .saturating_mul(span)
                .saturating_add(gap.saturating_mul(span.saturating_sub(1)))
        }
        .max(8);
        let child_path = format!("{node_path}/grid[{index}]");
        let mut child_cursor = row_start;

        layout_node(
            child,
            LayoutFrame {
                left: child_left,
                width: child_width,
            },
            depth + 1,
            &child_path,
            &mut child_cursor,
            boxes,
            inherited_interaction,
            next_focus_index,
        );

        if span >= columns {
            row_start = child_cursor;
            row_height = 0;
            column_index = 0;
            continue;
        }

        row_height = row_height.max(child_cursor.saturating_sub(row_start));
        column_index = column_index.saturating_add(span);

        if column_index >= columns {
            row_start = row_start.saturating_add(row_height.max(1));
            row_height = 0;
            column_index = 0;
        }
    }

    *cursor = if column_index == 0 {
        row_start
    } else {
        row_start.saturating_add(row_height.max(1))
    };
}

fn merge_interaction(
    inherited_interaction: &InteractionState,
    attributes: &Attributes,
) -> InteractionState {
    InteractionState {
        href: attribute_value(attributes, "href").or_else(|| inherited_interaction.href.clone()),
        action_id: attribute_value(attributes, "data-wf-action")
            .or_else(|| inherited_interaction.action_id.clone()),
    }
}

fn attribute_value(attributes: &Attributes, name: &str) -> Option<String> {
    attributes
        .get(name)
        .map(|value| value.trim().to_string())
        .filter(|value| !value.is_empty())
}

fn build_render_role(element: &ElementNode) -> String {
    let mut role_tokens = vec![format!("element:{}", element.tag_name)];

    if let Some(surface) = surface_token(&element.attributes) {
        role_tokens.push(surface);
    }

    if let Some(tone) = tone_token(&element.attributes) {
        role_tokens.push(tone);
    }

    if let Some(layout) = layout_token(&element.attributes) {
        role_tokens.push(layout);
    }

    if let Some(emphasis) = emphasis_token(&element.attributes) {
        role_tokens.push(emphasis);
    }

    if attribute_value(&element.attributes, "href").is_some() {
        role_tokens.push("link".to_string());
    }

    if attribute_value(&element.attributes, "data-wf-action").is_some() {
        role_tokens.push("action".to_string());
    }

    if let Some(control_kind) = attribute_value(&element.attributes, "data-wf-control") {
        role_tokens.push("control".to_string());
        role_tokens.push(control_kind.to_lowercase());
    }

    role_tokens.join(":")
}

fn hit_test_render_boxes(boxes: &[RenderBox], x: u16, y: u16) -> Option<HitTarget> {
    boxes
        .iter()
        .filter(|render_box| contains_point(render_box, x, y))
        .max_by_key(|render_box| {
            (
                if render_box.interactive { 1u8 } else { 0u8 },
                render_box.z_index,
                render_box.focus_index.unwrap_or(u16::MAX).wrapping_neg(),
                render_box.height,
                render_box.width,
            )
        })
        .map(|render_box| HitTarget {
            node_path: render_box.node_path.clone(),
            role: render_box.role.clone(),
            x: render_box.x,
            y: render_box.y,
            width: render_box.width,
            height: render_box.height,
            z_index: render_box.z_index,
            focus_index: render_box.focus_index,
            interactive: render_box.interactive,
            href: render_box.href.clone(),
            action_id: render_box.action_id.clone(),
            control_kind: render_box.control_kind.clone(),
            setting_path: render_box.setting_path.clone(),
            text: render_box.text.clone(),
            surface: render_box.surface.clone(),
            tone: render_box.tone.clone(),
        })
}

fn contains_point(render_box: &RenderBox, x: u16, y: u16) -> bool {
    let right = render_box.x.saturating_add(render_box.width);
    let bottom = render_box.y.saturating_add(render_box.height);

    x >= render_box.x && y >= render_box.y && x < right && y < bottom
}

fn required_lines(text: &str, width: u16) -> u16 {
    let width = usize::from(width.max(8));
    let len = text.chars().count();
    let lines = (len + width.saturating_sub(1)) / width;
    lines.max(1) as u16
}

fn is_block_tag(tag_name: &str) -> bool {
    BLOCK_TAGS.iter().any(|candidate| candidate == &tag_name)
}

fn surface_token(attributes: &Attributes) -> Option<String> {
    attribute_value(attributes, "data-wf-surface").map(|value| value.to_lowercase())
}

fn tone_token(attributes: &Attributes) -> Option<String> {
    attribute_value(attributes, "data-wf-tone").map(|value| value.to_lowercase())
}

fn layout_token(attributes: &Attributes) -> Option<String> {
    attribute_value(attributes, "data-wf-layout")
        .map(|value| value.to_lowercase())
        .filter(|value| matches!(value.as_str(), "stack" | "grid" | "columns"))
}

fn emphasis_token(attributes: &Attributes) -> Option<String> {
    attribute_value(attributes, "data-wf-emphasis").map(|value| value.to_lowercase())
}

fn extract_control_metadata(attributes: &Attributes) -> ControlMetadata {
    let control_kind = attribute_value(attributes, "data-wf-control")
        .map(|value| value.to_lowercase())
        .filter(|value| matches!(value.as_str(), "text" | "select" | "range"));
    let control_value = attribute_value(attributes, "data-wf-value");

    ControlMetadata {
        control_kind,
        setting_path: attribute_value(attributes, "data-wf-setting"),
        control_label: attribute_value(attributes, "data-wf-label"),
        control_caption: attribute_value(attributes, "data-wf-caption"),
        control_string_value: control_value.clone(),
        control_number_value: control_value.as_deref().and_then(parse_u16),
        control_placeholder: attribute_value(attributes, "data-wf-placeholder"),
        control_min: attribute_value(attributes, "data-wf-min")
            .as_deref()
            .and_then(parse_u16),
        control_max: attribute_value(attributes, "data-wf-max")
            .as_deref()
            .and_then(parse_u16),
        control_step: attribute_value(attributes, "data-wf-step")
            .as_deref()
            .and_then(parse_u16),
        control_options: attribute_value(attributes, "data-wf-options")
            .map(|value| parse_control_options(&value))
            .unwrap_or_default(),
    }
}

fn extract_layout_metadata(
    element: &ElementNode,
    control_metadata: &ControlMetadata,
) -> LayoutMetadata {
    let surface = surface_token(&element.attributes);
    let layout_kind = layout_token(&element.attributes)
        .map(|value| match value.as_str() {
            "grid" | "columns" => LayoutKind::Grid,
            _ => LayoutKind::Stack,
        })
        .unwrap_or(LayoutKind::Stack);
    let columns = attribute_value(&element.attributes, "data-wf-columns")
        .as_deref()
        .and_then(parse_u16)
        .map(|value| value.clamp(1, 4))
        .unwrap_or(match layout_kind {
            LayoutKind::Grid => 2,
            LayoutKind::Stack => 1,
        });
    let span = attribute_value(&element.attributes, "data-wf-span")
        .as_deref()
        .and_then(parse_u16)
        .map(|value| value.clamp(1, 4))
        .unwrap_or(1);
    let gap = attribute_value(&element.attributes, "data-wf-gap")
        .as_deref()
        .and_then(parse_u16)
        .map(|value| value.clamp(1, 4))
        .unwrap_or(match layout_kind {
            LayoutKind::Grid => 2,
            LayoutKind::Stack => 1,
        });

    let (padding_x, padding_y) = if control_metadata.control_kind.is_some() {
        (1, 1)
    } else {
        match surface.as_deref() {
            Some("hero") => (2, 1),
            Some("card") | Some("panel") | Some("cluster") | Some("control") => (1, 1),
            _ if matches!(element.tag_name.as_str(), "main" | "section" | "article" | "aside") => {
                (1, 1)
            }
            _ if matches!(element.tag_name.as_str(), "h1" | "h2" | "h3") => (1, 0),
            _ => (0, 0),
        }
    };

    LayoutMetadata {
        kind: layout_kind,
        columns,
        span,
        gap,
        padding_x,
        padding_y,
    }
}

fn grid_span_for_node(node: &Node, columns: u16) -> u16 {
    match node {
        Node::Text(_) => columns,
        Node::Element(element) => attribute_value(&element.attributes, "data-wf-span")
            .as_deref()
            .and_then(parse_u16)
            .map(|value| value.clamp(1, columns))
            .unwrap_or_else(|| {
                if defaults_to_single_grid_column(element) {
                    1
                } else {
                    columns
                }
            }),
    }
}

fn defaults_to_single_grid_column(element: &ElementNode) -> bool {
    if attribute_value(&element.attributes, "href").is_some()
        || attribute_value(&element.attributes, "data-wf-action").is_some()
        || attribute_value(&element.attributes, "data-wf-control").is_some()
    {
        return true;
    }

    if matches!(
        surface_token(&element.attributes).as_deref(),
        Some("card" | "control" | "metric" | "status" | "result" | "panel")
    ) {
        return true;
    }

    matches!(element.tag_name.as_str(), "section" | "article" | "aside" | "wf-control")
}

fn parse_control_options(raw_value: &str) -> Vec<ControlOption> {
    raw_value
        .split('|')
        .filter_map(|entry| {
            let trimmed = entry.trim();
            if trimmed.is_empty() {
                return None;
            }

            let (value, label) = trimmed
                .split_once(':')
                .map(|(value, label)| (value.trim(), label.trim()))
                .unwrap_or((trimmed, trimmed));

            if value.is_empty() || label.is_empty() {
                return None;
            }

            Some(ControlOption {
                value: value.to_string(),
                label: label.to_string(),
            })
        })
        .collect()
}

fn parse_u16(raw_value: &str) -> Option<u16> {
    raw_value.trim().parse::<u16>().ok()
}

fn minimum_box_height(
    element: &ElementNode,
    control_metadata: &ControlMetadata,
    layout_metadata: &LayoutMetadata,
) -> u16 {
    let base_height: u16 = match control_metadata.control_kind.as_deref() {
        Some("range") => 5,
        Some("text") | Some("select") => 4,
        _ if matches!(element.tag_name.as_str(), "h1") => 2,
        _ if matches!(element.tag_name.as_str(), "h2" | "h3") => 1,
        _ if matches!(surface_token(&element.attributes).as_deref(), Some("hero")) => 3,
        _ if matches!(
            surface_token(&element.attributes).as_deref(),
            Some("card" | "panel" | "cluster" | "control")
        ) =>
        {
            2
        }
        _ if is_block_tag(&element.tag_name) => 1,
        _ => 1,
    };

    base_height
        .saturating_add(layout_metadata.padding_y.saturating_mul(2))
        .max(if layout_metadata.kind == LayoutKind::Grid { 2 } else { 1 })
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeMap;

    use super::{
        build_render_blueprint, engine_identity, hit_test_blueprint, parse_html_fragment,
        render_internal_route, render_markup_document, ControlOption, Document, ElementNode,
        Node, TextNode,
    };

    #[test]
    fn engine_identity_reports_utf_sidecar_integration() {
        let identity = engine_identity();

        assert_eq!(identity.engine_id, "thirstys-waterfall-native");
        assert_eq!(identity.integration, "utf-sidecar");
        assert!(identity.focus.contains(&"block-layout"));
        assert!(identity.focus.contains(&"route-interactions"));
        assert!(identity.focus.contains(&"region-layout"));
    }

    #[test]
    fn parse_html_fragment_builds_nested_nodes() {
        let document = parse_html_fragment("<main><h1>WaterFall</h1><p>Native shell.</p></main>");

        assert_eq!(
            document,
            Document {
                children: vec![Node::Element(ElementNode {
                    tag_name: "main".to_string(),
                    attributes: BTreeMap::new(),
                    children: vec![
                        Node::Element(ElementNode {
                            tag_name: "h1".to_string(),
                            attributes: BTreeMap::new(),
                            children: vec![Node::Text(TextNode {
                                text: "WaterFall".to_string(),
                            })],
                        }),
                        Node::Element(ElementNode {
                            tag_name: "p".to_string(),
                            attributes: BTreeMap::new(),
                            children: vec![Node::Text(TextNode {
                                text: "Native shell.".to_string(),
                            })],
                        }),
                    ],
                })],
            }
        );
    }

    #[test]
    fn parse_html_fragment_retains_attributes() {
        let document = parse_html_fragment(
            "<section href=\"waterfall://home\" data-wf-action=\"go-home\"><p>Link</p></section>",
        );

        assert_eq!(
            document,
            Document {
                children: vec![Node::Element(ElementNode {
                    tag_name: "section".to_string(),
                    attributes: BTreeMap::from([
                        ("data-wf-action".to_string(), "go-home".to_string()),
                        ("href".to_string(), "waterfall://home".to_string()),
                    ]),
                    children: vec![Node::Element(ElementNode {
                        tag_name: "p".to_string(),
                        attributes: BTreeMap::new(),
                        children: vec![Node::Text(TextNode {
                            text: "Link".to_string(),
                        })],
                    })],
                })],
            }
        );
    }

    #[test]
    fn build_render_blueprint_emits_boxes_for_text_and_blocks() {
        let blueprint =
            build_render_blueprint("<main><h1>WaterFall</h1><p>Renders forward.</p></main>", 64);

        assert_eq!(blueprint.viewport_width, 64);
        assert!(blueprint.document_height >= 3);
        assert!(
            blueprint
                .boxes
                .iter()
                .any(|entry| entry.role == "element:main")
        );
        assert!(
            blueprint
                .boxes
                .iter()
                .any(|entry| entry.text.as_deref() == Some("WaterFall"))
        );
    }

    #[test]
    fn build_render_blueprint_propagates_interaction_metadata() {
        let blueprint = build_render_blueprint(
            "<main><section href=\"waterfall://home\"><p>Go home</p></section><section data-wf-action=\"open-settings\"><p>Open settings</p></section></main>",
            72,
        );

        assert!(
            blueprint
                .boxes
                .iter()
                .any(|entry| entry.text.as_deref() == Some("Go home")
                    && entry.href.as_deref() == Some("waterfall://home"))
        );
        assert!(
            blueprint
                .boxes
                .iter()
                .any(|entry| entry.text.as_deref() == Some("Open settings")
                    && entry.action_id.as_deref() == Some("open-settings"))
        );
    }

    #[test]
    fn build_render_blueprint_retains_control_metadata() {
        let blueprint = build_render_blueprint(
            "<main><wf-control data-wf-surface=\"control\" data-wf-control=\"range\" data-wf-setting=\"collective.cpuLimitPercent\" data-wf-label=\"CPU Cap\" data-wf-caption=\"Adjust the CPU pledge.\" data-wf-value=\"45\" data-wf-min=\"5\" data-wf-max=\"90\" data-wf-step=\"5\" /><wf-control data-wf-control=\"select\" data-wf-setting=\"searchEngine\" data-wf-label=\"Search\" data-wf-caption=\"Select a search engine.\" data-wf-value=\"kagi\" data-wf-options=\"duckduckgo:DuckDuckGo|startpage:Startpage|kagi:Kagi\" /></main>",
            72,
        );

        assert!(
            blueprint
                .boxes
                .iter()
                .any(|entry| entry.control_kind.as_deref() == Some("range")
                    && entry.setting_path.as_deref()
                        == Some("collective.cpuLimitPercent")
                    && entry.control_number_value == Some(45)
                    && entry.control_min == Some(5)
                    && entry.control_max == Some(90)
                    && entry.control_step == Some(5)
                    && entry.height >= 5)
        );
        assert!(
            blueprint
                .boxes
                .iter()
                .any(|entry| entry.control_kind.as_deref() == Some("select")
                    && entry.setting_path.as_deref() == Some("searchEngine")
                    && entry.control_string_value.as_deref() == Some("kagi")
                    && entry.control_options
                        == vec![
                            ControlOption {
                                value: "duckduckgo".to_string(),
                                label: "DuckDuckGo".to_string(),
                            },
                            ControlOption {
                                value: "startpage".to_string(),
                                label: "Startpage".to_string(),
                            },
                            ControlOption {
                                value: "kagi".to_string(),
                                label: "Kagi".to_string(),
                            },
                        ])
        );
    }

    #[test]
    fn build_render_blueprint_emits_structured_surface_metadata() {
        let blueprint = build_render_blueprint(
            "<main data-wf-surface=\"hero\" data-wf-tone=\"lagoon\" data-wf-layout=\"grid\" data-wf-columns=\"2\"><section data-wf-surface=\"card\" href=\"waterfall://home\"><h2>Home</h2><p>Open the home deck.</p></section></main>",
            72,
        );

        assert!(
            blueprint
                .boxes
                .iter()
                .any(|entry| entry.surface.as_deref() == Some("hero")
                    && entry.tone.as_deref() == Some("lagoon")
                    && entry.layout.as_deref() == Some("grid"))
        );
        assert!(
            blueprint
                .boxes
                .iter()
                .any(|entry| entry.surface.as_deref() == Some("card")
                    && entry.interactive
                    && entry.href.as_deref() == Some("waterfall://home"))
        );
    }

    #[test]
    fn build_render_blueprint_supports_grid_layout_and_spans() {
        let blueprint = build_render_blueprint(
            "<main><div data-wf-layout=\"grid\" data-wf-columns=\"3\"><section data-wf-surface=\"card\"><h2>One</h2><p>Alpha</p></section><section data-wf-surface=\"card\"><h2>Two</h2><p>Beta</p></section><section data-wf-surface=\"card\" data-wf-span=\"2\"><h2>Wide</h2><p>Gamma</p></section></div></main>",
            90,
        );

        let one_box = blueprint
            .boxes
            .iter()
            .find(|entry| entry.text.as_deref() == Some("One"))
            .expect("expected first card heading");
        let two_box = blueprint
            .boxes
            .iter()
            .find(|entry| entry.text.as_deref() == Some("Two"))
            .expect("expected second card heading");
        let wide_box = blueprint
            .boxes
            .iter()
            .find(|entry| entry.role.contains("card") && entry.width > one_box.width)
            .expect("expected wide card container");

        assert_eq!(one_box.y, two_box.y);
        assert!(two_box.x > one_box.x);
        assert!(wide_box.width > one_box.width);
    }

    #[test]
    fn build_render_blueprint_assigns_focus_order_to_interactive_boxes() {
        let blueprint = build_render_blueprint(
            "<main><section href=\"waterfall://home\"><h2>Home</h2></section><section data-wf-action=\"open-settings\"><h2>Settings</h2></section></main>",
            72,
        );

        let focus_targets = blueprint
            .boxes
            .iter()
            .filter_map(|entry| entry.focus_index.map(|focus_index| (focus_index, entry.node_path.clone())))
            .collect::<Vec<_>>();

        assert!(!focus_targets.is_empty());
        assert_eq!(focus_targets.first().map(|entry| entry.0), Some(0));
        assert!(focus_targets.windows(2).all(|window| window[0].0 <= window[1].0));
    }

    #[test]
    fn hit_test_blueprint_prefers_topmost_interactive_box() {
        let blueprint = build_render_blueprint(
            "<main data-wf-surface=\"hero\"><div data-wf-layout=\"grid\" data-wf-columns=\"2\"><section data-wf-surface=\"card\" href=\"waterfall://home\"><h2>Home</h2><p>Open home.</p></section><section data-wf-surface=\"card\" data-wf-action=\"open-settings\"><h2>Settings</h2><p>Open settings.</p></section></div></main>",
            72,
        );

        let hit_target = hit_test_blueprint(&blueprint, 4, 4).expect("expected hit target");

        assert!(hit_target.interactive);
        assert_eq!(hit_target.href.as_deref(), Some("waterfall://home"));
        assert!(hit_target.z_index > 0);
    }

    #[test]
    fn render_internal_route_uses_native_waterfall_pages() {
        let rendered = render_internal_route("waterfall://engine-lab", 84);

        assert_eq!(rendered.route, "waterfall://engine-lab");
        assert_eq!(rendered.title, "Engine Lab");
        assert_eq!(rendered.engine.engine_id, "thirstys-waterfall-native");
        assert!(
            rendered
                .boxes
                .iter()
                .any(|entry| entry.role.contains("hero"))
        );
    }

    #[test]
    fn render_markup_document_uses_supplied_markup() {
        let rendered = render_markup_document(
            "waterfall://history",
            "History",
            "Recent routes",
            "<main><h1>History</h1><section href=\"waterfall://home\"><p>waterfall://home</p></section></main>",
            72,
        );

        assert_eq!(rendered.route, "waterfall://history");
        assert_eq!(rendered.title, "History");
        assert!(
            rendered
                .boxes
                .iter()
                .any(|entry| entry.text.as_deref() == Some("waterfall://home")
                    && entry.href.as_deref() == Some("waterfall://home"))
        );
    }
}
