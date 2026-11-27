"""Job-title filter (PRD 2.1 第 3 點)."""
import re

# English terms match only when not glued to other ASCII letters, so "PM" matches in
# "專案經理PM實習" but not in "PMC" or "APM". Chinese terms are plain substrings.
_EN = r"(?<![A-Za-z]){}(?![A-Za-z])"


def _rx(terms):
    parts = [(_EN.format(re.escape(t)) if t.isascii() else re.escape(t)) for t in terms]
    return re.compile("|".join(parts), re.IGNORECASE)


GROUP_A = _rx(["PM", "PjM", "產品", "專案", "Project", "Product"])
GROUP_B = _rx(["經理", "專員", "工程師", "管理師", "Manager", "Engineer", "Specialist"])
STANDALONE = _rx(["PM", "PjM"])
# These words exclude the whole title, whatever else it says.
EXCLUDE = _rx(["產品工程師", "Product Engineer", "PE", "PMC", "生管", "製程工程師",
               "實習", "工讀", "Intern", "Internship"])
# 助理／Assistant titles are excluded (decided 2026-10-17), even with "PM" in the title, except as one
# side of a slash: "專案管理師/助理" offers either role and counts (decided 2026-11-27).
ASSISTANT = _rx(["助理", "Assistant"])
# "產品管理"／"專案管理" name the role even without 師／經理 (e.g. "新產品管理", decided 2026-11-27).
ROLE_PHRASE = _rx(["產品管理", "專案管理", "Product Management", "Project Management"])
_SLASH = re.compile(r"[/／]")

# "產品 + 工程師" alone is usually an R&D role (產品開發／設計／品質工程師). Such titles count only
# when they also say 企劃／規劃／管理 (decided 2026-10-17). 專案工程師 is unaffected.
_PROJECT = _rx(["專案", "Project", "PjM"])
_NON_ENGINEER_B = _rx(["經理", "專員", "管理師", "Manager", "Specialist"])
_PRODUCT_ENGINEER_OK = _rx(["企劃", "規劃", "管理", "Management", "Planning", "Planner"])


def _matches(title: str) -> bool:
    if ASSISTANT.search(title):
        return False
    if STANDALONE.search(title) or ROLE_PHRASE.search(title):
        return True
    if not (GROUP_A.search(title) and GROUP_B.search(title)):
        return False
    if not _PROJECT.search(title) and not _NON_ENGINEER_B.search(title):
        return bool(_PRODUCT_ENGINEER_OK.search(title))
    return True


def is_target_title(title: str) -> bool:
    """PRD 2.1 第 3 點. The whole title counts, or any one slash-separated alternative of it."""
    if not title or EXCLUDE.search(title):
        return False
    return _matches(title) or any(_matches(part) for part in _SLASH.split(title) if part.strip())
