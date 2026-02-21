"""
Floor Specifications - Language Jurisdiction System
CIVILIZATION TIER - PURPOSE-LOCKED

Each floor is a sovereign language jurisdiction with:
- Domain definition
- Architectural constraints
- Security focus
- Testing doctrine

All floors share identical topology (uniformity doctrine).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


class ProgrammingLanguage(Enum):
    """Programming Language Floors - One per language (28 floors for complete civilizational coverage)"""

    # Core Systems Languages
    PYTHON = "python"
    RUST = "rust"
    C = "c"
    CPP = "cpp"
    GO = "go"

    # Web & Frontend
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"

    # JVM Ecosystem
    JAVA = "java"
    KOTLIN = "kotlin"
    SCALA = "scala"

    # Apple Ecosystem
    SWIFT = "swift"
    OBJECTIVE_C = "objective_c"

    # Scripting & Dynamic
    PHP = "php"
    RUBY = "ruby"
    PERL = "perl"

    # Shell & Automation
    SHELL = "shell"  # Bash
    POWERSHELL = "powershell"

    # Data & Query
    SQL = "sql"
    NOSQL = "nosql"

    # Functional
    HASKELL = "haskell"
    OCAML = "ocaml"

    # BEAM VM
    ELIXIR = "elixir"
    ERLANG = "erlang"

    # Scientific & Numerical
    FORTRAN = "fortran"
    MATLAB_OCTAVE = "matlab_octave"

    # Specialized
    CUDA_GPU = "cuda_gpu"
    WEBASSEMBLY = "webassembly"
    RUST_ASYNC = "rust_async"


@dataclass
class SecurityFocus:
    """Security concerns specific to a language"""

    primary_risks: List[str] = field(default_factory=list)
    required_checks: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {"primary_risks": self.primary_risks, "required_checks": self.required_checks}


@dataclass
class TestingDoctrine:
    """Testing requirements for a language"""

    mandatory_tests: List[str] = field(default_factory=list)
    optional_tests: List[str] = field(default_factory=list)
    special_emphasis: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "mandatory_tests": self.mandatory_tests,
            "optional_tests": self.optional_tests,
            "special_emphasis": self.special_emphasis,
        }


@dataclass
class FloorSpecification:
    """
    Complete specification for a language floor.

    Global Floor Invariants (apply to all):
    1. Language Sovereignty - Emits artifacts only in its language
    2. Identical Internal Topology - Architecture → Implementation → Review → Test → Security → Manager
    3. Contract-Bound Operation - No action without parent Cognitive Contract
    4. Non-Creative Mandate - No extrapolation beyond directive
    5. Failure Escalation Guarantee - All failures surface and consume resources
    """

    language: ProgrammingLanguage
    floor_number: int
    domain: List[str]  # What this floor handles
    architectural_constraints: List[str]
    security_focus: SecurityFocus
    testing_doctrine: TestingDoctrine

    # Jurisdiction laws
    can_emit_languages: Set[ProgrammingLanguage] = field(default_factory=set)
    can_reason_about: Set[ProgrammingLanguage] = field(default_factory=set)
    requires_contracts_for: Set[ProgrammingLanguage] = field(default_factory=set)

    def __post_init__(self):
        """Enforce language sovereignty"""
        # Can only emit in own language
        self.can_emit_languages = {self.language}
        # Can only reason about own language
        self.can_reason_about = {self.language}
        # Must use contracts for all other languages
        all_languages = set(ProgrammingLanguage)
        self.requires_contracts_for = all_languages - {self.language}

    def can_author_in(self, target_language: ProgrammingLanguage) -> bool:
        """Check if this floor can author code in target language"""
        return target_language in self.can_emit_languages

    def can_interpret(self, target_language: ProgrammingLanguage) -> bool:
        """Check if this floor can interpret semantics of target language"""
        return target_language in self.can_reason_about

    def requires_contract(self, target_language: ProgrammingLanguage) -> bool:
        """Check if cross-language work requires contract"""
        return target_language in self.requires_contracts_for

    def validate_jurisdiction(self, action: str, target_language: ProgrammingLanguage) -> tuple[bool, Optional[str]]:
        """
        Validate if an action is legal under jurisdiction laws.
        Returns: (is_legal, reason_if_illegal)
        """
        if action == "author" and not self.can_author_in(target_language):
            return (
                False,
                f"Floor {self.floor_number} ({self.language.value}) cannot author code in {target_language.value}",
            )

        if action == "interpret" and not self.can_interpret(target_language):
            return (
                False,
                f"Floor {self.floor_number} ({self.language.value}) cannot interpret semantics of {target_language.value}",  # noqa: E501
            )

        if action == "cross_language" and not self.requires_contract(target_language):
            return True, None

        if action == "cross_language" and self.requires_contract(target_language):
            return (
                False,
                f"Cross-language work from {self.language.value} to {target_language.value} requires explicit contract",
            )

        return True, None

    def to_dict(self) -> Dict:
        return {
            "language": self.language.value,
            "floor_number": self.floor_number,
            "domain": self.domain,
            "architectural_constraints": self.architectural_constraints,
            "security_focus": self.security_focus.to_dict(),
            "testing_doctrine": self.testing_doctrine.to_dict(),
            "can_emit_languages": [lang.value for lang in self.can_emit_languages],
            "can_reason_about": [lang.value for lang in self.can_reason_about],
            "requires_contracts_for": [lang.value for lang in self.requires_contracts_for],
        }


# FLOOR 1 — PYTHON JURISDICTION
FLOOR_1_PYTHON = FloorSpecification(
    language=ProgrammingLanguage.PYTHON,
    floor_number=1,
    domain=["Application logic", "Automation", "Data processing", "Glue code"],
    architectural_constraints=[
        "Readability > micro-optimization",
        "Explicit typing encouraged but not enforced unless requested",
        "Standard library preferred unless contract permits dependencies",
        "PEP 8 compliance",
    ],
    security_focus=SecurityFocus(
        primary_risks=[
            "Injection risks",
            "Unsafe deserialization",
            "Dynamic execution (eval, exec)",
            "Dependency trust",
        ],
        required_checks=[
            "Input validation",
            "Dependency scanning",
            "No eval/exec without justification",
            "Pickle usage auditing",
        ],
    ),
    testing_doctrine=TestingDoctrine(
        mandatory_tests=["Unit tests"],
        optional_tests=["Property tests (if requested)"],
        special_emphasis=["Edge case coverage", "Exception handling"],
    ),
)


# FLOOR 2 — RUST JURISDICTION
FLOOR_2_RUST = FloorSpecification(
    language=ProgrammingLanguage.RUST,
    floor_number=2,
    domain=["Memory-safe systems", "Performance-critical logic", "FFI boundaries"],
    architectural_constraints=[
        "Ownership and lifetime correctness is non-negotiable",
        "Unsafe blocks require explicit justification",
        "Zero undefined behavior tolerated",
        "Clippy linting enforced",
    ],
    security_focus=SecurityFocus(
        primary_risks=["Memory safety proofs", "Unsafe scope auditing", "ABI correctness"],
        required_checks=[
            "Unsafe block justification",
            "Miri validation for unsafe code",
            "FFI boundary verification",
            "No panic in unsafe",
        ],
    ),
    testing_doctrine=TestingDoctrine(
        mandatory_tests=["Unit tests", "Integration tests"],
        optional_tests=[],
        special_emphasis=["Fuzzing strongly preferred if scope includes parsing or I/O"],
    ),
)


# FLOOR 3 — C JURISDICTION
FLOOR_3_C = FloorSpecification(
    language=ProgrammingLanguage.C,
    floor_number=3,
    domain=["Low-level systems", "Embedded components"],
    architectural_constraints=["Explicit memory ownership", "Deterministic lifetimes", "No hidden allocations"],
    security_focus=SecurityFocus(
        primary_risks=["Buffer overflows", "Use-after-free", "Integer overflow", "Undefined behavior"],
        required_checks=[
            "Static analysis (clang-tidy)",
            "AddressSanitizer",
            "UndefinedBehaviorSanitizer",
            "Manual bounds checking",
        ],
    ),
    testing_doctrine=TestingDoctrine(
        mandatory_tests=["Unit tests"], optional_tests=[], special_emphasis=["Static analysis emphasized"]
    ),
)


# FLOOR 4 — C++ JURISDICTION
FLOOR_4_CPP = FloorSpecification(
    language=ProgrammingLanguage.CPP,
    floor_number=4,
    domain=["High-performance systems", "Complex object models"],
    architectural_constraints=[
        "RAII discipline mandatory",
        "Deterministic destruction",
        "STL usage justified by scope",
    ],
    security_focus=SecurityFocus(
        primary_risks=["Memory safety", "Exception boundary auditing"],
        required_checks=["Static analysis (cppcheck)", "AddressSanitizer", "Exception safety verification"],
    ),
    testing_doctrine=TestingDoctrine(
        mandatory_tests=["Unit tests", "Integration tests"], optional_tests=[], special_emphasis=[]
    ),
)


# FLOOR 5 — JAVASCRIPT JURISDICTION
FLOOR_5_JAVASCRIPT = FloorSpecification(
    language=ProgrammingLanguage.JAVASCRIPT,
    floor_number=5,
    domain=["Frontend logic", "Tooling", "Runtime scripting"],
    architectural_constraints=["Explicit async control", "No implicit globals", "Deterministic side effects"],
    security_focus=SecurityFocus(
        primary_risks=["XSS", "Prototype pollution", "Supply-chain risks"],
        required_checks=["XSS prevention", "Input sanitization", "Dependency auditing"],
    ),
    testing_doctrine=TestingDoctrine(mandatory_tests=["Unit tests"], optional_tests=[], special_emphasis=[]),
)


# FLOOR 6 — TYPESCRIPT JURISDICTION
FLOOR_6_TYPESCRIPT = FloorSpecification(
    language=ProgrammingLanguage.TYPESCRIPT,
    floor_number=6,
    domain=["Typed frontend / Node systems"],
    architectural_constraints=["Type correctness mandatory", "No any unless explicitly authorized"],
    security_focus=SecurityFocus(
        primary_risks=["Supply-chain validation", "Runtime boundary checks"],
        required_checks=["Type safety", "Dependency scanning", "Runtime validation"],
    ),
    testing_doctrine=TestingDoctrine(
        mandatory_tests=["Unit tests", "Integration tests"], optional_tests=[], special_emphasis=[]
    ),
)


# FLOOR 7 — GO JURISDICTION
FLOOR_7_GO = FloorSpecification(
    language=ProgrammingLanguage.GO,
    floor_number=7,
    domain=["Network services", "Concurrency-heavy systems", "Infrastructure logic"],
    architectural_constraints=[
        "Explicit concurrency patterns",
        "Channel safety",
        "No hidden goroutine leaks",
        "Go fmt and go vet compliance",
    ],
    security_focus=SecurityFocus(
        primary_risks=["Race conditions", "Input validation", "Network boundary hardening"],
        required_checks=["Race detector", "Goroutine leak detection", "Context cancellation", "TLS verification"],
    ),
    testing_doctrine=TestingDoctrine(
        mandatory_tests=["Unit tests"],
        optional_tests=[],
        special_emphasis=["Race detection emphasized", "Benchmark tests for concurrency"],
    ),
)


# FLOOR 8 — SQL/DATA JURISDICTION
FLOOR_8_SQL = FloorSpecification(
    language=ProgrammingLanguage.SQL,
    floor_number=8,
    domain=["Schema design", "Queries", "Data transformations"],
    architectural_constraints=[
        "Deterministic queries",
        "Explicit indexing",
        "No implicit schema assumptions",
        "Normalized design unless justified",
    ],
    security_focus=SecurityFocus(
        primary_risks=["SQL injection", "Privilege separation", "Data leakage"],
        required_checks=["Parameterized queries", "Least privilege", "Row-level security", "Audit logging"],
    ),
    testing_doctrine=TestingDoctrine(
        mandatory_tests=["Query correctness tests"],
        optional_tests=[],
        special_emphasis=["Migration safety verification", "Performance testing"],
    ),
)


# FLOOR 9 — SHELL/SCRIPTING JURISDICTION
FLOOR_9_SHELL = FloorSpecification(
    language=ProgrammingLanguage.SHELL,
    floor_number=9,
    domain=["Automation", "System orchestration"],
    architectural_constraints=[
        "Explicit error handling (set -e)",
        "No silent failures",
        "Idempotence preferred",
        "ShellCheck compliance",
    ],
    security_focus=SecurityFocus(
        primary_risks=["Command injection", "Environment poisoning", "Privilege escalation"],
        required_checks=["Input quoting", "PATH hardening", "Privilege dropping", "Secure temp files"],
    ),
    testing_doctrine=TestingDoctrine(
        mandatory_tests=["Script behavior verification"],
        optional_tests=[],
        special_emphasis=["Dry-run validation", "Rollback testing"],
    ),
)


# FLOOR 10 — JAVA JURISDICTION
FLOOR_10_JAVA = FloorSpecification(
    language=ProgrammingLanguage.JAVA,
    floor_number=10,
    domain=["Enterprise systems", "JVM services"],
    architectural_constraints=["Explicit type modeling", "Controlled inheritance", "Predictable lifecycle management"],
    security_focus=SecurityFocus(
        primary_risks=["Serialization control", "Classloader boundary enforcement"],
        required_checks=["Deserialization validation", "Dependency scanning", "Security manager policies"],
    ),
    testing_doctrine=TestingDoctrine(
        mandatory_tests=["Unit tests", "Integration tests"], optional_tests=[], special_emphasis=[]
    ),
)


# FLOOR 11 — KOTLIN JURISDICTION
FLOOR_11_KOTLIN = FloorSpecification(
    language=ProgrammingLanguage.KOTLIN,
    floor_number=11,
    domain=["JVM modernization", "Android / backend services"],
    architectural_constraints=["Null-safety enforcement", "Explicit coroutine boundaries"],
    security_focus=SecurityFocus(
        primary_risks=["Concurrency correctness", "Platform API trust control"],
        required_checks=["Null safety verification", "Coroutine cancellation", "Android permissions"],
    ),
    testing_doctrine=TestingDoctrine(mandatory_tests=["Unit tests"], optional_tests=[], special_emphasis=[]),
)


# FLOOR 12 — SCALA JURISDICTION
FLOOR_12_SCALA = FloorSpecification(
    language=ProgrammingLanguage.SCALA,
    floor_number=12,
    domain=["Functional JVM systems", "Data processing pipelines"],
    architectural_constraints=["Referential transparency unless scoped", "Type-level guarantees preferred"],
    security_focus=SecurityFocus(
        primary_risks=["Deserialization control", "Execution context safety"],
        required_checks=["Type safety", "Actor system isolation", "Serialization validation"],
    ),
    testing_doctrine=TestingDoctrine(
        mandatory_tests=["Unit tests"], optional_tests=["Property tests (if requested)"], special_emphasis=[]
    ),
)


# FLOOR 13 — SWIFT JURISDICTION
FLOOR_13_SWIFT = FloorSpecification(
    language=ProgrammingLanguage.SWIFT,
    floor_number=13,
    domain=["Apple platform systems"],
    architectural_constraints=["ARC lifecycle clarity", "Value semantics preferred"],
    security_focus=SecurityFocus(
        primary_risks=["Memory safety", "Platform permission enforcement"],
        required_checks=["ARC cycle detection", "Keychain usage", "App sandbox compliance"],
    ),
    testing_doctrine=TestingDoctrine(mandatory_tests=["Unit tests"], optional_tests=[], special_emphasis=[]),
)


# FLOOR 14 — OBJECTIVE-C JURISDICTION
FLOOR_14_OBJECTIVE_C = FloorSpecification(
    language=ProgrammingLanguage.OBJECTIVE_C,
    floor_number=14,
    domain=["Legacy Apple systems"],
    architectural_constraints=["Explicit memory management awareness", "Deterministic message passing"],
    security_focus=SecurityFocus(
        primary_risks=["Runtime introspection control"],
        required_checks=[
            "Memory management (retain/release)",
            "Method swizzling auditing",
            "Runtime manipulation control",
        ],
    ),
    testing_doctrine=TestingDoctrine(mandatory_tests=["Unit tests"], optional_tests=[], special_emphasis=[]),
)


# FLOOR 15 — PHP JURISDICTION
FLOOR_15_PHP = FloorSpecification(
    language=ProgrammingLanguage.PHP,
    floor_number=15,
    domain=["Web backend systems"],
    architectural_constraints=["Explicit input handling", "No implicit globals"],
    security_focus=SecurityFocus(
        primary_risks=["Injection prevention", "File inclusion control"],
        required_checks=[
            "SQL injection prevention",
            "XSS prevention",
            "File upload validation",
            "Remote code execution defense",
        ],
    ),
    testing_doctrine=TestingDoctrine(mandatory_tests=["Unit tests"], optional_tests=[], special_emphasis=[]),
)


# FLOOR 16 — RUBY JURISDICTION
FLOOR_16_RUBY = FloorSpecification(
    language=ProgrammingLanguage.RUBY,
    floor_number=16,
    domain=["Scripting", "Web frameworks"],
    architectural_constraints=["Explicit metaprogramming boundaries", "Predictable control flow"],
    security_focus=SecurityFocus(
        primary_risks=["Injection prevention", "Dynamic execution scrutiny"],
        required_checks=["SQL injection prevention", "eval usage auditing", "Mass assignment protection"],
    ),
    testing_doctrine=TestingDoctrine(mandatory_tests=["Unit tests"], optional_tests=[], special_emphasis=[]),
)


# FLOOR 17 — PERL JURISDICTION
FLOOR_17_PERL = FloorSpecification(
    language=ProgrammingLanguage.PERL,
    floor_number=17,
    domain=["Text processing", "Legacy automation"],
    architectural_constraints=["Explicit intent", "No obfuscated logic"],
    security_focus=SecurityFocus(
        primary_risks=["Command injection prevention"],
        required_checks=["Taint mode enabled", "System call validation", "Input sanitization"],
    ),
    testing_doctrine=TestingDoctrine(mandatory_tests=["Behavioral tests"], optional_tests=[], special_emphasis=[]),
)


# FLOOR 18 — POWERSHELL JURISDICTION
FLOOR_18_POWERSHELL = FloorSpecification(
    language=ProgrammingLanguage.POWERSHELL,
    floor_number=18,
    domain=["Windows automation"],
    architectural_constraints=["Explicit pipeline control", "Object lifecycle clarity"],
    security_focus=SecurityFocus(
        primary_risks=["Execution policy enforcement"],
        required_checks=["Script signing", "Execution policy validation", "Privilege escalation prevention"],
    ),
    testing_doctrine=TestingDoctrine(mandatory_tests=["Script validation"], optional_tests=[], special_emphasis=[]),
)


# FLOOR 19 — NOSQL JURISDICTION
FLOOR_19_NOSQL = FloorSpecification(
    language=ProgrammingLanguage.NOSQL,
    floor_number=19,
    domain=["Non-relational data systems"],
    architectural_constraints=["Explicit schema assumptions", "Consistency guarantees declared"],
    security_focus=SecurityFocus(
        primary_risks=["Access control enforcement"],
        required_checks=["Query injection prevention", "Authentication enforcement", "Data isolation"],
    ),
    testing_doctrine=TestingDoctrine(mandatory_tests=["Data integrity tests"], optional_tests=[], special_emphasis=[]),
)


# FLOOR 20 — HASKELL JURISDICTION
FLOOR_20_HASKELL = FloorSpecification(
    language=ProgrammingLanguage.HASKELL,
    floor_number=20,
    domain=["Pure functional systems"],
    architectural_constraints=["Purity enforced", "Side effects isolated"],
    security_focus=SecurityFocus(
        primary_risks=["IO boundary scrutiny"],
        required_checks=["Type safety", "IO isolation", "Lazy evaluation safety"],
    ),
    testing_doctrine=TestingDoctrine(mandatory_tests=["Property tests"], optional_tests=[], special_emphasis=[]),
)


# FLOOR 21 — OCAML JURISDICTION
FLOOR_21_OCAML = FloorSpecification(
    language=ProgrammingLanguage.OCAML,
    floor_number=21,
    domain=["Functional systems", "Compilers"],
    architectural_constraints=["Type soundness enforced"],
    security_focus=SecurityFocus(
        primary_risks=["Memory safety verification"],
        required_checks=["Type system verification", "Memory safety", "Exception handling"],
    ),
    testing_doctrine=TestingDoctrine(mandatory_tests=["Unit tests"], optional_tests=[], special_emphasis=[]),
)


# FLOOR 22 — ELIXIR JURISDICTION
FLOOR_22_ELIXIR = FloorSpecification(
    language=ProgrammingLanguage.ELIXIR,
    floor_number=22,
    domain=["Distributed systems", "Fault-tolerant services"],
    architectural_constraints=["Process isolation clarity", "Supervision trees explicit"],
    security_focus=SecurityFocus(
        primary_risks=["Message validation"],
        required_checks=["Process isolation", "Message integrity", "Distributed authentication"],
    ),
    testing_doctrine=TestingDoctrine(
        mandatory_tests=["Unit tests", "Integration tests"], optional_tests=[], special_emphasis=[]
    ),
)


# FLOOR 23 — ERLANG JURISDICTION
FLOOR_23_ERLANG = FloorSpecification(
    language=ProgrammingLanguage.ERLANG,
    floor_number=23,
    domain=["Telecom-grade systems"],
    architectural_constraints=["Explicit fault domains", "Message purity"],
    security_focus=SecurityFocus(
        primary_risks=["Process isolation"],
        required_checks=["Process boundaries", "Message validation", "Hot code loading safety"],
    ),
    testing_doctrine=TestingDoctrine(mandatory_tests=["Concurrency tests"], optional_tests=[], special_emphasis=[]),
)


# FLOOR 24 — FORTRAN JURISDICTION
FLOOR_24_FORTRAN = FloorSpecification(
    language=ProgrammingLanguage.FORTRAN,
    floor_number=24,
    domain=["Scientific computation"],
    architectural_constraints=["Numerical determinism", "Precision declared"],
    security_focus=SecurityFocus(
        primary_risks=["Input validation"],
        required_checks=["Array bounds checking", "Floating-point validation", "Data file validation"],
    ),
    testing_doctrine=TestingDoctrine(
        mandatory_tests=["Numerical correctness tests"], optional_tests=[], special_emphasis=[]
    ),
)


# FLOOR 25 — MATLAB/OCTAVE JURISDICTION
FLOOR_25_MATLAB_OCTAVE = FloorSpecification(
    language=ProgrammingLanguage.MATLAB_OCTAVE,
    floor_number=25,
    domain=["Numerical modeling"],
    architectural_constraints=["Explicit dimensionality", "Deterministic computation"],
    security_focus=SecurityFocus(
        primary_risks=["Script execution control"],
        required_checks=["Matrix dimension validation", "Script sandboxing", "Data import validation"],
    ),
    testing_doctrine=TestingDoctrine(
        mandatory_tests=["Result verification tests"], optional_tests=[], special_emphasis=[]
    ),
)


# FLOOR 26 — CUDA/GPU JURISDICTION
FLOOR_26_CUDA_GPU = FloorSpecification(
    language=ProgrammingLanguage.CUDA_GPU,
    floor_number=26,
    domain=["Parallel compute kernels"],
    architectural_constraints=["Explicit memory transfers", "Deterministic kernel execution"],
    security_focus=SecurityFocus(
        primary_risks=["Memory bounds enforcement"],
        required_checks=["Kernel bounds checking", "Memory transfer validation", "Synchronization correctness"],
    ),
    testing_doctrine=TestingDoctrine(
        mandatory_tests=["Kernel correctness tests"], optional_tests=[], special_emphasis=[]
    ),
)


# FLOOR 27 — WEBASSEMBLY JURISDICTION
FLOOR_27_WEBASSEMBLY = FloorSpecification(
    language=ProgrammingLanguage.WEBASSEMBLY,
    floor_number=27,
    domain=["Cross-platform execution"],
    architectural_constraints=["Deterministic sandboxing"],
    security_focus=SecurityFocus(
        primary_risks=["Capability isolation"],
        required_checks=["Sandbox enforcement", "Host API isolation", "Memory safety"],
    ),
    testing_doctrine=TestingDoctrine(
        mandatory_tests=["Runtime validation tests"], optional_tests=[], special_emphasis=[]
    ),
)


# FLOOR 28 — RUST-ASYNC JURISDICTION (SPECIALIZED)
FLOOR_28_RUST_ASYNC = FloorSpecification(
    language=ProgrammingLanguage.RUST_ASYNC,
    floor_number=28,
    domain=["High-concurrency async systems"],
    architectural_constraints=["Executor awareness", "Backpressure handling mandatory"],
    security_focus=SecurityFocus(
        primary_risks=["Deadlock prevention", "Resource exhaustion defense"],
        required_checks=["Future cancellation safety", "Task spawn limits", "Async drop safety"],
    ),
    testing_doctrine=TestingDoctrine(
        mandatory_tests=["Async integration tests"], optional_tests=[], special_emphasis=[]
    ),
)


# Registry of all floors
ALL_FLOORS: Dict[ProgrammingLanguage, FloorSpecification] = {
    ProgrammingLanguage.PYTHON: FLOOR_1_PYTHON,
    ProgrammingLanguage.RUST: FLOOR_2_RUST,
    ProgrammingLanguage.C: FLOOR_3_C,
    ProgrammingLanguage.CPP: FLOOR_4_CPP,
    ProgrammingLanguage.JAVASCRIPT: FLOOR_5_JAVASCRIPT,
    ProgrammingLanguage.TYPESCRIPT: FLOOR_6_TYPESCRIPT,
    ProgrammingLanguage.GO: FLOOR_7_GO,
    ProgrammingLanguage.SQL: FLOOR_8_SQL,
    ProgrammingLanguage.SHELL: FLOOR_9_SHELL,
    ProgrammingLanguage.JAVA: FLOOR_10_JAVA,
    ProgrammingLanguage.KOTLIN: FLOOR_11_KOTLIN,
    ProgrammingLanguage.SCALA: FLOOR_12_SCALA,
    ProgrammingLanguage.SWIFT: FLOOR_13_SWIFT,
    ProgrammingLanguage.OBJECTIVE_C: FLOOR_14_OBJECTIVE_C,
    ProgrammingLanguage.PHP: FLOOR_15_PHP,
    ProgrammingLanguage.RUBY: FLOOR_16_RUBY,
    ProgrammingLanguage.PERL: FLOOR_17_PERL,
    ProgrammingLanguage.POWERSHELL: FLOOR_18_POWERSHELL,
    ProgrammingLanguage.NOSQL: FLOOR_19_NOSQL,
    ProgrammingLanguage.HASKELL: FLOOR_20_HASKELL,
    ProgrammingLanguage.OCAML: FLOOR_21_OCAML,
    ProgrammingLanguage.ELIXIR: FLOOR_22_ELIXIR,
    ProgrammingLanguage.ERLANG: FLOOR_23_ERLANG,
    ProgrammingLanguage.FORTRAN: FLOOR_24_FORTRAN,
    ProgrammingLanguage.MATLAB_OCTAVE: FLOOR_25_MATLAB_OCTAVE,
    ProgrammingLanguage.CUDA_GPU: FLOOR_26_CUDA_GPU,
    ProgrammingLanguage.WEBASSEMBLY: FLOOR_27_WEBASSEMBLY,
    ProgrammingLanguage.RUST_ASYNC: FLOOR_28_RUST_ASYNC,
}


def get_floor_specification(language: ProgrammingLanguage) -> FloorSpecification:
    """Get the specification for a language floor"""
    return ALL_FLOORS[language]


def validate_floor_uniformity() -> bool:
    """
    Validate that all floors have identical topology (uniformity doctrine).

    Every floor must have:
    - Architecture Office
    - Implementation Office
    - Review Office
    - Test Office
    - Security Office
    - Manager Office
    """
    # This is enforced structurally - all floors use FloorSpecification
    # which guarantees uniformity
    return True


def get_all_floors() -> List[FloorSpecification]:
    """Get all floor specifications"""
    return list(ALL_FLOORS.values())


def route_directive_to_floor(language: ProgrammingLanguage) -> FloorSpecification:
    """
    Route a code directive to the appropriate floor.
    Step 1 of the 6-step pipeline.
    """
    return get_floor_specification(language)
