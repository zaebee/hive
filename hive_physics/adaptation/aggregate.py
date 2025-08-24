"""
The Adaptation Aggregate - the core of the Adaptation Engine.
"""
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

from hive_physics.dna_core.royal_jelly import SacredAggregate, SacredCommand, PollenEnvelope
from hive_physics.adaptation.toxicity import calculate_toxicity_score
from hive_physics.adaptation.patcher import apply_patch_with_git

class EvolutionaryPulse(PollenEnvelope):
    """
    An event carrying a proposed code change for the Hive to consider.
    """
    def __init__(self, patch: str):
        super().__init__(
            event_type="EvolutionaryPulse",
            payload={"patch": patch}
        )
        self.patch = patch


class ApplyPatchCommand(SacredCommand):
    def __init__(self, patch: str):
        super().__init__(command_type="apply_patch", payload={"patch": patch})
        self.patch = patch

class AdaptationAggregate(SacredAggregate):
    def _execute_immune_logic(self, command: ApplyPatchCommand) -> List[PollenEnvelope]:
        print(f"Received ApplyPatchCommand for patch of length {len(command.patch)}")

        # 1. Parse patch to get file paths
        file_paths = re.findall(r'diff --git a/(.*?) b/', command.patch)
        if not file_paths: # Handle patches for a single file
            paths = re.findall(r'--- a/(.*?)\n', command.patch)
            if paths:
                file_paths = [paths[0]]

        # 2. Backup original files
        backup: Dict[str, Optional[str]] = {}
        for file_path in file_paths:
            p = Path(file_path)
            if p.exists():
                backup[file_path] = p.read_text()
            else:
                backup[file_path] = None # File is being created

        pre_toxicity = sum(calculate_toxicity_score(c) for c in backup.values() if c is not None)
        print(f"Pre-patch toxicity score: {pre_toxicity}")

        # 3. Apply the patch
        patch_applied = apply_patch_with_git(command.patch)

        if not patch_applied:
            self._rollback(backup)
            status = "rejected_by_git"
            post_toxicity = pre_toxicity
        else:
            # 4. Calculate post-patch toxicity
            new_contents: Dict[str, Optional[str]] = {}
            for file_path in file_paths:
                p = Path(file_path)
                if p.exists():
                    new_contents[file_path] = p.read_text()
                else:
                    new_contents[file_path] = None

            post_toxicity = sum(calculate_toxicity_score(c) for c in new_contents.values() if c is not None)
            print(f"Post-patch toxicity score: {post_toxicity}")

            # 5. Compare scores and decide
            if post_toxicity <= pre_toxicity:
                print("Toxicity did not increase. Patch is 'honey'.")
                status = "applied"
            else:
                print("Toxicity increased. Patch is 'poison'. Rolling back.")
                self._rollback(backup)
                status = "rejected_by_toxicity"

        # 6. Emit event
        event = PollenEnvelope(
            event_type="PatchAppliedEvent",
            payload={
                "command_id": command.command_id,
                "patch": command.patch,
                "status": status,
                "pre_toxicity": pre_toxicity,
                "post_toxicity": post_toxicity,
            }
        )
        print(f"Emitting PatchAppliedEvent with status: {status}")
        return [event]

    def _rollback(self, backup: Dict[str, Optional[str]]):
        print("Rolling back changes...")
        for file_path, content in backup.items():
            p = Path(file_path)
            if content is None:
                if p.exists():
                    p.unlink()
            else:
                p.write_text(content)
        print("Rollback complete.")
