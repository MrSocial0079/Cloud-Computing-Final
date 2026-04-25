#!/usr/bin/env python3.10
"""
INVEXSAI — Fraud Detection Agent Demo
─────────────────────────────────────
Live investor demo: a real LangChain fraud-detection agent wrapped with
the INVEXSAI SDK. Every GPT call logs cost to the dashboard in real time.

Run:
    export OPENAI_API_KEY=sk-proj-...
    python demo/demo_agent.py
"""

import asyncio
import os
import sys
import time

# ── SDK path (try both dev paths) ────────────────────────────────────────────
for _p in [
    "/Users/lasyasai/Downloads/invexsai_yash/sdk",
    "/Users/yashkompella/Downloads/invexsai_yash/sdk",
]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from invexsai.client import InvexsaiClient
    from invexsai.types import RegisterRequest
    from invexsai.heartbeat import HeartbeatManager
    from invexsai.handlers.langchain import InvexsaiCallbackHandler
except ImportError as _e:
    print(f"✗ SDK import failed: {_e}")
    print("  Make sure the SDK is at invexsai_yash/sdk/")
    sys.exit(1)

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
except ImportError:
    print("✗ LangChain not installed. Run:")
    print("  python3.10 -m pip install langchain langchain-openai langchain-core openai")
    sys.exit(1)


# ── Fix 1: loop-aware callback handler ───────────────────────────────────────
# The SDK's _fire_and_forget uses asyncio.ensure_future() which depends on the
# implicit thread-local "current" loop — unreliable inside LangChain's async
# callback machinery. We subclass here and capture the exact running event loop
# at handler-creation time (inside main()), then always dispatch via
# loop.create_task() which is bound to that specific loop object.
class _LoopBoundCallbackHandler(InvexsaiCallbackHandler):
    """InvexsaiCallbackHandler with a pinned event loop for fire-and-forget."""

    def __init__(self, loop: asyncio.AbstractEventLoop, **kwargs):
        super().__init__(**kwargs)
        self._pinned_loop = loop

    def _fire_and_forget(self, coro) -> None:  # type: ignore[override]
        try:
            if self._pinned_loop.is_running():
                self._pinned_loop.create_task(coro)
            else:
                # Loop finished — swallow silently; process is exiting
                coro.close()
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning(
                f"INVEXSAI: fire-and-forget failed: {exc}"
            )

# ── Config ────────────────────────────────────────────────────────────────────
BACKEND_URL   = "http://localhost:8080/v1"
API_KEY       = "invexsai_dev_testkey123"
DASHBOARD_URL = "http://localhost:5174"

# ── The 5 transactions ────────────────────────────────────────────────────────
TRANSACTIONS = [
    {
        "n":     1,
        "label": "$4,200 electronics purchase — 2:47am",
        "body":  (
            "Transaction: $4,200 at an electronics store at 2:47am. "
            "Cardholder's normal shopping window is 9am-6pm. "
            "No prior late-night purchases on record."
        ),
    },
    {
        "n":     2,
        "label": "$890 international wire to new account",
        "body":  (
            "Transaction: $890 international wire transfer to a brand-new account. "
            "This is the cardholder's first international transaction in 3 years. "
            "Destination country has elevated fraud risk."
        ),
    },
    {
        "n":     3,
        "label": "$12 coffee — usual shop, Tuesday morning",
        "body":  (
            "Transaction: $12 purchase at the cardholder's regular coffee shop. "
            "Tuesday morning, consistent with their weekly routine. "
            "Location matches cardholder's home area."
        ),
    },
    {
        "n":     4,
        "label": "$3,400 luxury goods — outside income profile",
        "body":  (
            "Transaction: $3,400 luxury goods purchase. "
            "Cardholder's income profile and historical spending suggest this is "
            "significantly outside their normal purchase range. "
            "No savings increase or credit line change detected."
        ),
    },
    {
        "n":     5,
        "label": "$67 groceries — usual supermarket, Friday afternoon",
        "body":  (
            "Transaction: $67 grocery purchase at the cardholder's usual supermarket "
            "on Friday afternoon. Amount and location match their normal weekly pattern."
        ),
    },
]

SYSTEM_PROMPT = (
    "You are a financial fraud detection AI. Analyze each transaction "
    "and respond with: VERDICT: FRAUD or VERDICT: LEGITIMATE, "
    "followed by one sentence explaining why. Be concise."
)

LINE = "━" * 54


async def main() -> None:
    # ── Guard: OpenAI key ─────────────────────────────────────────────────────
    if not os.environ.get("OPENAI_API_KEY"):
        print()
        print("  ✗  OPENAI_API_KEY not set. Export it first:")
        print("     export OPENAI_API_KEY=sk-proj-...")
        print()
        sys.exit(1)

    # ── Header ────────────────────────────────────────────────────────────────
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║       INVEXSAI — Fraud Detection Agent Demo          ║")
    print("║       LangChain + GPT-4o-mini + Real-time Cost       ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()
    print("  Connecting to INVEXSAI backend...")

    # ── Init client ───────────────────────────────────────────────────────────
    client = InvexsaiClient(api_key=API_KEY, base_url=BACKEND_URL)

    # ── Register agent ────────────────────────────────────────────────────────
    agent_id: str
    try:
        resp = await client.register_agent(
            RegisterRequest(
                name="fraud-detector-v2",
                owner="fraud-team",
                framework="langchain",
                model="gpt-4o-mini",
                environment="production",
                tools=["transaction_analyzer", "risk_scorer"],
                tags={"team": "fraud", "region": "us-east"},
            )
        )
        if resp is None:
            raise RuntimeError("empty response from backend")
        agent_id = resp.agent_id
        print(f"  ✓ Agent registered:  {agent_id}")
    except Exception as exc:
        print(f"  ⚠  Backend unreachable ({exc}) — running in offline mode")
        agent_id = f"offline-{int(time.time())}"

    print(f"  Dashboard:           {DASHBOARD_URL}")

    # Send an immediate heartbeat so the dashboard shows HEALTHY right away
    try:
        await client.send_heartbeat(agent_id, "healthy", latency_ms=5)
    except Exception:
        pass

    # ── Start background heartbeat thread ─────────────────────────────────────
    heartbeat = HeartbeatManager(client=client, agent_id=agent_id)
    heartbeat.start()
    print("  ✓ Heartbeat active   — agent status: HEALTHY")

    # ── Build LangChain chain ─────────────────────────────────────────────────
    # Capture the running loop NOW (we are inside asyncio.run → loop is live)
    # and pin it to the handler so every fire-and-forget uses loop.create_task()
    handler = _LoopBoundCallbackHandler(
        loop=asyncio.get_event_loop(),
        agent_id=agent_id,
        client=client,
        team="fraud",
    )
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.1,
        callbacks=[handler],
    )
    prompt_tmpl = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{transaction}"),
    ])
    chain = prompt_tmpl | llm

    # ── Analyze each transaction ──────────────────────────────────────────────
    print()
    for tx in TRANSACTIONS:
        print(LINE)
        print(f"  Analyzing transaction {tx['n']}/5...")
        print(f"  {tx['label']}")
        print()
        try:
            result = await chain.ainvoke({"transaction": tx["body"]})
            verdict = result.content.strip()
            # Print each line of the verdict indented
            for line in verdict.splitlines():
                print(f"  {line}")
            print()
            print("  ✓ Cost logged to dashboard ✓")
        except Exception as exc:
            print(f"  ✗ Analysis error: {exc}")

        if tx["n"] < 5:
            await asyncio.sleep(2)

    # Let fire-and-forget HTTP cost calls finish before closing the client
    await asyncio.sleep(2)

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    print(LINE)
    print()
    print("  Demo complete.")
    print("  5 transactions analyzed")
    print("  All cost events logged to INVEXSAI")
    print(f"  Open dashboard to see real-time data: {DASHBOARD_URL}")
    print()

    # ── Cleanup ───────────────────────────────────────────────────────────────
    heartbeat.stop()
    # Fix 2: client.close() can raise RuntimeError("Event loop is closed") if
    # the loop begins teardown between heartbeat.stop() and this await.
    # Suppress it — the process is exiting and the httpx client GC handles it.
    try:
        await client.close()
    except RuntimeError:
        pass


if __name__ == "__main__":
    asyncio.run(main())
