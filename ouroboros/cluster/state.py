from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class NodeRole(str, Enum):
    LEADER = "leader"
    CHALLENGER = "challenger"
    CANDIDATE = "candidate"


@dataclass
class NodeState:
    node_id: str
    role: NodeRole = NodeRole.CHALLENGER
    term: int = 0


class PromotionEngine:
    """Raft-like promotion decision with quorum requirement."""

    def __init__(self, quorum: int) -> None:
        self.quorum = quorum

    def can_promote(self, votes_for_promotion: int, challenger_score: float, leader_score: float) -> bool:
        return votes_for_promotion >= self.quorum and challenger_score > leader_score

    def promote(self, challenger: NodeState, current_leader: NodeState, votes: int) -> tuple[NodeState, NodeState]:
        if not self.can_promote(votes, challenger_score=1.0, leader_score=0.0):
            return current_leader, challenger

        next_term = max(challenger.term, current_leader.term) + 1
        current_leader.role = NodeRole.CHALLENGER
        current_leader.term = next_term

        challenger.role = NodeRole.LEADER
        challenger.term = next_term
        return challenger, current_leader
