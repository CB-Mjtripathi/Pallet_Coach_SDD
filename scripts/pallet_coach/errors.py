from __future__ import annotations


class ContractError(ValueError):
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.details = details or {}


class SolverError(RuntimeError):
    def __init__(self, message: str, reason_code: str | None = None) -> None:
        super().__init__(message)
        self.reason_code = reason_code
