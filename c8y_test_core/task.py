"""Task utilities"""
from typing import Any, Callable, Dict, List
from c8y_api import CumulocityApi
from c8y_test_core.timer import RepeatTimer


class BackgroundTask:
    """Background task that can be used to run periodic tasks"""

    # pylint: disable=too-many-arguments

    def __init__(self, client: CumulocityApi) -> None:
        self.client = client
        self._timers: List[RepeatTimer] = []

    def start(
        self,
        target: Callable[[], None],
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
        interval: float = 0.0,
        delay: float = 0.0,
        count: int = 0,
    ):
        """Start a new background task"""
        if interval <= 0:
            raise ValueError("interval needs to be greater than 0")

        timer = RepeatTimer(
            interval=interval,
            count=count,
            delay=delay,
            target=target,
            args=args,
            kwargs=kwargs,
        )
        timer.start()
        self._timers.append(timer)

    def stop(self):
        """Stop all timers"""
        for timer in self._timers:
            timer.cancel()
            timer.join()
