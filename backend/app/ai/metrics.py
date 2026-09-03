import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MetricsEvaluator:
    def __init__(self):
        self.ground_truth = []
        self.predictions = []
        
    def add_ground_truth(self, event_type: str, camera_id: str, timestamp: datetime):
        """Add a verified real-world event for evaluation."""
        self.ground_truth.append({
            "type": event_type,
            "camera_id": camera_id,
            "timestamp": timestamp
        })
        
    def add_prediction(self, event_type: str, camera_id: str, timestamp: datetime):
        """Add a model prediction (CONFIRMED state from TemporalEngine)."""
        self.predictions.append({
            "type": event_type,
            "camera_id": camera_id,
            "timestamp": timestamp
        })
        
    def evaluate(self, time_tolerance_seconds: float = 60.0) -> Dict[str, float]:
        """
        Calculates Precision, Recall, and F1.
        A prediction is a True Positive if there is a Ground Truth event of the 
        same type and camera within the time_tolerance_seconds.
        """
        tp = 0
        fp = 0
        fn = 0
        
        # Match predictions to ground truth
        matched_gt_indices = set()
        total_latency = 0.0
        
        for pred in self.predictions:
            matched = False
            for i, gt in enumerate(self.ground_truth):
                if i in matched_gt_indices:
                    continue
                    
                if gt["type"] == pred["type"] and gt["camera_id"] == pred["camera_id"]:
                    dt = abs((pred["timestamp"] - gt["timestamp"]).total_seconds())
                    if dt <= time_tolerance_seconds:
                        # Match found
                        tp += 1
                        matched = True
                        matched_gt_indices.add(i)
                        total_latency += (pred["timestamp"] - gt["timestamp"]).total_seconds()
                        break
                        
            if not matched:
                fp += 1
                
        fn = len(self.ground_truth) - len(matched_gt_indices)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        avg_latency = total_latency / tp if tp > 0 else 0.0
        
        results = {
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "avg_detection_latency_sec": round(avg_latency, 2)
        }
        
        logger.info(f"Temporal Engine Metrics Evaluation: {results}")
        return results
