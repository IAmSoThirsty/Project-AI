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
    publish_package,
    search_gallery,
    show_gallery_item,
)
from .formatter import Formatter
from .parser import Parser

_HIST = Path.home() / ".thirsty_history"
_ACH = Path.home() / ".thirsty_achievements.json"


def color(text: str, name: str) -> str:
    codes = {
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "blue": "\033[94m",
        "reset": "\033[0m",
    }
    return f"{codes.get(name, '')}{text}{codes['reset']}"


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


def run_source(
    source: str,
    file: str = "<memory>",
    input_values: list[str] | None = None,
    trace: bool = False,
    thirst_level: int = 1,
    return_interpreter: bool = False,
    governance_context: dict | None = None,
):
    idx = 0

    def input_provider() -> str:
        nonlocal idx
        if input_values is None or idx >= len(input_values):
            return ""
        val = input_values[idx]
        idx += 1
        return val

    program = check_source(source, file)
    project_root = (
        str(Path(file).resolve().parent)
        if file not in {"<memory>", "<repl>"}
        else str(Path(".").resolve())
    )
    interp = Interpreter(
        input_provider=input_provider,
        trace=trace,
        thirst_level=thirst_level,
        current_file=file,
        project_root=project_root,
    )
    if governance_context:
        interp.governance_context = dict(governance_context)
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
        from tarl.core import evaluate, load_context, parse_policy

        p = parse_policy((ex / "policy.tarl").read_text())
        _ = evaluate(p, load_context(str(ex / "context.json")))
        report.append(color("fully hydrated: TARL", "green"))
    except Exception as e:
        report.append(color(f"parched: TARL ({e})", "yellow"))
    try:
        from shadow_thirst.core import analyze, parse_shadow

        m = parse_shadow(
            (ex / "promote.shadowthirst").read_text(), str(ex / "promote.shadowthirst")
        )
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
        lines.append(
            f"- {item['name']}@{item['version']} :: {item.get('description', '')} [{tags}]"
        )
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
    (path / name / "README.md").write_text(
        f"# {name}\n\nA freshly poured Thirsty project.\n", encoding="utf-8"
    )


def emit_auto_tarl(program, module_name: str) -> str:
    """Generate a TARL policy file from GovernedFunctionDecl requires clauses.

    Each requires AuthorityClass.ACN annotation produces one policy block.
    Returns the full .auto.tarl text (may be empty string if no governed functions).
    """
    from . import ast as _ast

    blocks: list[str] = []
    for decl in program.declarations:
        if not isinstance(decl, _ast.GovernedFunctionDecl):
            continue
        fn_name = decl.name
        ac_clause = None
        has_audit = False
        for clause in decl.requires:
            ann = clause.annotation.strip()
            if ann.startswith("AuthorityClass."):
                ac_clause = ann.split(".", 1)[-1]
            elif ann == "AuditTrail.Immutable":
                has_audit = True
        if ac_clause:
            safe_name = f"{module_name}_{fn_name}_{ac_clause.lower()}"
            block = (
                f'policy allow_{safe_name} {{\n'
                f'  when ctx.authority_class >= "{ac_clause}" '
                f'and ctx.function == "{fn_name}" => ALLOW;\n'
                f'}}'
            )
            blocks.append(block)
        if has_audit:
            safe_name = f"{module_name}_{fn_name}_audit"
            block = (
                f'policy audit_{safe_name} {{\n'
                f'  when ctx.function == "{fn_name}" => ALLOW;\n'
                f'  when ctx.audit_trail != "immutable" => DENY;\n'
                f'}}'
            )
            blocks.append(block)
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def governance_report(program, source_file: str) -> list[str]:
    """Return a human-readable governance annotation report for a parsed program."""
    from . import ast as _ast

    lines: list[str] = []
    total = 0
    governed = 0
    for decl in program.declarations:
        if isinstance(decl, (_ast.FunctionDecl, _ast.GovernedFunctionDecl)):
            total += 1
            if isinstance(decl, _ast.GovernedFunctionDecl) and decl.requires:
                governed += 1
                lines.append(f"  ✓ glass {decl.name} — {len(decl.requires)} requires clause(s):")
                for c in decl.requires:
                    lines.append(f"      requires {c.annotation}")
            else:
                lines.append(f"  ○ glass {decl.name} — unannotated (mode core)")
    lines.insert(0, f"Governance report: {source_file}")
    lines.insert(1, f"  {governed}/{total} functions carry requires annotations")
    return lines


def scaffold_app(path: Path, name: str) -> None:
    (path / name).mkdir(parents=True, exist_ok=True)
    (path / name / "tests").mkdir(exist_ok=True)
    main_src = 'glass main() -> Int {\n  pour("hello from ' + name + '");\n  return 0;\n}\n'
    (path / name / "main.thirsty").write_text(main_src, encoding="utf-8")
    manifest = (
        f'[package]\nname = "{name}"\nversion = "0.1.0"\n'
        f'entry = "main.thirsty"\nmode = "core"\n\n'
        f"[dependencies]\n\n[governance]\naudit_level = \"none\"\n"
    )
    (path / name / "thirsty.toml").write_text(manifest, encoding="utf-8")


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
    run_p.add_argument(
        "--authority", default=None,
        help="authority class for governed mode (AC1–AC5)",
        choices=["AC1", "AC2", "AC3", "AC4", "AC5"],
    )

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

    add_p = sub.add_parser("add")
    add_p.add_argument("package")

    sub.add_parser("audit")

    sub.add_parser("lock")

    build_p = sub.add_parser("build")
    build_p.add_argument("file", nargs="?", default=None)
    build_p.add_argument("--emit-manifest", action="store_true")

    govern_p = sub.add_parser("govern")
    govern_p.add_argument("file")

    args = parser.parse_args(argv)
    achievements = load_achievements()

    if args.cmd == "repl":
        return repl()
    if args.cmd == "tutorial":
        print(
            "Lesson 1: drink declares. Lesson 2: pour speaks. Lesson 3: thirsty decides."
        )
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
        if args.kind == "fountain":
            scaffold_fountain(Path("."), args.name)
            achievements.add("first_fountain")
        elif args.kind == "app":
            scaffold_app(Path("."), args.name)
            achievements.add("first_app")
        else:
            print(color(f"parched: unknown scaffold kind '{args.kind}' (use: fountain, app)", "yellow"))
            return 1
        print(color(f"fully hydrated: scaffolded {args.kind} '{args.name}'", "green"))
        save_achievements(achievements)
        return 0
    if args.cmd == "install":
        result = install_package(Path(".").resolve(), args.package)
        print(
            color(
                f"fully hydrated: installed {result['name']}@{result['version']}",
                "green",
            )
        )
        return 0
    if args.cmd == "publish":
        entry = publish_package(Path(args.project).resolve())
        print(
            color(
                f"fully hydrated: published {entry['name']}@{entry['version']}", "green"
            )
        )
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

    if args.cmd == "add":
        result = install_package(Path(".").resolve(), args.package)
        print(color(f"fully hydrated: added {result['name']}@{result['version']}", "green"))
        return 0
    if args.cmd == "audit":
        from .package_manager import audit_dependencies
        findings = audit_dependencies(Path(".").resolve())
        if not findings:
            print(color("fully hydrated: no governance violations found", "green"))
        else:
            for f in findings:
                print(color(f"  {f}", "yellow"))
        return 0
    if args.cmd == "lock":
        from .package_manager import generate_lock
        generate_lock(Path(".").resolve())
        print(color("fully hydrated: thirsty.lock.json updated", "green"))
        return 0
    if args.cmd == "build":
        import hashlib as _hl
        import datetime as _dt
        target_file = args.file or "main.thirsty"
        text = Path(target_file).read_text(encoding="utf-8")
        tokens = Lexer(text).tokenize()
        program = Parser(tokens).parse()
        check_source(text, target_file)
        dist = Path("dist")
        dist.mkdir(exist_ok=True)
        if args.emit_manifest:
            prog_hash = "sha256:" + _hl.sha256(text.encode("utf-8")).hexdigest()
            module_name = (program.header.name if program.header else Path(target_file).stem)
            exec_mode = (program.header.mode if program.header else "core")
            # Emit auto.tarl and hash it
            tarl_text = emit_auto_tarl(program, module_name)
            policy_hash = "sha256:" + _hl.sha256(tarl_text.encode("utf-8")).hexdigest()
            if tarl_text:
                tarl_path = dist / f"{module_name}.auto.tarl"
                tarl_path.write_text(tarl_text, encoding="utf-8")
            # Collect capability manifest from requires clauses
            capabilities: list[str] = []
            from . import ast as _ast
            for decl in program.declarations:
                if isinstance(decl, _ast.GovernedFunctionDecl):
                    for clause in decl.requires:
                        cap = clause.annotation.strip()
                        if cap not in capabilities:
                            capabilities.append(cap)
            manifest = {
                "program_hash": prog_hash,
                "source_file": target_file,
                "module": module_name,
                "execution_mode": exec_mode,
                "dependency_hashes": {},
                "policy_hash": policy_hash,
                "capability_manifest": capabilities,
                "governance_proof": {
                    "tscg_expression": "COG -> SHD -> INV -> COM",
                    "build_time": _dt.datetime.utcnow().isoformat() + "Z",
                    "iron_path_run_id": __import__("uuid").uuid4().hex,
                },
            }
            (dist / "app.manifest.json").write_text(
                json.dumps(manifest, indent=2), encoding="utf-8"
            )
            print(color("fully hydrated: dist/app.manifest.json written", "green"))
            if capabilities:
                print(color(f"  capabilities: {', '.join(capabilities)}", "blue"))
        else:
            print(color(f"fully hydrated: {target_file} checked and ready", "green"))
        return 0
    if args.cmd == "govern":
        text = Path(args.file).read_text(encoding="utf-8")
        try:
            tokens = Lexer(text).tokenize()
            program = Parser(tokens).parse()
            check_source(text, args.file)
        except (ThirstyError, DiagnosticBundle) as err:
            print(format_error(err, text) if isinstance(err, ThirstyError) else format_bundle(err, text))
            return 1
        for line in governance_report(program, args.file):
            print(line)
        # Optionally emit the auto.tarl file
        module_name = (program.header.name if program.header else Path(args.file).stem)
        tarl_text = emit_auto_tarl(program, module_name)
        if tarl_text:
            dist = Path("dist")
            dist.mkdir(exist_ok=True)
            tarl_path = dist / f"{module_name}.auto.tarl"
            tarl_path.write_text(tarl_text, encoding="utf-8")
            print(color(f"fully hydrated: {tarl_path} emitted", "green"))
        else:
            print(color("no requires clauses found — no TARL policy generated", "yellow"))
        return 0

    text = Path(args.file).read_text(encoding="utf-8")
    try:
        if args.cmd == "check":
            check_source(text, args.file)
            print(color("fully hydrated", "green"))
            return 0
        if args.cmd == "fmt":
            tokens = Lexer(text).tokenize()
            tree = Parser(tokens).parse()
            out = Formatter().format(tree)
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
            from tscg.core import canonical
            from tscg.core import parse as parse_tscg

            result = promote(parse_shadow(text, args.file))
            sym = (
                "SHD -> INV -> COM" if result["decision"] == "PROMOTE" else "SHD -> RFX"
            )
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
        gov_ctx = {}
        if hasattr(args, "authority") and args.authority:
            gov_ctx["authority_class"] = args.authority
        out, interp = run_source(
            text,
            args.file,
            trace=args.trace,
            thirst_level=args.thirst_level,
            return_interpreter=True,
            governance_context=gov_ctx,
        )
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
