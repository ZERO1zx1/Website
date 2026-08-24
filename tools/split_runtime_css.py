from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source_path = ROOT / "frontend/static/css/style.css"
css = source_path.read_text(encoding="utf-8")


def split_blocks(value: str) -> list[str]:
    blocks = []
    start = 0
    index = 0
    while index < len(value):
        opening = value.find("{", index)
        if opening < 0:
            tail = value[start:].strip()
            if tail:
                blocks.append(tail)
            break
        depth = 1
        cursor = opening + 1
        while cursor < len(value) and depth:
            if value[cursor] == "{":
                depth += 1
            elif value[cursor] == "}":
                depth -= 1
            cursor += 1
        if depth:
            raise ValueError(f"Unclosed CSS block near offset {opening}")
        block = value[start:cursor].strip()
        if block:
            blocks.append(block)
        start = cursor
        index = cursor
    return blocks


def category(block: str) -> str:
    normalized = block.lower()
    if ":root" in normalized or "@font-face" in normalized:
        return "tokens"
    admin_terms = ("admin-", "test-row", "test-builder", "builder-", "preview-", "publish-checklist", "save-status")
    if any(term in normalized for term in admin_terms):
        return "admin"
    learning_terms = (
        "practice-", "challenge-", "project-", "path-", "course-", "lesson-", "workspace-",
        "dashboard-", "profile-", "editor-", "mastery-", "learning-", "quiz-",
    )
    if any(term in normalized for term in learning_terms):
        return "learning"
    component_terms = (
        ".button", ".card", ".panel", ".badge", ".modal", ".toast", ".field-", ".form-",
        ".auth-", ".filter-", ".chip", ".tag", ".avatar", ".progress-bar", ".empty-state",
    )
    if any(term in normalized for term in component_terms):
        return "components"
    return "base"


blocks = split_blocks(css)
files = {name: [] for name in ("tokens", "base", "components", "learning", "admin")}
for block in blocks:
    files[category(block)].append(block)

for name, contents in files.items():
    target = ROOT / f"frontend/static/css/{name}.css"
    header = f"/* CodeCraft runtime {name} styles. Generated from the legacy runtime stylesheet; edit this domain file directly. */\n"
    target.write_text(header + "\n\n".join(contents) + "\n", encoding="utf-8")

imports = """/* CodeCraft runtime stylesheet entrypoint. Keep load order stable. */
@import url(\"tokens.css\");
@import url(\"base.css\");
@import url(\"components.css\");
@import url(\"learning.css\");
@import url(\"admin.css\");
"""
source_path.write_text(imports, encoding="utf-8")
print("Split", len(blocks), "top-level blocks")
for name, contents in files.items():
    print(name, len(contents), "blocks")
