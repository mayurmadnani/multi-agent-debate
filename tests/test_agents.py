from debate_system.agents.aristotle import AristotleAgent
from debate_system.core.config import AgentConfig


def make_aristotle(tools_enabled: bool = True) -> AristotleAgent:
    cfg = AgentConfig(
        name="Aristotle",
        instruction="Test Aristotle",
        temperature=0.7,
        max_tokens=64,
        tools_enabled=tools_enabled,
    )
    return AristotleAgent(cfg)


def test_aristotle_tool_detection_math():
    agent = make_aristotle()
    assert agent._detect_tool_needed("Calculate 5 + 3") == "calculate"


def test_aristotle_tool_detection_search():
    agent = make_aristotle()
    assert agent._detect_tool_needed("Search for Plato's cave") == "web_search"


def test_aristotle_tool_detection_explain():
    agent = make_aristotle()
    assert agent._detect_tool_needed("Explain the theory of forms") == "web_search"


def test_aristotle_question_extraction():
    agent = make_aristotle()
    text = "I think we need to look up more info. What is justice?"
    assert "What is justice" in agent._extract_question_from_response(text)


def test_aristotle_tool_detection_time():
    agent = make_aristotle()
    assert agent._detect_tool_needed("What is the current time?") == "get_current_info"


def test_aristotle_calculate_query_normalization():
    agent = make_aristotle()
    expr = agent._detect_tool_needed("Could you calculate 12 * 7 for me?")
    assert expr == "calculate"
