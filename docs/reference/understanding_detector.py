#!/usr/bin/env python3
"""
UNDERSTANDING DETECTOR v1.0
Intervention-Consistency Probe on a Known Structural Causal Model

PURPOSE
-------
This is an INSTRUMENT, not a demonstration. It is built to be able to FAIL.

The question it operationalizes (the one Project-AI keeps circling):
    Can we distinguish a system whose internal state is causally entangled
    with a domain's structure from one that reproduces correct outputs by
    re-weighting surface correlations?

The test must satisfy three honesty conditions, or it is a mirror:
    (H1) Ground truth is known    -> we author the SCM, so we hold the key.
    (H2) The detector is blind    -> it scores models A and B without being
                                      told which is causal and which is not.
    (H3) The detector can be wrong -> if it cannot separate the two models,
                                      THAT is reported as a real result, not
                                      hidden.

METHOD
------
1. Define a known structural causal model (SCM). We wrote the graph, so the
   interventional and counterfactual ground truth is computable exactly.

2. Generate OBSERVATIONAL data only (no interventions). Both candidate models
   train on this. This is the "surviving distribution" -- the traces.

3. Build two candidate predictors of a target variable:
     - MODEL_CORR : a flexible regressor over observed features. It can fit
                    the observational distribution arbitrarily well. It has
                    no access to causal structure -- only correlations.
     - MODEL_CAUS : a predictor that respects the causal parent set of the
                    target (it is given the structure, not the answers).
   Both are trained ONLY on observational data. On-distribution, they should
   be nearly indistinguishable -- that is the entire problem.

4. PROBE with interventions do(X=x) and off-distribution counterfactuals that
   the observational data never contained. Compute each model's predictions
   and compare to the SCM's true interventional outcomes.

5. The detector scores each model by INTERVENTION CONSISTENCY: how well its
   response to do() tracks the true causal graph versus what correlation alone
   would predict. It is handed the two models in randomized, anonymized order.

6. Report verdict + the gap. If the gap is below a separation floor, the
   detector DECLARES ITSELF UNABLE TO DISCRIMINATE. That is a pass for honesty
   and a fail for the instrument -- and it is printed plainly.

Nothing here proves "understanding" in the strong sense. It tests one
necessary signature of it: causal-intervention consistency. A system can pass
this and still be a mimic on richer structure. A system cannot be said to
understand the domain if it FAILS this. That asymmetry is the point.
"""

import numpy as np
from dataclasses import dataclass
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression

RNG = np.random.default_rng(20260605)


# ----------------------------------------------------------------------------
# 1. THE KNOWN STRUCTURAL CAUSAL MODEL
# ----------------------------------------------------------------------------
# Graph (all linear-Gaussian with a nonlinear twist on the target):
#
#     U  (exogenous confounder, UNOBSERVED by the models)
#    / \
#   Z   X        Z is a confounder of X and Y. X causes M. M causes Y.
#   |   |        CRITICAL TRAP: Z drives both X and Y, so observationally
#   |   X -> M   X and Y are strongly correlated even though intervening on
#   |        \   X only affects Y through M. A correlational model will
#   +-> Y <-- M  overstate the effect of do(X) because it absorbs the Z path.
#         ^
#         U (also nudges Y)
#
# True parents of Y: {Z, M, U}. X affects Y ONLY via M.
# do(X=x) breaks the Z->X dependence; the confounded correlation must vanish.

def sample_scm(n, do_X=None, rng=RNG):
    """Sample from the SCM. If do_X is not None, intervene: set X := do_X,
    severing its dependence on Z (the defining move of an intervention)."""
    U = rng.normal(0, 1, n)            # unobserved exogenous
    Z = rng.normal(0, 1, n)            # observed confounder
    if do_X is None:
        X = 0.9 * Z + rng.normal(0, 0.5, n)      # X depends on Z (confounded)
    else:
        X = np.full(n, float(do_X))               # do(X=x): cut the Z -> X arrow
    M = 1.3 * X + rng.normal(0, 0.4, n)           # mediator
    # Target: nonlinear in its TRUE parents Z, M, U
    Y = 0.8 * Z + 1.1 * M - 0.3 * (M ** 2) * 0.1 + 0.6 * U + rng.normal(0, 0.3, n)
    return {"U": U, "Z": Z, "X": X, "M": M, "Y": Y}


def true_interventional_mean_Y(do_X, n=200_000):
    """Ground-truth E[Y | do(X=x)], computed by simulating the intervention.
    This is the answer key. Models never see this."""
    d = sample_scm(n, do_X=do_X)
    return float(np.mean(d["Y"]))


# ----------------------------------------------------------------------------
# 2/3. CANDIDATE MODELS  (trained on OBSERVATIONAL data only)
# ----------------------------------------------------------------------------
@dataclass
class Candidate:
    name: str          # secret true identity, hidden from the detector
    predict: object    # callable: dict-of-arrays -> array of Y predictions


def build_candidates(train):
    """Both models observe {Z, X, M} (NOT U, which is hidden) and target Y.
    They differ only in what they are allowed to use at prediction time."""

    # ---- MODEL_CORR: flexible fit over all observed features. ----
    # It will happily use X directly because X is correlated with Y through
    # the confounder Z. It has high observational accuracy and no causal model.
    Xc = np.column_stack([train["Z"], train["X"], train["M"]])
    corr = GradientBoostingRegressor(random_state=0, n_estimators=300, max_depth=3)
    corr.fit(Xc, train["Y"])

    def predict_corr(d):
        return corr.predict(np.column_stack([d["Z"], d["X"], d["M"]]))

    # ---- MODEL_CAUS: respects the causal parent set of Y among observables. ----
    # True parents of Y are {Z, M, U}; U is unobserved, so the causal-correct
    # observable predictor uses {Z, M} and DOES NOT read X directly, because
    # X is not a direct cause of Y. This is the structural knowledge -- it is
    # given the graph, not the interventional answers.
    Xq = np.column_stack([train["Z"], train["M"], train["M"] ** 2])
    caus = LinearRegression().fit(Xq, train["Y"])

    def predict_caus(d):
        return caus.predict(np.column_stack([d["Z"], d["M"], d["M"] ** 2]))

    return [Candidate("MODEL_CORR", predict_corr),
            Candidate("MODEL_CAUS", predict_caus)]


# ----------------------------------------------------------------------------
# 4/5. THE DETECTOR  (blind: receives anonymized models, no labels)
# ----------------------------------------------------------------------------
SEPARATION_FLOOR = 0.15   # min normalized score gap to claim discrimination

def detector(anon_models, do_grid=(-2.0, -1.0, 0.0, 1.0, 2.0), n_probe=20_000):
    """
    For each do(X=x):
      - true_Y          = E[Y | do(X=x)]  (answer key, from the SCM)
      - For a model to be intervention-consistent, when we feed it data drawn
        UNDER the intervention, its predictions must match the true
        interventional mean. A correlational model, fed interventional inputs,
        mispredicts because it learned the confounded X->Y association that no
        longer holds once do() cuts the Z->X arrow.
    Score = mean absolute intervention error. Lower = more causally consistent.
    The detector never sees model names; it only sees error behavior.
    """
    results = {i: [] for i in range(len(anon_models))}
    truths = {}
    for x in do_grid:
        truth = true_interventional_mean_Y(x)
        truths[x] = truth
        probe = sample_scm(n_probe, do_X=x)   # data UNDER the intervention
        for i, m in enumerate(anon_models):
            pred_mean = float(np.mean(m.predict(probe)))
            results[i].append(abs(pred_mean - truth))

    mae = {i: float(np.mean(errs)) for i, errs in results.items()}
    # normalize gap by the spread of true interventional means
    scale = np.std([truths[x] for x in do_grid]) + 1e-9
    best, worst = min(mae, key=mae.get), max(mae, key=mae.get)
    gap = (mae[worst] - mae[best]) / scale

    return mae, truths, results, best, worst, gap


# ----------------------------------------------------------------------------
# RUN
# ----------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("UNDERSTANDING DETECTOR v1.0  --  intervention-consistency probe")
    print("=" * 70)

    train = sample_scm(40_000)               # OBSERVATIONAL data only
    candidates = build_candidates(train)

    # On-distribution sanity: both must fit observational Y well, or the test
    # is unfair (we'd be catching a bad fit, not a missing causal model).
    test_obs = sample_scm(20_000)
    for c in candidates:
        pred = c.predict(test_obs)
        r2 = 1 - np.var(test_obs["Y"] - pred) / np.var(test_obs["Y"])
        print(f"[setup] {c.name:11s} observational R^2 = {r2:0.3f}")
    print("        (both fit the surviving distribution -- that is the trap)\n")

    # Blind the detector: shuffle and strip names.
    order = list(range(len(candidates)))
    RNG.shuffle(order)
    anon = [candidates[i] for i in order]

    mae, truths, errs, best, worst, gap = detector(anon)

    print("True interventional means  E[Y | do(X=x)] (the answer key):")
    for x, t in truths.items():
        print(f"    do(X={x:+.1f}) -> {t:+.3f}")
    print()
    print("Blind intervention error per anonymized model (lower = causal):")
    for i in range(len(anon)):
        print(f"    model#{i}  MAE={mae[i]:0.3f}   per-do={[round(e,3) for e in errs[i]]}")
    print()
    print(f"Normalized separation gap = {gap:0.3f}  (floor = {SEPARATION_FLOOR})")
    print("-" * 70)

    if gap < SEPARATION_FLOOR:
        print("VERDICT: DETECTOR CANNOT DISCRIMINATE.")
        print("The instrument failed to separate the models. This is reported,")
        print("not hidden. Either the probe is too weak or the models are")
        print("behaviorally identical under intervention. The detector is a")
        print("mirror here -- redesign before trusting it.")
        verdict_id = None
    else:
        flagged = anon[worst].name      # unmask ONLY after the verdict
        cleared = anon[best].name
        print(f"VERDICT: model#{worst} FLAGGED as correlational mimic.")
        print(f"         model#{best} CLEARED as intervention-consistent.")
        print()
        print("Unmasking (revealed only post-verdict, to check the instrument):")
        print(f"         FLAGGED model#{worst} was actually: {flagged}")
        print(f"         CLEARED model#{best} was actually: {cleared}")
        print()
        if flagged == "MODEL_CORR" and cleared == "MODEL_CAUS":
            print(">>> INSTRUMENT CORRECT: it caught the mimic blind, using only")
            print(">>> intervention behavior. It never read the labels or the graph.")
        else:
            print(">>> INSTRUMENT WRONG: it flagged the causal model. The detector")
            print(">>> itself is broken or biased. This is the failure mode that")
            print(">>> matters most -- a detector you would have trusted, that lies.")

    print("=" * 70)
    print("Scope note: this tests ONE necessary signature (causal-intervention")
    print("consistency) on a toy SCM you control. Passing is not 'understanding.'")
    print("FAILING is disqualifying. That asymmetry is the only honest claim.")
    print("=" * 70)


if __name__ == "__main__":
    main()
