import { type ReactNode } from "react";

/**
 * Minimal in-house markdown renderer for trusted repo documents.
 *
 * Supported subset: ATX headings (#..####), paragraphs, unordered and
 * ordered lists, blockquotes, fenced code blocks, inline code, bold,
 * and http(s) links. Everything is emitted as React elements — no
 * dangerouslySetInnerHTML, no third-party dependency. Unsupported
 * syntax degrades to plain text rather than breaking the page.
 */

const INLINE_PATTERN = /(\*\*[^*]+\*\*|`[^`]+`|\[[^\]]+\]\((?:https?:)[^)]+\))/g;
const LINK_PATTERN = /^\[([^\]]+)\]\((https?:[^)]+)\)$/;

function renderInline(text: string, keyPrefix: string): ReactNode[] {
  return text
    .split(INLINE_PATTERN)
    .filter((part) => part !== "")
    .map((part, index) => {
      const key = `${keyPrefix}-${index}`;
      if (part.startsWith("**") && part.endsWith("**")) {
        return <strong key={key}>{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith("`") && part.endsWith("`")) {
        return <code key={key}>{part.slice(1, -1)}</code>;
      }
      const link = LINK_PATTERN.exec(part);
      if (link) {
        return (
          <a key={key} href={link[2]} target="_blank" rel="noreferrer">
            {link[1]}
          </a>
        );
      }
      return part;
    });
}

type Block =
  | { kind: "heading"; level: 1 | 2 | 3 | 4; text: string }
  | { kind: "paragraph"; text: string }
  | { kind: "list"; ordered: boolean; items: string[] }
  | { kind: "quote"; lines: string[] }
  | { kind: "code"; lines: string[] };

function parseBlocks(source: string): Block[] {
  const blocks: Block[] = [];
  let paragraph: string[] = [];
  let code: string[] | null = null;

  const flushParagraph = () => {
    if (paragraph.length > 0) {
      blocks.push({ kind: "paragraph", text: paragraph.join(" ") });
      paragraph = [];
    }
  };

  for (const rawLine of source.split(/\r?\n/)) {
    const line = rawLine.trimEnd();
    if (code !== null) {
      if (line.trim().startsWith("```")) {
        blocks.push({ kind: "code", lines: code });
        code = null;
      } else {
        code.push(rawLine);
      }
      continue;
    }
    if (line.trim().startsWith("```")) {
      flushParagraph();
      code = [];
      continue;
    }
    const heading = /^(#{1,4})\s+(.*)$/.exec(line);
    if (heading) {
      flushParagraph();
      blocks.push({
        kind: "heading",
        level: heading[1].length as 1 | 2 | 3 | 4,
        text: heading[2],
      });
      continue;
    }
    const unordered = /^\s*[-*]\s+(.*)$/.exec(line);
    const ordered = /^\s*\d+\.\s+(.*)$/.exec(line);
    if (unordered || ordered) {
      flushParagraph();
      const item = (unordered ?? ordered)?.[1] ?? "";
      const isOrdered = Boolean(ordered);
      const last = blocks.at(-1);
      if (last?.kind === "list" && last.ordered === isOrdered) {
        last.items.push(item);
      } else {
        blocks.push({ kind: "list", ordered: isOrdered, items: [item] });
      }
      continue;
    }
    const quote = /^>\s?(.*)$/.exec(line);
    if (quote) {
      flushParagraph();
      const last = blocks.at(-1);
      if (last?.kind === "quote") {
        last.lines.push(quote[1]);
      } else {
        blocks.push({ kind: "quote", lines: [quote[1]] });
      }
      continue;
    }
    if (line.trim() === "") {
      flushParagraph();
      continue;
    }
    const continuation = /^\s{2,}(.*)$/.exec(rawLine);
    const last = blocks.at(-1);
    if (continuation && paragraph.length === 0 && last?.kind === "list") {
      last.items[last.items.length - 1] += ` ${continuation[1]}`;
      continue;
    }
    paragraph.push(line.trim());
  }
  if (code !== null) blocks.push({ kind: "code", lines: code });
  flushParagraph();
  return blocks;
}

export function Markdown({ source }: { source: string }) {
  const blocks = parseBlocks(source);
  return (
    <div className="markdown">
      {blocks.map((block, index) => {
        const key = `block-${index}`;
        if (block.kind === "heading") {
          const Tag = (["h1", "h2", "h3", "h4"] as const)[block.level - 1];
          return <Tag key={key}>{renderInline(block.text, key)}</Tag>;
        }
        if (block.kind === "list") {
          const items = block.items.map((item, itemIndex) => (
            <li key={`${key}-${itemIndex}`}>{renderInline(item, `${key}-${itemIndex}`)}</li>
          ));
          return block.ordered ? <ol key={key}>{items}</ol> : <ul key={key}>{items}</ul>;
        }
        if (block.kind === "quote") {
          return (
            <blockquote key={key}>
              {renderInline(block.lines.join(" "), key)}
            </blockquote>
          );
        }
        if (block.kind === "code") {
          return (
            <pre className="terminal" key={key}>
              <code>{block.lines.join("\n")}</code>
            </pre>
          );
        }
        return <p key={key}>{renderInline(block.text, key)}</p>;
      })}
    </div>
  );
}
