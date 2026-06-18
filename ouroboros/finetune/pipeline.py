from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class AdapterVersion:
    adapter_id: str
    base_model: str
    domain: str
    created_at: str


class FineTunePipeline:
    """Event-driven fine-tuning trigger model for LoRA adapters."""

    def __init__(self, threshold: int = 25) -> None:
        self.threshold = threshold

    def should_trigger(self, new_chunk_count: int) -> bool:
        return new_chunk_count >= self.threshold

    def create_adapter(self, base_model: str, domain: str) -> AdapterVersion:
        ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")
        return AdapterVersion(
            adapter_id=f"lora-{domain.replace(' ', '-')}-{ts}",
            base_model=base_model,
            domain=domain,
            created_at=ts,
        )
