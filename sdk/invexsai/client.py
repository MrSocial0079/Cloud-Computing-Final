import httpx
import logging
from typing import Optional
from .types import RegisterRequest, RegisterResponse, CostRequest, HeartbeatRequest

logger = logging.getLogger(__name__)


class InvexsaiClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8080/v1",
        timeout: float = 5.0,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    def _get_headers(self) -> dict:
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def register_agent(self, req: RegisterRequest) -> Optional[RegisterResponse]:
        try:
            client = await self._get_client()
            resp = await client.post(
                f"{self.base_url}/agents/register",
                json=req.__dict__,
                headers=self._get_headers(),
            )
            resp.raise_for_status()
            data = resp.json()
            return RegisterResponse(**data)
        except Exception as e:
            logger.warning(f"INVEXSAI: register failed: {e}")
            return None

    async def log_cost(self, req: CostRequest) -> bool:
        try:
            client = await self._get_client()
            payload = {k: v for k, v in req.__dict__.items() if v is not None}
            resp = await client.post(
                f"{self.base_url}/agents/cost",
                json=payload,
                headers=self._get_headers(),
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            logger.warning(f"INVEXSAI: cost log failed: {e}")
            return False

    async def send_heartbeat(
        self,
        agent_id: str,
        status: str = "healthy",
        latency_ms: Optional[int] = None,
    ) -> bool:
        try:
            client = await self._get_client()
            payload: dict = {"agent_id": agent_id, "status": status}
            if latency_ms is not None:
                payload["latency_ms"] = latency_ms
            resp = await client.post(
                f"{self.base_url}/agents/heartbeat",
                json=payload,
                headers=self._get_headers(),
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            logger.warning(f"INVEXSAI: heartbeat failed: {e}")
            return False

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
