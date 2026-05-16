"""
TARL LLVM Backend — compile LLVM IR to native machine code.

Takes LLVM IR text (from ThirstyFrontend) and produces:
  - Native object file (.o)
  - Native executable (via system linker)
  - LLVM bitcode (.bc)
  - Assembly listing (.s)

Requires: llvmlite 0.46.0+
"""

from __future__ import annotations

import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Literal

log = logging.getLogger("tarl.compiler.llvm_backend")

OptLevel = Literal[0, 1, 2, 3]


class LLVMBackendError(Exception):
    pass


class LLVMBackend:
    """
    LLVM backend: IR text → native object / executable / bitcode / assembly.

    Usage::

        backend = LLVMBackend(opt_level=2)
        ir_text = ThirstyFrontend().compile_source(source)

        # Compile to native object file
        backend.compile_to_object(ir_text, Path("out.o"))

        # Compile and link to executable
        backend.compile_to_executable(ir_text, Path("out"))

        # Emit LLVM bitcode
        backend.emit_bitcode(ir_text, Path("out.bc"))

        # Emit native assembly
        backend.emit_assembly(ir_text, Path("out.s"))
    """

    def __init__(self, opt_level: OptLevel = 2) -> None:
        self._opt_level = opt_level
        self._check_llvmlite()

    @staticmethod
    def _check_llvmlite() -> None:
        try:
            import llvmlite.binding as llvm  # noqa: F401
        except ImportError:
            raise LLVMBackendError(
                "llvmlite is required for LLVM compilation. "
                "Install with: pip install llvmlite"
            )

    def _get_engine(self) -> tuple:
        """Initialise LLVM and return (binding, target_machine)."""
        import llvmlite.binding as llvm

        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        target = llvm.Target.from_default_triple()
        cpu = llvm.get_host_cpu_name()
        features = llvm.get_host_cpu_features()
        tm = target.create_target_machine(
            cpu=cpu,
            features=features.flatten(),
            opt=self._opt_level,
            reloc="pic",
            codemodel="default",
        )
        return llvm, tm

    def _parse_ir(self, ir_text: str):
        import llvmlite.binding as llvm
        try:
            mod = llvm.parse_assembly(ir_text)
            mod.verify()
            return mod
        except Exception as exc:
            raise LLVMBackendError(f"LLVM IR parse/verify failed: {exc}") from exc

    def _optimise(self, mod):
        import llvmlite.binding as llvm
        if self._opt_level == 0:
            return
        pmb = llvm.create_pass_manager_builder()
        pmb.opt_level = self._opt_level
        pmb.inlining_threshold = 225 if self._opt_level >= 2 else 50
        pm = llvm.create_module_pass_manager()
        pmb.populate(pm)
        pm.run(mod)

    # ------------------------------------------------------------------
    # Public compilation methods
    # ------------------------------------------------------------------

    def compile_to_object(self, ir_text: str, output_path: Path) -> None:
        """
        Compile LLVM IR to a native object file (.o).

        The object file can be linked with system ``cc``/``ld`` to produce an executable.
        """
        llvm, tm = self._get_engine()
        mod = self._parse_ir(ir_text)
        self._optimise(mod)
        obj_bytes = tm.emit_object(mod)
        output_path.write_bytes(obj_bytes)
        log.info("LLVM backend: wrote object %s (%d bytes)", output_path, len(obj_bytes))

    def compile_to_executable(
        self,
        ir_text: str,
        output_path: Path,
        linker: str = "cc",
        extra_link_args: list[str] | None = None,
    ) -> None:
        """
        Compile LLVM IR to a native executable by:
          1. Emitting a temporary .o object file
          2. Invoking the system linker (``cc`` by default)

        Raises LLVMBackendError if the linker is not on PATH.
        """
        with tempfile.NamedTemporaryFile(suffix=".o", delete=False) as tf:
            obj_path = Path(tf.name)

        try:
            self.compile_to_object(ir_text, obj_path)
            link_cmd = [linker, str(obj_path), "-o", str(output_path)]
            if extra_link_args:
                link_cmd.extend(extra_link_args)
            result = subprocess.run(
                link_cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                raise LLVMBackendError(
                    f"Linker failed (exit {result.returncode}):\n{result.stderr}"
                )
            log.info("LLVM backend: linked executable %s", output_path)
        finally:
            try:
                obj_path.unlink()
            except OSError:
                pass

    def emit_bitcode(self, ir_text: str, output_path: Path) -> None:
        """Emit LLVM bitcode (.bc) — portable, inspectable with llvm-dis."""
        llvm, tm = self._get_engine()
        mod = self._parse_ir(ir_text)
        self._optimise(mod)
        bc = mod.as_bitcode()
        output_path.write_bytes(bc)
        log.info("LLVM backend: wrote bitcode %s (%d bytes)", output_path, len(bc))

    def emit_assembly(self, ir_text: str, output_path: Path) -> None:
        """Emit native assembly (.s) for the host target."""
        llvm, tm = self._get_engine()
        mod = self._parse_ir(ir_text)
        self._optimise(mod)
        asm = tm.emit_assembly(mod)
        output_path.write_text(asm, encoding="utf-8")
        log.info("LLVM backend: wrote assembly %s", output_path)

    def emit_ir(self, ir_text: str, output_path: Path) -> None:
        """
        Re-emit the LLVM IR after parsing + optimisation.
        Useful for inspecting what the optimiser did.
        """
        llvm, tm = self._get_engine()
        mod = self._parse_ir(ir_text)
        self._optimise(mod)
        output_path.write_text(str(mod), encoding="utf-8")
        log.info("LLVM backend: wrote optimised IR %s", output_path)

    def jit_run(self, ir_text: str, entry_fn: str = "main") -> int:
        """
        JIT-compile the module and call ``entry_fn``.

        Returns the integer return value of the entry function.
        Useful for testing without writing to disk.

        WARNING: executes native code in the current process — only
        use with trusted, verified IR.
        """
        import ctypes
        import llvmlite.binding as llvm

        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        mod = self._parse_ir(ir_text)
        self._optimise(mod)

        target = llvm.Target.from_default_triple()
        tm = target.create_target_machine(opt=self._opt_level)
        backing_mod = llvm.parse_assembly("")
        engine = llvm.create_mcjit_compiler(backing_mod, tm)
        engine.add_module(mod)
        engine.finalize_object()
        engine.run_static_constructors()

        fn_ptr = engine.get_function_address(entry_fn)
        if fn_ptr == 0:
            raise LLVMBackendError(f"Entry function '{entry_fn}' not found in JIT")

        cfn = ctypes.CFUNCTYPE(ctypes.c_int64)(fn_ptr)
        result = cfn()
        log.info("LLVM JIT: %s() returned %d", entry_fn, result)
        return int(result)
