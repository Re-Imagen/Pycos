"""Model tujuan dan mood inti; diekspor ulang melalui facade historis."""
from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional

@dataclass
class Goal:
    drive: str
    urgency: float
    statement: str
    created_tick: int
    age: int = 0
    subgoals: List["Goal"] = field(default_factory=list)
    completed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def active_subgoal(self) -> Optional["Goal"]:
        return next((g for g in self.subgoals if not g.completed), None)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Goal":
        return cls(drive=str(data.get("drive", "")),
                   urgency=float(data.get("urgency", 0.0)),
                   statement=str(data.get("statement", "")),
                   created_tick=int(data.get("created_tick", 0)),
                   age=int(data.get("age", 0)),
                   subgoals=[cls.from_dict(g) for g in (data.get("subgoals") or [])
                             if isinstance(g, dict)],
                   completed=bool(data.get("completed", False)))


@dataclass
class Mood:
    valence: float      # rata-rata level drive  [-1..1]  (senang ↔ murung)
    arousal: float      # rata-rata urgensi     [0..1]   (tenang ↔ gelisah)

    def modulation(self) -> Dict[str, float]:
        """Kembalikan dict parameter yang bisa di-sebar ke semua modul."""
        # valence+ → melebarkan pencabangan; valence− → menyempit.
        # arousal+ → lebih dalam dan belajar cepat; arousal− → hemat.
        branch_factor_mult = 1.0 + max(self.valence, -0.5) * 0.6   # 0.7 .. 1.6
        sigma_mult = 1.0 + max(self.valence, -0.5) * 0.5           # 0.75 .. 1.5
        max_layers_mult = 1.0 + max(self.arousal, 0.0) * 0.8       # 1.0 .. 1.8
        learning_rate_mult = 1.0 + max(self.arousal, 0.0) * 0.5
        pruning_aggressiveness = max(0.3, 1.0 - max(self.valence, -0.5) * 0.5)  # mood buruk → tegas
        energy_bias = -self.arousal * 0.2  # arousal tinggi = cenderung boros
        return {
            "branch_factor_mult": branch_factor_mult,
            "sigma_mult": sigma_mult,
            "max_layers_mult": max_layers_mult,
            "learning_rate_mult": learning_rate_mult,
            "pruning_aggressiveness": pruning_aggressiveness,
            "energy_bias": energy_bias,
            "valence": self.valence,
            "arousal": self.arousal,
        }


Goal.__module__ = Mood.__module__ = "pycos.inti.naluri"
