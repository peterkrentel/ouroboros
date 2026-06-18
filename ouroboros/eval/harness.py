from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EvalQuestion:
    question: str
    expected_terms: list[str]


@dataclass
class EvalResult:
    question: str
    leader_score: float
    challenger_score: float


def generate_questions_from_chunks(chunks: list[str]) -> list[EvalQuestion]:
    """Build deterministic eval prompts from newly acquired knowledge chunks."""
    questions: list[EvalQuestion] = []
    for chunk in chunks:
        words = [word.strip(".,:;!?()[]{}\"'").lower() for word in chunk.split()]
        terms = [word for word in words if len(word) > 5][:4]
        if not terms:
            continue
        questions.append(
            EvalQuestion(
                question=f"Summarize the operational impact of: {' '.join(terms[:2])}",
                expected_terms=terms,
            )
        )
    return questions


def score_answer(answer: str, expected_terms: list[str]) -> float:
    if not expected_terms:
        return 0.0
    normalized = answer.lower()
    hits = sum(1 for term in expected_terms if term in normalized)
    return hits / len(expected_terms)


def compare_models(
    questions: list[EvalQuestion],
    leader_answers: list[str],
    challenger_answers: list[str],
) -> list[EvalResult]:
    results: list[EvalResult] = []
    for idx, question in enumerate(questions):
        leader = leader_answers[idx] if idx < len(leader_answers) else ""
        challenger = challenger_answers[idx] if idx < len(challenger_answers) else ""
        results.append(
            EvalResult(
                question=question.question,
                leader_score=score_answer(leader, question.expected_terms),
                challenger_score=score_answer(challenger, question.expected_terms),
            )
        )
    return results
