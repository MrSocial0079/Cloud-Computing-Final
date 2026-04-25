import asyncio
import concurrent.futures
import logging
from typing import Optional

from .client import InvexsaiClient
from .handlers.langchain import InvexsaiCallbackHandler
from .handlers.autogen import InvexsaiAutoGenHook
from .heartbeat import HeartbeatManager
from .pricing import calculate_cost
from .types import RegisterRequest, RegisterResponse, CostRequest, HeartbeatRequest

logger = logging.getLogger(__name__)


def init(
    api_key: str,
    agent_name: str,
    owner: str = "default",
    framework: str = "langchain",
    model: str = "gpt-4o",
    environment: str = "development",
    base_url: str = "http://localhost:8080/v1",
    start_heartbeat: bool = True,
    team: Optional[str] = None,
) -> dict:
    """
    Initialize INVEXSAI for an agent. Registers it and starts heartbeat.

    Returns dict with:
    - client: InvexsaiClient
    - agent_id: str
    - handler: InvexsaiCallbackHandler (for LangChain)
    - heartbeat: HeartbeatManager
    """
    client = InvexsaiClient(api_key=api_key, base_url=base_url)

    req = RegisterRequest(
        name=agent_name,
        owner=owner,
        framework=framework,
        model=model,
        environment=environment,
    )

    resp = None
    try:
        try:
            asyncio.get_running_loop()
            # Inside a running event loop — use a thread
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, client.register_agent(req))
                resp = future.result(timeout=10)
        except RuntimeError:
            resp = asyncio.run(client.register_agent(req))
    except Exception as e:
        logger.warning(f"INVEXSAI: registration failed: {e}")

    agent_id = resp.agent_id if resp else f"unknown-{agent_name}"

    handler = InvexsaiCallbackHandler(
        agent_id=agent_id,
        client=client,
        team=team,
    )

    heartbeat = HeartbeatManager(client=client, agent_id=agent_id)
    if start_heartbeat:
        heartbeat.start()

    logger.info(f"INVEXSAI: initialized agent '{agent_name}' -> {agent_id}")

    return {
        "client": client,
        "agent_id": agent_id,
        "handler": handler,
        "heartbeat": heartbeat,
    }


__all__ = [
    "InvexsaiClient",
    "InvexsaiCallbackHandler",
    "InvexsaiAutoGenHook",
    "HeartbeatManager",
    "calculate_cost",
    "init",
    "RegisterRequest",
    "CostRequest",
    "HeartbeatRequest",
]
