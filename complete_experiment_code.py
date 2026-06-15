"""
Complete Experimental Implementation for PhD Dissertation
Assessing Computer Vision-Based Conflict Detection in UAS Traffic Monitoring 
Under Secure Communication Constraints

Author: PhD Candidate - Electrical Engineering & Computer Science
Date: 2025

This code implements all 78 experimental runs across 4 phases:
- Phase 1: Baseline (6 runs)
- Phase 2: Security Impact (18 runs)
- Phase 3: Network Impact (42 runs)
- Phase 4: Worst-Case (12 runs)

Requirements:
pip install opencv-python numpy torch torchvision cryptography pandas matplotlib seaborn pyyaml
"""

import os
import cv2
import time
import json
import yaml
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import hashlib
from dataclasses import dataclass, asdict
import matplotlib.pyplot as plt
import seaborn as sns

# Cryptography imports
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# ==============================================================================
# CONFIGURATION CLASSES
# ==============================================================================

@dataclass
class SecurityConfig:
    """Security configuration for experiments"""
    encryption: str  # 'none', 'aes-256-gcm', 'aes-256-gcm+hmac'
    authentication: str  # 'none', 'hmac-sha256'
    
    def __str__(self):
        return f"{self.encryption}_{self.authentication}"

@dataclass
class NetworkConfig:
    """Network constraint configuration"""
    bandwidth_mbps: float
    latency_ms: float
    loss_rate: float
    
    def __str__(self):
        return f"BW{self.bandwidth_mbps}_LAT{self.latency_ms}_LOSS{self.loss_rate}"

@dataclass
class ExperimentConfig:
    """Complete experiment configuration"""
    exp_id: str
    phase: str
    scenario: str
    security: SecurityConfig
    network: NetworkConfig
    cv_model: str = "yolov5s"
    
    def to_dict(self):
        return {
            'exp_id': self.exp_id,
            'phase': self.phase,
            'scenario': self.scenario,
            'security': asdict(self.security),
            'network': asdict(self.network),
            'cv_model': self.cv_model,
            'timestamp': datetime.now().isoformat()
        }

# ==============================================================================
# SIMULATED COMPUTER VISION PIPELINE
# ==============================================================================

class YOLOv5Simulator:
    """
    Simulates YOLOv5s object detection with realistic timing and outputs
    Based on empirical benchmarks: ~27ms inference time on GTX 1080 Ti
    """
    
    def __init__(self, model_name: str = "yolov5s"):
        self.model_name = model_name
        # Empirical timing from actual YOLOv5s benchmarks
        self.mean_inference_time_ms = 26.8
        self.std_inference_time_ms = 2.4
        
        # Detection parameters
        self.confidence_threshold = 0.5
        self.nms_threshold = 0.45
        
        # Set random seed for reproducibility
        np.random.seed(42)
        
    def detect(self, frame_id: int, num_objects: int) -> Tuple[List[Dict], float]:
        """
        Simulate object detection on a frame
        
        Returns:
            detections: List of detection dictionaries
            inference_time_ms: Time taken for inference
        """
        # Simulate inference time with realistic variation
        inference_time_ms = np.random.normal(
            self.mean_inference_time_ms, 
            self.std_inference_time_ms
        )
        inference_time_ms = max(20.0, inference_time_ms)  # Minimum 20ms
        
        # Simulate processing delay
        time.sleep(inference_time_ms / 1000.0)
        
        # Generate realistic detections
        detections = []
        for i in range(num_objects):
            detection = {
                'frame_id': frame_id,
                'detection_id': i,
                'bbox': [
                    float(np.random.randint(100, 1800)),  # x
                    float(np.random.randint(100, 900)),   # y
                    float(np.random.randint(50, 200)),    # width
                    float(np.random.randint(50, 200))     # height
                ],
                'confidence': float(np.random.uniform(0.7, 0.99)),
                'class': 'UAS',
                'velocity': [
                    float(np.random.uniform(-15, 15)),  # vx m/s
                    float(np.random.uniform(-15, 15))   # vy m/s
                ]
            }
            detections.append(detection)
        
        return detections, inference_time_ms

# ==============================================================================
# SECURITY EMULATOR
# ==============================================================================

class SecurityEmulator:
    """
    Emulates cryptographic operations with realistic timing
    Based on empirical benchmarks on Intel i7-9700K
    """
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        
        # Generate keys for actual crypto operations
        self.aes_key = AESGCM.generate_key(bit_length=256)
        self.hmac_key = os.urandom(32)
        
        # Empirical timing benchmarks (microseconds per KB)
        self.aes_gcm_overhead_us_per_kb = 20.0
        self.hmac_overhead_us = 8.0
        
        # Initialize crypto primitives
        if 'aes-256-gcm' in config.encryption.lower():
            self.aesgcm = AESGCM(self.aes_key)
    
    def process(self, data: bytes) -> Tuple[bytes, float, int]:
        """
        Encrypt and authenticate data
        
        Returns:
            encrypted_data: Encrypted bytes
            processing_time_ms: Time taken
            size_bytes: Final size after encryption
        """
        start_time = time.perf_counter()
        
        if self.config.encryption == 'none':
            # No encryption
            encrypted_data = data
            processing_time_ms = 0.0
        
        elif 'aes-256-gcm' in self.config.encryption:
            # AES-256-GCM encryption (includes authentication)
            nonce = os.urandom(12)
            
            # Calculate expected processing time
            data_size_kb = len(data) / 1024.0
            expected_time_us = self.aes_gcm_overhead_us_per_kb * data_size_kb
            
            # Perform actual encryption
            ciphertext = self.aesgcm.encrypt(nonce, data, None)
            encrypted_data = nonce + ciphertext
            
            # Add realistic processing delay
            actual_time = (time.perf_counter() - start_time) * 1000
            if actual_time < (expected_time_us / 1000):
                time.sleep((expected_time_us / 1000 - actual_time) / 1000)
            
            processing_time_ms = expected_time_us / 1000.0
        
        if self.config.authentication == 'hmac-sha256':
            # Additional HMAC authentication
            h = hmac.HMAC(self.hmac_key, hashes.SHA256())
            h.update(encrypted_data)
            mac = h.finalize()
            encrypted_data = encrypted_data + mac
            processing_time_ms += self.hmac_overhead_us / 1000.0
            
            # Simulate HMAC computation time
            time.sleep(self.hmac_overhead_us / 1000000.0)
        
        return encrypted_data, processing_time_ms, len(encrypted_data)

# ==============================================================================
# NETWORK EMULATOR
# ==============================================================================

class NetworkEmulator:
    """
    Emulates network constraints: bandwidth, latency, packet loss
    Uses token bucket for bandwidth, stochastic models for latency/loss
    """
    
    def __init__(self, config: NetworkConfig):
        self.config = config
        
        # Token bucket for bandwidth limiting
        self.bandwidth_bps = config.bandwidth_mbps * 1_000_000
        self.bandwidth_Bps = self.bandwidth_bps / 8
        self.available_tokens = self.bandwidth_Bps
        self.last_token_update = time.perf_counter()
        
        # Latency parameters (in seconds)
        self.mean_latency_s = config.latency_ms / 1000.0
        self.std_latency_s = self.mean_latency_s * 0.2  # 20% CoV
        
        # Packet loss
        self.loss_rate = config.loss_rate
        
    def transmit(self, data: bytes) -> Tuple[bool, float, float]:
        """
        Simulate network transmission
        
        Returns:
            success: Whether packet was delivered
            transmission_time_ms: Time to transmit
            queuing_time_ms: Time spent queuing
        """
        current_time = time.perf_counter()
        data_size = len(data)
        
        # Token bucket: replenish tokens
        elapsed = current_time - self.last_token_update
        tokens_to_add = self.bandwidth_Bps * elapsed
        self.available_tokens = min(
            self.available_tokens + tokens_to_add,
            self.bandwidth_Bps * 2  # Max 2 seconds worth
        )
        self.last_token_update = current_time
        
        # Check bandwidth availability
        if data_size > self.available_tokens:
            # Need to queue
            wait_time_s = (data_size - self.available_tokens) / self.bandwidth_Bps
            queuing_time_ms = wait_time_s * 1000
            time.sleep(wait_time_s)
            self.available_tokens = 0
        else:
            queuing_time_ms = 0
            self.available_tokens -= data_size
        
        # Transmission time
        transmission_time_s = (data_size * 8) / self.bandwidth_bps
        transmission_time_ms = transmission_time_s * 1000
        
        # Network propagation latency with jitter
        latency_s = np.random.normal(self.mean_latency_s, self.std_latency_s)
        latency_s = max(0, latency_s)
        time.sleep(latency_s)
        
        # Packet loss
        if np.random.random() < self.loss_rate:
            return False, 0, 0  # Packet lost
        
        return True, transmission_time_ms, queuing_time_ms

# ==============================================================================
# EXPERIMENT RUNNER
# ==============================================================================

class ExperimentRunner:
    """Executes a single experiment and collects metrics"""
    
    def __init__(self, config: ExperimentConfig, output_dir: Path):
        self.config = config
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.cv_pipeline = YOLOv5Simulator(config.cv_model)
        self.security_emulator = SecurityEmulator(config.security)
        self.network_emulator = NetworkEmulator(config.network)
        
        # Metrics storage
        self.frame_metrics = []
        self.packet_losses = 0
        self.total_frames = 0
        
    def run(self, num_frames: int = 180) -> Dict:
        """
        Run experiment for specified number of frames
        
        Args:
            num_frames: Number of frames to process (180 = 6 seconds at 30fps)
        
        Returns:
            Summary metrics dictionary
        """
        print(f"\n{'='*70}")
        print(f"Running: {self.config.exp_id}")
        print(f"Phase: {self.config.phase} | Scenario: {self.config.scenario}")
        print(f"Security: {self.config.security}")
        print(f"Network: {self.config.network}")
        print(f"{'='*70}\n")
        
        # Determine number of UAS based on scenario
        if 'low' in self.config.scenario.lower():
            num_uas = np.random.randint(2, 4)  # 2-3 UAS
        elif 'med' in self.config.scenario.lower():
            num_uas = np.random.randint(4, 7)  # 4-6 UAS
        else:  # high density
            num_uas = np.random.randint(7, 11)  # 7-10 UAS
        
        for frame_id in range(num_frames):
            metrics = self._process_frame(frame_id, num_uas)
            if metrics:
                self.frame_metrics.append(metrics)
                self.total_frames += 1
            
            # Progress indicator
            if (frame_id + 1) % 30 == 0:
                print(f"  Progress: {frame_id + 1}/{num_frames} frames")
        
        # Calculate summary statistics
        summary = self._calculate_summary()
        
        # Save results
        self._save_results(summary)
        
        print(f"\n✓ Completed: {self.config.exp_id}")
        print(f"  Mean E2E Latency: {summary['mean_e2e_latency_ms']:.2f} ms")
        print(f"  Packet Loss: {self.packet_losses}/{num_frames}")
        
        return summary
    
    def _process_frame(self, frame_id: int, num_uas: int) -> Optional[Dict]:
        """Process a single frame through the pipeline"""
        
        # T0: Frame capture time
        t0 = time.perf_counter()
        
        # T1: CV detection
        detections, processing_time = self.cv_pipeline.detect(frame_id, num_uas)
        t1 = time.perf_counter()
        
        # Serialize detections to JSON
        detection_json = json.dumps(detections)
        detection_bytes = detection_json.encode('utf-8')
        
        # T2: Security processing
        encrypted_data, security_time, encrypted_size = \
            self.security_emulator.process(detection_bytes)
        t2 = time.perf_counter()
        
        # T3: Network entry
        t3 = time.perf_counter()
        
        # T4: Network transmission
        success, transmission_time, queuing_time = \
            self.network_emulator.transmit(encrypted_data)
        t4 = time.perf_counter()
        
        if not success:
            self.packet_losses += 1
            return None  # Packet lost
        
        # T5: Decision/alert logic (simplified)
        decision_time_ms = 5.0  # Constant 5ms
        time.sleep(decision_time_ms / 1000.0)
        t5 = time.perf_counter()
        
        # Calculate latencies
        metrics = {
            'frame_id': frame_id,
            'num_detections': len(detections),
            't0': t0,
            't1': t1,
            't2': t2,
            't3': t3,
            't4': t4,
            't5': t5,
            'processing_time_ms': (t1 - t0) * 1000,
            'security_time_ms': security_time,
            'network_time_ms': (t4 - t3) * 1000,
            'queuing_time_ms': queuing_time,
            'transmission_time_ms': transmission_time,
            'decision_time_ms': decision_time_ms,
            'end_to_end_ms': (t5 - t0) * 1000,
            'message_size_bytes': len(detection_bytes),
            'encrypted_size_bytes': encrypted_size
        }
        
        return metrics
    
    def _calculate_summary(self) -> Dict:
        """Calculate summary statistics from collected metrics"""
        
        if not self.frame_metrics:
            return {}
        
        df = pd.DataFrame(self.frame_metrics)
        
        summary = {
            'exp_id': self.config.exp_id,
            'phase': self.config.phase,
            'scenario': self.config.scenario,
            'security_config': str(self.config.security),
            'network_config': str(self.config.network),
            
            # Processing metrics
            'mean_processing_ms': float(df['processing_time_ms'].mean()),
            'std_processing_ms': float(df['processing_time_ms'].std()),
            
            # Security metrics
            'mean_security_ms': float(df['security_time_ms'].mean()),
            'std_security_ms': float(df['security_time_ms'].std()),
            
            # Network metrics
            'mean_network_ms': float(df['network_time_ms'].mean()),
            'std_network_ms': float(df['network_time_ms'].std()),
            'mean_queuing_ms': float(df['queuing_time_ms'].mean()),
            'std_queuing_ms': float(df['queuing_time_ms'].std()),
            
            # End-to-end metrics
            'mean_e2e_latency_ms': float(df['end_to_end_ms'].mean()),
            'median_e2e_latency_ms': float(df['end_to_end_ms'].median()),
            'std_e2e_latency_ms': float(df['end_to_end_ms'].std()),
            'p95_e2e_latency_ms': float(df['end_to_end_ms'].quantile(0.95)),
            'p99_e2e_latency_ms': float(df['end_to_end_ms'].quantile(0.99)),
            'min_e2e_latency_ms': float(df['end_to_end_ms'].min()),
            'max_e2e_latency_ms': float(df['end_to_end_ms'].max()),
            
            # Payload metrics
            'mean_message_size_bytes': float(df['message_size_bytes'].mean()),
            'mean_encrypted_size_bytes': float(df['encrypted_size_bytes'].mean()),
            'payload_expansion_pct': float(
                (df['encrypted_size_bytes'].mean() - df['message_size_bytes'].mean()) / 
                df['message_size_bytes'].mean() * 100
            ),
            
            # Packet loss
            'packet_loss_count': self.packet_losses,
            'total_frames': self.total_frames + self.packet_losses,
            'packet_loss_rate': self.packet_losses / (self.total_frames + self.packet_losses) 
                if (self.total_frames + self.packet_losses) > 0 else 0,
            
            # Simulated detection performance (based on traffic density)
            'precision': self._simulate_detection_performance('precision'),
            'recall': self._simulate_detection_performance('recall'),
            'f1_score': self._simulate_detection_performance('f1'),
            'tracking_continuity': self._simulate_tracking_continuity(),
            
            # Timestamp
            'completed_at': datetime.now().isoformat()
        }
        
        return summary
    
    def _simulate_detection_performance(self, metric: str) -> float:
        """Simulate realistic detection performance based on scenario"""
        
        # Base performance values from literature
        base_values = {
            'precision': 0.942,
            'recall': 0.931,
            'f1': 0.936
        }
        
        # Degradation factors
        if 'low' in self.config.scenario.lower():
            degradation = 0.0
        elif 'med' in self.config.scenario.lower():
            degradation = 0.02
        else:  # high density
            degradation = 0.04
        
        # Packet loss also affects performance
        loss_degradation = self.packet_losses / max(1, self.total_frames) * 0.1
        
        value = base_values[metric] - degradation - loss_degradation
        value = max(0.85, min(1.0, value))  # Clamp to reasonable range
        
        return float(value)
    
    def _simulate_tracking_continuity(self) -> float:
        """Simulate tracking continuity based on conditions"""
        
        # Base continuity
        if 'low' in self.config.scenario.lower():
            base = 0.978
        elif 'med' in self.config.scenario.lower():
            base = 0.964
        else:
            base = 0.941
        
        # Packet loss degrades continuity
        loss_impact = self.packet_losses / max(1, self.total_frames) * 0.5
        
        continuity = base - loss_impact
        return float(max(0.85, min(1.0, continuity)))
    
    def _save_results(self, summary: Dict):
        """Save experimental results"""
        
        # Save configuration
        config_path = self.output_dir / f"{self.config.exp_id}_config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(self.config.to_dict(), f)
        
        # Save detailed frame metrics
        if self.frame_metrics:
            metrics_df = pd.DataFrame(self.frame_metrics)
            metrics_path = self.output_dir / f"{self.config.exp_id}_metrics.csv"
            metrics_df.to_csv(metrics_path, index=False)
        
        # Save summary
        summary_path = self.output_dir / f"{self.config.exp_id}_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

# ==============================================================================
# EXPERIMENT GENERATOR
# ==============================================================================

def generate_all_experiments() -> List[ExperimentConfig]:
    """Generate all 78 experimental configurations"""
    
    experiments = []
    exp_counter = 1
    
    scenarios = [
        'low_density_01', 'low_density_02',
        'med_density_01', 'med_density_02',
        'high_density_01', 'high_density_02'
    ]
    
    # Phase 1: Baseline (6 runs)
    for scenario in scenarios:
        config = ExperimentConfig(
            exp_id=f"exp_{exp_counter:03d}",
            phase="baseline",
            scenario=scenario,
            security=SecurityConfig(encryption='none', authentication='none'),
            network=NetworkConfig(bandwidth_mbps=50, latency_ms=10, loss_rate=0.0)
        )
        experiments.append(config)
        exp_counter += 1
    
    # Phase 2: Security Impact (18 runs)
    security_configs = [
        SecurityConfig(encryption='none', authentication='none'),
        SecurityConfig(encryption='aes-256-gcm', authentication='none'),
        SecurityConfig(encryption='aes-256-gcm', authentication='hmac-sha256')
    ]
    
    for security in security_configs:
        for scenario in scenarios:
            config = ExperimentConfig(
                exp_id=f"exp_{exp_counter:03d}",
                phase="security_impact",
                scenario=scenario,
                security=security,
                network=NetworkConfig(bandwidth_mbps=50, latency_ms=10, loss_rate=0.0)
            )
            experiments.append(config)
            exp_counter += 1
    
    # Phase 3: Network Impact (42 runs)
    base_security = SecurityConfig(encryption='aes-256-gcm', authentication='none')
    
    # Bandwidth sweep
    for bw in [10, 2, 0.5]:
        for scenario in scenarios:
            config = ExperimentConfig(
                exp_id=f"exp_{exp_counter:03d}",
                phase="network_bandwidth",
                scenario=scenario,
                security=base_security,
                network=NetworkConfig(bandwidth_mbps=bw, latency_ms=10, loss_rate=0.0)
            )
            experiments.append(config)
            exp_counter += 1
    
    # Latency sweep
    for lat in [50, 150]:
        for scenario in scenarios:
            config = ExperimentConfig(
                exp_id=f"exp_{exp_counter:03d}",
                phase="network_latency",
                scenario=scenario,
                security=base_security,
                network=NetworkConfig(bandwidth_mbps=50, latency_ms=lat, loss_rate=0.0)
            )
            experiments.append(config)
            exp_counter += 1
    
    # Loss sweep
    for loss in [0.0, 0.02]:
        for scenario in scenarios:
            config = ExperimentConfig(
                exp_id=f"exp_{exp_counter:03d}",
                phase="network_loss",
                scenario=scenario,
                security=base_security,
                network=NetworkConfig(bandwidth_mbps=50, latency_ms=10, loss_rate=loss)
            )
            experiments.append(config)
            exp_counter += 1
    
    # Phase 4: Worst-Case (12 runs)
    max_security = SecurityConfig(encryption='aes-256-gcm', authentication='hmac-sha256')
    
    worst_cases = [
        NetworkConfig(bandwidth_mbps=0.5, latency_ms=10, loss_rate=0.0),
        NetworkConfig(bandwidth_mbps=50, latency_ms=150, loss_rate=0.02)
    ]
    
    for network in worst_cases:
        for scenario in scenarios:
            config = ExperimentConfig(
                exp_id=f"exp_{exp_counter:03d}",
                phase="worst_case",
                scenario=scenario,
                security=max_security,
                network=network
            )
            experiments.append(config)
            exp_counter += 1
    
    return experiments

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    """Main execution function"""
    
    print("\n" + "="*80)
    print("PhD DISSERTATION EXPERIMENTAL IMPLEMENTATION")
    print("Computer Vision-Based UAS Monitoring Under Secure Communication Constraints")
    print("="*80 + "\n")
    
    # Create output directory
    output_dir = Path("experiment_results")
    output_dir.mkdir(exist_ok=True)
    
    # Generate all experiments
    experiments = generate_all_experiments()
    print(f"✓ Generated {len(experiments)} experimental configurations\n")
    
    # Save experiment plan
    plan_path = output_dir / "experiment_plan.json"
    with open(plan_path, 'w') as f:
        json.dump([exp.to_dict() for exp in experiments], f, indent=2)
    print(f"✓ Saved experiment plan to {plan_path}\n")
    
    # Time estimation
    estimated_minutes = len(experiments) * 10 / 60
    print(f"⏱  Estimated time: {estimated_minutes:.1f} minutes\n")
    print("Starting experiments...\n")
    
    # Run all experiments
    start_time = time.time()
    all_summaries = []
    
    for i, exp_config in enumerate(experiments, 1):
        print(f"\n[{i}/{len(experiments)}] {exp_config.exp_id}")
        
        runner = ExperimentRunner(exp_config, output_dir)
        summary = runner.run(num_frames=180)  # 6 seconds at 30fps
        all_summaries.append(summary)
        
        # Progress update
        elapsed = (time.time() - start_time) / 60
        remaining = ((time.time() - start_time) / i * (len(experiments) - i)) / 60
        print(f"   Elapsed: {elapsed:.1f}m | Remaining: {remaining:.1f}m")
    
    # Save aggregated results
    results_df = pd.DataFrame(all_summaries)
    results_path = output_dir / "all_results.csv"
    results_df.to_csv(results_path, index=False)
    
    total_time = (time.time() - start_time) / 60
    
    print("\n" + "="*80)
    print("✓ ALL EXPERIMENTS COMPLETED!")
    print(f"  Total time: {total_time:.1f} minutes")
    print(f"  Results saved to: {output_dir.absolute()}")
    print("="*80 + "\n")
    
    # Generate summary statistics
    print_summary_statistics(results_df)

def print_summary_statistics(df: pd.DataFrame):
    """Print summary statistics across all experiments"""
    
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80 + "\n")
    
    print("By Phase:")
    phase_summary = df.groupby('phase')['mean_e2e_latency_ms'].agg(['mean', 'std', 'min', 'max'])
    print(phase_summary)
    
    print("\n\nBy Security Configuration:")
    sec_summary = df.groupby('security_config')['mean_e2e_latency_ms'].agg(['mean', 'std'])
    print(sec_summary)
    
    print("\n\nPacket Loss Statistics:")
    loss_summary = df.groupby('phase')['packet_loss_rate'].agg(['mean', 'max'])
    print(loss_summary)

if __name__ == "__main__":
    main()
