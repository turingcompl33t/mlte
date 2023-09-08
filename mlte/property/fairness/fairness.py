"""
Fairness property definition.
"""

from mlte._private.text import cleantext
from mlte.property import Property


class Fairness(Property):
    """
    The Fairness property reflects the cost of model storage.
    """

    def __init__(self, rationale: str):
        """Initialize a Fairness instance."""
        super().__init__(
            self.__class__.__name__,
            cleantext(
                """
                TODO
                """
            ),
            rationale,
        )
