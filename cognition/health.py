#                                           [2026-03-03 13:45]
#                                          Productivity: Active
from dataclasses import dataclass


@dataclass(frozen=True)
class HealthSignal:
    alive: bool
    responsive: bool
    bounded: bool
    compliant: bool

    @property
    def healthy(self) -> bool:
        return all([self.alive, self.responsive, self.bounded, self.compliant])
