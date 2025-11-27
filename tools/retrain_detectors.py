"""CLI helper to retrain AI Persona detectors.

Usage:
    python tools/retrain_detectors.py [--async]

This script adds src/ to sys.path and imports AIPersona, then runs retraining using
examples found in data/ai_persona/training_examples/. By default it runs synchronously
so you can watch console output; pass --async to start background retraining and poll progress.
"""
import argparse
import os
import sys
import time

# Ensure src is on path so we can import the app package
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

try:
    from app.core.ai_persona import AIPersona
except Exception as e:
    print(f"Failed to import AIPersona: {e}")
    raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--async', dest='async_mode', action='store_true', help='Start retrain in background and poll progress')
    parser.add_argument('--data-dir', dest='data_dir', default=os.path.join(ROOT, 'data'), help='Path to data directory')
    args = parser.parse_args()

    persona = AIPersona(data_dir=args.data_dir)
    print('Starting retrain...')
    if args.async_mode:
        ok = persona.retrain_detectors_async()
        if not ok:
            print('Retrain already running.')
            return
        try:
            while True:
                prog = getattr(persona, 'retrain_progress', 0.0) or 0.0
                last = getattr(persona, 'ml_last_trained', None)
                print(f"Progress: {int(prog*100)}%", end='\r', flush=True)
                if prog >= 1.0 or last:
                    break
                time.sleep(1.0)
        except KeyboardInterrupt:
            print('\nInterrupted by user')
    else:
        ok = persona.retrain_detectors()
        if ok:
            print('Retrain finished successfully')
        else:
            print('Retrain did not run (no examples or error)')

    status = persona.get_detector_status()
    print('\nDetector status:')
    for k, v in status.items():
        print(f'  {k}: {v}')

    expl = persona.get_model_explainability('zeroth', top_n=20)
    if expl:
        print('\nTop explainability tokens (zeroth):')
        for t, w in expl:
            print(f'  {t}: {w:.4f}')


if __name__ == '__main__':
    main()
