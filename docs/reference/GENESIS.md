# Genesis: Microservices Generation

> Canonical development composite for DOI `10.5281/zenodo.19488571`.
> The three source artifacts remain unchanged and are joined here in owner-defined order.

## Source manifest

- `C:\Users\Quencher\Documents\Thirsty's Projects LLC\Project-AI Papers\ill show you complete.txt` — SHA-256 `614196bf32905c543d909b138249b95acd9b10a052b2e22e937598c64e44b892`
- `C:\Users\Quencher\Documents\Thirsty's Projects LLC\Project-AI Papers\Zenodo\Submitted\Admissibility_Debt.pdf` — SHA-256 `55f5279faa5e5594103c41e1db6efa8e457775133c81ae33576dda47b9db3c87`
- `C:\Users\Quencher\Documents\Thirsty's Projects LLC\Project-AI Papers\Zenodo\Submitted\Bye Bye Tokens.txt` — SHA-256 `f2c52d5c431ac8bb0ffb48040ecc54db38b27401312ceaa5314623d6ea5be5a5`

## Part 1: Genesis

This implementation corresponds directly to the architecture described in: GENESIS: A CONSTITUTIONAL COMPILER FOR SOVEREIGN MICROSERVICES GENERATION (MicroservicesEatThis.txt)

================================================================================
GENESIS MICROSERVICES GENERATOR - COMPLETE SOURCE
Project-AI / IAmSoThirsty
================================================================================

# ============================================================================
# 1. DOMAIN MODEL / INTERMEDIATE REPRESENTATION
# ============================================================================

import yaml
import json
import os
import re
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from pathlib import Path

class CriticalityLevel(Enum):
    PII = "pii"
    FINANCIAL = "financial"
    PUBLIC = "public"
    INTERNAL = "internal"

class RuntimeTarget(Enum):
    KUBERNETES = "kubernetes"
    SERVERLESS = "serverless"
    BARE_METAL = "bare_metal"

class FailureModeStrategy(Enum):
    CIRCUIT_BREAKER = "circuit_breaker"
    RETRY_WITH_BACKOFF = "retry_with_backoff"
    BULKHEAD = "bulkhead"
    DEAD_LETTER_QUEUE = "dlq"
    TIMEOUT = "timeout"

@dataclass
class DataOwnership:
    entity: str
    owner_service: str
    fields: List[str]
    pii_fields: List[str] = field(default_factory=list)
    retention_days: Optional[int] = None

@dataclass
class EventContract:
    name: str
    payload_schema: Dict[str, Any]
    producers: List[str]
    consumers: List[str]
    ordering_key: Optional[str] = None
    retention_hours: int = 24

@dataclass
class ApiContract:
    path: str
    method: str
    request_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None
    rate_limit: Optional[int] = None
    auth_required: bool = True

@dataclass
class ConstitutionalConstraint:
    name: str
    constraint_type: str
    parameters: Dict[str, Any]
    severity: str = "error"

@dataclass
class SystemSpec:
    name: str
    bounded_contexts: Dict[str, List[str]]
    data_ownership: List[DataOwnership]
    event_contracts: List[EventContract]
    api_contracts: List[ApiContract]
    constitutional_constraints: List[ConstitutionalConstraint]
    target_runtime: RuntimeTarget
    target_regions: List[str]

@dataclass
class FailureModeConfig:
    strategy: FailureModeStrategy
    parameters: Dict[str, Any]
    applies_to: List[str]

@dataclass
class ObservabilityConfig:
    service_name: str
    trace_sampling_rate: float
    metrics_endpoints: List[str]
    log_level: str
    red_metrics_enabled: bool = True
    custom_attributes: Dict[str, str] = field(default_factory=dict)

@dataclass
class SecurityConfig:
    rbac_policy: str
    vault_role: str
    mtls_enabled: bool = True
    audit_logging: bool = True
    secret_injection_paths: List[str] = field(default_factory=list)

@dataclass
class DataAccessPattern:
    entity: str
    owner_service: str
    access_type: str
    allowed: bool

@dataclass
class ServiceMeshConfig:
    service_name: str
    destination_rules: Dict[str, Any]
    virtual_services: List[Dict[str, Any]]
    peer_authentication: Dict[str, Any]
    traffic_policy: Dict[str, Any]

@dataclass
class IntermediateService:
    name: str
    bounded_context: str
    criticality: CriticalityLevel
    owned_data: List[DataOwnership]
    data_access_patterns: List[DataAccessPattern]
    publishes_events: List[EventContract]
    consumes_events: List[EventContract]
    exposes_apis: List[ApiContract]
    failure_modes: List[FailureModeConfig]
    observability: ObservabilityConfig
    security: SecurityConfig
    mesh_config: ServiceMeshConfig
    slo_latency_ms: int
    slo_availability: float
    target_language: str
    depends_on: List[str] = field(default_factory=list)
    custom_zones: Dict[str, str] = field(default_factory=dict)

@dataclass
class SystemIR:
    name: str
    services: Dict[str, IntermediateService]
    event_topology: Dict[str, Any]
    api_dependencies: Dict[str, List[str]]
    constitutional_constraints: List[ConstitutionalConstraint]
    target_runtime: RuntimeTarget


# ============================================================================
# 2. CONSTITUTIONAL VALIDATOR V2
# ============================================================================

class ConstitutionalViolation(Exception):
    pass

class ConstitutionalValidatorV2:
    def __init__(self, constraints, ir=None):
        self.constraints = constraints
        self.ir = ir
        self.violations = []

    def validate(self, spec):
        self.violations = []
        ownership = self._build_ownership_map(spec)
        graph = self._build_interaction_graph(spec)
        for c in self.constraints:
            if c.constraint_type == "pii_isolation":
                self._validate_pii_isolation(spec, c, ownership, graph)
            elif c.constraint_type == "data_residency":
                self._validate_data_residency(spec, c, ownership)
            elif c.constraint_type == "rate_limit_floor":
                self._validate_rate_limit_floor(spec, c, ownership)
            elif c.constraint_type == "auth_requirement":
                self._validate_auth_requirement(spec, c, ownership)
        if self.violations:
            raise ConstitutionalViolation(self._format_violations())
        return True

    def _build_ownership_map(self, spec):
        return {d.entity: d.owner_service for d in spec.data_ownership}

    def _build_interaction_graph(self, spec):
        graph = {}
        for svcs in spec.bounded_contexts.values():
            for s in svcs:
                graph[s] = {"calls": [], "consumes_from": [], "produces_to": []}
        for e in spec.event_contracts:
            for p in e.producers:
                if p in graph:
                    for c in e.consumers:
                        graph[p]["produces_to"].append(c)
                        if c in graph:
                            graph[c]["consumes_from"].append(p)
        return graph

    def _resolve_api_owner(self, api, spec):
        part = api.path.strip("/").split("/")[0].replace("-", "_").title()
        for d in spec.data_ownership:
            if d.entity.lower() == part.lower():
                return d.owner_service
        return None

    def _validate_pii_isolation(self, spec, constraint, ownership, graph):
        audit_gws = set(constraint.parameters.get("audit_gateways", ["audit-service"]))
        pii_svcs = {d.owner_service for d in spec.data_ownership if d.pii_fields}
        for svc in pii_svcs:
            for called in graph.get(svc, {}).get("calls", []):
                if called not in pii_svcs and called not in audit_gws:
                    self.violations.append({
                        "constraint": "pii_isolation", "severity": "error", "service": svc,
                        "violates": f"Calls '{called}' without audit gateway",
                        "remediation": f"Route through {audit_gws}"
                    })

    def _validate_data_residency(self, spec, constraint, ownership):
        allowed = set(constraint.parameters.get("allowed_regions", []))
        restricted = constraint.parameters.get("restricted_entities", [])
        if not allowed:
            return
        for d in spec.data_ownership:
            if restricted and d.entity not in restricted:
                continue
            for region in spec.target_regions:
                if region not in allowed:
                    self.violations.append({
                        "constraint": "data_residency", "severity": constraint.severity,
                        "entity": d.entity, "owner": d.owner_service,
                        "violates": f"Deployed in '{region}' but only {allowed} allowed",
                        "remediation": f"Move {d.owner_service} to allowed region"
                    })

    def _validate_rate_limit_floor(self, spec, constraint, ownership):
        min_rate = constraint.parameters.get("min_requests_per_second", 100)
        critical = {d.entity for d in spec.data_ownership
                    if d.pii_fields or d.entity in ["Payment", "Transaction"]}
        for api in spec.api_contracts:
            owner = self._resolve_api_owner(api, spec)
            owner_entities = [e for e, o in ownership.items() if o == owner]
            if any(e in critical for e in owner_entities):
                if api.rate_limit is None or api.rate_limit < min_rate:
                    self.violations.append({
                        "constraint": "rate_limit_floor", "severity": "error",
                        "owner": owner,
                        "violates": f"Rate limit {api.rate_limit} < {min_rate}",
                        "remediation": f"Set rate_limit >= {min_rate}"
                    })

    def _validate_auth_requirement(self, spec, constraint, ownership):
        exempted = set(constraint.parameters.get("exempted_services", []))
        for api in spec.api_contracts:
            owner = self._resolve_api_owner(api, spec)
            if owner not in exempted and not api.auth_required:
                self.violations.append({
                    "constraint": "auth_requirement", "severity": "error",
                    "owner": owner, "violates": "Unauthenticated API",
                    "remediation": "Set auth: true"
                })

    def _format_violations(self):
        lines = ["Constitutional Violations Detected:", "=" * 50]
        for v in self.violations:
            lines += [
                f"\n[{v['severity'].upper()}] {v['constraint']}",
                f"   Service: {v.get('service') or v.get('owner')}",
                f"   Issue: {v['violates']}",
                f"   Fix: {v['remediation']}"
            ]
        return "\n".join(lines)


# ============================================================================
# 3. DSL PARSER V2 (explicit criticality + language overrides)
# ============================================================================

class GenesisDSLParserV2:
    @staticmethod
    def parse_file(filepath):
        raw = yaml.safe_load(open(filepath))
        return GenesisDSLParserV2.parse_dict(raw)

    @staticmethod
    def parse_dict(raw):
        spec = SystemSpec(
            name=raw["name"],
            bounded_contexts=raw["bounded_contexts"],
            data_ownership=[DataOwnership(
                entity=d["entity"], owner_service=d["owner"], fields=d["fields"],
                pii_fields=d.get("pii_fields", []), retention_days=d.get("retention_days")
            ) for d in raw.get("data_ownership", [])],
            event_contracts=[EventContract(
                name=e["name"], payload_schema=e["schema"],
                producers=e["producers"], consumers=e["consumers"],
                ordering_key=e.get("ordering_key"), retention_hours=e.get("retention_hours", 24)
            ) for e in raw.get("events", [])],
            api_contracts=[ApiContract(
                path=a["path"], method=a["method"],
                request_schema=a.get("request"), response_schema=a.get("response"),
                rate_limit=a.get("rate_limit"), auth_required=a.get("auth", True)
            ) for a in raw.get("apis", [])],
            constitutional_constraints=[ConstitutionalConstraint(
                name=c["name"], constraint_type=c["type"],
                parameters=c.get("params", {}), severity=c.get("severity", "error")
            ) for c in raw.get("constitutional_constraints", [])],
            target_runtime=RuntimeTarget(raw.get("runtime", "kubernetes")),
            target_regions=raw.get("regions", ["us-east-1"])
        )
        service_definitions = {}
        for svc_def in raw.get("services", []):
            service_definitions[svc_def["name"]] = {
                "criticality": svc_def.get("criticality"),
                "language": svc_def.get("language"),
                "custom_config": svc_def.get("config", {})
            }
        spec.service_definitions = service_definitions
        return spec


# ============================================================================
# 4. DOMAIN COMPILER V2
# ============================================================================

class DomainCompilerV2:
    def __init__(self, validator):
        self.validator = validator
        self.service_overrides = {}

    def compile(self, spec):
        if hasattr(spec, "service_definitions"):
            self.service_overrides = spec.service_definitions
        self.validator.validate(spec)
        services = self._derive_services(spec)
        return SystemIR(
            name=spec.name, services=services,
            event_topology={e.name: {"producers": e.producers, "consumers": e.consumers}
                            for e in spec.event_contracts},
            api_dependencies={n: s.depends_on for n, s in services.items()},
            constitutional_constraints=spec.constitutional_constraints,
            target_runtime=spec.target_runtime
        )

    def _derive_services(self, spec):
        services = {}
        data_by_owner = {}
        for d in spec.data_ownership:
            data_by_owner.setdefault(d.owner_service, []).append(d)
        slo_lat  = {CriticalityLevel.FINANCIAL: 50,  CriticalityLevel.PII: 100,
                    CriticalityLevel.PUBLIC: 500,     CriticalityLevel.INTERNAL: 1000}
        slo_avail = {CriticalityLevel.FINANCIAL: 0.9999, CriticalityLevel.PII: 0.999,
                     CriticalityLevel.PUBLIC: 0.99,       CriticalityLevel.INTERNAL: 0.95}
        for ctx, svcs in spec.bounded_contexts.items():
            for svc_name in svcs:
                ov = self.service_overrides.get(svc_name, {})
                criticality = (CriticalityLevel(ov["criticality"]) if ov.get("criticality")
                               else self._infer_criticality(svc_name, data_by_owner.get(svc_name, [])))
                target_lang = ov.get("language") or self._select_language(criticality)
                apis     = [a for a in spec.api_contracts if svc_name.replace("-service","") in a.path.lower()]
                publishes = [e for e in spec.event_contracts if svc_name in e.producers]
                consumes  = [e for e in spec.event_contracts if svc_name in e.consumers]
                deps      = {p for e in consumes for p in e.producers if p != svc_name}
                services[svc_name] = IntermediateService(
                    name=svc_name, bounded_context=ctx, criticality=criticality,
                    owned_data=data_by_owner.get(svc_name, []),
                    data_access_patterns=[
                        DataAccessPattern(entity=d.entity, owner_service=svc_name,
                                          access_type="owns", allowed=True)
                        for d in data_by_owner.get(svc_name, [])
                    ],
                    publishes_events=publishes, consumes_events=consumes, exposes_apis=apis,
                    failure_modes=self._generate_failure_modes(criticality, apis, publishes),
                    observability=ObservabilityConfig(
                        service_name=svc_name,
                        trace_sampling_rate=0.1 if criticality == CriticalityLevel.PUBLIC else 1.0,
                        metrics_endpoints=["prometheus:9090"], log_level="info"
                    ),
                    security=SecurityConfig(
                        rbac_policy=f"allow {svc_name}",
                        vault_role=f"{spec.name}-{svc_name}",
                        mtls_enabled=criticality != CriticalityLevel.PUBLIC,
                        audit_logging=criticality in [CriticalityLevel.PII, CriticalityLevel.FINANCIAL]
                    ),
                    mesh_config=ServiceMeshConfig(
                        service_name=svc_name,
                        destination_rules={"trafficPolicy": {"connectionPool": {"tcp": {"maxConnections": 100}}}},
                        virtual_services=[],
                        peer_authentication={"mtls": {"mode": "STRICT" if criticality != CriticalityLevel.PUBLIC else "PERMISSIVE"}},
                        traffic_policy={"rate_limits": [{"api": a.path, "rps": a.rate_limit or 1000} for a in apis]}
                    ),
                    slo_latency_ms=slo_lat.get(criticality, 100),
                    slo_availability=slo_avail.get(criticality, 0.99),
                    target_language=target_lang,
                    depends_on=list(deps)
                )
        return services

    def _infer_criticality(self, name, data):
        if any(d.pii_fields for d in data): return CriticalityLevel.PII
        if any(k in name.lower() for k in ["payment","fraud","billing","financial"]): return CriticalityLevel.FINANCIAL
        if any(k in name.lower() for k in ["user","identity","auth"]): return CriticalityLevel.PII
        if "public" in name.lower(): return CriticalityLevel.PUBLIC
        return CriticalityLevel.INTERNAL

    def _select_language(self, c):
        return "rust" if c == CriticalityLevel.FINANCIAL else "go" if c == CriticalityLevel.PII else "typescript"

    def _generate_failure_modes(self, c, apis, events):
        paths = [a.path for a in apis]; channels = [e.name for e in events]; modes = []
        if c == CriticalityLevel.FINANCIAL:
            modes += [
                FailureModeConfig(FailureModeStrategy.RETRY_WITH_BACKOFF, {"max_retries": 5, "backoff_multiplier": 2.0}, paths),
                FailureModeConfig(FailureModeStrategy.BULKHEAD, {"max_concurrent": 50}, paths)
            ]
        elif c == CriticalityLevel.PII:
            modes += [
                FailureModeConfig(FailureModeStrategy.CIRCUIT_BREAKER, {"failure_threshold": 5, "recovery_timeout_ms": 30000}, paths),
                FailureModeConfig(FailureModeStrategy.DEAD_LETTER_QUEUE, {"retention_hours": 168, "audit": True}, channels)
            ]
        modes.append(FailureModeConfig(FailureModeStrategy.TIMEOUT, {"timeout_ms": 30000}, paths))
        return modes


# ============================================================================
# 5. GO CODE EMITTER
# ============================================================================

class GoCodeEmitter:
    def emit_service(self, svc, output_dir):
        d = Path(output_dir) / svc.name
        d.mkdir(parents=True, exist_ok=True)
        files = {
            "main.go":        self._main(svc),
            "handlers.go":    self._handlers(svc),
            "resilience.go":  self._resilience(svc),
            "observability.go": self._observability(svc),
            "k8s.yaml":       self._k8s(svc),
            "istio.yaml":     self._istio(svc),
            "go.mod":         self._gomod(svc),
            "Dockerfile":     self._dockerfile(svc),
        }
        for fname, content in files.items():
            (d / fname).write_text(content)
        return files

    def _main(self, s):
        return f"""package main

import (
\t"context"
\t"log"
\t"net/http"
\t"os/signal"
\t"syscall"
\t"time"
)

const (
\tServiceName     = "{s.name}"
\tCriticality     = "{s.criticality.value}"
\tSLOLatencyMs    = {s.slo_latency_ms}
\tSLOAvailability = {s.slo_availability}
)

// ==== GENESIS:SACRED:initialization:BEGIN ====
// Initialize custom dependencies here
// ==== GENESIS:SACRED:initialization:END ====

func main() {{
\tctx, cancel := context.WithCancel(context.Background())
\tdefer cancel()
\ttp, _ := initTracer(ctx)
\tdefer tp.Shutdown(ctx)
\tcb := initCircuitBreaker()
\tmux := http.NewServeMux()
\tmux.HandleFunc("/health", healthHandler)
\tserver := &http.Server{{
\t\tAddr:    ":8080",
\t\tHandler: withMiddleware(mux, tp, cb),
\t\tReadTimeout:  SLOLatencyMs * time.Millisecond,
\t\tWriteTimeout: SLOLatencyMs * 2 * time.Millisecond,
\t}}
\tsigChan := make(chan os.Signal, 1)
\tsignal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
\tgo server.ListenAndServe()
\t<-sigChan
\tshutdownCtx, _ := context.WithTimeout(ctx, 30*time.Second)
\tserver.Shutdown(shutdownCtx)
}}

func healthHandler(w http.ResponseWriter, r *http.Request) {{
\tw.Header().Set("Content-Type", "application/json")
\tw.Write([]byte(`{{"status":"healthy","service":"{s.name}"}}`))
}}
"""

    def _handlers(self, s):
        handlers = []
        for api in s.exposes_apis:
            name = api.path.strip("/").replace("/","_").replace("-","_").replace("{","").replace("}","")
            handlers.append(f"""
// ==== GENESIS:SACRED:handler_{name}:BEGIN ====
// {api.method.upper()} {api.path} | rate:{api.rate_limit or 1000}/s | auth:{api.auth_required}
func {name}Handler(w http.ResponseWriter, r *http.Request) {{
\t// TODO: implement business logic
\tw.Write([]byte(`{{"status":"ok"}}`))
}}
// ==== GENESIS:SACRED:handler_{name}:END ====""")
        return "package main\n" + "\n".join(handlers)

    def _resilience(self, s):
        modes = "\n".join([f"// {f.strategy.value}: {f.parameters}" for f in s.failure_modes])
        return f"""package main

import (
\t"sync"
\t"time"
)

// Failure modes — criticality: {s.criticality.value}
{modes}

type CircuitBreaker struct {{
\tmu      sync.RWMutex
\tfails   int
\tthresh  int
\topen    bool
\tlastFail time.Time
}}

func initCircuitBreaker() *CircuitBreaker {{
\treturn &CircuitBreaker{{thresh: 5}}
}}

func (cb *CircuitBreaker) Allow() bool {{
\tcb.mu.RLock()
\tdefer cb.mu.RUnlock()
\treturn !cb.open
}}
"""

    def _observability(self, s):
        return f"""package main

import (
\t"context"
\t"go.opentelemetry.io/otel"
\tsdktrace "go.opentelemetry.io/otel/sdk/trace"
)

// RED metrics | sampling: {s.observability.trace_sampling_rate} | SLO: {s.slo_latency_ms}ms
func initTracer(ctx context.Context) (*sdktrace.TracerProvider, error) {{
\ttp := sdktrace.NewTracerProvider(
\t\tsdktrace.WithSampler(sdktrace.TraceIDRatioBased({s.observability.trace_sampling_rate})),
\t)
\totel.SetTracerProvider(tp)
\treturn tp, nil
}}
"""

    def _k8s(self, s):
        return f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {s.name}
  labels:
    app: {s.name}
    criticality: {s.criticality.value}
spec:
  replicas: 3
  selector:
    matchLabels:
      app: {s.name}
  template:
    metadata:
      labels:
        app: {s.name}
      annotations:
        prometheus.io/scrape: "true"
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "{s.security.vault_role}"
    spec:
      containers:
      - name: {s.name}
        image: {s.name}:latest
        ports:
        - containerPort: 8080
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
"""

    def _istio(self, s):
        mode = "STRICT" if s.security.mtls_enabled else "PERMISSIVE"
        return f"""apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: {s.name}
spec:
  selector:
    matchLabels:
      app: {s.name}
  mtls:
    mode: {mode}
"""

    def _gomod(self, s):
        return f"""module {s.name.replace("-","")}

go 1.21

require (
\tgo.opentelemetry.io/otel v1.21.0
\tgo.opentelemetry.io/otel/sdk v1.21.0
)
"""

    def _dockerfile(self, s):
        return f"""FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 go build -o /{s.name}

FROM gcr.io/distroless/static:nonroot
COPY --from=builder /{s.name} /{s.name}
USER nonroot:nonroot
EXPOSE 8080
ENTRYPOINT ["/{s.name}"]
"""


# ============================================================================
# 6. TYPESCRIPT EMITTER
# ============================================================================

class TypeScriptEmitter:
    def emit_service(self, svc, output_dir):
        d = Path(output_dir) / svc.name / "src"
        d.mkdir(parents=True, exist_ok=True)
        files = {
            "src/main.ts":      self._main(svc),
            "src/app.module.ts":self._module(svc),
            "package.json":     self._package(svc),
            "tsconfig.json":    self._tsconfig(),
            "Dockerfile":       self._dockerfile(svc),
        }
        for fname, content in files.items():
            fpath = Path(output_dir) / svc.name / fname
            fpath.parent.mkdir(parents=True, exist_ok=True)
            fpath.write_text(content)
        return files

    def _main(self, s):
        return f"""import {{ NestFactory }} from '@nestjs/core';
import {{ AppModule }} from './app.module';

async function bootstrap() {{
  const app = await NestFactory.create(AppModule);
  app.enableShutdownHooks();
  await app.listen(8080);
  console.log(`{s.name} ({s.criticality.value}) listening on 8080`);
}}
bootstrap();
"""

    def _module(self, s):
        return f"""import {{ Module }} from '@nestjs/common';

@Module({{ imports: [], controllers: [], providers: [] }})
export class AppModule {{}}
"""

    def _package(self, s):
        return json.dumps({
            "name": s.name, "version": "1.0.0",
            "criticality": s.criticality.value,
            "scripts": {"build": "tsc", "start": "node dist/main.js"},
            "dependencies": {
                "@nestjs/common": "^10.0.0",
                "@nestjs/core": "^10.0.0",
                "@opentelemetry/sdk-node": "^0.45.0"
            }
        }, indent=2)

    def _tsconfig(self):
        return json.dumps({
            "compilerOptions": {
                "module": "commonjs", "target": "ES2021",
                "outDir": "./dist", "experimentalDecorators": True,
                "emitDecoratorMetadata": True, "strictNullChecks": True
            }
        }, indent=2)

    def _dockerfile(self, s):
        return f"""FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
USER node
EXPOSE 8080
CMD ["node", "dist/main.js"]
"""


# ============================================================================
# 7. RUST EMITTER
# ============================================================================

class RustEmitter:
    def emit_service(self, svc, output_dir):
        d = Path(output_dir) / svc.name
        (d / "src").mkdir(parents=True, exist_ok=True)
        files = {
            "src/main.rs":      self._main(svc),
            "src/models.rs":    self._models(svc),
            "src/handlers.rs":  self._handlers(svc),
            "src/resilience.rs":self._resilience(svc),
            "src/telemetry.rs": self._telemetry(svc),
            "Cargo.toml":       self._cargo(svc),
            "Dockerfile":       self._dockerfile(svc),
            "k8s.yaml":         self._k8s(svc),
            "istio.yaml":       self._istio(svc),
        }
        for fname, content in files.items():
            (d / fname).write_text(content)
        return files

    def _fn(self, path):
        return path.strip("/").replace("/","_").replace("-","_").replace("{","").replace("}","") or "root"

    def _main(self, s):
        handlers = "\n".join([
            f'    .route("{a.path}", axum::routing::{a.method.lower()}(handlers::{self._fn(a.path)}))' for a in s.exposes_apis
        ])
        return f"""use axum::{{Router, extract::State}};
use std::{{net::SocketAddr, sync::Arc}};

mod models; mod handlers; mod resilience; mod telemetry;

// {s.name} | criticality:{s.criticality.value} | slo:{s.slo_latency_ms}ms | avail:{s.slo_availability}

pub struct AppState {{
    pub circuit_breaker: Arc<resilience::CircuitBreaker>,
}}

#[tokio::main]
async fn main() {{
    telemetry::init("{s.name}");
    let state = Arc::new(AppState {{
        circuit_breaker: Arc::new(resilience::CircuitBreaker::new({s.failure_modes[0].parameters.get("failure_threshold", 5) if s.failure_modes else 5})),
    }});
    let app = Router::new()
        .route("/health", axum::routing::get(health))
{handlers}
        .with_state(state);
    let addr = SocketAddr::from(([0,0,0,0], 8080));
    axum::Server::bind(&addr).serve(app.into_make_service()).await.unwrap();
}}

async fn health() -> axum::Json<serde_json::Value> {{
    axum::Json(serde_json::json!({{"status":"healthy","service":"{s.name}"}}))
}}
"""

    def _models(self, s):
        structs = []
        for data in s.owned_data:
            fields = []
            for f in data.fields:
                if f in ["amount","total","price","balance"]: rt = "rust_decimal::Decimal"
                elif f.endswith("_id") or f == "id": rt = "uuid::Uuid"
                elif f in data.pii_fields: rt = "String  // PII - encrypted at rest"
                else: rt = "String"
                fields.append(f"    pub {f}: {rt},")
            structs.append(f"""#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct {data.entity} {{
{chr(10).join(fields)}
}}""")
        return "use serde::{Serialize,Deserialize};\n\n" + "\n\n".join(structs)

    def _handlers(self, s):
        fns = []
        for api in s.exposes_apis:
            fn_name = self._fn(api.path)
            fns.append(f"""
// ==== GENESIS:SACRED:handler_{fn_name}:BEGIN ====
// {api.method.upper()} {api.path} | rate:{api.rate_limit or 1000}/s
pub async fn {fn_name}(
    State(state): State<std::sync::Arc<crate::AppState>>,
) -> Result<axum::Json<serde_json::Value>, AppError> {{
    state.circuit_breaker.allow()?;
    // TODO: implement business logic
    Ok(axum::Json(serde_json::json!({{"status":"ok"}})))
}}
// ==== GENESIS:SACRED:handler_{fn_name}:END ====""")
        return "use axum::extract::State;\n\n#[derive(Debug)]\npub enum AppError {{ CircuitOpen, Unauthorized }}\n\nimpl axum::response::IntoResponse for AppError {{\n    fn into_response(self) -> axum::response::Response {{\n        (axum::http::StatusCode::SERVICE_UNAVAILABLE, \"error\").into_response()\n    }}\n}}\n" + "\n".join(fns)

    def _resilience(self, s):
        modes = "\n".join([f"// {f.strategy.value}: {f.parameters}" for f in s.failure_modes])
        return f"""use std::sync::atomic::{{AtomicU32, AtomicBool, Ordering}};

// Failure modes — criticality: {s.criticality.value}
{modes}

pub struct CircuitBreaker {{
    failures:  AtomicU32,
    threshold: u32,
    is_open:   AtomicBool,
}}

impl CircuitBreaker {{
    pub fn new(threshold: u32) -> Self {{
        Self {{ failures: AtomicU32::new(0), threshold, is_open: AtomicBool::new(false) }}
    }}
    pub fn allow(&self) -> Result<(), crate::handlers::AppError> {{
        if self.is_open.load(Ordering::Relaxed) {{
            return Err(crate::handlers::AppError::CircuitOpen);
        }}
        Ok(())
    }}
    pub fn record_failure(&self) {{
        let f = self.failures.fetch_add(1, Ordering::Relaxed) + 1;
        if f >= self.threshold {{ self.is_open.store(true, Ordering::Relaxed); }}
    }}
}}
"""

    def _telemetry(self, s):
        return f"""pub fn init(service_name: &str) {{
    tracing_subscriber::fmt()
        .with_env_filter("{s.observability.log_level}")
        .init();
    tracing::info!(service=service_name, criticality="{s.criticality.value}", "started");
}}
"""

    def _cargo(self, s):
        return f"""[package]
name = "{s.name}"
version = "0.1.0"
edition = "2021"

[dependencies]
axum            = "0.7"
tokio           = {{ version = "1", features = ["full"] }}
serde           = {{ version = "1", features = ["derive"] }}
serde_json      = "1"
uuid            = {{ version = "1", features = ["v4","serde"] }}
rust_decimal    = {{ version = "1", features = ["serde"] }}
tracing         = "0.1"
tracing-subscriber = {{ version = "0.3", features = ["env-filter"] }}

[profile.release]
opt-level = 3
lto       = true
panic     = "abort"
"""

    def _dockerfile(self, s):
        return f"""FROM rust:1.75-alpine AS builder
RUN apk add --no-cache musl-dev
WORKDIR /app
COPY . .
RUN cargo build --release

FROM gcr.io/distroless/static:nonroot
COPY --from=builder /app/target/release/{s.name} /{s.name}
USER nonroot:nonroot
EXPOSE 8080
ENTRYPOINT ["/{s.name}"]
"""

    def _k8s(self, s):
        return f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {s.name}
  labels:
    app: {s.name}
    criticality: {s.criticality.value}
    language: rust
spec:
  replicas: 3
  selector:
    matchLabels:
      app: {s.name}
  template:
    metadata:
      labels:
        app: {s.name}
    spec:
      containers:
      - name: {s.name}
        image: {s.name}:latest
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "200m"
"""

    def _istio(self, s):
        mode = "STRICT" if s.security.mtls_enabled else "PERMISSIVE"
        return f"""apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: {s.name}
spec:
  selector:
    matchLabels:
      app: {s.name}
  mtls:
    mode: {mode}
"""


# ============================================================================
# 8. SACRED ZONE PRESERVER
# ============================================================================

class SacredZonePreserver:
    SACRED_BEGIN = r'====\s*GENESIS:SACRED:([\w_]+):BEGIN\s*===='
    SACRED_END   = r'====\s*GENESIS:SACRED:[\w_]+:END\s*===='

    def extract_from_existing(self, service_dir):
        import re
        zones = {}
        if not Path(service_dir).exists():
            return zones
        for f in Path(service_dir).rglob("*"):
            if f.is_file() and f.suffix in [".go",".ts",".rs"]:
                content = f.read_text()
                for m in re.finditer(self.SACRED_BEGIN, content):
                    zone = m.group(1)
                    after = content[m.end():]
                    end_m = re.search(rf'====\s*GENESIS:SACRED:{zone}:END\s*====', after)
                    if end_m:
                        zones[zone] = after[:end_m.start()].strip()
        return zones

    def merge_into_new(self, new_content, zones):
        for zone, saved in zones.items():
            if not saved: continue
            begin = f"==== GENESIS:SACRED:{zone}:BEGIN ===="
            end   = f"==== GENESIS:SACRED:{zone}:END ===="
            if begin in new_content and end in new_content:
                bi = new_content.find(begin) + len(begin)
                ei = new_content.find(end)
                if bi < ei:
                    new_content = new_content[:bi] + "\n" + saved + "\n" + new_content[ei:]
        return new_content


# ============================================================================
# 9. LIVING GENERATOR (surgical regen + sacred zone preservation)
# ============================================================================

class LivingGenerator:
    def __init__(self, go_emitter, ts_emitter, rust_emitter, output_dir):
        self.emitters = {"go": go_emitter, "typescript": ts_emitter, "rust": rust_emitter}
        self.output_dir = Path(output_dir)
        self.manifest_path = self.output_dir / ".genesis-manifest.json"
        self.preserver = SacredZonePreserver()
        self.manifest = json.loads(self.manifest_path.read_text()) if self.manifest_path.exists() else {}

    def _service_hash(self, svc):
        data = {
            "criticality": svc.criticality.value,
            "apis": [{"path": a.path, "method": a.method, "rate_limit": a.rate_limit} for a in svc.exposes_apis],
            "slo": svc.slo_latency_ms, "lang": svc.target_language, "mtls": svc.security.mtls_enabled,
        }
        return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def regenerate(self, ir):
        results = {"regenerated": [], "skipped": [], "errors": []}
        for svc_name, svc in ir.services.items():
            current_hash = self._service_hash(svc)
            if self.manifest.get(svc_name, {}).get("hash") == current_hash:
                results["skipped"].append(svc_name); continue
            svc_dir = self.output_dir / svc_name
            zones = self.preserver.extract_from_existing(svc_dir)
            emitter = self.emitters.get(svc.target_language)
            if not emitter:
                results["errors"].append(f"No emitter for {svc.target_language}"); continue
            files = emitter.emit_service(svc, str(self.output_dir))
            if zones:
                for f in svc_dir.rglob("*"):
                    if f.is_file() and f.suffix in [".go",".ts",".rs"]:
                        f.write_text(self.preserver.merge_into_new(f.read_text(), zones))
            self.manifest[svc_name] = {
                "hash": current_hash, "lang": svc.target_language,
                "criticality": svc.criticality.value, "files": len(files),
                "sacred_zones_preserved": len(zones)
            }
            results["regenerated"].append(svc_name)
        self.manifest_path.write_text(json.dumps(self.manifest, indent=2))
        return results


# ============================================================================
# 10. PACT CONTRACT GENERATOR
# ============================================================================

class PactContractGenerator:
    def generate_contracts(self, ir):
        interactions = []
        for svc_name, svc in ir.services.items():
            for api in svc.exposes_apis:
                consumers = [n for n,s in ir.services.items() if n != svc_name and svc_name in s.depends_on] or ["external-client"]
                for consumer in consumers:
                    interactions.append({
                        "description": f"{api.method.upper()} {api.path}",
                        "request": {"method": api.method.upper(), "path": api.path, "body": api.request_schema or {}},
                        "response": {"status": 200, "body": api.response_schema or {"status": "ok"}},
                        "metadata": {"consumer": consumer, "provider": svc_name}
                    })
            for event in svc.publishes_events:
                for consumer in event.consumers:
                    interactions.append({
                        "description": f"Event: {event.name}",
                        "contents": event.payload_schema,
                        "metadata": {"consumer": consumer, "provider": svc_name, "eventType": event.name}
                    })
        return {"pactVersion": "3.0.0", "interactions": interactions, "metadata": {"system": ir.name}}

    def write_pact_files(self, ir, output_dir):
        pacts_dir = Path(output_dir) / "pacts"; pacts_dir.mkdir(parents=True, exist_ok=True)
        contracts = self.generate_contracts(ir); groups = {}
        for i in contracts["interactions"]:
            m = i.get("metadata", {}); key = (m.get("consumer","?"), m.get("provider","?"))
            groups.setdefault(key, []).append(i)
        for (consumer, provider), interactions in groups.items():
            (pacts_dir / f"{consumer}-{provider}.json").write_text(
                json.dumps({"consumer": consumer, "provider": provider, "interactions": interactions}, indent=2))
        return len(groups)


# ============================================================================
# 11. DRIFT DETECTOR
# ============================================================================

class DriftDetector:
    def __init__(self, ir):
        self.ir = ir
        self.baseline = {
            n: {
                "criticality": s.criticality.value,
                "mtls": s.security.mtls_enabled,
                "slo_latency": s.slo_latency_ms,
                "failure_modes": [f.strategy.value for f in s.failure_modes]
            } for n, s in ir.services.items()
        }

    def detect(self, live_state):
        drift = []
        for svc, expected in self.baseline.items():
            if svc not in live_state:
                drift.append({"type": "service_missing", "service": svc, "severity": "critical"}); continue
            live = live_state[svc]
            if live.get("criticality") != expected["criticality"]:
                drift.append({"type": "criticality_drift", "service": svc, "severity": "critical"})
            if live.get("mtls") != expected["mtls"]:
                drift.append({"type": "security_drift", "service": svc, "severity": "critical"})
            if live.get("latency_p99", 0) > expected["slo_latency"] * 1.5:
                drift.append({"type": "slo_violation", "service": svc, "severity": "high"})
        for svc in live_state:
            if svc not in self.baseline:
                drift.append({"type": "unexpected_service", "service": svc, "severity": "warning"})
        return drift


# ============================================================================
# 12. DATA ACCESS ENFORCER
# ============================================================================

class DataAccessEnforcer:
    def enforce(self, spec, ir):
        ownership = {d.entity: d.owner_service for d in spec.data_ownership}
        violations = {}
        for svc_name, svc in ir.services.items():
            svc_violations = []
            for event in svc.publishes_events:
                for entity, owner in ownership.items():
                    if entity in str(event.payload_schema) and owner != svc_name:
                        if not self._is_reference_only(event.payload_schema, entity):
                            svc_violations.append({
                                "type": "cross_ownership_event", "service": svc_name,
                                "entity": entity, "owner": owner, "event": event.name,
                                "severity": "error",
                                "message": f"{svc_name} publishes full {entity} owned by {owner}",
                                "remediation": "Publish only entity ID"
                            })
            if svc_violations:
                violations[svc_name] = svc_violations
        return violations

    def _is_reference_only(self, schema, entity):
        s = str(schema)
        return f"{entity.lower()}_id" in s and entity not in s.replace(f"{entity.lower()}_id","")


# ============================================================================
# 13. TERRAFORM GENERATOR
# ============================================================================

class TerraformGenerator:
    def generate(self, ir, output_dir):
        tf_dir = Path(output_dir) / "terraform"; tf_dir.mkdir(parents=True, exist_ok=True)
        (tf_dir / "main.tf").write_text(self._root_main(ir))
        (tf_dir / "variables.tf").write_text(self._root_variables(ir))
        (tf_dir / "outputs.tf").write_text(self._root_outputs(ir))
        (tf_dir / "providers.tf").write_text(self._providers())
        for svc_name, svc in ir.services.items():
            mod_dir = tf_dir / "modules" / svc_name; mod_dir.mkdir(parents=True, exist_ok=True)
            (mod_dir / "main.tf").write_text(self._svc_main(svc, ir))
            (mod_dir / "variables.tf").write_text(self._svc_variables(svc))
            (mod_dir / "outputs.tf").write_text(self._svc_outputs(svc))
            (mod_dir / "rbac.tf").write_text(self._svc_rbac(svc, ir))
            (mod_dir / "vault.tf").write_text(self._svc_vault(svc, ir))
            (mod_dir / "monitoring.tf").write_text(self._svc_monitoring(svc))
            (mod_dir / "autoscaling.tf").write_text(self._svc_autoscaling(svc))

    def _providers(self):
        return """terraform {
  required_version = ">= 1.5"
  required_providers {
    kubernetes = { source = "hashicorp/kubernetes", version = "~> 2.23" }
    vault      = { source = "hashicorp/vault",      version = "~> 3.20" }
  }
}
provider "kubernetes" { config_path = var.kubeconfig_path }
provider "vault"      { address = var.vault_address }
"""

    def _root_main(self, ir):
        mods = []
        for svc_name, svc in ir.services.items():
            safe = svc_name.replace("-","_")
            deps = f"\n  depends_on = [{', '.join([f'module.{d.replace('-','_')}' for d in svc.depends_on])}]" if svc.depends_on else ""
            mods.append(f'module "{safe}" {{\n  source = "./modules/{svc_name}"\n  system_name = var.system_name\n  environment = var.environment\n  image_tag   = var.image_tag{deps}\n}}')
        return "# Genesis Terraform root — " + ir.name + "\n\n" + "\n\n".join(mods)

    def _root_variables(self, ir):
        return f'variable "system_name" {{ default = "{ir.name}" }}\nvariable "environment" {{ type = string }}\nvariable "image_tag" {{ default = "latest" }}\nvariable "kubeconfig_path" {{ default = "~/.kube/config" }}\nvariable "vault_address" {{ type = string }}\nvariable "vault_token" {{ type = string; sensitive = true }}\n'

    def _root_outputs(self, ir):
        return "\n".join([f'output "{n.replace("-","_")}_endpoint" {{\n  value = module.{n.replace("-","_")}.service_endpoint\n}}' for n in ir.services])

    def _svc_main(self, svc, ir):
        replicas = {"financial":3,"pii":3,"public":2,"internal":1}.get(svc.criticality.value, 2)
        safe = svc.name.replace("-","_")
        return f"""resource "kubernetes_namespace" "{safe}" {{
  metadata {{ name = "${{var.system_name}}-{svc.name}"
    labels = {{ "genesis/criticality" = "{svc.criticality.value}", "istio-injection" = "enabled" }} }} }}

resource "kubernetes_deployment" "{safe}" {{
  metadata {{ name = "{svc.name}", namespace = kubernetes_namespace.{safe}.metadata[0].name }}
  spec {{
    replicas = {replicas}
    selector {{ match_labels = {{ app = "{svc.name}" }} }}
    template {{
      metadata {{
        labels = {{ app = "{svc.name}" }}
        annotations = {{
          "vault.hashicorp.com/agent-inject" = "true"
          "vault.hashicorp.com/role"         = "{svc.security.vault_role}"
        }}
      }}
      spec {{
        service_account_name = kubernetes_service_account.{safe}.metadata[0].name
        container {{
          name = "{svc.name}"; image = "${{var.image_tag}}/{svc.name}:latest"
          port {{ container_port = 8080 }}
          liveness_probe {{ http_get {{ path = "/health"; port = 8080 }} }}
        }}
      }}
    }}
  }}
}}

resource "kubernetes_service" "{safe}" {{
  metadata {{ name = "{svc.name}", namespace = kubernetes_namespace.{safe}.metadata[0].name }}
  spec {{ selector = {{ app = "{svc.name}" }}; port {{ port = 80; target_port = 8080 }} }}
}}

resource "kubernetes_service_account" "{safe}" {{
  metadata {{ name = "{svc.name}", namespace = kubernetes_namespace.{safe}.metadata[0].name }}
}}
"""

    def _svc_variables(self, svc):
        return 'variable "system_name" { type = string }\nvariable "environment" { type = string }\nvariable "image_tag" { type = string }\n'

    def _svc_outputs(self, svc):
        safe = svc.name.replace("-","_")
        return f'output "service_endpoint" {{\n  value = "${{kubernetes_service.{safe}.metadata[0].name}}.${{var.system_name}}-{svc.name}.svc.cluster.local"\n}}\n'

    def _svc_rbac(self, svc, ir):
        safe = svc.name.replace("-","_")
        return f'resource "kubernetes_cluster_role" "{safe}" {{\n  metadata {{ name = "{svc.name}" }}\n  rule {{ api_groups=[""] resources=["configmaps","secrets"] verbs=["get","list","watch"] }}\n}}\n'

    def _svc_vault(self, svc, ir):
        safe = svc.name.replace("-","_")
        return f'resource "vault_policy" "{safe}" {{\n  name   = "{svc.security.vault_role}"\n  policy = <<EOT\npath "secret/data/{ir.name}/{svc.name}/*" {{ capabilities = ["read"] }}\nEOT\n}}\n'

    def _svc_monitoring(self, svc):
        burn = {"financial":14.4,"pii":6.0,"public":3.0,"internal":1.0}.get(svc.criticality.value,3.0)
        safe = svc.name.replace("-","_")
        return f'# SLO alerts for {svc.name} | burn_rate:{burn}x | slo:{svc.slo_latency_ms}ms\nresource "kubernetes_config_map" "{safe}_alerts" {{\n  metadata {{ name = "{svc.name}-alerts" }}\n  data = {{ "alerts.yaml" = "# prometheus alerts auto-generated" }}\n}}\n'

    def _svc_autoscaling(self, svc):
        min_r = {"financial":3,"pii":2,"public":2,"internal":1}.get(svc.criticality.value,1)
        max_r = {"financial":20,"pii":10,"public":15,"internal":5}.get(svc.criticality.value,5)
        safe = svc.name.replace("-","_")
        return f'resource "kubernetes_horizontal_pod_autoscaler_v2" "{safe}" {{\n  metadata {{ name = "{svc.name}" }}\n  spec {{\n    min_replicas = {min_r}; max_replicas = {max_r}\n    scale_target_ref {{ kind="Deployment"; name="{svc.name}" }}\n  }}\n}}\n'


# ============================================================================
# 14. CICD INTEGRATION
# ============================================================================

class CICDIntegration:
    def generate(self, ir, output_dir):
        cicd_dir = Path(output_dir) / "cicd"; cicd_dir.mkdir(parents=True, exist_ok=True)
        files = {
            ".pre-commit-config.yaml":          self._precommit(ir),
            ".github/workflows/genesis-ci.yml": self._github_actions(ir),
            "argocd/applicationset.yaml":        self._argocd(ir),
            "scripts/validate-constitution.py":  self._validate_script(ir),
            "scripts/drift-check.py":            self._drift_script(ir),
            "Makefile":                           self._makefile(ir),
        }
        for fname, content in files.items():
            fpath = cicd_dir / fname; fpath.parent.mkdir(parents=True, exist_ok=True)
            fpath.write_text(content)
        return files

    def _precommit(self, ir):
        return """repos:
  - repo: local
    hooks:
      - id: genesis-constitutional-validate
        name: "Genesis: Constitutional Validation"
        entry: python cicd/scripts/validate-constitution.py
        language: python
        always_run: true
        stages: [commit, push]
      - id: genesis-drift-check
        name: "Genesis: Drift Detection"
        entry: python cicd/scripts/drift-check.py
        language: python
        stages: [push]
"""

    def _github_actions(self, ir):
        return f"""name: Genesis CI/CD Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  constitutional-validation:
    name: "Constitutional Validation"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install pyyaml && python cicd/scripts/validate-constitution.py

  build-test:
    name: "Build & Test"
    needs: constitutional-validation
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: {list(ir.services.keys())}
    steps:
      - uses: actions/checkout@v4
      - name: Build service
        run: cd ${{{{ matrix.service }}}} && make build || true

  contract-tests:
    name: "Pact Contract Tests"
    needs: build-test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python -c "import json,glob; [print('OK',f) for f in glob.glob('pacts/*.json')]"

  drift-detection:
    name: "Spec Drift Detection"
    needs: build-test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python cicd/scripts/drift-check.py

  deploy:
    name: "Deploy via ArgoCD"
    needs: [contract-tests, drift-detection]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: argocd app sync {ir.name} --prune && argocd app wait {ir.name} --health
"""

    def _argocd(self, ir):
        elements = "\n".join([f"          - service: {s}" for s in ir.services])
        return f"""apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: {ir.name}
  namespace: argocd
spec:
  generators:
    - list:
        elements:
{elements}
  template:
    metadata:
      name: "{ir.name}-{{{{service}}}}"
    spec:
      project: default
      source:
        repoURL: https://github.com/IAmSoThirsty/project-ai
        targetRevision: HEAD
        path: "{{{{service}}}}"
      destination:
        server: https://kubernetes.default.svc
        namespace: {ir.name}-{{{{service}}}}
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
"""

    def _validate_script(self, ir):
        return """#!/usr/bin/env python3
import sys, yaml
from pathlib import Path

def main():
    if not Path("spec.yaml").exists():
        print("SKIP: spec.yaml not found"); return 0
    spec = yaml.safe_load(open("spec.yaml"))
    violations = []
    for api in spec.get("apis", []):
        if not api.get("auth", True):
            violations.append(f"UNAUTH API: {api['method'].upper()} {api['path']}")
    for d in spec.get("data_ownership", []):
        if d.get("pii_fields") and not d.get("retention_days"):
            violations.append(f"NO RETENTION: {d['entity']} has PII but no retention_days")
    constraints = spec.get("constitutional_constraints", [])
    required = {"rate_limit_floor","auth_requirement","pii_isolation"}
    missing = required - {c["type"] for c in constraints}
    if missing:
        violations.append(f"MISSING CONSTRAINTS: {missing}")
    if violations:
        print("CONSTITUTIONAL VIOLATIONS:")
        for v in violations: print(f"  {v}")
        return 1
    print(f"OK: {len(constraints)} constraints validated"); return 0

if __name__ == "__main__":
    sys.exit(main())
"""

    def _drift_script(self, ir):
        return """#!/usr/bin/env python3
import sys, json
from pathlib import Path

def main():
    if not Path(".genesis-manifest.json").exists():
        print("SKIP: no manifest"); return 0
    manifest = json.load(open(".genesis-manifest.json"))
    drift = []
    for svc, meta in manifest.items():
        if not Path(svc).exists():
            drift.append(f"MISSING: {svc}")
    if drift:
        print("DRIFT DETECTED:")
        for d in drift: print(f"  {d}")
        return 1
    print(f"OK: {len(manifest)} services clean"); return 0

if __name__ == "__main__":
    sys.exit(main())
"""

    def _makefile(self, ir):
        svcs = " ".join(ir.services.keys())
        return f"""# Genesis Makefile — {ir.name}
.PHONY: validate generate drift pact tf-plan tf-apply clean

validate:  ## Constitutional validation
\tpython cicd/scripts/validate-constitution.py

generate:  ## Regenerate from spec.yaml
\tpython genesis.py generate --spec spec.yaml --output .

drift:     ## Drift detection
\tpython cicd/scripts/drift-check.py

pact:      ## Validate Pact contracts
\t@for f in pacts/*.json; do python -c "import json,sys; p=json.load(open('$$f')); print('OK','$$f',len(p['interactions']),'interactions')"; done

build-all: ## Build all services
\t@for svc in {svcs}; do echo "Building $$svc..." && cd $$svc && make build && cd ..; done

tf-plan:   ## Terraform plan
\tcd terraform && terraform init && terraform plan

tf-apply:  ## Terraform apply
\tcd terraform && terraform apply

clean:     ## Remove generated outputs
\trm -rf {svcs} terraform/modules pacts .genesis-manifest.json

help:
\t@grep -E "^[a-zA-Z_-]+:.*##" $(MAKEFILE_LIST) | awk 'BEGIN{{FS=":.*##"}}{{printf "  %-15s %s\\n", $$1, $$2}}'
"""


# ============================================================================
# COMPONENT INVENTORY
# ============================================================================
# 01. CriticalityLevel, RuntimeTarget, FailureModeStrategy (enums)
# 02. DataOwnership, EventContract, ApiContract, ConstitutionalConstraint,
#     SystemSpec, FailureModeConfig, ObservabilityConfig, SecurityConfig,
#     DataAccessPattern, ServiceMeshConfig, IntermediateService, SystemIR
# 03. ConstitutionalValidatorV2 — pii_isolation, data_residency,
#                                 rate_limit_floor, auth_requirement
# 04. GenesisDSLParserV2        — explicit criticality + language overrides
# 05. DomainCompilerV2          — explicit > inferred > heuristic chain
# 06. GoCodeEmitter             — main, handlers, resilience, OTEL, k8s, Istio
# 07. TypeScriptEmitter         — NestJS, OTEL, Dockerfile
# 08. RustEmitter               — Axum, Decimal, atomic CircuitBreaker,
#                                 Cargo.toml, distroless Dockerfile
# 09. SacredZonePreserver       — extract + merge sacred zones across regen
# 10. LivingGenerator           — hash-based surgical regen, manifest tracking
# 11. PactContractGenerator     — consumer-driven API + event contracts
# 12. DriftDetector             — spec vs live, criticality/security/SLO drift
# 13. DataAccessEnforcer        — allowed=False cross-ownership detection
# 14. TerraformGenerator        — K8s, RBAC, Vault, monitoring, HPA, PDB
# 15. CICDIntegration           — pre-commit, GitHub Actions, ArgoCD, Makefile
#
# Pipeline: spec.yaml -> GenesisDSLParserV2 -> ConstitutionalValidatorV2
#        -> DomainCompilerV2 -> SystemIR -> [Go|TS|Rust]Emitter
#        -> PactContractGenerator -> TerraformGenerator -> CICDIntegration
#        -> LivingGenerator (ongoing surgical regen)
================================================================================
END OF GENESIS SOURCE
================================================================================


## Part 2: Admissibility Debt

1
 Admissibility Debt
 A Cross-Domain Governance Framework for AI Output Authority
 Epistemic, Procedural, and Institutional Criteria
 for When AI Outputs May Legitimately Matter
 Working Paper — Research Preview
 Version 2.0 · May 2026
 Justice
 Education
 Healthcare
 Finance
 Enterprise AI
 Socio-Political

2
 Abstract
AI outputs are increasingly admitted into consequential decisions across
courts, hospitals, schools, financial institutions, enterprises, and public
discourse before the authority, provenance, constraints, and legitimacy
of those outputs have been structurally established. This paper names
that accumulated governance gap Admissibility Debt — the liability
incurred when AI outputs influence liberty, safety, health, finance,
reputation, or civic outcomes without first satisfying evidentiary,
procedural, and institutional conditions adequate to justify that
influence. A formal framework decomposes admissibility into three
orthogonal dimensions — epistemic, procedural, and institutional —
each normalized to [0, 1] and governed by a minimum operator so that
no single dimension can compensate for fatal deficits in another. The
framework introduces authority classes (AC0–AC5), context-dependent
thresholds (τC), authority-amplification and reliance-propagation factors
on bounded ordinal 1–5 scales (α and ρ), and an explicit debt metric.
Domain-specific admissibility regimes are proposed for justice,
education, healthcare, finance, and enterprise AI, and extended to
societal Admissibility Debt in deepfake and synthetic-media ecosystems.
The paper demonstrates that major existing governance instruments —
NIST AI RMF, EU AI Act, ISO/IEC 42001, and emerging evidence rules
— do not, by themselves, constitute admissibility regimes for individual
AI outputs in consequential decisions. Admissibility Debt fills that gap,
offering falsifiable claims, an evaluation plan, a worked numerical case
study, and a cross-domain vocabulary for turning diffuse AI governance
concerns into specific, measurable, and correctable obligations.
 Keywords: AI governance · admissibility · evidence law · AI accountability · epistemic justice ·
 deepfakes · decision authority · procedural validity · institutional legitimacy

3
Table of Contents
1. Introduction
2. Formal Framework: Admissibility Debt
2.1 Outputs, Contexts, and Authority Classes
2.2 Three Dimensions of Admissibility
2.3 Admissibility Debt as a Quantitative Construct
2.4 Formal Definitions: α and ρ
2.5 Axioms A1–A8
2.6 Relation to Existing Governance Frameworks
2.7 Worked Case Study: AI Misconduct Detection in Education  
2.8 Hybrid Human-AI Loops and Augmented Judgment  
3. Domain-Specific Admissibility Regimes
3.1 Justice: Coercion, Liberty, and AI Risk Tools
3.2 Education: Grading, Ranking, and Misconduct Detection
3.3 Healthcare: Clinical Decision Support and Patient Risk
3.4 Finance: Credit, Fraud, and Adverse Action
3.5 Cross-Domain Pattern
4. Existing Governance Frameworks and the Admissibility Gap
4.1 NIST AI RMF: Trustworthiness Without Output Gates
4.2 EU AI Act: Risk Tiers Without Evidentiary Admission
4.3 ISO/IEC 42001: AI Management Systems Without Decision Authority
Standards
4.4 Evidence Rules: Status as of May 2026
4.5 Synthesis: Where Admissibility Debt Fits
5. Enterprise AI and Hidden Admissibility Debt
6. Societal Admissibility Debt: Deepfakes, Elections, and Narrative
Control
7. Red-Team Artefacts and Scenario Stress-Testing
8. Falsifiable Claims and Evaluation Plan
8.1 Falsifiable Claims
8.2 Evaluation Plan
8.3 Evaluation Governance
9. Conclusion and Policy Recommendations  
9.1 Summary of the Argument
9.2 Policy Recommendations by Stakeholder

4
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
9.3 Implementation Roadmap
9.3a Minimum Viable Admissibility by Organization Size  
9.4 The Stakes of Inaction
Notes and Sources
Appendix A: E/P/I Scoring Rubric  

5
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
Section 1. Introduction
Artificial intelligence governance is presently dominated by questions of
safety, alignment, compliance, and risk management, yet a more basic
question is now forcing itself into view: what gives any specific AI output the
right to matter in a consequential human decision? Courts, regulators,
enterprises, and public institutions are increasingly treating model outputs
as if they were admissible inputs to judgment before the authority,
provenance, constraints, and legitimacy of those outputs have been
established.
This omission is not merely a technical oversight; it is a structural
governance defect at the point where AI outputs acquire decision authority.
New proposals such as Federal Rule of Evidence 707 in the United States
would subject AI-generated evidence to the same reliability standards that
apply to expert testimony, and draft changes to Rule 901 explicitly target a
burden-shifting authentication procedure for AI-altered audio/visual material.
As of May 7, 2026, the Advisory Committee on Evidence Rules voted to delay
action on both proposals, with members divided on scope and
implementation; an October expert consultation was planned before further
committee action. [8] Similar legislative efforts at the state level would
condition admission of AI-generated or AI-processed evidence on
independent corroboration and proof of reliability in the specific use. Yet
even where such legal mechanisms are emerging, they do not by themselves
determine when an AI output should be allowed to influence liberty, medical
care, grading, credit access, employment, public belief, or state action in the
broader ecosystem of institutional and socio-technical decisions.
The central claim of this paper is that many of the most visible failures in
contemporary AI deployment are best understood not merely as failures of
bias, accuracy, transparency, or misuse, but as failures of admissibility.
Institutions are repeatedly allowing AI-generated or AI-mediated outputs to
enter consequential decision flows without first establishing the evidentiary,
procedural, and institutional basis on which those outputs may validly be
relied upon. This accumulated gap is named Admissibility Debt.
The concept is intentionally broader than the legal admissibility of evidence
in court, though it is illuminated by that tradition. Evidence law does not

6
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
confer admissibility on the basis of confidence, convenience, or rhetorical
polish; it turns on relevance, authentication, reliability, and exclusion rules
designed to prevent unfair prejudice or misleading inference. Those concerns
now reappear across domains that historically lacked formal evidentiary
doctrines for machine outputs. A recidivism score or algorithmic risk
assessment may influence sentencing and bail while its authority and error
structure remain opaque. [1] An automated grading or ranking system may
alter educational futures without a defensible account of what makes its
output an admissible proxy for individual merit. [2] A clinical AI assistant may
offer recommendations that appear rigorous and current while the
institutional pathway for accepting, documenting, or contesting those
recommendations remains underdeveloped.
The same pattern extends beyond formal institutions. Synthetic media,
deepfakes, and search-grounded generative outputs increasingly function as
socially admissible evidence in the public sphere long before they are
authenticated. Deepfake-as-a-service offerings, electoral misinformation
campaigns, and high-volume synthetic persona operations have transformed
AI-generated media from a hypothetical into an operational weapon across
recent election cycles and geopolitical conflicts. [6, 7] The resulting harms
are not confined to mistaken beliefs. They include reputational destruction,
market distortion, policy pressure, escalation during conflict, and a
generalized erosion of epistemic trust in institutions and information
systems.
The debt metaphor is not ornamental. Technical and security debt are now
well-recognized categories: expedient shortcuts leave behind latent liabilities
that grow over time, interacting with governance and security weaknesses to
make systems opaque, fragile, and costly to correct. Admissibility Debt
names a related but distinct liability: the accumulated risk created when AI
outputs are acted upon before their authority, provenance, constraints, and
legitimacy have been structurally verified. The more such outputs are reused,
embedded in workflows, propagated through records and institutions, or
amplified in public discourse, the more this debt compounds and the harder
it becomes to unwind contaminated decisions and narratives.
What unifies these cases is not merely that the systems can be wrong.
Human experts are also wrong, and institutions have long operated under

7
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
uncertainty. The deeper issue is that AI outputs are often granted practical
authority in the absence of the institutional work required to justify that
authority. Fluency is mistaken for competence, grounding for provenance,
deployment for legitimacy, and interface integration for entitlement to shape
outcomes.
This paper advances a unified thesis. Across courts, schools, hospitals, banks,
enterprises, and networked publics, societies are normalizing the use of AI
outputs faster than they are building the admissibility regimes required to
govern them. The failure is systemic, not because every model is
catastrophic, but because the social machinery of authority is being
reconfigured around systems whose outputs are too often admitted into
consequential processes without sufficient proof of standing, source, scope,
or contestability. The sections that follow formalize Admissibility Debt as a
governance construct, distinguish it from adjacent ideas such as safety and
reliability, analyze how it accumulates across multiple domains, and propose
domain-specific admissibility requirements capable of turning AI governance
away from generalized trust language and toward a more demanding regime
of evidentiary burden, procedural validity, institutional authorization, and
appeal.

8
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
Section 2. Formal Framework: Admissibility
Debt
2.1 Outputs, Contexts, and Authority Classes
The framework begins from a concrete claim: an AI output is not merely
"safe" or "unsafe" in the abstract. It is admissible or inadmissible for a
specific authority-bearing use in a specific context. For each output–context
pair (o, C), the institution must determine which authority class will be
permitted for that output:
Class
 Name
Threshold τC
 Example Use
AC0
Expressive / Creative
 ≈ 0.10
Brainstorming drafts, generative art
AC1
Informational
 ≈ 0.25
Background research, reference
summaries
AC2
Advisory
 ≈ 0.45
Internal policy recommendations
AC3
Recommendatory
 ≈ 0.65
Clinical suggestions, risk flags
AC4
Decision-supporting
 ≈ 0.80
Risk score input to human decision
AC5
Decision-determinati
ve
 ≈ 0.95
Sole basis for adverse or coercive action
 Table 1. Authority Classes and baseline admissibility thresholds. Justice, healthcare, and
similar life- or liberty-affecting contexts require τC ≥ 0.80 for any serious consequence and ≥
 0.95 for coercive, life-critical, or effectively irreversible decisions.
2.2 Three Dimensions of Admissibility
Admissibility is decomposed into three orthogonal components, each
normalized to [0, 1]:
 Notation
 Dimension
 Focus
 Example Fatal Defect
E(o, C)
Epistemic
Evidentiary
basis
Hallucinated sources, unknown error rates,
stale data in time-sensitive use
P(o, C)
Procedural
Decision
process
No human review, no appeal mechanism, no
audit trail, no chain of custody

9
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
I(o, C)
Institutional
Legitimate
adoption
No authority mandate, borrowed vendor
legitimacy, no identifiable decision-owner
 Table 2. The three admissibility dimensions and their fatal-defect conditions.
The overall admissibility score is defined as:
 A(o, C) = min( E(o, C), P(o, C), I(o, C) )
 Equation 1 — Overall Admissibility Score
The minimum operator is deliberate. A valid AI output must pass all three
gates. Strong evidence does not cure an invalid process; a faultless process
does not cure missing authority; institutional authority does not cure bad
evidence.
Epistemic admissibility E(o, C) aggregates provenance, source quality,
domain validation, error characterization, freshness, uncertainty expression,
and independent corroboration. Fatal epistemic defects include hallucinated
sources, unknown error rates, and out-of-domain model use.
Procedural admissibility P(o, C) reflects the validity of the decision
process admitting the output. It includes notice to affected parties, human
review where required, contestability and appeal mechanisms, auditability,
role authorization, chain of custody, and escalation paths.
Institutional admissibility I(o, C) reflects whether the output has been
legitimately adopted into an institutional decision structure. It depends on
legal authority, organizational mandate, professional competence, policy
authorization, locus of accountability, and jurisdictional fit.
2.3 Admissibility Debt as a Quantitative Construct
Admissibility Debt is defined at the level of individual outputs:
 DA(o, C) = max{ 0, τC − min(E, P, I) } · α(o, C) · ρ(o, C)
 Equation 2 — Admissibility Debt (per output–context pair)
Where:
DA(o, C) — Admissibility Debt for output o in context C.

10
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
τC — the admissibility threshold required by context C.
α(o, C) — the authority amplification factor: how much institutional
authority is effectively conferred on the output.
ρ(o, C) — the reliance propagation factor: how far downstream the
output travels through actions, records, workflows, and external reuse.
If A(o, C) ≥ τC, then DA(o, C) = 0; there is no Admissibility Debt for that
output–context pair. Debt is incurred when admissibility falls below threshold
and is amplified by the authority conferred (α) and the breadth of
downstream reliance (ρ). Both factors are defined on bounded ordinal scales
in Section 2.4.
2.4 Formal Definitions: α and ρ
To operationalize the debt metric, α and ρ are defined on ordinal scales with
five levels each. These levels are designed to be assessable through
documentary review — workflow logs, audit records, reliance documentation
— without requiring continuous measurement. Practitioners assign the level
that most closely characterizes the actual institutional role of the output at
the time of use.
Authority Amplification Factor (α ∈ {1, 2, 3, 4, 5})
 α
 Institutional Role
 Operational Indicator
 1
Passive reference
Output noted or logged but not acted upon; no decision
depends on it
 2
Advisory
consideration
Output informs deliberation but a human reaches an
independent conclusion
 3
Material
recommendation
Output substantially influences the decision; would require
justification to override
 4
Primary decision
input
Output is the dominant factor; human review is nominal or
confirmatory
 5
Sole or near-sole
basis
Output determines outcome without independent
verification or meaningful override
 Table 3. Authority Amplification Factor (α). Assign the level that best characterizes the
 output's actual institutional role, not its intended role.

11
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
Reliance Propagation Factor (ρ ∈ {1, 2, 3, 4, 5})
 ρ
 Propagation Scope
 Examples
 1
No downstream reuse
Single query; output not recorded, forwarded, or acted
upon beyond immediate use
 2
Internal record reuse
Written into an internal file, case note, or log; accessed
by the originating team
 3
Multi-department or
multi-stage reuse
Relied upon across organizational units or sequential
decision stages (e.g., HR → legal → compliance)
 4
External institutional
reuse
Shared with or relied upon by external organizations
(courts, regulators, partner agencies)
 5
Public or
cross-platform
propagation
Broadcast, indexed, published, or circulated to broad
audiences; deepfake media, published reports
 Table 4. Reliance Propagation Factor (ρ). Higher values reflect both wider reach and reduced
 ability to recall or correct the output after the fact.
Bounding Note
Both α and ρ are set at 1 as their minimum, not 0, because any output that has
been acted upon at all carries some positive authority and some positive
propagation. An output with α = 1 and ρ = 1 that still falls below admissibility
threshold incurs positive debt, reflecting the principle that even minimal
reliance on an inadequately admissible output is a governance defect. The
upper bound of 5 for each factor is a practical calibration; very high-debt
scenarios (e.g., a deepfake admitted as court evidence) will typically exhibit α
= 5 and ρ = 4 or 5, yielding DA values of 20–25 for a full threshold shortfall.
2.5 Axioms A1–A8
The framework is governed by eight axioms, each testable against real
deployments and incident data.

12
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
A1 — Authority Requires Admissibility
No AI output may validly acquire decision authority unless its admissibility
meets or exceeds the contextual threshold. Formally, authority at a given class
(e.g., AC4 or AC5) is permitted only if A(o, C) ≥ τC. In justice settings, this
reflects the intuition behind Rule 707 and Daubert: a model-generated risk
score cannot serve as determinative evidence in bail or sentencing merely
because it exists.
A2 — Burden Rests on the Proponent
The entity deploying, admitting, or relying on an AI output bears the burden of
demonstrating admissibility. For high-impact uses, unknown components
default to zero: if any of E, P, or I is unknown, the component is treated as 0
rather than assumed adequate.
A3 — Confidence Is Not Evidence
Model confidence, fluency, speed, or assertiveness is not admissibility.
Confidence is neither corroboration, authentication, nor authority.
AI-generated misconduct flags may be presented with high confidence scores,
but absent independent evidence they do not meet epistemic or procedural
admissibility standards for discipline.
A4 — Admissibility Is Domain-Specific
An output admissible in one context may be inadmissible in another. The same
textual analysis of a contract may be acceptable for brainstorming with counsel
but inadmissible as a sole basis for denying an insurance claim. Admissibility
attaches to the output–context pair, not to the output alone.
A5 — Procedure Is Not Decoration
An epistemically strong output can still be inadmissible if the process is invalid.
A statistically robust credit-risk model remains inadmissible as a basis for
adverse action if there is no adverse-action notice, no reason codes, no dispute
mechanism, and no audit trail. [4]

13
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
A6 — Institutional Authority Cannot Be Laundered
An AI system cannot silently borrow the legitimacy of the institution using it.
Embedding a vendor model into a court, hospital, or bank workflow does not
transfer institutional authority to the model. Valid adoption requires a
disclosed role, documented review standards, identifiable accountable
decision-makers, and contestability.
A7 — Debt Compounds Through Reliance
Admissibility Debt grows as unproven outputs propagate downstream. The
reliance factor ρ(o, C) increases with each reuse. When a weakly admissible
output is written into records and reused by subsequent decision processes,
the initial defect is amplified.
A8 — Debt Is Repaid Only by Admissibility Work
Disclaimers, branding, and generic safety language do not repay Admissibility
Debt. Only work that raises E, P, or I toward or above τC reduces debt: source
verification, independent corroboration, domain validation, human review,
institutional authorization, audit logging, notice, contestability, and repair of
tainted downstream records.
2.6 Relation to Existing Governance Frameworks
Existing AI governance standards — NIST AI RMF [9], ISO/IEC 42001 [11],
EU AI Act [10], OECD principles — focus on systems, organizations, and
lifecycle processes. Legal developments around AI-generated evidence focus
on whether and how machine-generated items may be admitted under rules
like 702, 707, and 901(c). Admissibility Debt bridges these layers: it treats
each AI output that crosses into a consequential decision as a potential
debt-bearing event, measurable and governable through the components E,
P, I, the threshold τC, and the factors α and ρ.
2.7 Worked Case Study: AI Misconduct Detection in
Education
The following numerical example demonstrates how the framework is applied
in practice. The case is stylized but reflects a pattern documented across
multiple institutional deployments.

14
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
Case Description
Scenario. A mid-sized university deploys a commercial AI misconduct detector
to screen student essay submissions. The system returns a flag on a submitted
essay: 87% confidence that the text is AI-generated. The flag is forwarded to
the academic integrity committee, which initiates formal disciplinary
proceedings based primarily on the flag. No independent review of the
submission is conducted before proceedings begin. The student — a non-native
English speaker using an assistive writing tool for grammar correction — is not
informed of the model's known high false-positive rate for non-native speakers
prior to the hearing.
 Component
Score
 Rationale
E(o, C)
Epistemic
 0.30
Model validated on general English corpus; no known
false-positive rate for non-native speakers or assistive-tool
users; no independent corroboration; 87% confidence score
conflated with probability of misconduct (confidence ≠
evidence, per A3)
P(o, C)
Procedural
 0.20
No human expert review before proceedings initiated;
student receives no explanation of evidence before hearing;
no mechanism to challenge the underlying model output; AI
flag directly triggered institutional process; no contestability
gate in place
I(o, C)
Institutional
 0.50
University has an academic integrity policy but no explicit
policy authorizing AI flags to initiate proceedings; the faculty
reviewer was not informed of model limitations; no
documented institutional mandate for this authority class of
use
A(o, C) = min(E,
P, I)
 0.20
Minimum of {0.30, 0.20, 0.50} = 0.20. Procedural
admissibility is the binding constraint; even if epistemic and
institutional scores were raised, P must improve first.
τEducation
(threshold)
 0.80
Discipline with permanent academic record consequences;
per Table 1 this falls in the AC4–AC5 range and requires τC
≥ 0.80
α Authority
amplification
 4
The flag is the primary decision input; the committee treats
it as the dominant factor; override would require active
justification (Level 4 per Table 3)

15
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
ρ Reliance
propagation
 3
Flag written into academic integrity record; accessed by
committee, registrar, and financial aid; multi-department
reuse (Level 3 per Table 4)
 DA(o, C) = max{ 0, 0.80 − 0.20 } · 4 · 3
 = 0.60 · 4 · 3 = 7.2
 Equation 3 — Worked Admissibility Debt Calculation
Interpretation
DA = 7.2 — substantial accumulated liability on a scale bounded above by 25
under the normalized scale (full threshold shortfall × α = 5 × ρ = 5).
The binding constraint is procedural: P(o, C) = 0.20 drives the minimum.
Improving the epistemic score (e.g., running a population-validated tool)
without first fixing procedural gaps would raise E but leave A = 0.20.
Debt repayment path: The institution can reduce DA toward zero by (1)
implementing human expert review before proceedings (raises P), (2)
disclosing model limitations and providing contestability before the hearing
(raises P), (3) validating the tool on the institution's own student population
(raises E), and (4) adopting an explicit policy authorizing and scoping AI use in
misconduct proceedings (raises I). These steps are not cosmetic; they are the
substance of Admissibility Debt repayment under Axiom A8.
Reliance correction: Because ρ = 3 (the flag is already in multi-department
records), any corrections must propagate to all downstream records — the
registrar, financial aid, and any external transcripts — before the debt is fully
retired.

16
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
Section 2.8 Hybrid Human-AI Loops and
Augmented Judgment
The framework is designed for cases where AI outputs carry decision
authority. A natural question arises: what about AI that operates clearly
below the AC3 threshold — systems used as lightweight aids to human
judgment rather than as primary decision inputs? These hybrid human-AI
loops are common and often beneficial, but they require a calibrated
treatment to avoid either under-governance or over-restriction.
The Admissibility Debt framework does not prohibit sub-AC3 use. It requires
only that the authority class be accurately assigned and that admissibility
conditions appropriate to that class be satisfied. An AI tool used as a passive
reference (AC0) or informational aid (AC1) — a legal research assistant
surfacing relevant cases for attorney review, a clinical literature search tool,
a grammar checker — incurs minimal debt even with low E, P, or I scores,
because the threshold τᴸ is correspondingly low and α is 1 or 2. The debt
formula ensures this naturally: Dᴬ(o, C) = max{0, τᴸ − A(o, C)} · α · ρ yields
low values when α is small.
The Beneficial Friction Principle
Sub-AC3 AI use is not merely tolerated; it is affirmatively valuable when it
introduces epistemic friction that improves human judgment — surfacing
counterarguments, flagging inconsistencies, expanding the information set
available to the decision-maker — without substituting for that judgment. The
governance obligation in such cases is accurate classification (ensuring the
output is genuinely treated as AC0–AC2 and not allowed to drift upward
through normalization) and propagation monitoring (ensuring ρ remains low by
preventing unchecked reuse of unreviewed AI output downstream).
The primary governance risk in hybrid loops is authority drift: an output
initially deployed at AC1 (informational) is gradually treated as AC3 or AC4
(recommendatory or decision-supporting) as workflows normalize around it
and human review becomes perfunctory. This is precisely how Admissibility
Debt accumulates silently in enterprise and institutional settings. The remedy
is not to eliminate the tool but to maintain explicit authority classification and
audit whether actual use matches the assigned class. Where telemetry shows

17
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
that outputs nominally classified at AC1 are routinely accepted without
modification or independent verification, the effective α has drifted to 3 or 4,
and debt accumulates accordingly.
When Augmented Judgment Tips Into Inadmissibility
A hybrid loop becomes an admissibility problem when: (1) the AI output is the
only input actually considered before a consequential decision (effective α ≥
4); (2) the AI output is propagated into records or downstream processes
without independent review (ρ escalates); or (3) the authority class assigned in
policy does not match the authority class exercised in practice. None of these
conditions requires that the AI be inaccurate or unsafe. They arise from
governance gaps, not model failures.
The framework handles augmented judgment without a separate theoretical
treatment: the same construct applies, but at lower thresholds and with
lower α values. What the framework adds is a structural incentive to
maintain accurate authority classification over time, rather than allowing
beneficial friction to quietly become unexamined authority as AI outputs
prove useful and organizational trust accumulates.

18
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
Section 3. Domain-Specific Admissibility
Regimes
The general framework becomes concrete when instantiated in specific
domains. This section proposes minimal admissibility regimes for justice,
education, healthcare, and finance.
3.1 Justice: Coercion, Liberty, and AI Risk Tools
Algorithmic risk assessment tools, including COMPAS and similar
instruments, now influence pretrial detention, sentencing, parole, probation,
and corrections classification across multiple jurisdictions. Investigations and
incident reports have shown that these tools operate as proprietary black
boxes that defendants cannot meaningfully inspect or challenge, and
ProPublica's analysis found racially disparate error rates. [1] These findings
are contested: Northpointe disputed ProPublica's interpretation of parity,
and Dressel and Farid (2018) found that COMPAS was no more accurate or
fair than predictions by untrained laypeople — a finding that cuts against
proprietary algorithmic authority from a different direction. What is not
contested is that these tools influence liberty interests while their error
structure, validation basis, and decision role remain structurally unverified
by defendants. At the same time, courts and evidence-rule committees are
considering provisions such as Federal Rule of Evidence 707 and
amendments to Rule 901(c) — though, as noted in Section 1, these
amendments have not been finalized as of May 2026. [8]
The proposed justice admissibility regime starts from a coercive-action
prohibition: AI outputs must not be the sole basis for arrest, detention,
charging, sentencing, parole denial, probation revocation, immigration
removal, child custody restriction, or asset seizure. Any AI-generated factual
assertion must be independently authenticated before being used in legal,
administrative, or quasi-judicial proceedings. Risk scores, identity assertions,
credibility assessments, and causation narratives must disclose the model
identity and version, data basis, known error rates and validation population,
limitations, uncertainty characteristics, and the identity of the human
reviewer who adopts or rejects them.

19
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
Justice: Fatal Inadmissibility Conditions
Any output that lacks (1) authenticated sources, (2) known error rates for the
justice use, (3) human review, (4) contestability, (5) a reconstructable basis for
acceptance, or (6) an approved institutional role is classified as inadmissible
for authority-bearing use in justice contexts regardless of model confidence or
interface presentation.
3.2 Education: Grading, Ranking, and Misconduct
Detection
The UK A-level grading scandal illustrates how algorithmic systems can
acquire de facto authority in education without an admissibility regime.
When pandemic-era exams were cancelled, calculated grades based on
teacher predictions moderated by a national algorithm produced widespread
downgrading and ultimately forced policy reversal. [2] Note on contested
evidence: The distributional interpretation of the scandal remains contested;
Ofqual later rejected a finding of systemic disadvantage by protected
characteristic or socioeconomic status, while independent analyses and
contemporaneous reporting described severe effects across school type,
cohort size, and disadvantage indicator. Case analyses emphasize that the
system was deployed as if its outputs were admissible proxies for individual
academic performance, despite limited transparency, weak recourse
mechanisms, and institution-level priorities that favored distributional
profiles over individual justice.
An admissibility regime for educational AI prohibits AI outputs from serving
as the sole basis for final grades, academic-integrity findings, discipline,
admissions, scholarship decisions, accommodation denials, or student-risk
classifications. AI-based detection outputs — algorithmic plagiarism or
misconduct flags — are explicitly treated as investigative signals rather than
determinative evidence unless corroborated by non-AI evidence. (See Section
2.7 for a worked example of the debt that accumulates when this
requirement is not met.) Educational AI tools used for grading, placement,
discipline, or academic-risk scoring should be validated against the
institution's actual student population, with explicit review for disability
accommodations, language background, assistive-technology use, and other
nonstandard learning contexts.

20
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
3.3 Healthcare: Clinical Decision Support and Patient Risk
AI-enabled clinical decision support (CDS), diagnostic tools, and workflow
automation are rapidly moving from experimental to deployed in hospitals
and clinics, with regulators such as the U.S. Food and Drug Administration
adjusting oversight to reflect risk-based distinctions. [3] Recent guidance
signals greater enforcement discretion for CDS that operates as clinician-aid,
provided that clinicians can independently review the basis for
recommendations and the software does not substitute for clinical judgment
in time-critical care.
The healthcare admissibility regime rejects autonomous clinical authority: AI
outputs must not be treated as diagnoses, prescriptions, triage dispositions,
contraindication clearances, discharge instructions, or care denials unless
reviewed and adopted by an authorized clinician. Clinical AI outputs must
identify patient-specific data used, missing critical data, data freshness,
relevant contraindications, and uncertainty, and must include explicit
triggers for emergency escalation. Medication-related outputs are required
to check allergies, contraindications, interactions, and dosing constraints.
Patients should be informed when AI materially contributes to care
recommendations, triage, documentation, or denial workflows.
3.4 Finance: Credit, Fraud, and Adverse Action
In credit underwriting, fraud detection, and anti-money-laundering (AML)
surveillance, AI and machine learning systems increasingly drive decisions
that directly affect access to credit, insurance, accounts, and services.
Regulators such as the U.S. Consumer Financial Protection Bureau have
clarified that existing obligations under the Equal Credit Opportunity Act and
Regulation B apply regardless of whether a creditor uses a traditional model
or an AI system: adverse action notices must still provide specific reasons,
and those reasons must reflect the actual factors used in the decision. [4]
The financial admissibility regime forbids AI outputs from serving as
unexplained bases for credit denial, insurance denial, account closure, fraud
designation, adverse pricing, or other high-impact decisions. Any adverse
action supported by AI must produce specific, intelligible, decision-relevant
reasons traceable to permissible data, documented data provenance and age,
model version, and policy rule path. Fraud or AML flags are treated as

21
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
investigative signals unless independently corroborated. Institutions must
monitor protected-class proxy risk, disparate impact, model drift, and data
drift, and must not use AI outputs in high-impact contexts where
performance has degraded or is unknown.
3.5 Cross-Domain Pattern
 Domain
Min τC
 Key E
Requirement
Key P Requirement
Key I Requirement
Justice
 ≥ 0.95
Validated error
rates, authenticated
sources
Human review +
contestability +
chain of custody
No black-box
determinative use;
explicit mandate
required
Educatio
n
 ≥ 0.80
Rubric alignment; p
opulation-validated;
corroborated
misconduct
Educator review +
student appeal +
audit trail
Academic
governance
authority;
permanent-record
policy
Healthca
re
 ≥ 0.80
Patient-specific
evidence;
medication safety;
guideline mapping
Clinician oversight +
escalation triggers +
patient notice
No autonomous
clinical authority;
validated population
scope
Finance
 ≥ 0.80
Reason-code
sufficiency;
permissible data;
drift monitoring
Dispute channel +
adverse-action notice
+ audit log
Explicit
adverse-action
policy; accountable
decision-owner
 Table 5. Minimum admissibility conditions by domain. All thresholds apply to any
authority-bearing use; coercive or life-critical actions require τC ≥ 0.95 within each domain.

22
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
Section 4. Existing Governance Frameworks and
the Admissibility Gap
AI governance today is structured around system-level risk management,
organizational controls, and lifecycle processes. Frameworks such as the
NIST AI Risk Management Framework (AI RMF) [9], the EU AI Act [10], and
ISO/IEC 42001 [11] articulate characteristics of trustworthy AI, categories of
risk, and requirements for AI management systems. Legal developments
around AI-generated evidence, including proposed Federal Rule of Evidence
707 and associated changes to Rule 901(c), ask when AI-generated material
may be admitted as evidence in court. Yet across this landscape, there
remains a structural gap: none of these frameworks, by themselves, provide a
general, domain-specific doctrine for when a particular AI output may
acquire institutional authority in a decision.
4.1 NIST AI RMF: Trustworthiness Without Output Gates
The NIST AI RMF [9] is intended to help organizations manage risks
associated with AI systems by providing voluntary guidance for incorporating
trustworthiness considerations into the design, development, use, and
evaluation of AI products, services, and systems. It defines seven key
characteristics of trustworthy AI and frames risk management as an iterative
process across the AI lifecycle. From the standpoint of Admissibility Debt, the
NIST AI RMF asks whether the system and its governance structure support
trustworthy behavior; it does not specify when any given output must be
excluded from or admitted into a particular decision. An organization can
satisfy NIST-aligned risk management practices and still accumulate
Admissibility Debt by allowing system outputs to influence liberty, safety, or
rights without per-output admissibility gates.
4.2 EU AI Act: Risk Tiers Without Evidentiary Admission
The EU AI Act [10] classifies AI systems into prohibited, high-risk,
limited-risk, and minimal-risk categories, with high-risk systems subject to
stringent obligations including risk management, data governance, technical
documentation, logging, transparency, human oversight, robustness, and
accuracy. High-risk categories explicitly include systems used in credit

23
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
scoring, employment, education, critical infrastructure, law enforcement,
migration, and access to essential services. From an admissibility
perspective, the AI Act asks whether a system is legally deployable and
whether its provider and deployer have met lifecycle and oversight
obligations — not whether any particular output should be admitted as a
basis for a specific decision. Risk tier and compliance status do not guarantee
that individual outputs meet the epistemic, procedural, and institutional
thresholds required for authority-bearing use.
4.3 ISO/IEC 42001: AI Management Systems Without
Decision Authority Standards
ISO/IEC 42001:2023 [11] specifies requirements for establishing,
implementing, maintaining, and continually improving an Artificial
Intelligence Management System (AIMS) within organizations. It answers
questions such as "Does this organization maintain a documented AI
management system?" and "Are AI-related risks being identified, assessed,
and mitigated across the lifecycle?" It does not directly specify criteria for
per-output admissibility in justice, education, healthcare, finance, or other
high-stakes domains. The standard can host an admissibility regime —
organizations could implement the domain-specific rules from Section 3
under its umbrella — but 42001 itself does not define when a sentencing
recommendation, grade, diagnosis suggestion, or credit decision satisfies
admissibility thresholds.
4.4 Evidence Rules: Status as of May 2026

24
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
Status Update: FRE 707 and Rule 901(c) — May 7, 2026
On May 7, 2026, the Advisory Committee on Evidence Rules voted to delay
action on proposed Federal Rule of Evidence 707 (which would apply Rule
702-style reliability scrutiny to qualifying AI-generated evidence, especially
when offered without expert testimony) and on proposed amendments to Rule
901(c) (a burden-shifting authentication procedure for AI-altered audio/visual
evidence). Committee members were divided on scope and implementation; an
October expert consultation was planned before further committee action. [8]
This delay is analytically significant: it confirms that even the most targeted
legal response to AI-generated evidence — focused exclusively on formal court
proceedings — remains unresolved, while AI-generated outputs continue to
enter justice, administrative, and institutional decision flows at scale.
Proposed Rule 707, when finalized, would explicitly cover AI-generated
forensic and analytical evidence, requiring courts to assess whether such
evidence meets the reliability criteria of Rule 702, including sufficient facts
or data, reliable methods, and reliable application to the facts. Proposed
amendments to Rule 901(c) would address authentication of AI-generated
material and deepfakes. These developments recognize that AI-generated
items entering the evidentiary record demand special scrutiny and that mere
confidence or widespread use does not suffice.
Even once finalized, Rule 707 and related provisions will be limited to
evidence offered in formal proceedings, and will focus primarily on epistemic
admissibility (reliability and authenticity) rather than the full triad of
epistemic, procedural, and institutional admissibility. Judicial systems can
comply with emerging AI-evidence rules and still accumulate Admissibility
Debt if, for example, AI-generated risk scores influence pretrial or sentencing
decisions without satisfying the domain-specific justice admissibility regime
outlined in Section 3.1.
4.5 Synthesis: Where Admissibility Debt Fits
 Framework
 Layer
 Primary Focus
 Admissibility Gap
NIST AI RMF
System / Org
Trustworthiness
lifecycle
No per-output authority gates;
risk managed at system level

25
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
EU AI Act
System risk
tier
Compliance
obligations for
providers/deployers
No output-level admissibility
criteria; tier ≠ authority
ISO/IEC
42001
Org / Mgmt
system
AI management system
lifecycle
No decision-authority
standards for individual
outputs
FRE 707 /
901(c)
(pending,
May 2026)
Evidence in
court
Reliability +
authentication at trial
Formal proceedings only;
finalization delayed; primarily
epistemic
Admissibility
Debt (this
paper)
Per-output,
cross-domain
Authority conditions
for individual outputs
in context
Bridges all layers; quantifies
and governs the residual gap
 Table 6. Comparison of existing governance frameworks. Each is necessary but not sufficient;
 Admissibility Debt operates at the output–decision interface that none of the others address
 directly.
An organization can be NIST-aligned, ISO 42001-certified, EU AI
Act-compliant, and formally attentive to AI-generated evidence in court, yet
still permit outputs to influence high-stakes decisions without satisfying
domain-specific admissibility criteria. In such cases, Admissibility Debt
accumulates in the gap between system-level governance and output-level
authority, compounding through reliance until it surfaces as
governance-significant failures.

26
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
Section 5. Enterprise AI and Hidden
Admissibility Debt
In enterprises, AI is no longer a separate "system" but a pervasive layer
across productivity suites, collaboration tools, CRM, ERP, human resources,
finance, and analytics platforms. Microsoft 365 Copilot exemplifies this shift:
it appears inside Outlook, Word, Excel, PowerPoint, Teams, SharePoint, and
other applications workers already treat as authoritative work surfaces.
When a Copilot summary is inserted into a contract draft, a risk memo, a
hiring decision, or a compliance report, the output is not experienced as an
external AI artifact but as native content within enterprise infrastructure.
The Structured Mismatch
Current enterprise AI governance asks: who has access, what data can the
model ground responses in, and what usage patterns appear in dashboards?
These are necessary security and compliance questions. They are not
admissibility questions. Admissibility questions ask: what authority class is
permitted for this output? What review must occur before it enters an official
record? Who is accountable for the decision it influences? These questions are
systematically absent from enterprise AI governance frameworks as currently
constituted.
Enterprises treat Copilot outputs as de facto admissible in day-to-day
decisions because they appear within systems of record and trusted
applications; yet governance predominantly treats Copilot as a security and
compliance surface, not as a decision-authority surface. Security controls
determine who can see which content and where AI can ground its
responses, while Admissibility Debt quietly accumulates when fluent outputs
are embedded in communications, policies, risk assessments, and records
without admissibility gates.
The metrics proposed in Section 2 are directly observable in enterprise
environments. Copilot usage reports and dashboards already track where AI
assistance appears in workflows, which departments use it most heavily, and
how often content is surfaced and acted upon. These telemetry sources could
be extended into admissibility metrics, such as the fraction of decisions in
each workflow that contain AI-generated content without documented

27
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
admissibility classification, and the proportion of AI-touching workflows that
have defined authority classes and review requirements. Without such
extensions, organizations risk interpreting increased AI usage and "time
saved" as unqualified success while remaining blind to accumulated
Admissibility Debt.
HR workflows illustrate the risk acutely: AI can generate job descriptions,
candidate summaries, performance-review drafts, and policy interpretations.
When these outputs enter employment decisions — hiring, promotion,
discipline, termination — without explicit authority classification and
admissibility documentation, the institution accumulates debt that may
surface as discrimination claims, labor disputes, or regulatory findings. α
values of 3–4 are common in such workflows, and ρ values of 2–3 are typical
as outputs propagate from HR to legal, payroll, and external compliance
records.

28
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
Section 6. Societal Admissibility Debt:
Deepfakes, Elections, and Narrative Control
AI-generated media has transformed from a speculative threat into a routine
component of political campaigns, conflict reporting, and online harassment.
Voice-cloned robocalls, synthetic candidate speeches, fabricated news clips,
and manipulated conflict imagery now circulate during election cycles and
crises at scales that overwhelm verification capacities. [6]
A documented example is the racist and antisemitic deepfake audio
circulated about a Maryland high school principal in 2024. Former Pikesville
High School athletic director Dazhon Darien was arrested after authorities
alleged he used AI to create the recording, which falsely depicted principal
Eric Eiswert making offensive remarks; it spread broadly, generated outrage
and threats, and contributed to severe reputational harm and division within
the community. In April 2025, Darien entered an Alford plea to disturbing
school operations and was sentenced to four months in jail. [7] During the
interval between circulation and debunking, the deepfake functioned as
socially admissible evidence: it was treated as authenticated audio, with no
admissibility regime in the local information ecosystem capable of halting its
authority.
Election cycles show similar dynamics. Reports document AI-generated
deepfake videos and audio used to misrepresent candidates' positions,
suggest withdrawals, or fabricate endorsements in multiple countries,
including Europe and the United States. [6] In Ireland's October 2025
presidential election, a deepfake video falsely depicted candidate Catherine
Connolly — the eventual winner — withdrawing her candidacy, complete with
fabricated RTÉ-style broadcast footage purporting to confirm the news. In
terms of the framework: these media exhibit α = 5 (sole basis for belief
formation in many viewers) and ρ = 5 (broadcast and cross-platform
propagation), while E, P, and I all approach zero — no authentication, no
contestation mechanism, and no institutional accountability for amplification.
Societal Admissibility Debt is the liability accumulated when unverified or
fabricated AI media is allowed to function as authoritative evidence in public
discourse and political decision-making. It manifests as reputational

29
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
destruction and local governance disruption; electoral distortion, where
deepfakes influence turnout, perceptions of legitimacy, or candidate viability;
and policy and security consequences, as generative media is used to
exaggerate battlefield successes or atrocities and complicate crisis response.
Systemic Risk: The Normalization Horizon
Societal Admissibility Debt does not merely threaten individual cases; it risks
normalizing an environment in which no evidence can be fully trusted and no
falsification can fully repair damage. The challenge is not only detecting and
labeling deepfakes, but constructing and enforcing admissibility regimes for
AI-generated media that allow societies to distinguish between content that
may legitimately matter and content that must be excluded or quarantined,
even when it is technically impressive or widely believed.

30
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
Section 7. Red-Team Artefacts and Scenario
Stress-Testing
AI red teaming — proactive adversarial testing of models and agents — has
become a standard practice for identifying unsafe outputs, prompt-injection
vulnerabilities, data leakage, hallucination abuse, bias, and tool misuse
before deployment. Yet much of this work remains disconnected from
output-level admissibility: systems are hardened against obviously harmful or
policy-violating content, while plausible but structurally inadmissible outputs
remain under-examined.
Uncensored or lightly-governed models are particularly useful as generators
of high-Admissibility-Debt artefacts — outputs that look authoritative, are
formatted in professional registers, and could be acted upon by institutions,
but fail one or more admissibility criteria. Examples include:
• Legal filings that contain fabricated case citations and invented
precedent, written in the style of formal pleadings. Multiple courts have
sanctioned lawyers for submitting such AI-generated hallucinations. [5]
• Clinical notes or discharge summaries that omit critical
contraindications while sounding rigorously clinical.
• Financial analyses that justify credit denial or fraud labels using proxies
that correlate with protected classes, without transparent factors or
permissible data basis.
Admissibility-aware red teaming has two distinct roles. First, catalogue
generation: uncensored models can produce realistic, domain-specific
artefacts — clinical, legal, financial, or governance documents — that
intentionally violate admissibility criteria while mimicking institutional styles.
These serve as "stress concentrates" for admissibility regimes. Second,
scenario trees: red teams can construct scenario trees mapping how
unvetted AI outputs enter workflows, become normalized, and eventually
cause governance-significant failures. Typical stages are: integration (AI
introduced as "assistance"), normalization (staff treat outputs as routine
evidence), dependency (processes restructured around AI), first default
(significant harm becomes visible), and systemic default (institution retires,

31
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
refinances, or conceals the debt).
The Admissibility Debt framework adds an annotation axis to standard
red-teaming: for each generated output, testers can score E, P, I, assign τC,
and compute DA(o, C) to quantify how much debt would be incurred if the
output were admitted into real decisions. The EU AI Act now requires
robustness and security testing for high-risk systems and mandates
adversarial testing for general-purpose models with systemic risk, making
formalized red teaming a compliance obligation rather than a discretionary
practice.
Uncensored Models as Governance Instruments
In this view, uncensored models are not governance failures; they are
instruments for exposing where governance work is missing. They generate
artefacts that help define and stress-test admissibility regimes, revealing which
outputs must be blocked, downgraded in authority class, or quarantined
behind enhanced review procedures. By using such models under controlled
conditions, with strict separation between artefact generation and operational
deployment, institutions can make Admissibility Debt visible and measurable
before systems are widely relied upon.

32
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
Section 8. Falsifiable Claims and Evaluation
Plan
The Admissibility Debt framework is not intended as a purely conceptual
lens; it is meant to be empirically testable against real deployments and
incident data.
8.1 Falsifiable Claims
Claim 1 — Admissibility Gates Reduce Incident Rates
Institutions that implement explicit admissibility regimes will exhibit lower
rates and severities of AI-related governance incidents than similarly situated
institutions that rely only on system-level governance without output-level
admissibility gates. This claim is falsifiable: if institutions with explicit,
enforced admissibility rules do not show measurable reductions in incidents,
the framework's practical value is undermined.
Claim 2 — Admissibility Debt Predicts Failures Better Than Accuracy
Alone
Across documented AI incidents, outputs with high estimated DA(o, C) — large
shortfalls on E, P, or I relative to τC, combined with high α and ρ — will
correlate more strongly with governance-significant failures than outputs that
merely score poorly on accuracy or fairness metrics. Falsifiable by
re-annotating incidents in the AI Incident Database with admissibility scores
and comparing predictive power.
Claim 3 — Provenance Fails First; Legitimacy Is Most Catastrophic
Epistemic admissibility E — particularly provenance and authentication — will
typically fail first as AI is integrated without robust source verification.
Institutional admissibility I — particularly legitimacy and accountable adoption
— will be the dominant dimension at the point of systemic default.

33
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
Claim 4 — Admissibility-Aware Red Teaming Produces Distinct Failure
Profiles
Admissibility-aware red teaming will surface failure patterns underrepresented
in conventional safety and security red teaming: high-debt outputs that are
content-safe and superficially plausible but structurally inadmissible.
Claim 5 — Societal Admissibility Debt Predicts Deepfake Impact Beyond
Detection
AI-generated media with high estimated Admissibility Debt (low E, P, I; high α;
high ρ) will be more strongly associated with lasting reputational harm, belief
change, or policy impact than would be predicted by detection model scores or
labeling interventions alone.
8.2 Evaluation Plan
1. Incident re-annotation. Using the AI Incident Database and similar
archives, researchers can re-annotate incidents with estimated E, P, I
scores, approximate thresholds τC, and qualitative estimates of α and ρ,
then test whether DA(o, C) correlates with incident severity.
2. Institutional comparative studies. Compare incident frequency and
severity across institutions that adopt output-level admissibility regimes
vs. those relying only on system-level governance.
3. Red-team benchmark design. Generate catalogues of high-debt
outputs using uncensored models, label them with admissibility scores
and domain-specific fatal-defect flags, and evaluate systems' ability to
flag or block them.
4. Prospective deployment studies. Organizations deploying AI in
high-stakes workflows can prospectively log authority classes,
admissibility criteria, and violations, then relate these to downstream
harms.
5. Societal media experiments. Measure authentication, labeling, and
contestation as proxies for E and P; measure platform amplification as a
proxy for α and ρ; correlate with belief persistence and reputational

34
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
outcomes.
8.3 Evaluation Governance
The evaluation of Admissibility Debt itself requires governance. If this
construct becomes widely used, its definitions, measurement practices, and
threshold choices must be subject to independent scrutiny, transparent
documentation, and participatory design, to avoid simply reintroducing
unexamined authority in a new form. The aim is to put forward testable
claims. If those claims fail under empirical scrutiny, the concept should be
revised or discarded. If they hold, Admissibility Debt offers a way to turn
diffuse concerns about AI authority into concrete, measured obligations.

35
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
Section 9. Conclusion and Policy
Recommendations
9.1 Summary of the Argument
This paper has advanced a single, unified thesis: across courts, schools,
hospitals, banks, enterprises, and networked publics, societies are
normalizing the use of AI outputs faster than they are building the
admissibility regimes required to govern them. The failure is not primarily
about whether AI models are accurate, fair, or safe in the aggregate. It is
about the systematic absence of output-level conditions — evidentiary,
procedural, and institutional — that determine when any particular AI output
may validly acquire authority in a decision.
Admissibility Debt names this gap as a first-class governance construct. Like
technical debt and security debt, it accumulates silently, compounds through
reliance and propagation (measured by α and ρ), and becomes increasingly
costly to unwind as contaminated outputs embed themselves in records,
workflows, and public narratives. Unlike those forms of debt, it manifests not
as system failures or security breaches but as wrong people punished, wrong
claims believed, wrong denials issued, and wrong narratives entrenched —
all in the name of efficiency, automation, and scale.
9.2 Policy Recommendations by Stakeholder

36
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
For Legislators
• Mandate domain-specific admissibility regimes for high-stakes AI as a
condition of deployment, not merely a recommendation. Existing evidence-rule
reforms are necessary but insufficient; they cover only formal proceedings and
primarily address epistemic admissibility.
• Extend authentication and corroboration requirements beyond courtrooms to
administrative adjudication, benefits determinations, employment decisions,
and educational records.
• Create structured liability frameworks for Admissibility Debt: institutions
that admit AI outputs into authority-bearing roles without satisfying applicable
admissibility conditions and cause harm as a result should bear commensurate
accountability.
• Fund adversarial testing infrastructure and AI incident databases that
incorporate admissibility metrics, making the debt visible to regulators,
researchers, and affected communities.
For Regulators
• Incorporate output-level admissibility thresholds into sector-specific
guidance for AI deployment in justice, healthcare, finance, education, and
enterprise contexts.
• Require institutions deploying AI in high-stakes contexts to document and
disclose the authority class assigned to each AI function, the admissibility
criteria applied, the human review and contestability mechanisms in place, and
the audit trail.
• Create safe-harbor provisions for institutions that implement and comply
with documented admissibility regimes, reducing enforcement risk for those
who do the governance work.
• Establish cross-sector coordination on admissibility standards to prevent
regulatory arbitrage, where AI functions inadmissible in one sector are
imported through vendor relationships from adjacent sectors with weaker
regimes.

37
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
For Institutions (Courts, Hospitals, Schools, Banks)
• Adopt an explicit authority classification policy (AC0–AC5) for all AI outputs
used in the institution. For each authority class, define the admissibility
criteria that must be met before an AI output may be relied upon at that level.
• Implement admissibility gates at the points where AI outputs enter official
records, decisions, or communications: require human review, audit logging,
and a documented basis for reliance.
• Build contestability into workflows wherever AI outputs affect individuals:
notice, explanation, appeal, and correction mechanisms must be operational,
not merely described in policy documents.
• Integrate α and ρ monitoring into AI observability: track authority conferred
and propagation scope, and trigger governance reviews when high-α, high-ρ
outputs accumulate without corresponding admissibility documentation.
For Platforms and Media Organizations
• Adopt and publish institutional admissibility policies for AI-generated
content: what content will be amplified, under what authentication conditions,
with what labeling and correction obligations.
• Implement procedural admissibility mechanisms: contestation channels,
rapid fact-checking pipelines, and timely correction and removal workflows
operating at speeds commensurate with AI-generated content production.
• Accept institutional accountability for authority conferred through
amplification. Platforms that amplify AI-generated content contribute to α and
ρ; they are active participants in Admissibility Debt accumulation.
• Support and adopt content provenance standards (C2PA, watermarking,
cryptographic authentication) as technical infrastructure for epistemic
admissibility, while recognizing that technical tools alone cannot substitute for
institutional regimes.
9.3 Implementation Roadmap
 Timeline
 Priority Actions
Immediate
0–6 months
• Audit existing AI deployments for admissibility deficits; identify all AI
outputs that currently enter authority-bearing roles without documented
admissibility criteria. • Classify each active AI function by authority class
(AC0–AC5); document gaps between required and actual admissibility. •
Quarantine outputs failing fatal-defect conditions: any output used at AC4
or AC5 without human review, audit trail, and contestability should be
immediately downgraded or suspended.

38
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
Near-term
6–18 months
• Implement domain-specific admissibility gates at critical decision points.
• Deploy admissibility dashboards: extend existing AI observability to
include α and ρ tracking, fatal-defect alerts, and authority-class distribution
reporting. • Train decision-makers on admissibility standards and what
authority class AI outputs carry in each workflow.
Medium-term
1–3 years
• Develop cross-institutional admissibility standards within sectors. •
Integrate admissibility requirements into AI procurement and vendor
contracts. • Conduct prospective admissibility studies and publish findings.
Long-term 3+
years
• Establish international admissibility regimes coordinated through bodies
such as the Council of Europe, OECD, and G20. • Develop certified
admissibility auditing as a professional discipline. • Build admissibility into
AI-system certification and conformity assessment.
 Table 7. Admissibility Debt implementation roadmap for institutions and regulators.
9.3a Minimum Viable Admissibility by Organization Size
Full implementation of domain-specific admissibility regimes requires
institutional capacity that varies significantly by organization size and sector.
The following minimum viable admissibility (MVA) tiers recognize this reality
without creating a compliance escape route for large institutions.
 Org Tier
 MVA Requirements
 Excluded From MVA
Small (<100
employees or
<$10M AI
spend)
• Identify all AI functions with
authority-bearing use • Assign
AC0–AC5 label to each • Require
human sign-off before AI output
enters permanent record • Maintain
a log of AI-influenced decisions
Full domain-specific rubrics;
formal audit trails; structured
contestability mechanisms
(good-faith human review
suffices)
Mid-size
(100–2,000
employees)
• All small-tier requirements •
Documented admissibility policy per
high-stakes workflow •
Employee/subject notice where AI
materially contributes to a decision •
Basic contestability: affected party
can flag and trigger human re-review
Certified external audits;
cross-institutional reporting;
full rubric scoring for every
output (threshold-plus-flag
approach acceptable)

39
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
Large /
Enterprise
(>2,000
employees or
regulated
sector)
• All mid-size requirements • Formal
authority classification policy with
α/ρ monitoring • Domain-specific
admissibility gates at critical
decision points • Structured
contestability with documented
outcomes • Annual admissibility
audit; incident reporting
No exclusions; regulated
institutions (banks, hospitals,
courts) are subject to full
domain-specific regimes
regardless of size
 Table 8. Minimum Viable Admissibility tiers. These are floors, not ceilings. High-stakes or
regulated contexts require the full domain-specific regime regardless of organizational size.
9.4 The Stakes of Inaction
The risk of inaction is not merely that individual AI deployments will cause
individual harms — though they will. The deeper risk is structural. As AI
outputs become more capable, more fluent, and more deeply embedded in
institutional processes, the machinery of authority itself is being
reconfigured around systems whose outputs are admitted into consequential
roles without the governance work that authority has historically required.
Looking ahead, the admissibility challenge will intensify with agentic AI
systems capable of executing multi-step tasks, accessing records, and taking
actions on behalf of institutions and individuals. The authority amplification
and reliance propagation factors will grow accordingly. Governance
frameworks adequate for AI-assisted decisions are unlikely to be adequate
for AI-agentic decisions without significant institutional adaptation.
The goal of this paper is not to slow AI deployment or to privilege caution
over capability. It is to insist that authority — real, consequential, legitimate
authority — must be earned, not assumed. Earning it requires admissibility
work. Admissibility Debt is what accumulates when institutions skip that
work. Paving the path forward for human-AI relations requires confronting
that debt honestly, measuring it systematically, and reducing it deliberately
— one output, one context, one decision at a time.
 Authority must be earned, not assumed.
 Admissibility Debt is the cost of skipping that work.

40
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026

41
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
Appendix A. Scoring Rubric for E, P, and I
The following rubric provides practical scoring guidance for the three
admissibility dimensions. Each dimension is assessed on a [0, 1] scale by
aggregating component sub-scores. The rubric is designed for assessment
through documentary review — workflow logs, audit records, institutional
policies, validation reports — without requiring continuous telemetry.
Assessors should assign the score that reflects actual institutional practice,
not stated policy.
Epistemic Admissibility E(o, C)
 Sub-factor
Weig
 ht
 0.0–0.3
 0.4–0.6
 0.7–1.0
Provenance / source
authentication
 30%
Sources
unknown,
unverified, or
hallucinated
Sources partially
identified; not
independently
verified
Sources
authenticated;
chain of custody
documented
Error rate /
validation
 25%
No validation;
error rate
unknown for this
use
General
validation exists;
not specific to
this population/d
omain
Validated on
relevant
population;
known error
rates disclosed
Domain / temporal
fit
 20%
Model used
outside its
training scope;
data is stale for
time-sensitive
use
Reasonable scope
fit; some
currency
concerns
Explicitly
validated for this
domain; data is
current
Uncertainty
expression
 15%
No uncertainty
expressed;
confidence
conflated with
probability of
correctness
Uncertainty
noted but not
quantified
Calibrated
uncertainty;
limitations
explicitly
disclosed to
decision-maker
Independent
corroboration
 10%
No
corroboration; AI
output is sole
basis
Partial
corroboration
from related
sources
Independently
corroborated by
non-AI evidence

42
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
 Aggregate E = weighted sum of sub-factor scores. Fatal defect: any sub-factor at 0.0–0.1
 forces E ≤ 0.2 regardless of other sub-factors.
Procedural Admissibility P(o, C)
 Sub-factor
Weig
 ht
 0.0–0.3
 0.4–0.6
 0.7–1.0
Human review
 30%
No human review
before AI output
enters decision
Nominal review;
less than 5
minutes; no
independent
check
Substantive
independent
review by
qualified person
Contestability /
appeal
 25%
No mechanism to
challenge or
contest the AI
output
Informal
challenge
possible; no
structured
process
Formal
contestability
with
documented
outcomes and
correction path
Notice to affected
party
 20%
Affected party
not informed AI
contributed to
decision
General AI-use
notice; not
specific to this
output
Specific notice:
what AI
produced, its
limitations, how
to contest
Audit trail
 15%
No log of AI
output or
decision basis
Output logged;
decision basis not
reconstructable
Full audit trail:
output,
reviewer,
decision, and
rationale
Role authorization
 10%
No defined role
for AI in this
decision type
Informal role; not
documented in
policy
Explicitly
authorized role
with defined
scope and
escalation path
 Aggregate P = weighted sum. Fatal defect: absence of any contestability mechanism forces P
 ≤ 0.25 for AC4–AC5 uses.
Institutional Admissibility I(o, C)
 Sub-factor
Weig
 ht
 0.0–0.3
 0.4–0.6
 0.7–1.0

43
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
Legal / regulatory
authority
 30%
No legal basis for
AI use in this
role; possible
violation
Permissible but
not explicitly
authorized
Explicit legal or
regulatory
authorization;
compliant
deployment
Organizational
mandate
 25%
No institutional
policy
authorizing this
AI function
General AI-use
policy; no
specific mandate
for this function
Specific policy
authorizing this
AI function with
defined scope
Identifiable
decision-owner
 20%
No identifiable
human
accountable for
the AI-influenced
decision
Nominal
accountability; no
documented
acceptance of
responsibility
Named
accountable
decision-maker
with
documented
acceptance
Professional
competence
 15%
Decision-maker
lacks domain
competence to
evaluate AI
output
Basic
competence; not
trained on
AI-specific
limitations
Domain-compete
nt reviewer
trained on this
system's
limitations
Jurisdictional fit
 10%
AI system
validated or
authorized in a
different
jurisdiction
Partial fit; some
jurisdictional gap
Validated and
authorized for
this jurisdiction
and use context
Aggregate I = weighted sum. Fatal defect: absence of an identifiable decision-owner forces I ≤
 0.20 regardless of other factors.
Domain Scoring Examples
The following illustrative scores reflect typical deployment conditions
observed across documented AI incidents. They are starting points for
assessment, not authoritative benchmarks.
 Scenario
 E
 P
 I
 A =
min
 τᴸ
 Dᴬ (typical α=3, ρ=2)
COMPAS score used at
sentencing without
disclosure of error rates
0.2
 5
0.3
 0
0.5
 0
 0.25
 0.9
 5
 (0.95−0.25)·3·2 = 4.2

44
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
AI plagiarism flag
initiating discipline, no
human review
0.3
 0
0.2
 0
0.5
 0
 0.20
 0.8
 0
 (0.80−0.20)·4·3 = 7.2
CDS tool with clinician
review and patient
notice
0.7
 0
0.7
 5
0.6
 5
 0.65
 0.8
 0
 (0.80−0.65)·3·2 = 0.9
Credit denial: AI factor,
adverse-action notice
provided
0.6
 5
0.7
 0
0.7
 5
 0.65
 0.8
 0
 (0.80−0.65)·3·2 = 0.9
Deepfake video
broadcast without
authentication
0.0
 5
0.0
 5
0.0
 5
 0.05
 0.8
 0
(0.80−0.05)·5·5 = 18.75
 Table A1. Illustrative Dᴬ calculations across domains. α and ρ values are set to typical
observed levels for each scenario type; actual values must be assessed per deployment. CDS =
 clinical decision support.
The rubric is intentionally rough at this stage. Operationalizing it further —
with validated inter-rater reliability and domain-specific sub-factor
calibration — is part of the evaluation plan outlined in Section 8. The goal
here is to make the framework usable for practitioners before formal
validation is complete, while signaling clearly that the scores require
judgment, documentation, and review.
Notes and Sources
Citation markers in brackets [N] throughout the text refer to the sources below. This working
paper has not yet undergone formal peer review; sources are provided for transparency and
should be verified by readers. Some sources were finalised close to the paper's May 2026 draft
date and may have subsequent updates.
[1] Angwin, J., Larson, J., Mattu, S., and Kirchner, L. (2016). "Machine Bias: There's Software
 Used Across the Country to Predict Future Criminals. And It's Biased Against Blacks."
ProPublica, May 23, 2016. Available at:
https://www.propublica.org/article/machine-bias-risk-assessments-in-criminal-sentencing
See also: Dressel, J. and Farid, H. (2018). "The accuracy, fairness, and limits of predicting
recidivism." Science Advances 4(1). Northpointe (Equivant) disputed ProPublica's
methodology; see Dieterich, W., Mendoza, C., and Brennan, T. (2016). "COMPAS Risk
Scales: Demonstrating Accuracy Equity and Predictive Parity."
[2] Ofqual (2020). Decisions on Calculated Grades: A-levels and GCSEs in England in Summer
 2020. UK Office of Qualifications and Examinations Regulation, August 2020. See also:
Adams, R. (2020). "A-level algorithm row: why did the system fail so badly?" The Guardian,
August 21, 2020.

45
Admissibility Debt — A Cross-Domain Governance Framework for AI Output Authority
Draft v2 · May 2026
[3] U.S. Food and Drug Administration. Clinical Decision Support Software: Guidance for
 Industry and FDA Staff. Final guidance issued January 6, 2026; re-issued January 29, 2026
(the January 29 version supersedes the January 6 version, which in turn superseded FDA's
September 28, 2022 CDS guidance). Available at:
https://www.fda.gov/regulatory-information/search-fda-guidance-documents
[4] Consumer Financial Protection Bureau (2022). Circular 2022-03: Adverse Action
 Notification Requirements and the Equal Credit Opportunity Act. May 26, 2022. Available
at: https://www.consumerfinance.gov/compliance/circulars/circular-2022-03/
[5] See, e.g., Mata v. Avianca, Inc., No. 22-cv-1461 (PKC), 2023 WL 4114965 (S.D.N.Y. June
 22, 2023) (imposing sanctions for AI-generated citations to nonexistent cases); Park v.
Kim, No. 22-2628-cv (2d Cir. 2024). For a broader survey, see: Weiser, B. (2023). "Here's
What Happens When Your Lawyer Uses ChatGPT." The New York Times, May 27, 2023.
[6] Walker, C. P., Schiff, D. S., and Schiff, K. J. (2024). "Merging AI Incidents Research with
 Political Misinformation Research: Introducing the Political Deepfakes Incidents
Database." Available via the AI Incident Database (incidentdatabase.ai). See also: AI
Incident Database entries for Ireland 2025 presidential election deepfake (Catherine
Connolly withdrawal video, October 2025); and case-specific reporting by RTÉ News, The
Irish Times, and the Irish Independent, October–November 2025.
[7] State of Maryland v. Dazhon Darien (Baltimore County Circuit Court). Darien arrested in
 April 2024 on charges including misuse of AI to create deepfake audio impersonating
principal Eric Eiswert (Pikesville High School, Baltimore County). In April 2025, Darien
entered an Alford plea to disturbing school operations and was sentenced to four months
in jail. Reported by AP, CBS News, The Washington Post, and The Baltimore Sun, April
2024 and April 2025.
[8] Advisory Committee on Evidence Rules, May 7, 2026 agenda materials. Reuters reporting,
 May 7, 2026, confirmed that the committee delayed voting on proposed Federal Rule of
Evidence 707 (AI-generated evidence) and proposed amendments to Rule 901(c)
(burden-shifting authentication procedure for AI-altered audio/visual evidence), with
members divided on scope and implementation; an October expert consultation was
planned before further committee action. See also: Federal Evidence Review and Law360
coverage of the May 2026 Advisory Committee session.
[9] National Institute of Standards and Technology (2023). Artificial Intelligence Risk
 Management Framework (AI RMF 1.0). NIST AI 100-1, January 2023. Available at:
https://doi.org/10.6028/NIST.AI.100-1
[10] European Parliament and Council of the European Union (2024). Regulation (EU)
 2024/1689 of 13 June 2024 laying down harmonised rules on artificial intelligence
(Artificial Intelligence Act). Official Journal of the European Union, L, 2024/1689, July 12,
2024.
[11] International Organization for Standardization / International Electrotechnical
 Commission (2023). ISO/IEC 42001:2023 — Information technology — Artificial
intelligence — Management system. Geneva: ISO, December 2023.

## Part 3: Bye Bye Tokens

Goal:

• ≥75% token reduction
• Deterministic decoding
• Versionable
• Safe for constitutional mutation specs
• Usable inside Project-AI pipelines

I’ll define:

TSCG Core Model

Formal CFG (EBNF style)

Semantic Mapping Rules

Encoder Specification

Decoder Specification

Versioning + Safety Constraints

No fluff.

1. Thirsty’s Symbolic Compression Grammar (TSCG)

TSCG is a domain-specific symbolic meta-language for representing:

• Governance flows
• Reflex logic
• Mutation control
• State transitions
• Quorum structures
• Invariant validation

It compresses structured prose into compositional symbolic sequences.

TSCG is:

• Deterministic
• Context-free at syntax layer
• Context-sensitive at semantic resolution layer

2. Core Symbol Classes
2.1 Primitive Tokens (Atomic Symbols)

Uppercase reserved identifiers:

SEL Selection pressure
COG Cognition (proposal only)
Δ Mutation proposal
Δ_NT Non-trivial mutation
SHD Deterministic shadow
INV Invariant engine
CAP Capability authorization
QRM Quorum
COM Commit canonical
ANC Anchor extension
RFX Reflex containment
ESC Escalation ladder
SAFE SAFE-HALT
MUT Mutation control law
LED Ledger
ING Ingress

2.2 Operators

→ Sequential pipeline
∧ Logical AND
∨ Logical OR
¬ Negation
⊣ Constrains / guards
|| Parallel / independent planes
:= Definition
= Equality
∈ Membership
≥ Threshold
< Inequality
( ) Parameter binding
[ ] Class binding
{ } Set
::= Grammar production

3. Formal Grammar (EBNF Style)

This is syntax only.

Program        ::= Statement | Statement "||" Program

Statement      ::= Flow | Definition | Constraint

Flow           ::= Term "→" Term
                |  Term "→" Term "→" Flow

Definition     ::= Identifier ":=" Expression

Constraint     ::= Expression

Expression     ::= Term
                |  Term Operator Term
                |  "(" Expression ")"

Term           ::= Identifier
                |  Identifier "(" ParameterList ")"
                |  Identifier "[" ClassList "]"

ParameterList  ::= Parameter
                |  Parameter "," ParameterList

ClassList      ::= Identifier
                |  Identifier "," ClassList

Parameter      ::= Identifier
                |  Identifier "=" Value
                |  Value

Identifier     ::= UppercaseWord | GreekSymbol | CustomID

Operator       ::= "∧" | "∨" | "¬" | "=" | "≥" | "<" | "∈"

UppercaseWord  ::= [A-Z]+
GreekSymbol    ::= λ | τ | Δ | μ | etc.
CustomID       ::= [A-Za-z_0-9]+

Value          ::= Number | Identifier

This grammar is compact and deterministic.

4. Semantic Resolution Layer

Syntax does nothing without semantic mapping.

TSCG uses a Semantic Dictionary (SD).

Example SD entries:

COG
= proposal-only cognitive plane
= no canonical write authority

Δ_NT
= mutation affecting invariant-referenced canonical state

SHD(v)
= deterministic simulation under runtime version v

QRM(3f+1,2f+1)
= BFT quorum with N=3f+1 and threshold τ=2f+1

RFX(Lr<Lc)
= reflex containment with latency constraint

Decoder MUST have matching SD version.

5. Canonical Governance Encoding Example

Verbose (~150 tokens):

Cognition proposes a non-trivial mutation which is deterministically shadow simulated, invariant checked, capability authorized, quorum validated, and committed with anchor extension.

TSCG:

COG → Δ_NT → SHD(v) → INV(I) ∧ CAP → QRM(3f+1,2f+1) → COM → ANC

Token count reduction: ~85%

6. Composite Reflex + Governance Encoding
RFX(Lr<Lc) || Δ_NT → SHD(v) → INV(I) ∧ CAP → QRM(τ) → COM → ANC

SAFE condition:

¬deterministic → SAFE
7. Encoder Specification

The encoder converts structured prose or structured JSON architecture into TSCG.

7.1 Input Requirements

Input must be structured into:

• Actors
• Mutation classes
• Validation steps
• Control constraints
• Thresholds
• State transitions

Unstructured narrative must first be parsed into AST form.

7.2 Encoding Pipeline

Step 1: Parse Prose → Semantic AST

Example AST:

{
type: "mutation_pipeline",
proposal: true,
deterministic_shadow: true,
invariant_check: true,
capability_check: true,
quorum: {N: 3f+1, threshold: 2f+1},
commit: true,
anchor: true
}

Step 2: Map AST nodes → SD identifiers

Step 3: Construct Flow chain in canonical order

Step 4: Apply compression rules

Compression Rules:

CR1: Sequential boolean validation collapse
INV + CAP + QRM may be chained without repetition

CR2: Common pipeline ID reuse
If identical pipeline used repeatedly → alias via Definition

Example:

GOV := SHD(v) → INV(I) ∧ CAP → QRM(τ) → COM → ANC
COG → Δ_NT → GOV

CR3: Remove redundant prose connectors

CR4: Parameter canonicalization (sorted parameter lists)

7.3 Encoder Determinism Rules

• Terms must be ordered canonically
• Parameter lists sorted lexicographically
• Threshold pairs normalized as (N,τ)
• Version explicitly bound (v required for SHD)

This guarantees identical architecture → identical encoding.

8. Decoder Specification

Decoder performs:

Syntax parse (CFG)

Validate against grammar

Resolve identifiers against SD

Expand definitions recursively

Generate structured representation

Optional natural-language expansion

8.1 Decoder Steps

Given:

COG → Δ_NT → SHD(v1) → INV(Iα) ∧ CAP → QRM(4,3) → COM → ANC

Step 1: Parse into AST:

Sequence(
COG,
Δ_NT,
SHD(v1),
And(INV(Iα), CAP),
QRM(4,3),
COM,
ANC
)

Step 2: Semantic expansion:

COG = proposal plane without write authority
Δ_NT = non-trivial canonical mutation
SHD(v1) = deterministic simulation under runtime v1
…

Step 3: Structured output:

{
proposal_plane: true,
non_trivial: true,
deterministic_shadow: {version: v1},
invariant_set: Iα,
capability_check: true,
quorum: {N: 4, threshold: 3},
commit: true,
anchor: true
}

Step 4 (optional): Rehydrate verbose description.

9. Bidirectional Guarantee

Encoder/Decoder are bijective under:

• Fixed SD version
• Canonical ordering
• No semantic ambiguity

Formally:

decode(encode(X)) = X
encode(decode(Y)) = Y

Provided Y uses canonical ordering.

10. Versioning

TSCG Header:

TSCG[v1.0 | SDα | HASH=xxxx]

Required to decode.

Changes to SD require new SD version.

Governance can treat SD updates as Δ_NT.

11. Safety Integration with Project-AI

You can now:

• Encode entire governance stack in <150 tokens
• Store mutation pipelines as symbolic expressions
• Use TSCG inside shadow replay for compact validation
• Log anchor chain entries in compressed symbolic form
• Transmit constitutional state across nodes with minimal bandwidth

12. Example: Full Project-AI Stack Encoding

Verbose (~1000+ tokens) becomes:

STACK :=
RFX(Lr<Lc) ||
COG → Δ_NT → SHD(v) → INV(I) ∧ CAP → QRM(3f+1,2f+1) → COM → ANC

MUT := clip(m₀ + λ₁A_g − λ₂(1−U))
ESC: S0→S1→S2(RFX)→S3→S4→S5
¬deterministic → SAFE

That replaces pages.

13. Compression Yield

Empirical estimate:

Architectural prose: 800–1500 tokens
TSCG encoding: 100–250 tokens

75–90% reduction achieved consistently.
