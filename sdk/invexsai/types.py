from dataclasses import dataclass, field
from typing import Optional, List, Dict


@dataclass
class RegisterRequest:
    name: str
    owner: str
    framework: str
    model: str
    environment: str
    tools: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class RegisterResponse:
    agent_id: str
    name: str
    registered_at: str


@dataclass
class CostRequest:
    agent_id: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    tool_name: Optional[str] = None
    trace_id: Optional[str] = None
    team: Optional[str] = None
    mcp_server_origin: Optional[str] = None


@dataclass
class HeartbeatRequest:
    agent_id: str
    status: str
    latency_ms: Optional[int] = None
    metadata: Optional[Dict] = None
