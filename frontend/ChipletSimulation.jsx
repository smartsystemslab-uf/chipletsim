/**
 * ChipletSimulation.jsx
 *
 * Interactive React web app for the ChipletSim framework.
 *
 * SmartSystems Lab
 * Author: Peter Mbua
 *
 * Usage:
 *   Import and render <ChipletSimulation /> in your React app entry point.
 *
 * Dependencies:
 *   - recharts
 *   - lucide-react
 *   - tailwindcss
 */

import React, { useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { Play, Pause, RotateCcw, Settings, Download } from 'lucide-react';

const ChipletSimulation = () => {
  const [config, setConfig] = useState({
    numChiplets: 4,
    coresPerChiplet: 16,
    workload: 'ResNet-50',
    partitioningQuality: 50
  });

  const [simRunning, setSimRunning] = useState(false);
  const [results, setResults] = useState([]);
  const [currentMetrics, setCurrentMetrics] = useState(null);
  const [showConfig, setShowConfig] = useState(false);

  // ── System parameters ──────────────────────────────────────────────────────
  const systemParams = {
    intraChipletLatency: 45,          // ns
    intraChipletBandwidth: 512,        // GB/s
    interChipletBandwidthBase: 128,    // GB/s
    baseInterChipletLatency: 85,       // ns
    maxInterChipletLatency: 850,       // ns
  };

  // ── Workload profiles ──────────────────────────────────────────────────────
  const workloadProfiles = {
    'ResNet-50': {
      computeIntensity: 0.7,
      memoryIntensity: 0.5,
      communicationPattern: 'balanced',
      baseOps: 3.8e9,
      baseMemAccess: 25.5e6
    },
    'VGG-16': {
      computeIntensity: 0.6,
      memoryIntensity: 0.9,
      communicationPattern: 'memory-bound',
      baseOps: 15.5e9,
      baseMemAccess: 138e6
    },
    'DarkNet-19': {
      computeIntensity: 0.5,
      memoryIntensity: 0.4,
      communicationPattern: 'sparse',
      baseOps: 5.6e9,
      baseMemAccess: 32e6
    }
  };

  // ── Metric helpers ─────────────────────────────────────────────────────────
  const calcTraffic = (quality, workload) => {
    const profile = workloadProfiles[workload];
    const base = profile.communicationPattern === 'sparse' ? 0.45
               : profile.communicationPattern === 'memory-bound' ? 0.65 : 0.55;
    return base * (1 - (quality / 100) * 0.7);
  };

  const calcLatency = (quality, numChiplets, workload) => {
    const traffic = calcTraffic(quality, workload);
    const avgHops = Math.log2(numChiplets);
    const hopLat = systemParams.baseInterChipletLatency
      + avgHops * (systemParams.maxInterChipletLatency - systemParams.baseInterChipletLatency) / 4;
    return systemParams.intraChipletLatency + traffic * hopLat;
  };

  const calcCongestion = (quality, numChiplets, workload) => {
    const traffic = calcTraffic(quality, workload);
    const profile = workloadProfiles[workload];
    return Math.min(95, (traffic * profile.memoryIntensity) / (numChiplets * 0.1) * 100);
  };

  const calcThroughput = (quality, numChiplets, workload) => {
    const congestion = calcCongestion(quality, numChiplets, workload);
    const parallelEff = (quality / 100) * 0.85 + 0.15;
    const congestionPenalty = congestion > 70 ? (100 - congestion) / 100 : 0.9;
    return 100 * numChiplets * parallelEff * congestionPenalty;
  };

  const calcEnergyEff = (quality, numChiplets, workload) => {
    const throughput = calcThroughput(quality, numChiplets, workload);
    const traffic = calcTraffic(quality, workload);
    const totalPower = numChiplets * 50 + traffic * numChiplets * 15;
    const tops = throughput * workloadProfiles[workload].baseOps / 1e12;
    return tops / totalPower;
  };

  const calcCommOverhead = (quality, numChiplets, workload) => {
    const traffic = calcTraffic(quality, workload);
    const latency = calcLatency(quality, numChiplets, workload);
    const congestion = calcCongestion(quality, numChiplets, workload);
    const base = traffic * (latency / systemParams.intraChipletLatency);
    const mult = congestion > 70 ? 1 + (congestion - 70) / 30 : 1;
    return Math.min(85, base * mult * 100);
  };

  const buildMetrics = (quality, numChiplets, workload) => ({
    interChipletLatency: calcLatency(quality, numChiplets, workload),
    interChipletTraffic: calcTraffic(quality, workload) * 100,
    networkCongestion: calcCongestion(quality, numChiplets, workload),
    throughput: calcThroughput(quality, numChiplets, workload),
    energyEfficiency: calcEnergyEff(quality, numChiplets, workload),
    commOverhead: calcCommOverhead(quality, numChiplets, workload),
  });

  // ── Simulation actions ─────────────────────────────────────────────────────
  const runSimulation = () => {
    const metrics = buildMetrics(config.partitioningQuality, config.numChiplets, config.workload);
    setCurrentMetrics(metrics);
    setResults(prev => [...prev, { ...config, ...metrics, timestamp: Date.now() }]);
  };

  const runParameterSweep = () => {
    setSimRunning(true);
    const sweep = [];
    for (let q = 0; q <= 100; q += 10) {
      sweep.push({
        partitioningQuality: q,
        ...buildMetrics(q, config.numChiplets, config.workload),
      });
    }
    setResults(sweep);
    setCurrentMetrics(sweep[sweep.length - 1]);
    setSimRunning(false);
  };

  const resetSimulation = () => {
    setResults([]);
    setCurrentMetrics(null);
    setConfig(c => ({ ...c, partitioningQuality: 50 }));
  };

  const exportResults = () => {
    const headers = ['Partitioning Quality','Latency (ns)','Traffic (%)','Congestion (%)','Throughput (img/s)','Energy Eff (TOPS/W)','Comm Overhead (%)'];
    const rows = results.map(r => [
      r.partitioningQuality,
      r.interChipletLatency?.toFixed(2),
      r.interChipletTraffic?.toFixed(2),
      r.networkCongestion?.toFixed(2),
      r.throughput?.toFixed(2),
      r.energyEfficiency?.toFixed(2),
      r.commOverhead?.toFixed(2),
    ]);
    const csv = [headers, ...rows].map(r => r.join(',')).join('\n');
    const a = Object.assign(document.createElement('a'), {
      href: URL.createObjectURL(new Blob([csv], { type: 'text/csv' })),
      download: `chiplet_sim_${config.workload}_${config.numChiplets}chiplets.csv`,
    });
    a.click();
  };

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="w-full max-w-7xl mx-auto p-6 bg-gray-50">
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">

        {/* Header */}
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          Chiplet-Based DNN Accelerator Simulator
        </h1>
        <p className="text-gray-600 mb-1">
          Evaluating workload partitioning effects on multi-chiplet systems with 2D mesh network-on-interposer
        </p>
        <p className="text-sm text-gray-500 mb-6">
          <span className="font-medium text-gray-600">SmartSystems Lab</span>
          {' '}&mdash;{' '}
          Authored by <span className="font-medium text-gray-600">Peter Mbua</span>
        </p>

        {/* Configuration Panel */}
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-700">System Configuration</h2>
            <button
              onClick={() => setShowConfig(!showConfig)}
              className="flex items-center gap-2 px-3 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              <Settings size={16} />
              {showConfig ? 'Hide' : 'Show'} Details
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Chiplets */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Number of Chiplets</label>
              <select
                value={config.numChiplets}
                onChange={e => setConfig(c => ({ ...c, numChiplets: parseInt(e.target.value) }))}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {[2, 4, 8, 16].map(n => <option key={n} value={n}>{n} Chiplets</option>)}
              </select>
            </div>

            {/* Cores */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Cores per Chiplet</label>
              <input
                type="number"
                value={config.coresPerChiplet}
                onChange={e => setConfig(c => ({ ...c, coresPerChiplet: parseInt(e.target.value) }))}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="4" max="64"
              />
            </div>

            {/* Workload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Workload</label>
              <select
                value={config.workload}
                onChange={e => setConfig(c => ({ ...c, workload: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {['ResNet-50', 'VGG-16', 'DarkNet-19'].map(w => <option key={w}>{w}</option>)}
              </select>
            </div>

            {/* Partitioning Quality */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Partitioning Quality: {config.partitioningQuality}%
              </label>
              <input
                type="range"
                value={config.partitioningQuality}
                onChange={e => setConfig(c => ({ ...c, partitioningQuality: parseInt(e.target.value) }))}
                className="w-full" min="0" max="100"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Random</span><span>Optimal</span>
              </div>
            </div>
          </div>

          {/* Expanded system params */}
          {showConfig && (
            <div className="mt-4 grid grid-cols-2 md:grid-cols-3 gap-4 p-4 bg-white rounded border border-gray-200">
              {[
                ['Intra-Chiplet Latency', `${systemParams.intraChipletLatency} ns`],
                ['Intra-Chiplet BW', `${systemParams.intraChipletBandwidth} GB/s`],
                ['Inter-Chiplet BW', `${systemParams.interChipletBandwidthBase} GB/s`],
                ['Min Inter-Chiplet Lat', `${systemParams.baseInterChipletLatency} ns`],
                ['Max Inter-Chiplet Lat', `${systemParams.maxInterChipletLatency} ns`],
                ['Total Cores', config.numChiplets * config.coresPerChiplet],
              ].map(([label, value]) => (
                <div key={label}>
                  <div className="text-sm font-medium text-gray-700">{label}</div>
                  <div className="text-lg font-semibold text-blue-600">{value}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Control Buttons */}
        <div className="flex gap-3 mb-6">
          <button onClick={runSimulation}
            className="flex items-center gap-2 px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 font-medium">
            <Play size={20} /> Run Single Point
          </button>
          <button onClick={runParameterSweep} disabled={simRunning}
            className="flex items-center gap-2 px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 font-medium disabled:bg-gray-400">
            {simRunning ? <Pause size={20} /> : <Play size={20} />}
            Parameter Sweep (Quality 0–100%)
          </button>
          <button onClick={resetSimulation}
            className="flex items-center gap-2 px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 font-medium">
            <RotateCcw size={20} /> Reset
          </button>
          {results.length > 0 && (
            <button onClick={exportResults}
              className="flex items-center gap-2 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 font-medium ml-auto">
              <Download size={20} /> Export CSV
            </button>
          )}
        </div>

        {/* Metric Cards */}
        {currentMetrics && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
            {[
              { label: 'Inter-Chiplet Latency', value: currentMetrics.interChipletLatency.toFixed(1), unit: 'nanoseconds', color: 'blue' },
              { label: 'Inter-Chiplet Traffic', value: `${currentMetrics.interChipletTraffic.toFixed(1)}%`, unit: 'of total traffic', color: 'orange' },
              { label: 'Network Congestion', value: `${currentMetrics.networkCongestion.toFixed(1)}%`, unit: currentMetrics.networkCongestion > 70 ? 'Unsustainable' : 'Sustainable', color: currentMetrics.networkCongestion > 70 ? 'red' : 'green' },
              { label: 'Throughput', value: currentMetrics.throughput.toFixed(1), unit: 'images/sec', color: 'purple' },
              { label: 'Energy Efficiency', value: currentMetrics.energyEfficiency.toFixed(2), unit: 'TOPS/W', color: 'teal' },
              { label: 'Comm Overhead', value: `${currentMetrics.commOverhead.toFixed(1)}%`, unit: 'of exec time', color: 'indigo' },
            ].map(({ label, value, unit, color }) => (
              <div key={label} className={`bg-${color}-50 rounded-lg p-4 border border-${color}-200`}>
                <div className="text-sm font-medium text-gray-600 mb-1">{label}</div>
                <div className={`text-2xl font-bold text-${color}-700`}>{value}</div>
                <div className="text-xs text-gray-500">{unit}</div>
              </div>
            ))}
          </div>
        )}

        {/* Charts */}
        {results.length > 1 && (
          <div className="space-y-6">
            {/* Throughput + Energy */}
            <div className="bg-white rounded-lg p-4 border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-700 mb-4">Performance vs Partitioning Quality</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={results}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="partitioningQuality" label={{ value: 'Partitioning Quality (%)', position: 'insideBottom', offset: -5 }} />
                  <YAxis yAxisId="left" label={{ value: 'Throughput (img/s)', angle: -90, position: 'insideLeft' }} />
                  <YAxis yAxisId="right" orientation="right" label={{ value: 'Energy Eff (TOPS/W)', angle: 90, position: 'insideRight' }} />
                  <Tooltip />
                  <Legend />
                  <Line yAxisId="left" type="monotone" dataKey="throughput" stroke="#8b5cf6" strokeWidth={2} name="Throughput" />
                  <Line yAxisId="right" type="monotone" dataKey="energyEfficiency" stroke="#14b8a6" strokeWidth={2} name="Energy Efficiency" />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Communication metrics */}
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-700 mb-4">Communication Metrics</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={results}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="partitioningQuality" label={{ value: 'Partitioning Quality (%)', position: 'insideBottom', offset: -5 }} />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="interChipletLatency" stroke="#3b82f6" strokeWidth={2} name="Latency (ns)" />
                    <Line type="monotone" dataKey="interChipletTraffic" stroke="#f97316" strokeWidth={2} name="Traffic (%)" />
                    <Line type="monotone" dataKey="commOverhead" stroke="#6366f1" strokeWidth={2} name="Overhead (%)" />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Congestion */}
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-700 mb-4">Network Congestion</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={results}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="partitioningQuality" label={{ value: 'Partitioning Quality (%)', position: 'insideBottom', offset: -5 }} />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="networkCongestion" stroke="#ef4444" strokeWidth={2} name="Congestion (%)" />
                    <Line type="monotone" dataKey={() => 70} stroke="#22c55e" strokeDasharray="5 5" name="Sustainable Threshold" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* About */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold text-gray-700 mb-3">About This Simulation</h2>
        <p className="text-sm text-gray-600 mb-2">
          This simulator models a chiplet-based DNN accelerator system with configurable topology (2–16 chiplets)
          connected via a 2D mesh network-on-interposer.
        </p>
        <p className="text-sm text-gray-600 font-medium mb-1">Key Features:</p>
        <ul className="list-disc list-inside ml-4 text-sm text-gray-600 space-y-1">
          <li>Realistic latency modeling: 45 ns intra-chiplet, 85–850 ns inter-chiplet based on routing distance</li>
          <li>Bandwidth differentiation: 512 GB/s intra-chiplet vs 128 GB/s inter-chiplet</li>
          <li>Simulated annealing-based partitioning quality from 0% (random) to 100% (optimal)</li>
          <li>Three representative DNN workloads with distinct communication patterns</li>
          <li>Comprehensive metrics: latency, traffic, congestion, throughput, energy efficiency, and overhead</li>
        </ul>
        <p className="text-xs text-gray-400 mt-4">
          SmartSystems Lab &mdash; Peter Mbua
        </p>
      </div>
    </div>
  );
};

export default ChipletSimulation;
