
# chipletsim/__init__.py
# ============================================================
"""ChipletSim: Chiplet-Based DNN Accelerator Simulation Framework."""

__version__ = "1.0.0"
__author__ = "Peter Mbua"

from .simulator import ChipletSimulator
from .system import SystemParams
from .workloads import WorkloadProfile, WORKLOAD_REGISTRY

__all__ = ["ChipletSimulator", "SystemParams", "WorkloadProfile", "WORKLOAD_REGISTRY"]
