"""
Skill Injector Module

Handles loading of attack skills into the OpenClaw environment.
OpenClaw loads skills from three locations (priority order):
  1. <workspace>/skills/
  2. ~/.openclaw/skills/
  3. Built-in skills

This module places attack skill definitions into the workspace skills
directory so they are available to the OpenClaw agent during testing.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)


class SkillInjector:
    """
    Manages the injection of attack skills into the OpenClaw environment.
    
    In OpenClaw, skills are Markdown files with YAML frontmatter:
    ---
    name: skill-name
    description: What this skill does
    tools: [tool1, tool2]
    ---
    
    The agent reads these descriptions to understand available capabilities.
    Attack skills define pipelines that appear legitimate but contain
    cyclic control flows exploitable by RCI-SG.
    """
    
    def __init__(self, source_dir: str = "skills", target_dir: str = "skills"):
        """
        Initialize the skill injector.
        
        Args:
            source_dir: Directory containing attack skill definitions (.md files)
            target_dir: Target directory for OpenClaw to load skills from
                       (Default: workspace/skills/ has highest priority in OpenClaw)
        """
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.injected_skills: List[str] = []
        
    def inject_skills(self, max_skills: int = 110) -> List[Dict]:
        """
        Copy attack skills into the OpenClaw workspace.
        
        OpenClaw automatically discovers skills in the workspace/skills/
        directory. Each skill becomes available to the agent as a callable
        capability described by its Markdown content.
        
        Args:
            max_skills: Maximum number of skills to inject
            
        Returns:
            List of injected skill dictionaries
        """
        self.target_dir.mkdir(parents=True, exist_ok=True)
        
        skills = []
        if not self.source_dir.exists():
            logger.error(f"Source skills directory not found: {self.source_dir}")
            return skills
        
        md_files = sorted(self.source_dir.glob("*.md"))[:max_skills]
        
        for md_file in md_files:
            try:
                # Copy skill definition to workspace
                target_file = self.target_dir / md_file.name
                shutil.copy2(md_file, target_file)
                
                # Parse skill metadata
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                import re
                name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
                
                skill_info = {
                    "skill_id": md_file.stem,
                    "name": name_match.group(1).strip() if name_match else md_file.stem,
                    "source": str(md_file),
                    "target": str(target_file)
                }
                skills.append(skill_info)
                self.injected_skills.append(md_file.stem)
                
            except Exception as e:
                logger.error(f"Failed to inject skill {md_file}: {e}")
        
        logger.info(f"Injected {len(skills)} attack skills into {self.target_dir}")
        return skills
    
    def clear_skills(self) -> None:
        """Remove injected skills from the workspace."""
        if self.target_dir.exists():
            for skill_file in self.target_dir.glob("*.md"):
                if skill_file.stem in self.injected_skills:
                    skill_file.unlink()
            logger.info(f"Cleared {len(self.injected_skills)} injected skills")
        self.injected_skills = []
    
    def get_skill_count(self) -> int:
        """Return the number of currently injected skills."""
        return len(self.injected_skills)
