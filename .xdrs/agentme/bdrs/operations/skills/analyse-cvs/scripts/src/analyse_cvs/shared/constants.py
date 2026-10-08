"""Names and limits shared by the commands."""

from decimal import Decimal
from pathlib import Path

SUPPORTED = {".pdf", ".docx", ".pptx", ".html", ".htm", ".txt", ".md"}
WORK = Path(".work")
STAGING = WORK / "staging"
MANIFEST = STAGING / "manifest.json"
SOURCES_DIR = WORK / "sources"
MD_DIR = WORK / "md"
CHART_NAME = "interview-chart.md"
MARK = "[REDACTED]"

SCALE_MIN = Decimal("1.0")
SCALE_MAX = Decimal("10.0")
NEUTRAL_CREDIBILITY = Decimal("5.5")
CREDIBILITY_SPAN = Decimal("4.5")
INVITE_ABOVE = Decimal("5.0")

SCENARIOS = ("S1", "S2", "S3")
SCENARIO_LIMIT = Decimal("1.0")
ASPECT_LIMIT = Decimal("2.0")

WEIGHT_TOTAL = Decimal(100)
MAX_CRITERION_WEIGHT = Decimal(25)
MIN_ASPECT_WEIGHT = Decimal(20)
MAX_ASPECT_WEIGHT = Decimal(50)
ASPECT_COUNT = 3
MIN_CRITERIA = 6
MAX_CRITERIA = 12

BASE_GAP_LIMIT = Decimal(2)
RATIONALE_WORDS = 25
NOTE_WORDS = 15

DOC_TYPES = {"cv", "cover-letter", "portfolio", "certificate", "reference-letter", "other"}

INTERVIEW_HEADING = "## Interview list (Overall > 5.0)"
INTERVIEW_CLOSING = "This list is a recommendation; a human decides who to interview."
NONE_INVITED = "No candidate scored above 5.0; consider reviewing the criteria or the candidate pool."
PLACEHOLDER = "<fill>"
