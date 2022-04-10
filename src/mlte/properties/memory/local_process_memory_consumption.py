"""
Memory consumption measurement for local training processes.
"""

import time
import subprocess
from typing import Dict, Any

from ..property import Property
from ...platform.os import is_windows


class MemoryStatistics:
    """
    The MemoryStatistics class encapsulates data
    and functionality for tracking and updating memory
    consumption statistics for a running process.
    """

    def __init__(self, avg: float, min: int, max: int):
        """
        Initialize a MemoryStatistics instance.

        :param avg: The average memory consumtion (bytes)
        :type avg: float
        :param min: The minimum memory consumption (bytes)
        :type avg: float
        :param max: The maximum memory consumption (bytes)
        :type max: float
        """
        # The statistics
        self.avg = avg
        self.min = min
        self.max = max

    def __str__(self) -> str:
        """Return a string representation of MemoryStatistics."""
        s = ""
        s += f"Average: {int(self.avg)}\n"
        s += f"Minimum: {self.min}\n"
        s += f"Maximum: {self.max}"
        return s


def _get_memory_usage(pid: int) -> int:
    """
    Get the current memory usage for the process with `pid`.

    :param pid: The identifier of the process
    :type pid: int

    :return: The current memory usage in KB
    :rtype: int
    """
    # sudo pmap 917 | tail -n 1 | awk '/[0-9]K/{print $2}'
    try:
        with subprocess.Popen(
            ["pmap", f"{pid}"], stdout=subprocess.PIPE
        ) as pmap, subprocess.Popen(
            ["tail", "-n", "1"], stdin=pmap.stdout, stdout=subprocess.PIPE
        ) as tail:
            used = subprocess.check_output(
                ["awk", "/[0-9]K/{print $2}"], stdin=tail.stdout
            )
        return int(used.decode("utf-8").strip()[:-1])
    except ValueError:
        return 0


class LocalProcessMemoryConsumption(Property):
    """Measure memory consumption for a local training process."""

    def __init__(self):
        """Initialize a LocalProcessMemoryConsumption instance."""
        super().__init__("LocalProcessMemoryConsumption")
        if is_windows():
            raise RuntimeError(
                f"Property {self.name} is not supported on Windows."
            )

    def evaluate(self, pid: int, poll_interval: int = 1) -> MemoryStatistics:
        """
        Monitor memory consumption of process at `pid` until exit.

        :param pid: The process identifier
        :type pid: int
        :param poll_interval: The poll interval, in seconds
        :type poll_interval: int

        :return The collection of memory usage statistics
        :rtype: MemoryStatistics
        """
        return LocalProcessMemoryConsumption._semantics(
            self._evaluate(pid, poll_interval)
        )

    def _evaluate(self, pid: int, poll_interval: int) -> Dict[str, Any]:
        """See evaluate()."""
        stats = []
        while True:
            kb = _get_memory_usage(pid)
            if kb == 0:
                break
            stats.append(kb)
            time.sleep(poll_interval)

        return {
            "avg_consumption": sum(stats) / len(stats),
            "min_consumption": min(stats),
            "max_consumption": max(stats),
        }

    @staticmethod
    def _semantics(output: Dict[str, Any]) -> MemoryStatistics:
        """Provide semantics for property output."""
        assert "avg_consumption" in output, "Broken invariant."
        assert "min_consumption" in output, "Broken invariant."
        assert "max_consumption" in output, "Broken invariant."
        return MemoryStatistics(
            avg=output["avg_consumption"],
            min=output["min_consumption"],
            max=output["max_consumption"],
        )
