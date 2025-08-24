"""
The Cognitive Aggregate - the "Mind" of the Hive.
"""
import litellm
import os
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Protocol

from hive_physics.dna_core.royal_jelly import SacredAggregate, SacredCommand, PollenEnvelope
from hive_physics.adaptation.aggregate import EvolutionaryPulse

# --- LLM Configuration and Client ---
class LLMClientProtocol(Protocol):
    def completion(self, **kwargs) -> dict:
        ...

@dataclass
class LLMConfig:
    model: str
    temperature: float = 0.7
    max_tokens: int = 2048
    api_key: Optional[str] = None
    api_base: Optional[str] = None

# --- Commands and Pulses ---
class ThinkCommand(SacredCommand):
    """A command that instructs the Cognitive Core to think."""
    def __init__(self, problem_description: str, target_component_id: str):
        self.problem_description = problem_description
        self.target_component_id = target_component_id
        super().__init__(
            command_type="think",
            payload={
                "problem_description": self.problem_description,
                "target_component_id": self.target_component_id
            }
        )

class CognitiveAggregate(SacredAggregate):
    """
    The aggregate responsible for self-reflection and proposing changes.
    """
    def _get_llm_suggestion(self, prompt: str, config: LLMConfig) -> str:
        if not config.model:
            raise ValueError("LLM 'model' not specified in configuration.")
        messages = [{"role": "user", "content": prompt}]
        api_params = {
            "model": config.model, "messages": messages, "temperature": config.temperature,
            "max_tokens": config.max_tokens, "api_key": config.api_key, "api_base": config.api_base
        }
        api_params = {k: v for k, v in api_params.items() if v is not None}
        response = litellm.completion(**api_params)
        content = response.choices[0].message.content
        return content.strip() if content else ""

    def _generate_state_report(self, component_id: str, problem_description: str) -> str:
        try:
            with open(component_id, 'r') as f:
                source_code = f.read()
        except FileNotFoundError:
            source_code = f"# Error: Source code file not found at {component_id}"

        return f"""
# MISTRAL AGENT STATE REPORT

## MISSION: AI-Powered Refactoring (Guided Evolution)

An issue has been detected in the Hive. Your task is to analyze the following context and propose a code modification to resolve the issue. The output should be a code block in the git merge-diff format (`<<<<<<< SEARCH`, `=======`, `>>>>>>> REPLACE`).

---

## 1. PROBLEM DESCRIPTION

{problem_description}

---

## 2. TARGET COMPONENT

- **Component ID:** `{component_id}`
- **Source Code Path:** `{component_id}`

```python
{source_code}
```

---

## 4. TASK

Based on all the provided context, generate a code patch in the git merge-diff format to resolve the stated problem.
""".strip()

    def _execute_immune_logic(self, command: ThinkCommand, llm_config: LLMConfig) -> List[EvolutionaryPulse]:
        print(f"CognitiveAggregate received ThinkCommand for target: {command.target_component_id}")

        print("Generating state report...")
        report = self._generate_state_report(
            component_id=command.target_component_id,
            problem_description=command.problem_description
        )

        print("Getting LLM suggestion...")
        patch_suggestion = self._get_llm_suggestion(report, llm_config)

        print("Emitting EvolutionaryPulse...")
        return [EvolutionaryPulse(patch=patch_suggestion)]
