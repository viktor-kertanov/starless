import time
from functools import wraps
from aiohttp.client_exceptions import ClientConnectionError, ServerDisconnectedError, ServerTimeoutError
from config import starless_logger

def backoff(
        exceptions: tuple = (
            ClientConnectionError,
            TimeoutError,
            ConnectionError,
            ServerDisconnectedError,
            ServerTimeoutError
        ),
        start_sleep_time: float = 0.1,
        factor: int = 2,
        border_sleep_time: int = 20,
):
    """
    Main backoff mechanism, decorator that helps handle connection errors for both ElasticSearch and PostgreSQL.

    Formula:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: initial sleep time in seconds
    :param factor: factor by which we multiply sleep time after each iteration
    :param border_sleep_time: max sleep time after which the growth stops
    :return: result of the funciton
    """
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time = start_sleep_time
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    starless_logger.warning(
                        "#%g. Now we'll sleep for %gs. Error type: %s. Message: %s" %
                        (retries, sleep_time, type(e).__name__, e),
                    )
                    time.sleep(sleep_time)
                    sleep_time = start_sleep_time * factor**retries
                    if sleep_time >= border_sleep_time:
                        sleep_time = border_sleep_time
                    continue
        return inner
    return func_wrapper


@backoff(start_sleep_time=0.2, factor=2, border_sleep_time=50)
def test_backoff():
    """Run this module as __main__ in order to see how @backoff decorator performs during errors"""
    raise ClientConnectionError("Some error message")


if __name__ == '__main__':
    test_backoff()
