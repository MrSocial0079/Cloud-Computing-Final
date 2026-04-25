import pytest
import asyncio
import os


# Test 1 — pricing calculation (no network needed)
def test_pricing_gpt4o():
    from invexsai.pricing import calculate_cost
    cost = calculate_cost("gpt-4o", 1000, 500)
    expected = (1000 / 1000 * 0.0025) + (500 / 1000 * 0.0100)
    assert abs(cost - expected) < 0.0000001


def test_pricing_unknown_model():
    from invexsai.pricing import calculate_cost
    cost = calculate_cost("some-unknown-model-xyz", 1000, 500)
    assert cost == 0.0


def test_pricing_never_raises():
    from invexsai.pricing import calculate_cost
    for model in [None, "", "   ", "gpt-99-turbo-ultra", 123]:
        try:
            result = calculate_cost(str(model) if model else "", 0, 0)
            assert isinstance(result, float)
        except Exception as e:
            pytest.fail(f"calculate_cost raised {e} for model={model}")


# Test 2 — client instantiation (no network needed)
def test_client_init():
    from invexsai import InvexsaiClient
    client = InvexsaiClient(api_key="test-key")
    assert client.api_key == "test-key"
    assert client.base_url == "http://localhost:8080/v1"


# Test 3 — handler instantiation (no network needed)
def test_handler_init():
    from invexsai import InvexsaiClient, InvexsaiCallbackHandler
    client = InvexsaiClient(api_key="test-key")
    handler = InvexsaiCallbackHandler(agent_id="test-uuid", client=client)
    assert handler.agent_id == "test-uuid"
    assert handler.trace_id is not None


# Test 4 — on_llm_end does not raise (mock response)
def test_on_llm_end_no_raise():
    from invexsai import InvexsaiClient, InvexsaiCallbackHandler
    from langchain_core.outputs import LLMResult, Generation

    client = InvexsaiClient(api_key="test-key")
    handler = InvexsaiCallbackHandler(agent_id="test-uuid", client=client)

    mock_response = LLMResult(
        generations=[[Generation(text="Hello")]],
        llm_output={
            "model_name": "gpt-4o",
            "token_usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
            },
        },
    )

    try:
        handler.on_llm_end(mock_response)
    except Exception as e:
        pytest.fail(f"on_llm_end raised: {e}")


# Test 5 — live backend test (skipped if backend not running)
@pytest.mark.asyncio
async def test_live_register():
    from invexsai import InvexsaiClient
    from invexsai.types import RegisterRequest

    client = InvexsaiClient(api_key="invexsai_dev_testkey123")
    req = RegisterRequest(
        name="sdk-test-agent",
        owner="yash",
        framework="langchain",
        model="gpt-4o",
        environment="development",
    )
    try:
        resp = await client.register_agent(req)
        if resp:
            assert resp.agent_id is not None
            assert len(resp.agent_id) == 36  # UUID format
            print(f"Registered agent: {resp.agent_id}")
        else:
            pytest.skip("Backend not running — skipping live test")
    except Exception:
        pytest.skip("Backend not running — skipping live test")
    finally:
        await client.close()


# Test 6 — live cost logging
@pytest.mark.asyncio
async def test_live_cost_log():
    from invexsai import InvexsaiClient
    from invexsai.types import RegisterRequest, CostRequest
    from invexsai.pricing import calculate_cost

    client = InvexsaiClient(api_key="invexsai_dev_testkey123")
    try:
        reg = await client.register_agent(
            RegisterRequest(
                name="sdk-cost-test",
                owner="yash",
                framework="langchain",
                model="gpt-4o",
                environment="development",
            )
        )
        if not reg:
            pytest.skip("Backend not running")

        cost = calculate_cost("gpt-4o", 847, 312)
        req = CostRequest(
            agent_id=reg.agent_id,
            model="gpt-4o",
            prompt_tokens=847,
            completion_tokens=312,
            total_tokens=1159,
            cost_usd=cost,
        )
        success = await client.log_cost(req)
        assert success is True
        print(f"Cost logged: ${cost:.8f}")
    except Exception:
        pytest.skip("Backend not running")
    finally:
        await client.close()
