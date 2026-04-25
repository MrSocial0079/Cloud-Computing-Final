import asyncio
import time
import uuid
import logging
from typing import Any, Dict, List, Optional, Union

from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import LLMResult

from ..client import InvexsaiClient
from ..pricing import calculate_cost, get_model_display_name
from ..types import CostRequest

logger = logging.getLogger(__name__)


class InvexsaiCallbackHandler(BaseCallbackHandler):
    """
    Add this to any LangChain agent to get full cost and health visibility.
    Zero latency impact. All HTTP calls are fire-and-forget async.

    Usage:
        from invexsai.handlers.langchain import InvexsaiCallbackHandler
        from invexsai import InvexsaiClient

        client = InvexsaiClient(api_key="your-key")
        handler = InvexsaiCallbackHandler(agent_id="your-agent-uuid", client=client)
        agent = AgentExecutor(agent=..., tools=..., callbacks=[handler])
    """

    def __init__(
        self,
        agent_id: str,
        client: InvexsaiClient,
        trace_id: Optional[str] = None,
        team: Optional[str] = None,
        mcp_server_origin: Optional[str] = None,
    ):
        super().__init__()
        self.agent_id = agent_id
        self.client = client
        self.trace_id = trace_id or str(uuid.uuid4())
        self.team = team
        self.mcp_server_origin = mcp_server_origin
        self._call_start_times: Dict[str, float] = {}
        self._serialized_cache: Dict[str, Dict] = {}

    def _fire_and_forget(self, coro) -> None:
        """Schedule a coroutine without blocking. Never raises."""
        try:
            loop = asyncio.get_running_loop()
            asyncio.ensure_future(coro)
        except RuntimeError:
            try:
                asyncio.run(coro)
            except Exception as e:
                logger.warning(f"INVEXSAI: fire-and-forget failed: {e}")
        except Exception as e:
            logger.warning(f"INVEXSAI: fire-and-forget failed: {e}")

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        **kwargs: Any,
    ) -> None:
        run_id = str(kwargs.get("run_id", ""))
        self._call_start_times[run_id] = time.time()
        self._serialized_cache[run_id] = serialized

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        try:
            run_id = str(kwargs.get("run_id", ""))
            self._call_start_times.pop(run_id, None)
            serialized = self._serialized_cache.pop(run_id, {})

            llm_output = response.llm_output or {}
            usage = (
                llm_output.get("token_usage")
                or llm_output.get("usage")
                or llm_output.get("usageMetadata")
                or {}
            )

            prompt_tokens = int(
                usage.get("prompt_tokens")
                or usage.get("input_tokens")
                or usage.get("promptTokenCount")
                or 0
            )
            completion_tokens = int(
                usage.get("completion_tokens")
                or usage.get("output_tokens")
                or usage.get("candidatesTokenCount")
                or 0
            )
            total_tokens = int(
                usage.get("total_tokens")
                or (prompt_tokens + completion_tokens)
            )

            model_raw = (
                llm_output.get("model_name")
                or llm_output.get("model")
                or serialized.get("kwargs", {}).get("model_name")
                or serialized.get("kwargs", {}).get("model")
                or "unknown"
            )
            model = get_model_display_name(str(model_raw))
            cost = calculate_cost(model, prompt_tokens, completion_tokens)

            req = CostRequest(
                agent_id=self.agent_id,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost_usd=cost,
                trace_id=self.trace_id,
                team=self.team,
                mcp_server_origin=self.mcp_server_origin,
            )
            self._fire_and_forget(self.client.log_cost(req))
        except Exception as e:
            logger.warning(f"INVEXSAI: on_llm_end failed: {e}")

    def on_llm_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        **kwargs: Any,
    ) -> None:
        run_id = str(kwargs.get("run_id", ""))
        self._call_start_times.pop(run_id, None)
        self._serialized_cache.pop(run_id, None)

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs: Any,
    ) -> None:
        run_id = str(kwargs.get("run_id", ""))
        self._call_start_times[f"tool_{run_id}"] = time.time()

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        try:
            run_id = str(kwargs.get("run_id", ""))
            tool_name = kwargs.get("name") or "unknown_tool"
            req = CostRequest(
                agent_id=self.agent_id,
                model="tool",
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                cost_usd=0.0,
                tool_name=tool_name,
                trace_id=self.trace_id,
                team=self.team,
            )
            self._fire_and_forget(self.client.log_cost(req))
            self._call_start_times.pop(f"tool_{run_id}", None)
        except Exception as e:
            logger.warning(f"INVEXSAI: on_tool_end failed: {e}")
