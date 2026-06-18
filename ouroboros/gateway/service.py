from __future__ import annotations

from dataclasses import dataclass

from ouroboros.cluster.state import NodeRole, NodeState, PromotionEngine
from ouroboros.config import Settings
from ouroboros.core.llm import create_llm_client
from ouroboros.eval.harness import compare_models, generate_questions_from_chunks
from ouroboros.finetune.pipeline import FineTunePipeline
from ouroboros.knowledge.ingest import chunk_text
from ouroboros.knowledge.store import InMemoryKnowledgeStore


@dataclass
class AskResult:
    answer: str
    retrieved: list[dict[str, str | int]]


class OuroborosService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.llm = create_llm_client(settings)
        self.store = InMemoryKnowledgeStore()
        self.finetune = FineTunePipeline()
        self.promotion = PromotionEngine(quorum=settings.promotion_quorum)
        self.leader = NodeState(node_id="leader-a", role=NodeRole.LEADER, term=1)
        self.challenger = NodeState(node_id="challenger-a", role=NodeRole.CHALLENGER, term=1)

    def ingest(self, source: str, content: str) -> dict[str, object]:
        chunks = chunk_text(content, source=source)
        added = self.store.add_chunks(chunks)
        trigger = self.finetune.should_trigger(added)
        adapter = self.finetune.create_adapter(self.settings.llm_model, self.settings.domain) if trigger else None

        eval_questions = generate_questions_from_chunks([chunk.text for chunk in chunks[:3]])

        return {
            "chunks_added": added,
            "knowledge_size": self.store.size(),
            "finetune_triggered": trigger,
            "adapter": adapter.__dict__ if adapter else None,
            "eval_questions": [item.question for item in eval_questions],
        }

    def ask(self, query: str) -> AskResult:
        retrieved = self.store.retrieve(query)
        context = "\n\n".join([item.text for item in retrieved])
        prompt = f"Domain: {self.settings.domain}\n\nContext:\n{context}\n\nQuestion: {query}"
        answer = self.llm.generate(prompt)
        return AskResult(
            answer=answer,
            retrieved=[{"source": item.source, "score": item.score, "text": item.text} for item in retrieved],
        )

    def run_eval_round(self) -> dict[str, object]:
        sample_chunks = [item.text for item in self.store.retrieve(self.settings.domain, top_k=2)]
        questions = generate_questions_from_chunks(sample_chunks)

        leader_answers = [self.llm.generate(question.question) for question in questions]
        challenger_answers = [self.llm.generate(question.question + " improved") for question in questions]
        results = compare_models(questions, leader_answers, challenger_answers)

        avg_leader = sum(result.leader_score for result in results) / len(results) if results else 0.0
        avg_challenger = sum(result.challenger_score for result in results) / len(results) if results else 0.0

        promoted = False
        if self.promotion.can_promote(votes_for_promotion=self.settings.promotion_quorum, challenger_score=avg_challenger, leader_score=avg_leader):
            self.leader, self.challenger = self.promotion.promote(self.challenger, self.leader, votes=self.settings.promotion_quorum)
            promoted = True

        return {
            "avg_leader_score": avg_leader,
            "avg_challenger_score": avg_challenger,
            "promoted": promoted,
            "leader": {"node_id": self.leader.node_id, "role": self.leader.role, "term": self.leader.term},
            "challenger": {"node_id": self.challenger.node_id, "role": self.challenger.role, "term": self.challenger.term},
            "results": [result.__dict__ for result in results],
        }
