"""Check discovery metadata and relative references in installed skill packages."""

from pathlib import Path
import re
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents/skills"


class PackageTests(unittest.TestCase):
    def check_links(self, source):
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", source.read_text(encoding="utf-8")):
            if "://" in link or link.startswith("#"):
                continue
            target = source.parent / link.split("#", 1)[0]
            self.assertTrue(target.exists(), f"Broken reference in {source}: {link}")

    def test_skill_metadata_and_references(self):
        for skill in SKILLS.iterdir():
            if not skill.is_dir():
                continue
            entry = skill / "SKILL.md"
            content = entry.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---\n"), str(entry))
            frontmatter = content.split("---", 2)[1]
            name = re.search(r"^name: (.+)$", frontmatter, re.MULTILINE)
            self.assertIsNotNone(name, str(entry))
            self.assertEqual(name.group(1), skill.name)
            self.assertRegex(skill.name, r"^[a-z0-9-]{1,64}$")
            self.assertRegex(frontmatter, r"(?m)^description: .+\S$")
            for source in skill.rglob("*.md"):
                self.check_links(source)

    def test_sibling_links_work_after_local_host_installation(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / ".claude/skills"
            destination.mkdir(parents=True)
            for skill in SKILLS.iterdir():
                if skill.is_dir():
                    (destination / skill.name).symlink_to(skill, target_is_directory=True)
            for skill in destination.iterdir():
                self.check_links(skill / "SKILL.md")

    def test_documentation_links_resolve(self):
        sources = [ROOT / "README.md"]
        for folder in ("docs", "examples", "tests/behavioral"):
            sources.extend((ROOT / folder).rglob("*.md"))
        for source in sources:
            self.check_links(source)


if __name__ == "__main__":
    unittest.main()
