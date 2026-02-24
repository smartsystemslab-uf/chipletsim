# chipletsim/metrics.py
# ============================================================
import math
from .system import SystemParams
from .workloads import WorkloadProfile


def inter_chiplet_traffic_ratio(
    partitioning_quality: float,
    workload: WorkloadProfile,
) -> float:
    """
    Compute the fraction of traffic crossing chiplet boundaries.

    Args:
        partitioning_quality: float in [0, 1]. 0 = random, 1 = optimal.
        workload: WorkloadProfile instance.

    Returns:
        Traffic ratio in [0, 1].
    """
    assert 0.0 <= partitioning_quality <= 1.0, "quality must be in [0, 1]"
    max_reduction = 0.70  # optimal partitioning reduces cross-traffic by up to 70%
    return workload.base_traffic_ratio * (1.0 - partitioning_quality * max_reduction)


def compute_latency_ns(
    partitioning_quality: float,
    num_chiplets: int,
    workload: WorkloadProfile,
    params: SystemParams,
) -> float:
    """Average inference latency in nanoseconds."""
    traffic = inter_chiplet_traffic_ratio(partitioning_quality, workload)
    hop_lat = params.hop_latency(num_chiplets)
    return params.intra_chiplet_latency_ns + traffic * hop_lat


def compute_congestion(
    partitioning_quality: float,
    num_chiplets: int,
    workload: WorkloadProfile,
    params: SystemParams,
) -> float:
    """
    Network congestion as a percentage (0–100%).
    Values above 70% are considered unsustainable.
    """
    traffic = inter_chiplet_traffic_ratio(partitioning_quality, workload)
    raw = (traffic * workload.memory_intensity) / (num_chiplets * 0.1)
    return min(95.0, raw * 100.0)


def compute_throughput(
    partitioning_quality: float,
    num_chiplets: int,
    workload: WorkloadProfile,
    params: SystemParams,
    baseline_images_per_sec: float = 100.0,
) -> float:
    """System throughput in images/sec."""
    congestion = compute_congestion(partitioning_quality, num_chiplets, workload, params)
    parallel_eff = partitioning_quality * 0.85 + 0.15
    congestion_penalty = (100.0 - congestion) / 100.0 if congestion > 70.0 else 0.9
    return baseline_images_per_sec * num_chiplets * parallel_eff * congestion_penalty


def compute_energy_efficiency(
    partitioning_quality: float,
    num_chiplets: int,
    workload: WorkloadProfile,
    params: SystemParams,
) -> float:
    """Energy efficiency in TOPS/W."""
    throughput = compute_throughput(partitioning_quality, num_chiplets, workload, params)
    traffic = inter_chiplet_traffic_ratio(partitioning_quality, workload)
    compute_power = num_chiplets * params.power_per_chiplet_W
    comm_power = traffic * num_chiplets * params.comm_power_per_unit_W
    total_power = compute_power + comm_power
    tops = throughput * workload.flops_per_image / 1e12
    return tops / total_power


def compute_comm_overhead(
    partitioning_quality: float,
    num_chiplets: int,
    workload: WorkloadProfile,
    params: SystemParams,
) -> float:
    """Communication overhead as a percentage of execution time."""
    traffic = inter_chiplet_traffic_ratio(partitioning_quality, workload)
    latency = compute_latency_ns(partitioning_quality, num_chiplets, workload, params)
    congestion = compute_congestion(partitioning_quality, num_chiplets, workload, params)
    base = traffic * (latency / params.intra_chiplet_latency_ns)
    mult = 1.0 + ((congestion - 70.0) / 30.0) if congestion > 70.0 else 1.0
    return min(85.0, base * mult * 100.0)
