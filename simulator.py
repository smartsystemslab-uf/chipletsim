
# chipletsim/simulator.py
# ============================================================
from dataclasses import dataclass, field, asdict
from typing import Optional
from .system import SystemParams
from .workloads import WorkloadProfile, WORKLOAD_REGISTRY
from . import metrics as m


@dataclass
class SimulationResult:
    """Output of a single simulation run."""
    num_chiplets: int
    cores_per_chiplet: int
    workload: str
    partitioning_quality: float           # 0–1

    # Computed metrics
    inter_chiplet_latency_ns: float = 0.0
    inter_chiplet_traffic_pct: float = 0.0
    network_congestion_pct: float = 0.0
    throughput_img_per_sec: float = 0.0
    energy_efficiency_tops_per_w: float = 0.0
    comm_overhead_pct: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


class ChipletSimulator:
    """
    Main simulation engine for chiplet-based DNN accelerator evaluation.

    Example
    -------
    >>> sim = ChipletSimulator()
    >>> result = sim.run(num_chiplets=4, workload="ResNet-50", partitioning_quality=0.75)
    >>> print(result.throughput_img_per_sec)
    """

    def __init__(
        self,
        params: Optional[SystemParams] = None,
        baseline_images_per_sec: float = 100.0,
    ):
        self.params = params or SystemParams()
        self.baseline = baseline_images_per_sec

    def run(
        self,
        num_chiplets: int,
        workload: str,
        partitioning_quality: float,
        cores_per_chiplet: int = 16,
    ) -> SimulationResult:
        """
        Execute a single simulation point.

        Args:
            num_chiplets: Number of chiplets (2, 4, 8, or 16).
            workload: Workload name from WORKLOAD_REGISTRY.
            partitioning_quality: Partitioning quality in [0, 1].
            cores_per_chiplet: Cores per chiplet (affects labeling only).

        Returns:
            SimulationResult with all computed metrics.
        """
        if workload not in WORKLOAD_REGISTRY:
            raise ValueError(f"Unknown workload '{workload}'. "
                             f"Choose from {list(WORKLOAD_REGISTRY.keys())}")
        if not (0.0 <= partitioning_quality <= 1.0):
            raise ValueError("partitioning_quality must be in [0.0, 1.0]")

        wl = WORKLOAD_REGISTRY[workload]
        p = self.params

        return SimulationResult(
            num_chiplets=num_chiplets,
            cores_per_chiplet=cores_per_chiplet,
            workload=workload,
            partitioning_quality=partitioning_quality,
            inter_chiplet_latency_ns=m.compute_latency_ns(partitioning_quality, num_chiplets, wl, p),
            inter_chiplet_traffic_pct=m.inter_chiplet_traffic_ratio(partitioning_quality, wl) * 100,
            network_congestion_pct=m.compute_congestion(partitioning_quality, num_chiplets, wl, p),
            throughput_img_per_sec=m.compute_throughput(partitioning_quality, num_chiplets, wl, p, self.baseline),
            energy_efficiency_tops_per_w=m.compute_energy_efficiency(partitioning_quality, num_chiplets, wl, p),
            comm_overhead_pct=m.compute_comm_overhead(partitioning_quality, num_chiplets, wl, p),
        )

    def sweep(
        self,
        num_chiplets: int,
        workload: str,
        quality_steps: int = 11,
        cores_per_chiplet: int = 16,
    ) -> list[SimulationResult]:
        """
        Sweep partitioning quality from 0 to 1 in `quality_steps` steps.
        """
        import numpy as np
        qualities = np.linspace(0.0, 1.0, quality_steps)
        return [
            self.run(num_chiplets, workload, float(q), cores_per_chiplet)
            for q in qualities
        ]
