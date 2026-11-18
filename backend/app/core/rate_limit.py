"""Brute-force protection for sign-in: limits FAILED attempts per account and per client IP.

In memory, per process: enough for the single-worker deploy (one uvicorn process behind Caddy). With several
workers or servers each one counts separately; move the counters to Redis/Postgres if that ever matters.
"""
import threading
import time
from collections import defaultdict, deque
from math import ceil

from app.core.config import get_settings


class LoginRateLimiter:
    def __init__(self, max_per_account: int, max_per_ip: int, window_seconds: int, clock=time.monotonic):
        self.max_per_account = max_per_account
        self.max_per_ip = max_per_ip
        self.window = window_seconds
        self.clock = clock
        self._failures: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def _recent(self, key: str, now: float) -> deque[float]:
        q = self._failures[key]
        while q and q[0] <= now - self.window:
            q.popleft()
        if not q:
            self._failures.pop(key, None)
            return deque()
        return q

    def blocked_for(self, ip: str, email: str) -> int:
        """Seconds until another attempt is allowed (0 = allowed now)."""
        now = self.clock()
        with self._lock:
            wait = 0.0
            for key, limit in ((f"acct:{email}", self.max_per_account), (f"ip:{ip}", self.max_per_ip)):
                q = self._recent(key, now)
                if len(q) >= limit:
                    # blocked until enough old failures leave the window
                    wait = max(wait, q[len(q) - limit] + self.window - now)
            return ceil(wait) if wait > 0 else 0

    def record_failure(self, ip: str, email: str) -> None:
        now = self.clock()
        with self._lock:
            for key in (f"acct:{email}", f"ip:{ip}"):
                self._recent(key, now)
                self._failures[key].append(now)

    def record_success(self, email: str) -> None:
        """A correct password clears the account's failures (the IP's stay, so one good account can't reset a spray)."""
        with self._lock:
            self._failures.pop(f"acct:{email}", None)

    def reset(self) -> None:
        with self._lock:
            self._failures.clear()


_settings = get_settings()
login_limiter = LoginRateLimiter(
    max_per_account=_settings.login_max_failures_per_account,
    max_per_ip=_settings.login_max_failures_per_ip,
    window_seconds=_settings.login_window_seconds,
)


def get_login_limiter() -> LoginRateLimiter:
    return login_limiter
