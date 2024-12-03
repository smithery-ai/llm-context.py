from dataclasses import dataclass
from pathlib import Path

from llm_context.exceptions import LLMContextError
from llm_context.profile import Profile, ProfileResolver
from llm_context.project_setup import ProjectSetup
from llm_context.state import StateStore
from llm_context.utils import ProjectLayout, Toml


@dataclass(frozen=True)
class ContextSpec:
    project_layout: ProjectLayout
    templates: dict[str, str]
    context_descriptor: Profile

    @staticmethod
    def create(project_root: Path, profile_name: str) -> "ContextSpec":
        ContextSpec.ensure_gitignore_exists(project_root)
        project_layout = ProjectLayout(project_root)
        ProjectSetup.create(project_layout).initialize()
        raw_config = Toml.load(project_layout.config_path)
        profile = ProfileResolver.create(raw_config).get_profile(profile_name)
        return ContextSpec(project_layout, raw_config["templates"], profile)

    @staticmethod
    def ensure_gitignore_exists(root_path: Path) -> None:
        if not (root_path / ".gitignore").exists():
            raise LLMContextError(
                "A .gitignore file is essential for this tool to function correctly. Please create one before proceeding.",
                "GITIGNORE_NOT_FOUND",
            )

    def has_profile(self, profile_name: str):
        raw_config = Toml.load(self.project_layout.config_path)
        return ProfileResolver.create(raw_config).has_profile(profile_name)

    @property
    def state_store(self):
        return StateStore(self.project_layout.state_store_path)

    @property
    def project_root_path(self):
        return self.project_layout.root_path

    @property
    def project_root(self):
        return str(self.project_root_path)