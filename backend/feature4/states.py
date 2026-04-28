"""Candidate lifecycle state machine."""
from enum import Enum


class CandidateStatus(str, Enum):
    PENDING     = "pending"
    SHORTLISTED = "shortlisted"
    SAVED       = "saved"        # UI bookmark — treated as shortlisted for pipeline
    CONTACTED   = "contacted"
    INTERVIEWED = "interviewed"
    EVALUATED   = "evaluated"
    OFFERED     = "offered"
    REJECTED    = "rejected"


# Allowed forward transitions per status
_TRANSITIONS: dict[CandidateStatus, set[CandidateStatus]] = {
    CandidateStatus.PENDING:      {CandidateStatus.SHORTLISTED, CandidateStatus.SAVED, CandidateStatus.REJECTED},
    CandidateStatus.SHORTLISTED:  {CandidateStatus.CONTACTED, CandidateStatus.EVALUATED, CandidateStatus.REJECTED},
    CandidateStatus.SAVED:        {CandidateStatus.SHORTLISTED, CandidateStatus.CONTACTED, CandidateStatus.EVALUATED, CandidateStatus.REJECTED},
    CandidateStatus.CONTACTED:    {CandidateStatus.INTERVIEWED, CandidateStatus.REJECTED},
    CandidateStatus.INTERVIEWED:  {CandidateStatus.EVALUATED, CandidateStatus.REJECTED},
    CandidateStatus.EVALUATED:    {CandidateStatus.CONTACTED, CandidateStatus.OFFERED, CandidateStatus.REJECTED},
    CandidateStatus.OFFERED:      {CandidateStatus.REJECTED},
    CandidateStatus.REJECTED:     {CandidateStatus.SHORTLISTED, CandidateStatus.SAVED},
}

# Statuses from which evaluation is permitted
EVALUABLE_STATUSES: set[CandidateStatus] = {
    CandidateStatus.SHORTLISTED,
    CandidateStatus.SAVED,
    CandidateStatus.INTERVIEWED,
}

# Statuses from which outreach (contact) is permitted
CONTACTABLE_STATUSES: set[CandidateStatus] = {
    CandidateStatus.SHORTLISTED,
    CandidateStatus.SAVED,
    CandidateStatus.EVALUATED,
}


def is_valid_transition(current: str, new: str) -> bool:
    """Return True if the status transition current → new is allowed."""
    try:
        return CandidateStatus(new) in _TRANSITIONS.get(CandidateStatus(current), set())
    except ValueError:
        return False


def assert_valid_transition(current: str, new: str) -> None:
    """Raise ValueError if the transition is not permitted."""
    if not is_valid_transition(current, new):
        raise ValueError(
            f"Invalid status transition: '{current}' → '{new}'"
        )
