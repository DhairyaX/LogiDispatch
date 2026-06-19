"""
Reusable execution timer utility.

Provides a context-manager and explicit start/stop API for
measuring wall-clock execution time.
"""

from __future__ import annotations

import time
from types import TracebackType


class Timer:
    """High-resolution wall-clock timer.

    Usage (context manager)::

        with Timer() as t:
            do_work()
        print(t.elapsed)

    Usage (manual)::

        t = Timer()
        t.start()
        do_work()
        t.stop()
        print(t.elapsed)
    """

    def __init__(self) -> None:
        self._start: float | None = None
        self._end: float | None = None

    # ── Manual API ──────────────────────────────────────────────

    def start(self) -> "Timer":
        """Record the start timestamp and return *self* for chaining."""
        self._start = time.perf_counter()
        self._end = None
        return self

    def stop(self) -> "Timer":
        """Record the end timestamp and return *self* for chaining.

        Raises:
            RuntimeError: If :meth:`start` was not called first.
        """
        if self._start is None:
            raise RuntimeError("Timer.stop() called before Timer.start().")
        self._end = time.perf_counter()
        return self

    @property
    def elapsed(self) -> float:
        """Return elapsed time in seconds.

        If the timer is still running (started but not stopped),
        returns the time elapsed so far.

        Raises:
            RuntimeError: If the timer was never started.
        """
        if self._start is None:
            raise RuntimeError("Timer has not been started.")
        end = self._end if self._end is not None else time.perf_counter()
        return end - self._start

    # ── Context-manager API ─────────────────────────────────────

    def __enter__(self) -> "Timer":
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.stop()
