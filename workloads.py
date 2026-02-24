
# chipletsim/workloads.py
# ============================================================
from dataclasses import dataclass
from typing import Literal

CommunicationPattern = Literal["balanced", "memory-bound", "sparse"]

@dataclass
class WorkloadProfile:
    """Characterization of a DNN workload for simulation purposes."""
    name: str
    compute_intensity: float        # 0–1, relative compute demand
    memory_intensity: float         # 0–1, relative memory demand
    communication_pattern: CommunicationPattern
    flops_per_image: float          # total FLOPs per inference
    mem_access_bytes: float         # memory accesses per inference

    @property
    def base_traffic_ratio(self) -> float:
        """
        Baseline fraction of traffic that crosses chiplet boundaries
        before any partitioning optimization.
        """
        pattern_map = {
            "sparse": 0.45,
            "memory-bound": 0.65,
            "balanced": 0.55,
        }
        return pattern_map[self.communication_pattern]


WORKLOAD_REGISTRY: dict[str, WorkloadProfile] = {
    "ResNet-50": WorkloadProfile(
        name="ResNet-50",
        compute_intensity=0.7,
        memory_intensity=0.5,
        communication_pattern="balanced",
        flops_per_image=3.8e9,
        mem_access_bytes=25.5e6,
    ),
    "VGG-16": WorkloadProfile(
        name="VGG-16",
        compute_intensity=0.6,
        memory_intensity=0.9,
        communication_pattern="memory-bound",
        flops_per_image=15.5e9,
        mem_access_bytes=138e6,
    ),
    "DarkNet-19": WorkloadProfile(
        name="DarkNet-19",
        compute_intensity=0.5,
        memory_intensity=0.4,
        communication_pattern="sparse",
        flops_per_image=5.6e9,
        mem_access_bytes=32e6,
    ),
}
