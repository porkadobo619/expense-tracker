from .money import Money


class Budget:
    NEAR_THRESHOLD = 0.8

    def __init__(self, category: str, limit: Money):
        self.category = category
        self._limit = limit

    def remaining(self, spent: Money) -> Money:
        return self._limit.subtract(spent)

    def status(self, spent: Money) -> str:
        if spent.centavos > self._limit.centavos:
            return "exceeded"
        if spent.centavos >= self._limit.centavos * self.NEAR_THRESHOLD:
            return "near"
        return "ok"
