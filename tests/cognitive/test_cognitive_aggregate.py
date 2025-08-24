"""
Unit tests for the Cognitive Aggregate.
"""
import pytest
from unittest.mock import MagicMock
from pathlib import Path
from hive_physics.cognitive.aggregate import CognitiveAggregate, ThinkCommand, LLMConfig

@pytest.fixture
def dummy_component(tmp_path: Path) -> Path:
    """Creates a dummy component file for testing."""
    p = tmp_path / "dummy_component.py"
    p.write_text("def hello():\n    print('hello')\n")
    return p

def test_generate_state_report(dummy_component: Path):
    """Tests that the state report is generated correctly."""
    aggregate = CognitiveAggregate("test_agg")
    problem = "This is a test problem."

    report = aggregate._generate_state_report(
        component_id=str(dummy_component),
        problem_description=problem
    )

    assert problem in report
    assert str(dummy_component) in report
    assert "def hello():" in report
    assert "# MISTRAL AGENT STATE REPORT" in report

def test_get_llm_suggestion(mocker):
    """Tests that the LLM suggestion is retrieved and processed correctly."""
    aggregate = CognitiveAggregate("test_agg")
    mock_response_content = "This is a mock suggestion."

    mocker.patch(
        'hive_physics.cognitive.aggregate.litellm.completion',
        return_value=MagicMock(choices=[MagicMock(message=MagicMock(content=mock_response_content))])
    )

    llm_config = LLMConfig(model="test_model")
    suggestion = aggregate._get_llm_suggestion("test prompt", llm_config)

    assert suggestion == mock_response_content

def test_execute_immune_logic(mocker, dummy_component: Path):
    """
    Tests the full _execute_immune_logic workflow.
    """
    aggregate = CognitiveAggregate("test_agg")
    mock_patch = "mock patch content"

    mocker.patch.object(aggregate, '_get_llm_suggestion', return_value=mock_patch)

    command = ThinkCommand(
        problem_description="A test problem",
        target_component_id=str(dummy_component)
    )
    llm_config = LLMConfig(model="test_model")

    events = aggregate._execute_immune_logic(command, llm_config)

    assert len(events) == 1
    event = events[0]
    assert event.event_type == "EvolutionaryPulse"
    assert event.patch == mock_patch
