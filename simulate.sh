#!/usr/bin/env bash
# INVEXSAI Fleet Simulator
# Registers 3 agents then sends heartbeats + cost events every 10 seconds.

set -euo pipefail

BASE_URL="https://invexsai-backend-rxnmjktvlq-uc.a.run.app"
API_KEY="invexsai_prod_key_2025"

# ── Helpers ────────────────────────────────────────────────────────────────────

get_token() {
  gcloud auth print-identity-token 2>/dev/null
}

api_post() {
  local path="$1"
  local body="$2"
  local token="$3"
  curl -s -X POST "${BASE_URL}${path}" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${API_KEY}" \
    -H "Authorization: Bearer ${token}" \
    -d "${body}"
}

# ── Bootstrap ──────────────────────────────────────────────────────────────────

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║          INVEXSAI Fleet Simulator Starting               ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

TOKEN=$(get_token)
echo "[init] Obtained identity token: ${TOKEN:0:20}..."
echo ""

# Register agents (idempotent — 200 if exists, 201 if new)
echo "[init] Registering agents..."

REG1=$(api_post "/v1/agents/register" \
  '{"name":"fraud-detector","owner":"fraud-team","framework":"langchain","model":"gpt-4o","environment":"production"}' \
  "$TOKEN")
AGENT1=$(echo "$REG1" | python3 -c "import sys,json; print(json.load(sys.stdin)['agent_id'])")
echo "  fraud-detector      → ${AGENT1}"

REG2=$(api_post "/v1/agents/register" \
  '{"name":"loan-approval-agent","owner":"lending-team","framework":"autogen","model":"gpt-4o","environment":"production"}' \
  "$TOKEN")
AGENT2=$(echo "$REG2" | python3 -c "import sys,json; print(json.load(sys.stdin)['agent_id'])")
echo "  loan-approval-agent → ${AGENT2}"

REG3=$(api_post "/v1/agents/register" \
  '{"name":"compliance-checker","owner":"risk-team","framework":"langchain","model":"gpt-4o-mini","environment":"staging"}' \
  "$TOKEN")
AGENT3=$(echo "$REG3" | python3 -c "import sys,json; print(json.load(sys.stdin)['agent_id'])")
echo "  compliance-checker  → ${AGENT3}"

echo ""
echo "[init] All agents registered. Starting simulation loop..."
echo "       Press Ctrl+C to stop."
echo ""

# ── Simulation loop ────────────────────────────────────────────────────────────

ROUND=0

while true; do
  ROUND=$((ROUND + 1))
  TOKEN=$(get_token)

  echo "────────────────────────────────────────────────────"
  echo "  Round ${ROUND}  |  $(date '+%Y-%m-%d %H:%M:%S')"
  echo "────────────────────────────────────────────────────"

  # ── fraud-detector heartbeat ──
  LATENCY1=$((RANDOM % 200 + 20))
  HB1=$(api_post "/v1/agents/heartbeat" \
    "{\"agent_id\":\"${AGENT1}\",\"status\":\"healthy\",\"latency_ms\":${LATENCY1}}" \
    "$TOKEN")
  NEXT1=$(echo "$HB1" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('next_expected','?'))" 2>/dev/null || echo "error")
  echo "  [heartbeat] fraud-detector       healthy  ${LATENCY1}ms  next=${NEXT1}"

  # ── loan-approval-agent heartbeat — DEGRADED every 4th round ──
  if [ $((ROUND % 4)) -eq 0 ]; then
    STATUS2="degraded"
  else
    STATUS2="healthy"
  fi
  LATENCY2=$((RANDOM % 200 + 20))
  HB2=$(api_post "/v1/agents/heartbeat" \
    "{\"agent_id\":\"${AGENT2}\",\"status\":\"${STATUS2}\",\"latency_ms\":${LATENCY2}}" \
    "$TOKEN")
  NEXT2=$(echo "$HB2" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('next_expected','?'))" 2>/dev/null || echo "error")
  echo "  [heartbeat] loan-approval-agent  ${STATUS2}  ${LATENCY2}ms  next=${NEXT2}"

  # ── compliance-checker heartbeat ──
  LATENCY3=$((RANDOM % 200 + 20))
  HB3=$(api_post "/v1/agents/heartbeat" \
    "{\"agent_id\":\"${AGENT3}\",\"status\":\"healthy\",\"latency_ms\":${LATENCY3}}" \
    "$TOKEN")
  NEXT3=$(echo "$HB3" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('next_expected','?'))" 2>/dev/null || echo "error")
  echo "  [heartbeat] compliance-checker   healthy  ${LATENCY3}ms  next=${NEXT3}"

  echo ""

  # ── fraud-detector cost event ──
  P1=$((RANDOM % 3000 + 500))
  C1=$((RANDOM % 800 + 100))
  T1=$((P1 + C1))
  COST1=$(echo "scale=6; ($P1 * 0.000005) + ($C1 * 0.000015)" | bc)
  api_post "/v1/agents/cost" \
    "{\"agent_id\":\"${AGENT1}\",\"model\":\"gpt-4o\",\"prompt_tokens\":${P1},\"completion_tokens\":${C1},\"total_tokens\":${T1},\"cost_usd\":${COST1}}" \
    "$TOKEN" > /dev/null
  echo "  [cost]      fraud-detector       prompt=${P1} completion=${C1} cost=\$${COST1}"

  # ── loan-approval-agent cost event ──
  P2=$((RANDOM % 3000 + 500))
  C2=$((RANDOM % 800 + 100))
  T2=$((P2 + C2))
  COST2=$(echo "scale=6; ($P2 * 0.000005) + ($C2 * 0.000015)" | bc)
  api_post "/v1/agents/cost" \
    "{\"agent_id\":\"${AGENT2}\",\"model\":\"gpt-4o\",\"prompt_tokens\":${P2},\"completion_tokens\":${C2},\"total_tokens\":${T2},\"cost_usd\":${COST2}}" \
    "$TOKEN" > /dev/null
  echo "  [cost]      loan-approval-agent  prompt=${P2} completion=${C2} cost=\$${COST2}"

  # ── compliance-checker cost event ──
  P3=$((RANDOM % 2000 + 200))
  C3=$((RANDOM % 400 + 50))
  T3=$((P3 + C3))
  COST3=$(echo "scale=6; ($P3 * 0.0000001) + ($C3 * 0.0000004)" | bc)
  api_post "/v1/agents/cost" \
    "{\"agent_id\":\"${AGENT3}\",\"model\":\"gpt-4o-mini\",\"prompt_tokens\":${P3},\"completion_tokens\":${C3},\"total_tokens\":${T3},\"cost_usd\":${COST3}}" \
    "$TOKEN" > /dev/null
  echo "  [cost]      compliance-checker   prompt=${P3} completion=${C3} cost=\$${COST3}"

  echo ""
  echo "  Sleeping 10s... (round $((ROUND + 1)) in 10s)"
  sleep 10
done
