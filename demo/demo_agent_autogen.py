#!/usr/bin/env python3.10
"""
INVEXSAI — Loan Approval Agent Demo (AutoGen)
──────────────────────────────────────────────
Live investor demo: AutoGen ConversableAgent wrapped with the INVEXSAI SDK.
Every LLM call is manually logged to the dashboard in real time.

Run:
    export OPENAI_API_KEY=sk-proj-...
    python demo/demo_agent_autogen.py
"""

import asyncio
import logging
import os
import sys
import time
import warnings

# Silence AutoGen / flaml noise
warnings.filterwarnings("ignore")
logging.disable(logging.CRITICAL)     # silence autogen.oai.client WARNING spam
os.environ.setdefault("AUTOGEN_USE_DOCKER", "False")

# ── SDK path ──────────────────────────────────────────────────────────────────
for _p in [
    "/Users/lasyasai/Downloads/invexsai_yash/sdk",
    "/Users/yashkompella/Downloads/invexsai_yash/sdk",
]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from invexsai.client import InvexsaiClient
    from invexsai.types import RegisterRequest, CostRequest
    from invexsai.heartbeat import HeartbeatManager
    from invexsai.pricing import calculate_cost
except ImportError as _e:
    print(f"✗ SDK import failed: {_e}")
    sys.exit(1)

try:
    from autogen import ConversableAgent
except ImportError:
    print("✗ AutoGen not installed. Run:")
    print("  python3.10 -m pip install pyautogen")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────
BACKEND_URL = "http://localhost:8080/v1"
API_KEY     = "invexsai_dev_testkey123"
DASHBOARD_URL = "http://localhost:5174"
MODEL       = "gpt-4o-mini"

# Estimated tokens per call (AutoGen does not expose usage directly in 0.2.x)
PROMPT_TOKENS     = 150
COMPLETION_TOKENS = 50
TOTAL_TOKENS      = 200

# ── The 5 loan applications ───────────────────────────────────────────────────
APPLICATIONS = [
    {
        "n":     1,
        "label": "$25,000 personal loan — credit 780, income $95k",
        "body":  (
            "Loan application: $25,000 personal loan. "
            "Applicant credit score: 780. Annual income: $95,000. "
            "Employment: stable, 5 years at current employer."
        ),
    },
    {
        "n":     2,
        "label": "$180,000 mortgage — credit 620, income $52k",
        "body":  (
            "Loan application: $180,000 mortgage. "
            "Applicant credit score: 620. Annual income: $52,000. "
            "Employment: 8 months at current employer."
        ),
    },
    {
        "n":     3,
        "label": "$8,000 auto loan — credit 710, income $48k",
        "body":  (
            "Loan application: $8,000 auto loan. "
            "Applicant credit score: 710. Annual income: $48,000. "
            "Employment: stable, 3 years at current employer."
        ),
    },
    {
        "n":     4,
        "label": "$50,000 business loan — credit 690, self-employed",
        "body":  (
            "Loan application: $50,000 business loan. "
            "Applicant credit score: 690. Annual income: $120,000. "
            "Self-employed for 2 years. No business collateral provided."
        ),
    },
    {
        "n":     5,
        "label": "$3,500 personal loan — credit 750, income $38k",
        "body":  (
            "Loan application: $3,500 personal loan. "
            "Applicant credit score: 750. Annual income: $38,000. "
            "Employment: stable, 4 years at current employer."
        ),
    },
]

SYSTEM_MSG = (
    "You are a loan approval AI. Analyze each application and respond with: "
    "DECISION: APPROVE or DECISION: DENY, followed by one sentence explaining why. "
    "Be concise."
)

LINE = "━" * 54


async def log_cost(client: InvexsaiClient, agent_id: str, team: str) -> None:
    """Log estimated cost for one LLM call."""
    cost_usd = calculate_cost(MODEL, PROMPT_TOKENS, COMPLETION_TOKENS)
    req = CostRequest(
        agent_id=agent_id,
        model=MODEL,
        prompt_tokens=PROMPT_TOKENS,
        completion_tokens=COMPLETION_TOKENS,
        total_tokens=TOTAL_TOKENS,
        cost_usd=cost_usd,
        team=team,
    )
    try:
        await client.log_cost(req)
    except Exception as exc:
        print(f"  ⚠  Cost log warning: {exc}")


async def main() -> None:
    # ── Guard ────────────────────────────────────────────────────────────────
    if not os.environ.get("OPENAI_API_KEY"):
        print()
        print("  ✗  OPENAI_API_KEY not set. Export it first:")
        print("     export OPENAI_API_KEY=sk-proj-...")
        print()
        sys.exit(1)

    # ── Banner ────────────────────────────────────────────────────────────────
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║       INVEXSAI — Loan Approval Agent Demo            ║")
    print("║       Framework: AutoGen  |  Model: gpt-4o-mini      ║")
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
                name="loan-approval-agent",
                owner="lending-team",
                framework="autogen",
                model=MODEL,
                environment="production",
                tools=["credit_scorer", "income_verifier", "risk_assessor"],
                tags={"team": "lending", "region": "us-west"},
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

    # Immediate heartbeat → dashboard shows HEALTHY now
    try:
        await client.send_heartbeat(agent_id, "healthy", latency_ms=5)
    except Exception:
        pass

    # ── Start heartbeat thread ────────────────────────────────────────────────
    heartbeat = HeartbeatManager(client=client, agent_id=agent_id)
    heartbeat.start()
    print("  ✓ Heartbeat active   — agent status: HEALTHY")

    # ── Build AutoGen agent ───────────────────────────────────────────────────
    config_list = [{"model": MODEL, "api_key": os.environ["OPENAI_API_KEY"]}]
    autogen_agent = ConversableAgent(
        name="loan-approval-agent",
        system_message=SYSTEM_MSG,
        llm_config={"config_list": config_list},
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
    )

    # ── Analyze each application ──────────────────────────────────────────────
    print()
    for app in APPLICATIONS:
        print(LINE)
        print(f"  Analyzing application {app['n']}/5...")
        print(f"  {app['label']}")
        print()
        try:
            reply = autogen_agent.generate_reply(
                messages=[{"role": "user", "content": app["body"]}]
            )
            decision = str(reply).strip() if reply else "(no response)"
            for line in decision.splitlines():
                print(f"  {line}")
            print()
            # Log cost to INVEXSAI dashboard
            await log_cost(client, agent_id, team="lending")
            # Heartbeat each iteration
            try:
                await client.send_heartbeat(agent_id, "healthy", latency_ms=10)
            except Exception:
                pass
            print("  ✓ Cost logged to dashboard ✓")
        except Exception as exc:
            print(f"  ✗ Analysis error: {exc}")

        if app["n"] < 5:
            await asyncio.sleep(2)

    # Let any pending HTTP calls finish
    await asyncio.sleep(1)

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    print(LINE)
    print()
    total_cost = calculate_cost(MODEL, PROMPT_TOKENS * 5, COMPLETION_TOKENS * 5)
    print("  Demo complete.")
    print("  5 loan applications analyzed")
    print(f"  Estimated total cost: ${total_cost:.6f}")
    print("  All cost events logged to INVEXSAI")
    print(f"  Open dashboard to see real-time data: {DASHBOARD_URL}")
    print()

    # ── Cleanup ───────────────────────────────────────────────────────────────
    heartbeat.stop()
    try:
        await client.close()
    except RuntimeError:
        pass


if __name__ == "__main__":
    asyncio.run(main())
