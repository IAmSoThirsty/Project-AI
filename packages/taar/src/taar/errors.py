"""Explicit TAAR exception types. Expected failures are never anonymous."""


class TaarError(Exception):
    """Base class for all TAAR errors."""


class ConfigError(TaarError):
    pass


class RegistryError(TaarError):
    pass


class AdmissionDenied(TaarError):
    def __init__(self, reasons: list[str]):
        super().__init__("; ".join(reasons))
        self.reasons = reasons


class LockError(TaarError):
    pass


class EvidenceError(TaarError):
    pass


class ClassificationError(TaarError):
    pass


class QuarantineError(TaarError):
    pass


class CommandExecutionError(TaarError):
    pass
