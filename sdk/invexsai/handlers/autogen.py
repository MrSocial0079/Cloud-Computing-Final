import asyncio
import uuid
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class InvexsaiAutoGenHook:
    """
    Wraps an AutoGen ConversableAgent to track LLM costs.

    Usage:
        from invexsai.handlers.autogen import InvexsaiAutoGenHook

        hook = InvexsaiAutoGenHook(agent_id="your-agent-uuid", client=client)
        hook.attach(your_autogen_agent)
    """

    def __init__(
        self,
        agent_id: str,
        client,
        trace_id: Optional[str] = None,
        team: Optional[str] = None,
    ):
        self.agent_id = agent_id
        self.client = client
        self.trace_id = trace_id or str(uuid.uuid4())
        self.team = team

    def attach(self, agent):
        """Attach to a ConversableAgent by wrapping generate_reply."""
        original_generate_reply = agent.generate_reply
        hook = self

        async def tracked_generate_reply(*args, **kwargs):
            import time
            start = time.time()
            result = await original_generate_reply(*args, **kwargs)
            try:
                cost_info = getattr(agent, "last_message_cost", None)
                if cost_info:
                    from ..types import CostRequest
                    from ..pricing import calculate_cost
                    req = CostRequest(
                        agent_id=hook.agent_id,
                        model=cost_info.get("model", "unknown"),
                        prompt_tokens=cost_info.get("prompt_tokens", 0),
                        completion_tokens=cost_info.get("completion_tokens", 0),
                        total_tokens=cost_info.get("total_tokens", 0),
                        cost_usd=cost_info.get("cost", 0.0),
                        trace_id=hook.trace_id,
                        team=hook.team,
                    )
                    try:
                        loop = asyncio.get_running_loop()
                        asyncio.ensure_future(hook.client.log_cost(req))
                    except RuntimeError:
                        asyncio.run(hook.client.log_cost(req))
            except Exception as e:
                logger.warning(f"INVEXSAI AutoGen: tracking failed: {e}")
            return result

        agent.generate_reply = tracked_generate_reply
        logger.debug(f"INVEXSAI: attached to AutoGen agent {agent.name}")
        return agent
