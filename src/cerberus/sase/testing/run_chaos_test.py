"""
SASE 10k Chaos Test Runner

Comprehensive validation against synthetic adversarial events.
"""

import logging
import time
from typing import Any

from ..sase_orchestrator import SASEOrchestrator
from ..testing.chaos_suite import ChaosValidator, EventGenerator, SyntheticEvent

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)

logger = logging.getLogger("SASE.ChaosTest")


def run_chaos_test() -> dict[str, Any]:
    """
    Run 10k synthetic event chaos test

    Validates SASE against ground truth with:
    - 500 credential harvesting attacks
    - 1000 API enumeration attacks
    - 8000 benign users
    - 500 VPN edge cases

    God-tier criteria:
    - Accuracy > 99.5%
    - False positive rate < 0.5%
    - Recall > 95%
    """
    logger.critical("=" * 60)
    logger.critical("STARTING SASE 10K CHAOS VALIDATION")
    logger.critical("=" * 60)

    # Initialize SASE
    sase = SASEOrchestrator()

    # Generate 10k synthetic events
    logger.info("Generating 10,000 synthetic events...")
    generator = EventGenerator(seed=42)
    events = generator.generate_10k_mix()
    logger.info(f"Generated {len(events)} events")

    # Validate against ground truth
    validator = ChaosValidator(containment_threshold=0.50)

    start_time = time.time()
    processed_count = 0

    logger.info("Processing events through SASE pipeline...")

    for i, event in enumerate(events):
        # Convert synthetic event to SASE telemetry format
        telemetry = _synthetic_to_telemetry(event)

        # Process through SASE
        result = sase.process_telemetry(telemetry)

        if result.get("success"):
            sase_confidence = result["confidence"]["confidence_percentage"] / 100.0
            validator.validate_result(event, sase_confidence)
            processed_count += 1

        # Progress logging
        if (i + 1) % 1000 == 0:
            logger.info(f"Processed {i + 1}/{len(events)} events...")

    elapsed_time = time.time() - start_time

    logger.critical("=" * 60)
    logger.critical("CHAOS TEST COMPLETE")
    logger.critical("=" * 60)

    # Calculate metrics
    metrics = validator.get_metrics()
    passes_god_tier = validator.passes_god_tier()

    logger.critical(f"Events Processed: {processed_count}/{len(events)}")
    logger.critical(f"Elapsed Time: {elapsed_time:.2f}s")
    logger.critical(f"Throughput: {processed_count / elapsed_time:.2f} events/sec")
    logger.critical("")
    logger.critical("VALIDATION METRICS:")
    logger.critical(f"  Accuracy:             {metrics['accuracy'] * 100:.2f}%")
    logger.critical(f"  Precision:            {metrics['precision'] * 100:.2f}%")
    logger.critical(f"  Recall:               {metrics['recall'] * 100:.2f}%")
    logger.critical(f"  F1 Score:             {metrics['f1_score']:.4f}")
    logger.critical(
        f"  False Positive Rate:  {metrics['false_positive_rate'] * 100:.3f}%"
    )
    logger.critical("")
    logger.critical("CONFUSION MATRIX:")
    logger.critical(f"  True Positives:       {metrics['true_positives']}")
    logger.critical(f"  True Negatives:       {metrics['true_negatives']}")
    logger.critical(f"  False Positives:      {metrics['false_positives']}")
    logger.critical(f"  False Negatives:      {metrics['false_negatives']}")
    logger.critical("")

    if passes_god_tier:
        logger.critical("✅ GOD-TIER CRITERIA MET!")
        logger.critical("   - Accuracy > 99.5%")
        logger.critical("   - FPR < 0.5%")
        logger.critical("   - Recall > 95%")
    else:
        logger.critical("❌ GOD-TIER CRITERIA NOT MET")
        if metrics["accuracy"] < 0.995:
            logger.critical(f"   - Accuracy {metrics['accuracy']*100:.2f}% < 99.5%")
        if metrics["false_positive_rate"] > 0.005:
            logger.critical(
                f"   - FPR {metrics['false_positive_rate']*100:.3f}% > 0.5%"
            )
        if metrics["recall"] < 0.95:
            logger.critical(f"   - Recall {metrics['recall']*100:.2f}% < 95%")

    logger.critical("=" * 60)

    return {
        "metrics": metrics,
        "passes_god_tier": passes_god_tier,
        "elapsed_time": elapsed_time,
        "throughput": processed_count / elapsed_time,
    }


def _synthetic_to_telemetry(event: SyntheticEvent) -> dict[str, Any]:
    """Convert synthetic event to SASE telemetry format"""
    return {
        "artifact_type": event.event_type,
        "source_ip": event.source_ip,
        "timestamp": time.time(),
        "payload": {
            "asn": event.asn,
            "country": event.country,
            "tor_flag": event.is_tor,
            "vpn_flag": event.is_vpn,
            "token_reuse": event.token_reuse,
        },
        "model_version": "1.0.0",
    }


if __name__ == "__main__":
    results = run_chaos_test()

    if results["passes_god_tier"]:
        print("\n✅ SASE is production-ready!")
    else:
        print("\n⚠️  SASE needs further tuning before production deployment")
