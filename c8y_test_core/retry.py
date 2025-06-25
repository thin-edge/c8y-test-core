"""Retry utils"""
import logging
import re
from functools import wraps
from typing import Dict, Any
from c8y_test_core.errors import FinalAssertionError
from tenacity import (
    RetryError,
    Retrying,
    retry,
    RetryCallState,
)
from tenacity.wait import (
    wait_fixed,
)
from tenacity.stop import (
    stop_after_delay,
)
from tenacity.retry import (
    retry_if_exception_type,
    retry_if_not_exception_type,
)
from requests.exceptions import RequestException

log = logging.getLogger("c8y")


def strip_retry_parameters(options: Dict[str, Any]) -> Dict[str, Any]:
    """Strip any keys from a given dictionary which are related
    to the retry mechanism
    """
    output = options.copy()
    output.pop("timeout", None)
    output.pop("wait", None)
    return output


def configure_retry(obj: object, func_name: str, **kwargs):
    """Configure retry mechanism to a function"""
    wait = float(kwargs.pop("wait", 2))
    timeout = float(kwargs.pop("timeout", 30))

    decorator = retry(
        retry=retry_if_exception_type(AssertionError),
        stop=(stop_after_delay(timeout)),
        wait=wait_fixed(wait),
        reraise=True,
    )
    setattr(obj, func_name, decorator(getattr(obj, func_name)))


def configure_retry_on_members(obj: object, pattern: str, **kwargs):
    """Configure retry mechanism to all functions matching a pattern"""
    # apply retry mechanism
    pattern_re = re.compile(pattern)
    for name in dir(obj):
        if pattern_re.match(name, pos=0):

            def wrapper(func):
                @wraps(func)
                def retry_custom(*args, **kwargs):
                    return retrier(func, *args, **kwargs)

                return retry_custom

            setattr(obj, name, wrapper(getattr(obj, name)))


def before_first_attempt(retry_state: RetryCallState):
    """Before retry setup

    The function is called before the first attempt
    """
    log.debug("Setting up retry: retry_state=%s", retry_state)


def after_failed_attempt(retry_state: RetryCallState):
    """Callback after each failed attempt"""
    log.info(
        "Failed attempt [attempt=%d]: retry_state=%s",
        retry_state.attempt_number,
        retry_state,
    )


def retrier(func, *args, **kwargs):
    attempt = None
    wait = float(kwargs.pop("wait", 2))
    timeout = float(kwargs.pop("timeout", 30))
    try:
        for attempt in Retrying(
            retry=(
                retry_if_exception_type((AssertionError, RequestException, OSError))
                & retry_if_not_exception_type(FinalAssertionError)
            ),
            stop=(stop_after_delay(timeout)),
            wait=wait_fixed(wait),
            reraise=True,
            before=before_first_attempt,
            after=after_failed_attempt,
        ):
            with attempt:
                if attempt.retry_state.attempt_number > 0:
                    log.debug(
                        "[attempt=%d] Executing %s",
                        attempt.retry_state.attempt_number,
                        func.__name__,
                    )
                result = func(*args, **kwargs)
                log.info(
                    "[attempt=%d] Successful %s",
                    attempt.retry_state.attempt_number,
                    func.__name__,
                )
                return result
    except RetryError as ex:
        raise ex
    except Exception as ex:
        # Append additional context information
        if attempt:
            message = (
                f"Retries ended. duration={attempt.retry_state.seconds_since_start:.3f}s, "
                f"attempts={attempt.retry_state.attempt_number}, "
                f"timeout={timeout:.3f}s, wait={wait:.3f}s"
            )
            raise ex from AssertionError(message)
        raise ex from AssertionError("Retries ended")
