ChipletSim: A Simulation Framework for Chiplet-Based DNN Accelerator Design

Associated Paper: Effects of Poor Workload Partitioning on System Performance for Chiplet-Based Systems
[Peter Mbua, Peter Forcha, Christophe Bobda], [in Review at MDIP Electronics(Preprints.org)], [2026]
[https://www.preprints.org/manuscript/202602.0486] | [Cite]


Overview
ChipletSim is an open-source simulation framework for evaluating the impact of workload partitioning on chiplet-based DNN accelerator systems. It models a configurable multi-chiplet architecture connected via a 2D mesh Network-on-Interposer (NoI), and exposes key metrics including:

Inter-chiplet communication latency and traffic
Network congestion under varying partitioning strategies
System throughput (images/sec)
Energy efficiency (TOPS/W)
Communication overhead as a fraction of execution time

The framework supports three representative DNN workloads (ResNet-50, VGG-16, DarkNet-19) and simulates partitioning quality from random assignment (0%) to near-optimal (100%), inspired by simulated annealing-based partitioning algorithms.
