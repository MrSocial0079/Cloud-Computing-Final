#!/usr/bin/env python3.10
"""
INVEXSAI — Insurance Claims Processor Demo (CrewAI)
────────────────────────────────────────────────────
Live investor demo: CrewAI agent wrapped with the INVEXSAI SDK.
Every LLM call is manually logged to the dashboard in real time.

Run:
    export OPENAI_API_KEY=sk-proj-...
    python demo/demo_agent_crewai.py
"""

import asyncio
import logging
import os
import sys
import time
import warnings

# Suppress verbose CrewAI / telemetry / root logger noise
warnings.filterwarnings("ignore")
logging.disable(logging.CRITICAL)          # silence ERROR:root from CrewAI retries
os.environ.setdefault("CREWAI_TELEMETRY", "false")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")
os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")

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
    from crewai import Agent, Task, Crew
except ImportError:
    print("✗ CrewAI not installed. Run:")
    print("  python3.10 -m pip install crewai")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────
BACKEND_URL   = "http://localhost:8080/v1"
API_KEY       = "invexsai_dev_testkey123"
DASHBOARD_URL = "http://localhost:5174"
MODEL         = "gpt-4o-mini"

# Estimated tokens per claim processed
PROMPT_TOKENS     = 150
COMPLETION_TOKENS = 50
TOTAL_TOKENS      = 200

# ── The 5 insurance claims ────────────────────────────────────────────────────
CLAIMS = [
    {
        "n":     1,
        "label": "Auto claim — rear-end collision, $4,200",
        "body":  (
            "Insurance claim: Auto accident, rear-end collision. "
            "Repair estimate: $4,200. Valid active policy. "
            "Police report filed. Fault clearly established."
        ),
    },
    {
        "n":     2,
        "label": "Home claim — burst pipe water damage, $18,000",
        "body":  (
            "Insurance claim: Home water damage from burst pipe. "
            "Damage estimate: $18,000. Valid active policy. "
            "Damage verified by independent adjuster on site."
        ),
    },
    {
        "n":     3,
        "label": "Auto claim — windshield crack, $380 (3rd claim this year)",
        "body":  (
            "Insurance claim: Windshield crack. "
            "Repair estimate: $380. Valid active policy. "
            "No police report. This is the third claim filed this year by this policyholder."
        ),
    },
    {
        "n":     4,
        "label": "Health claim — emergency appendectomy, $32,000",
        "body":  (
            "Insurance claim: Emergency appendectomy surgery. "
            "Total cost: $32,000. Valid active health policy. "
            "Pre-authorization obtained prior to procedure."
        ),
    },
    {
        "n":     5,
        "label": "Auto claim — total loss from flood, $22,000 (no flood coverage)",
        "body":  (
            "Insurance claim: Vehicle total loss due to flooding. "
            "Vehicle value: $22,000. Policy is active but explicitly "
            "DOES NOT include flood damage coverage."
        ),
    },
]

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
    # ── Guard ─────────────────────────────────────────────────────────────────
    if not os.environ.get("OPENAI_API_KEY"):
        print()
        print("  ✗  OPENAI_API_KEY not set. Export it first:")
        print("     export OPENAI_API_KEY=sk-proj-...")
        print()
        sys.exit(1)

    # ── Banner ────────────────────────────────────────────────────────────────
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║       INVEXSAI — Insurance Claims Processor Demo     ║")
    print("║       Framework: CrewAI   |  Model: gpt-4o-mini      ║")
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
                name="claims-processor-v1",
                owner="insurance-team",
                framework="crewai",
                model=MODEL,
                environment="production",
                tools=["claims_validator", "damage_assessor", "policy_checker"],
                tags={"team": "claims", "region": "us-east"},
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

    # ── Build CrewAI agent ────────────────────────────────────────────────────
    # CrewAI 1.x uses string llm identifier (not a LangChain object)
    claims_agent = Agent(
        role="Insurance Claims Processor",
        goal="Accurately evaluate insurance claims based on policy terms and evidence",
        backstory=(
            "Expert claims adjuster with 20 years of experience processing "
            "auto, home, and health insurance claims with strict adherence to policy terms."
        ),
        llm=f"openai/{MODEL}",
        verbose=False,
        allow_delegation=False,
    )

    # ── Process each claim ────────────────────────────────────────────────────
    print()
    for claim in CLAIMS:
        print(LINE)
        print(f"  Processing claim {claim['n']}/5...")
        print(f"  {claim['label']}")
        print()
        try:
            task = Task(
                description=(
                    f"Process this insurance claim: {claim['body']} "
                    "Respond with DECISION: APPROVED or DECISION: REJECTED "
                    "followed by one sentence explaining why."
                ),
                expected_output="DECISION: APPROVED or DECISION: REJECTED with one sentence reason",
                agent=claims_agent,
            )
            crew = Crew(
                agents=[claims_agent],
                tasks=[task],
                verbose=False,
                tracing=False,   # disable the interactive trace prompt entirely
            )
            # Run synchronously inside async context (crew.kickoff is sync in 1.x)
            result = await asyncio.get_event_loop().run_in_executor(
                None, crew.kickoff
            )
            decision = str(result).strip()
            # Print only the decision line(s), skip empty lines
            for line in decision.splitlines():
                if line.strip():
                    print(f"  {line.strip()}")
            print()
            # Log cost to INVEXSAI dashboard
            await log_cost(client, agent_id, team="claims")
            # Heartbeat each iteration
            try:
                await client.send_heartbeat(agent_id, "healthy", latency_ms=10)
            except Exception:
                pass
            print("  ✓ Cost logged to dashboard ✓")
        except Exception as exc:
            print(f"  ✗ Processing error: {exc}")

        if claim["n"] < 5:
            await asyncio.sleep(2)

    # Let any pending HTTP calls finish
    await asyncio.sleep(1)

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    print(LINE)
    print()
    total_cost = calculate_cost(MODEL, PROMPT_TOKENS * 5, COMPLETION_TOKENS * 5)
    print("  Demo complete.")
    print("  5 insurance claims processed")
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
