"""Job-title filter (PRD 2.1 第 3 點)."""
import re

# English terms match only when not glued to other ASCII letters, so "PM" matches in
# "專案經理PM實習" but not in "PMC" or "APM". Chinese terms are plain substrings.
_EN = r"(?<![A-Za-z]){}(?![A-Za-z])"


def _rx(terms):
    parts = [(_EN.format(re.escape(t)) if t.isascii() else re.escape(t)) for t in terms]
    return re.compile("|".join(parts), re.IGNORECASE)


GROUP_A = _rx(["PM", "PjM", "產品", "專案", "Project", "Product"])
GROUP_B = _rx(["經理", "專員", "工程師", "助理", "管理師", "Manager", "Engineer", "Specialist", "Assistant"])
STANDALONE = _rx(["PM", "PjM"])
EXCLUDE = _rx(["產品工程師", "Product Engineer", "PE", "PMC", "生管", "製程工程師",
               "實習", "工讀", "Intern", "Internship"])


def is_target_title(title: str) -> bool:
    if not title or EXCLUDE.search(title):
        return False
    if STANDALONE.search(title):
        return True
    return bool(GROUP_A.search(title) and GROUP_B.search(title))
