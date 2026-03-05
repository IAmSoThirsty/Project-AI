#                                           [2026-03-05 08:49]
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
