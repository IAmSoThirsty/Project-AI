"""
TARL Compiler — compile Thirsty-Lang programs to native code via LLVM IR.

Entry points:
    from tarl.compiler.frontend import ThirstyFrontend
    from tarl.compiler.llvm_backend import LLVMBackend

    ir = ThirstyFrontend().compile_source(source)
    LLVMBackend().compile_to_object(ir, output_path)
"""

from .frontend import ThirstyFrontend
from .llvm_backend import LLVMBackend, LLVMBackendError

__all__ = ["ThirstyFrontend", "LLVMBackend", "LLVMBackendError"]
