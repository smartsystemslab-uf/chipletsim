
# tests/test_simulator.py
# ============================================================
import pytest
from chipletsim import ChipletSimulator

sim = ChipletSimulator()

def test_run_returns_result():
    r = sim.run(4, "ResNet-50", 0.75)
    assert r.throughput_img_per_sec > 0
    assert r.energy_efficiency_tops_per_w > 0

def test_sweep_length():
    results = sim.sweep(4, "VGG-16", quality_steps=11)
    assert len(results) == 11

def test_invalid_workload():
    with pytest.raises(ValueError):
        sim.run(4, "UnknownNet", 0.5)

def test_invalid_quality():
    with pytest.raises(ValueError):
        sim.run(4, "ResNet-50", 1.5)

def test_all_workloads_run():
    for wl in ["ResNet-50", "VGG-16", "DarkNet-19"]:
        r = sim.run(4, wl, 0.5)
        assert r.inter_chiplet_latency_ns > 0
