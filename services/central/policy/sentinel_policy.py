from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock


@dataclass
class RateLimit:
    max_calls: int
    window_seconds: int


@dataclass
class PolicyRejection:
    agent: str
    tool: str
    reason: str
    timestamp: datetime


class SentinelPolicy:
    def __init__(
        self,
        policy_map: dict[str, set[str]],
        rate_limits: dict[str, dict[str, RateLimit]] | None = None,
    ) -> None:
        # Freeze sets to prevent external mutation from silently changing enforcement
        self._policy_map: dict[str, frozenset[str]] = {
            k: frozenset(v) for k, v in policy_map.items()
        }
        self._rate_limits: dict[str, dict[str, RateLimit]] = rate_limits or {}
        self._call_log: defaultdict[str, defaultdict[str, deque[datetime]]] = defaultdict(
            lambda: defaultdict(deque)
        )
        self._lock = Lock()

    def check(self, agent: str, tool: str) -> PolicyRejection | None:
        now = datetime.now(timezone.utc)

        if agent not in self._policy_map:
            return PolicyRejection(agent=agent, tool=tool, reason="unknown agent", timestamp=now)

        if tool not in self._policy_map[agent]:
            return PolicyRejection(agent=agent, tool=tool, reason="not authorised", timestamp=now)

        limit = self._rate_limits.get(agent, {}).get(tool)
        if limit is not None:
            with self._lock:
                log = self._call_log[agent][tool]
                cutoff = now.timestamp() - limit.window_seconds
                while log and log[0].timestamp() < cutoff:
                    log.popleft()
                if len(log) >= limit.max_calls:
                    return PolicyRejection(
                        agent=agent, tool=tool, reason="rate limit exceeded", timestamp=now
                    )
                log.append(now)
        else:
            with self._lock:
                self._call_log[agent][tool].append(now)

        return None
