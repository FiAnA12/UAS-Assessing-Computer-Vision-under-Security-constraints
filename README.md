# UAS Computer Vision Conflict Detection Under Secure Communication Constraints

**Dissertation:** *Assessing Computer Vision-Based Conflict Detection in UAS Traffic Monitoring Under Secure Communication Constraints*  
**Author:** Fadjimata Issoufou Anaroua  
**Degree:** Doctor of Philosophy in Electrical Engineering and Computer Science  
**Institution:** Embry-Riddle Aeronautical University, Daytona Beach, Florida  
**Year:** 2026  
**Advisor:** Dr. Bryan Watson

---

## Overview

This repository contains the complete Python implementation used to conduct all 78 experimental runs reported in the dissertation. It contains the replay-based emulation/simulation implementation used to reproduce the experimental structure. The framework replays fixed UAS traffic scenarios through simulated YOLOv5s-style detection outputs, security emulation, network emulation, and monitoring-evaluation stages. The computer vision stage uses empirically parameterized YOLOv5s timing and detection-performance assumptions rather than live neural-network inference on raw video frames. The code evaluates the impact of cryptographic security mechanisms and network constraints on a computer vision-based UAS traffic monitoring pipeline, across four evaluation phases and six traffic density scenarios.

---

## Repository Structure

```
uas-cv-conflict-detection/
├── complete_experiment_code.py   # All 78 experimental runs (Phases 1–4)
├── data_analysis_script.py       # Figures and statistical tables for Chapter 7
├── requirements.txt              # Pinned Python dependencies
└── README.md
```

---

## Experimental Design

| Phase | Description | Runs |
|-------|-------------|------|
| 1 — Baseline | No security, unconstrained network | 6 |
| 2 — Security Impact | None / AES-256-GCM / AES-256-GCM + HMAC-SHA256 | 18 |
| 3 — Network Constraints | Bandwidth, latency, and packet loss sweeps | 42 |
| 4 — Worst-Case | Maximum security + most constrained network | 12 |
| **Total** | | **78** |

Each full dissertation run processes the complete replay scenario duration, approximately 3,600–5,400 frames per scenario at 30 fps. For quick functional testing, the script can be run with a reduced frame count such as 180 frames.

---

## Requirements

- Python 3.10+
- NVIDIA GPU recommended for CV inference benchmarking (experiments were run on GTX 1080 Ti)

Install dependencies:

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
opencv-python==4.9.0.80
numpy==1.26.4
torch==2.2.1
torchvision==0.17.1
cryptography==42.0.5
pandas==2.2.1
matplotlib==3.8.3
seaborn==0.13.2
scipy==1.12.0
pyyaml==6.0.1
```

---

## Running the Experiments

### Step 1 — Run all 78 experiments

```bash
python complete_experiment_code.py
```

Output is written to `experiment_results/`:
- `experiment_plan.json` — structured ablation/factor-isolation configuration list
- `exp_NNN_config.yaml` — per-run configuration
- `exp_NNN_metrics.csv` — per-frame latency measurements
- `exp_NNN_summary.json` — aggregated run statistics
- `all_results.csv` — consolidated results for all 78 runs

> **Estimated runtime:** ~13 hours on the reference hardware. For a quick functional test, reduce `num_frames` from 180 to 10 in `main()`.

### Step 2 — Generate figures and tables

```bash
python data_analysis_script.py
```

Output is written to `analysis_output/`:
- `figure_7_1_latency_breakdown.png / .pdf`
- `figure_7_2_baseline_performance.png / .pdf`
- `figure_7_3_bandwidth_impact.png / .pdf`
- `figure_7_4_network_latency.png / .pdf`
- `figure_7_5_packet_loss.png / .pdf`
- `figure_7_6_worst_case.png / .pdf`
- `figure_7_7_security_overhead.png / .pdf`
- `figure_7_8_throughput.png / .pdf`
- `table_7_1_baseline_performance.csv / .tex`
- `table_7_2_security_overhead.csv / .tex`
- `table_7_3_bandwidth_constraints.csv / .tex`
- `summary_report.json / .txt`

---

## Key Results Summary

| Metric | Value |
|--------|-------|
| Baseline E2E latency (no security, 50 Mbps) | ~42 ms |
| AES-256-GCM overhead | +0.3 ms (+0.6%) |
| AES-256-GCM + HMAC-SHA256 overhead | +0.7 ms (+1.4%) |
| Critical bandwidth threshold | 2 Mbps |
| Propagation latency limit (100 ms budget) | ~58 ms |
| Baseline F1-score (low density) | 0.942 |
| Baseline tracking continuity (low density) | 0.978 |

---

## Reproducibility

- All random seeds are fixed (`np.random.seed(42)`) for deterministic output.
- The exact code snapshot used for dissertation results is tagged: `v1.0-dissertation-submission`

---

## Citation

If you use this code in your research, please cite:

```
Anaroua, F. I. (2026). Assessing Computer Vision-Based Conflict Detection in UAS 
Traffic Monitoring Under Secure Communication Constraints [Doctoral dissertation, 
Embry-Riddle Aeronautical University].
```

---

## License

This code is released for academic reproducibility purposes. Please contact the author for any other use.
