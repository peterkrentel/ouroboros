from ouroboros.cluster.state import NodeRole, NodeState, PromotionEngine


def test_promotion_requires_quorum_and_higher_score() -> None:
    engine = PromotionEngine(quorum=2)
    assert engine.can_promote(votes_for_promotion=2, challenger_score=0.8, leader_score=0.7)
    assert not engine.can_promote(votes_for_promotion=1, challenger_score=0.8, leader_score=0.7)
    assert not engine.can_promote(votes_for_promotion=2, challenger_score=0.6, leader_score=0.7)


def test_promotion_updates_roles_and_term() -> None:
    leader = NodeState(node_id="leader", role=NodeRole.LEADER, term=3)
    challenger = NodeState(node_id="challenger", role=NodeRole.CHALLENGER, term=3)
    engine = PromotionEngine(quorum=2)

    next_leader, next_challenger = engine.promote(challenger, leader, votes=2)

    assert next_leader.node_id == "challenger"
    assert next_leader.role == NodeRole.LEADER
    assert next_challenger.node_id == "leader"
    assert next_challenger.role == NodeRole.CHALLENGER
    assert next_leader.term == 4
    assert next_challenger.term == 4
