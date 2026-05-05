
from __future__ import annotations

import argparse
import json
import readline
from pathlib import Path
from time import perf_counter

from .diagnostics import DiagnosticBundle, ThirstyError, format_bundle, format_error
from .interpreter import Interpreter, RuntimeFault, ThrownSignal
from .lexer import Lexer
from .package_manager import (
    ensure_hydration_dirs,
    install_package,
    list_installed_packages,
    load_manifest,
    publish_package,
    search_gallery,
    show_gallery_item,
)
from .parser import Parser

_HIST = Path.home() / ".thirsty_history"
_ACH = Path.home() / ".thirsty_achievements.json"


def color(text: str, name: str) -> str:
    codes = {"green": "\033[92m", "yellow": "\033[93m", "red": "\033[91m", "blue": "\033[94m", "reset": "\033[0m"}
    return f"{codes.get(name,'')}{text}{codes['reset']}"


def load_achievements() -> set[str]:
    if _ACH.exists():
        try:
            return set(json.loads(_ACH.read_text()))
        except Exception:
            return set()
    return set()


def save_achievements(items: set[str]) -> None:
    _ACH.write_text(json.dumps(sorted(items), indent=2), encoding="utf-8")


def parse_source(source: str, file: str = "<memory>"):
    tokens = Lexer(source, file).lex()
    return Parser.from_tokens(tokens).parse_program()


def check_source(source: str, file: str = "<memory>"):
    from .checker import Checker
    program = parse_source(source, file)
    Checker().check(program)
    return program


def run_source(source: str, file: str = "<memory>", input_values: list[str] | None = None, trace: bool = False, thirst_level: int = 1, return_interpreter: bool = False):
    idx = 0
    def input_provider() -> str:
        nonlocal idx
        if input_values is None or idx >= len(input_values):
            return ""
        val = input_values[idx]
        idx += 1
        return val
    program = check_source(source, file)
    project_root = str(Path(file).resolve().parent) if file not in {"<memory>", "<repl>"} else str(Path(".").resolve())
    interp = Interpreter(input_provider=input_provider, trace=trace, thirst_level=thirst_level, current_file=file, project_root=project_root)
    out = interp.run(program)
    return (out, interp) if return_interpreter else out


def thirsty_fmt(text: str) -> str:
    indent = 0
    lines = []
    current = []
    def flush():
        nonlocal current
        if current:
            line = "".join(current).strip()
            if line:
                lines.append("  " * indent + line)
            current = []
    for ch in text:
        if ch == "{":
            current.append(" {")
            flush()
            indent += 1
        elif ch == "}":
            flush()
            indent = max(0, indent - 1)
            lines.append("  " * indent + "}")
        elif ch == ";":
            current.append(";")
            flush()
        elif ch == "\n":
            flush()
        else:
            current.append(ch)
    flush()
    return "\n".join(lines) + ("\n" if lines else "")


def doctor(project: Path) -> list[str]:
    report = []
    ex = project / "examples"
    try:
        check_source((ex / "hello.thirsty").read_text(), str(ex / "hello.thirsty"))
        report.append(color("fully hydrated: Thirsty-Lang", "green"))
    except Exception as e:
        report.append(color(f"thirsty for fixes: Thirsty-Lang ({e})", "red"))
    try:
        from tarl.core import parse_policy, evaluate, load_context
        p = parse_policy((ex / "policy.tarl").read_text())
        _ = evaluate(p, load_context(str(ex / "context.json")))
        report.append(color("fully hydrated: TARL", "green"))
    except Exception as e:
        report.append(color(f"parched: TARL ({e})", "yellow"))
    try:
        from shadow_thirst.core import parse_shadow, analyze
        m = parse_shadow((ex / "promote.shadowthirst").read_text(), str(ex / "promote.shadowthirst"))
        _ = analyze(m)
        report.append(color("fully hydrated: Shadow Thirst", "green"))
    except Exception as e:
        report.append(color(f"parched: Shadow Thirst ({e})", "yellow"))
    try:
        from tscg.core import parse, validate
        validate(parse("COG -> DNT -> SHD(v1) ^ CAP -> COM"))
        report.append(color("fully hydrated: TSCG", "green"))
    except Exception as e:
        report.append(color(f"parched: TSCG ({e})", "yellow"))
    return report


def gallery_lines(term: str | None = None) -> list[str]:
    ensure_hydration_dirs()
    items = search_gallery(term)
    if not items:
        return [color("parched: no Great Wells found", "yellow")]
    lines = [color("Great Wells:", "blue")]
    for item in items:
        tags = ",".join(item.get("tags", []))
        lines.append(f"- {item['name']}@{item['version']} :: {item.get('description','')} [{tags}]")
    return lines


def show_package(name: str) -> list[str]:
    item = show_gallery_item(name)
    if not item:
        return [color(f"thirsty for fixes: no such Great Well '{name}'", "red")]
    return [json.dumps(item, indent=2)]


def scaffold_fountain(path: Path, name: str) -> None:
    for part in ["src", "examples", "policies", "shadows", "canonical"]:
        (path / name / part).mkdir(parents=True, exist_ok=True)
    main_src = """glass main() -> Int {
  pour("welcome to the fountain");
  return 0;
}
"""
    (path / name / "src" / "main.thirsty").write_text(main_src, encoding="utf-8")
    (path / name / "README.md").write_text(f"# {name}\n\nA freshly poured Thirsty project.\n", encoding="utf-8")


def repl() -> int:
    print("Thirsty REPL. Type :quit to exit.")
    _HIST.parent.mkdir(parents=True, exist_ok=True)
    try:
        readline.read_history_file(_HIST)
    except Exception:
        pass
    env_lines: list[str] = []
    last_interp = None
    while True:
        try:
            line = input("thirsty> ")
        except EOFError:
            print()
            try:
                readline.write_history_file(_HIST)
            except Exception:
                pass
            return 0
        if line.strip() == ":quit":
            try:
                readline.write_history_file(_HIST)
            except Exception:
                pass
            return 0
        if line.strip() == ":thirst":
            if last_interp is None:
                print("{}")
            else:
                print(json.dumps(last_interp.globals.describe(), indent=2))
            continue
        if line.strip().startswith(":drink "):
            file = line.strip()[7:].strip()
            env_lines.append(Path(file).read_text(encoding="utf-8"))
            print(color(f"loaded {file}", "blue"))
            continue
        env_lines.append(line)
        if not line.strip().endswith(";") and not line.strip().endswith("}"):
            continue
        source = "\n".join(env_lines)
        try:
            out, last_interp = run_source(source, "<repl>", return_interpreter=True)
            for item in out:
                print(item)
        except DiagnosticBundle as bundle:
            print(format_bundle(bundle, source))
        except (ThirstyError, RuntimeFault) as err:
            print(format_error(err, source))
        except ThrownSignal as thrown:
            print(f"unhandled thrown value: {thrown.value!r}")
        env_lines.clear()


def main(argv: list[str] | None = None) -> int:
    if argv == ["--quench"] or argv == ["quench"]:
        print("The springs approve you. Fully hydrated.")
        return 0
    parser = argparse.ArgumentParser(prog="thirsty")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run")
    run_p.add_argument("file")
    run_p.add_argument("--trace", action="store_true")
    run_p.add_argument("--thirst-level", type=int, default=1)

    check_p = sub.add_parser("check")
    check_p.add_argument("file")

    fmt_p = sub.add_parser("fmt")
    fmt_p.add_argument("file")
    fmt_p.add_argument("--write", action="store_true")

    sub.add_parser("repl")

    ast_p = sub.add_parser("ast")
    ast_p.add_argument("file")

    sub.add_parser("tutorial")

    doctor_p = sub.add_parser("doctor")
    doctor_p.add_argument("project", nargs="?", default=".")

    promote_p = sub.add_parser("promote")
    promote_p.add_argument("file")

    new_p = sub.add_parser("new")
    new_p.add_argument("kind")
    new_p.add_argument("name")

    install_p = sub.add_parser("install")
    install_p.add_argument("package")

    publish_p = sub.add_parser("publish")
    publish_p.add_argument("project", nargs="?", default=".")

    packages_p = sub.add_parser("packages")
    packages_p.add_argument("action", choices=["list"])

    gallery_p = sub.add_parser("gallery")
    gallery_p.add_argument("action", choices=["list", "search", "show"])
    gallery_p.add_argument("term", nargs="?")

    bench_p = sub.add_parser("bench")
    bench_p.add_argument("file")

    args = parser.parse_args(argv)
    achievements = load_achievements()

    if args.cmd == "repl":
        return repl()
    if args.cmd == "tutorial":
        print("Lesson 1: drink declares. Lesson 2: pour speaks. Lesson 3: thirsty decides.")
        achievements.add("tutorial_started")
        save_achievements(achievements)
        return 0
    if args.cmd == "doctor":
        for line in doctor(Path(args.project)):
            print(line)
        achievements.add("doctor_ran")
        save_achievements(achievements)
        return 0
    if args.cmd == "new":
        if args.kind != "fountain":
            print(color("parched: only 'fountain' scaffolding is implemented", "yellow"))
            return 1
        scaffold_fountain(Path("."), args.name)
        print(color(f"fully hydrated: scaffolded {args.name}", "green"))
        achievements.add("first_fountain")
        save_achievements(achievements)
        return 0
    if args.cmd == "install":
        result = install_package(Path(".").resolve(), args.package)
        print(color(f"fully hydrated: installed {result['name']}@{result['version']}", "green"))
        return 0
    if args.cmd == "publish":
        entry = publish_package(Path(args.project).resolve())
        print(color(f"fully hydrated: published {entry['name']}@{entry['version']}", "green"))
        return 0
    if args.cmd == "packages":
        for item in list_installed_packages(Path(".").resolve()):
            print(json.dumps(item, indent=2))
        return 0
    if args.cmd == "gallery":
        if args.action == "show":
            for line in show_package(args.term or ""):
                print(line)
        else:
            for line in gallery_lines(None if args.action == "list" else args.term):
                print(line)
        return 0

    text = Path(args.file).read_text(encoding="utf-8")
    try:
        if args.cmd == "check":
            check_source(text, args.file)
            print(color("fully hydrated", "green"))
            return 0
        if args.cmd == "fmt":
            out = thirsty_fmt(text)
            if args.write:
                Path(args.file).write_text(out, encoding="utf-8")
            else:
                print(out, end="")
            return 0
        if args.cmd == "ast":
            import dataclasses
            program = parse_source(text, args.file)
            def walk(node):
                if dataclasses.is_dataclass(node):
                    return {k: walk(v) for k, v in dataclasses.asdict(node).items()}
                if isinstance(node, list):
                    return [walk(x) for x in node]
                return node
            print(json.dumps(walk(program), indent=2))
            return 0
        if args.cmd == "promote":
            from shadow_thirst.core import parse_shadow, promote
            from tscg.core import canonical, parse as parse_tscg
            result = promote(parse_shadow(text, args.file))
            sym = "SHD -> INV -> COM" if result["decision"] == "PROMOTE" else "SHD -> RFX"
            result["tscg"] = canonical(parse_tscg(sym))
            print(json.dumps(result, indent=2))
            return 0
        if args.cmd == "bench":
            start = perf_counter()
            for _ in range(100):
                run_source(text, args.file)
            duration = perf_counter() - start
            print(json.dumps({"runs": 100, "seconds": duration}, indent=2))
            return 0
        out, interp = run_source(text, args.file, trace=args.trace, thirst_level=args.thirst_level, return_interpreter=True)
        for item in out:
            print(item)
        achievements.update(interp.achievements)
        if args.trace:
            achievements.add("trace_walker")
        save_achievements(achievements)
        return 0
    except DiagnosticBundle as bundle:
        print(format_bundle(bundle, text))
        return 1
    except (ThirstyError, RuntimeFault) as err:
        print(format_error(err, text))
        return 1
    except ThrownSignal as thrown:
        print(f"unhandled thrown value: {thrown.value!r}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
