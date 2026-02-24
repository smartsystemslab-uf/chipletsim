
# chipletsim/system.py
# ============================================================
from dataclasses import dataclass

@dataclass
class SystemParams:
    """
    Hardware parameters for the chiplet system.
    Based on representative values from open-source chiplet literature.
    """
    intra_chiplet_latency_ns: float = 45.0       # ns
    intra_chiplet_bandwidth_GBs: float = 512.0   # GB/s
    inter_chiplet_bandwidth_GBs: float = 128.0   # GB/s
    min_inter_chiplet_latency_ns: float = 85.0   # ns (1 hop)
    max_inter_chiplet_latency_ns: float = 850.0  # ns (max hops in 2D mesh)
    power_per_chiplet_W: float = 50.0            # W
    comm_power_per_unit_W: float = 15.0          # W per unit traffic ratio

    def hop_latency(self, num_chiplets: int) -> float:
        """
        Average hop latency for a 2D mesh with `num_chiplets` nodes.
        Uses log2(N) as average hop count approximation.
        """
        import math
        avg_hops = math.log2(max(num_chiplets, 2))
        lat_range = self.max_inter_chiplet_latency_ns - self.min_inter_chiplet_latency_ns
        return self.min_inter_chiplet_latency_ns + avg_hops * lat_range / 4.0
