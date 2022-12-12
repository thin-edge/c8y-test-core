"""Global fixtures"""
import threading
import time
from typing import Any, Dict, List


class RepeatTimer(threading.Thread):
    """Repeat timer which runs the given target at an interval until cancel is called"""

    # pylint: disable=too-many-instance-attributes,too-many-arguments
    def __init__(
        self,
        target: Any,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
        delay: float = 0.0,
        interval: float = 10.0,
        count: int = None,
        event: threading.Event = None,
    ):
        threading.Thread.__init__(self)
        self.stopped = event or threading.Event()
        self.target = target
        self.interval = interval or 0.5
        self.delay = delay
        self.max_count = count or 0
        self._count = 0
        self.target_args = args or []
        self.target_kwargs = kwargs or {}

    def cancel(self):
        """Stop the timer"""
        self.stopped.set()

    def run(self):
        next_at = time.monotonic() + self.delay
        while not self.stopped.wait(0.5):
            if time.monotonic() >= next_at:
                self.target(*self.target_args, **self.target_kwargs)
                next_at += self.interval
                self._count += 1

                if self.max_count > 0 and self._count > self.max_count:
                    break
