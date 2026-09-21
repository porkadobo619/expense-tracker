from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    centavos: int

    @classmethod
    def of(cls, pesos: float) -> "Money":
        return cls(round(pesos * 100))

    def add(self, other: "Money") -> "Money":
        return Money(self.centavos + other.centavos)

    def subtract(self, other: "Money") -> "Money":
        return Money(self.centavos - other.centavos)

    def __str__(self) -> str:
        return f"PHP {self.centavos / 100:,.2f}"
