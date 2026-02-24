
# tests/test_metrics.py
# ============================================================
import pytest
from chipletsim.system import SystemParams
from chipletsim.workloads import WORKLOAD_REGISTRY
from chipletsim import metrics as m

params = SystemParams()
resnet = WORKLOAD_REGISTRY["ResNet-50"]

def test_traffic_ratio_bounds():
    for q in [0.0, 0.5, 1.0]:
        r = m.inter_chiplet_traffic_ratio(q, resnet)
        assert 0.0 <= r <= 1.0

def test_traffic_decreases_with_quality():
    r0 = m.inter_chiplet_traffic_ratio(0.0, resnet)
    r1 = m.inter_chiplet_traffic_ratio(1.0, resnet)
    assert r1 < r0

def test_congestion_bounds():
    for n in [2, 4, 8, 16]:
        c = m.compute_congestion(0.5, n, resnet, params)
        assert 0.0 <= c <= 100.0

def test_congestion_decreases_with_chiplets():
    c4 = m.compute_congestion(0.3, 4, resnet, params)
    c16 = m.compute_congestion(0.3, 16, resnet, params)
    assert c16 < c4

def test_throughput_scales_with_chiplets():
    t4 = m.compute_throughput(0.8, 4, resnet, params)
    t8 = m.compute_throughput(0.8, 8, resnet, params)
    assert t8 > t4

def test_invalid_quality_raises():
    with pytest.raises(AssertionError):
        m.inter_chiplet_traffic_ratio(-0.1, resnet)
    with pytest.raises(AssertionError):
        m.inter_chiplet_traffic_ratio(1.1, resnet)
