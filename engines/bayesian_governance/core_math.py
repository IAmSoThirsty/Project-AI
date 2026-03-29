# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / core_math.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / core_math.py

"""


               #
# COMPLIANCE: Sovereign Bayesian Governance / Project-AI                       #


"""

import math


class BayesianGovernanceMath:
    """
    Implements Real-Time Bayesian Signal Processing and
    Logarithmic Market Scoring Rule (LMSR) primitives.
    """

    @staticmethod
    def log_bayesian_update(
        prior_log_prob: float, likelihood_log_probs: list[float]
    ) -> float:
        """
        Calculates the log posterior probability given a stream of data points.
        Formula: log P(H|D) = log P(H) + sum(log P(D_k|H)) - log Z
        Note: Scaling/Normalization (log Z) should be handled across all hypotheses.
        """
        return prior_log_prob + sum(likelihood_log_probs)

    @staticmethod
    def lmsr_cost(quantities: list[float], b: float) -> float:
        """
        LMSR Cost Function: C(q) = b * ln(sum(e^(q_i/b)))
        Larger b => more liquidity, tighter spreads.
        """
        if b <= 0:
            raise ValueError("Liquidity parameter 'b' must be positive.")

        try:
            # Use max subtractions for numerical stability in exp
            max_q = max(quantities)
            sum_exp = sum(math.exp((q - max_q) / b) for q in quantities)
            return b * (max_q / b + math.log(sum_exp))
        except OverflowError:
            # Fallback for extreme values: cost is effectively infinite
            return float("inf")

    @staticmethod
    def lmsr_price(quantities: list[float], b: float, index: int) -> float:
        """
        LMSR Price Function (Softmax): p_i(q) = e^(q_i/b) / sum(e^(q_j/b))
        Identical to softmax function in neural network classifiers.
        """
        if b <= 0:
            raise ValueError("Liquidity parameter 'b' must be positive.")

        max_q = max(quantities)
        exps = [math.exp((q - max_q) / b) for q in quantities]
        sum_exps = sum(exps)
        return exps[index] / sum_exps

    @staticmethod
    def calculate_edge(true_prob: float, price: float) -> float:
        """
        Calculates the mispricing or trader edge: Edge = p_hat - p
        p_hat: true probability belief, p: current market price.
        """
        return true_prob - price

    @staticmethod
    def cost_of_trade(
        current_quantities: list[float], index: int, delta: float, b: float
    ) -> float:
        """
        Calculates the cost to move outcome i from quantity q_i to q_i + delta.
        Formula: Cost = C(q_1, ..., q_i + delta, ..., q_n) - C(q_1, ..., q_n)
        """
        new_quantities = list(current_quantities)
        new_quantities[index] += delta
        return BayesianGovernanceMath.lmsr_cost(
            new_quantities, b
        ) - BayesianGovernanceMath.lmsr_cost(current_quantities, b)


if __name__ == "__main__":
    # Internal Verification
    math_lib = BayesianGovernanceMath()
    q = [1.0, 1.0, 1.0]  # Equal quantities
    b_param = 100.0

    prices = [math_lib.lmsr_price(q, b_param, i) for i in range(len(q))]
    print(f"Initial Prices (Liquid Market): {prices}")
    assert abs(sum(prices) - 1.0) < 1e-9

    # Simulate a trade (adding quantity to outcome 0)
    cost = math_lib.cost_of_trade(q, 0, 10.0, b_param)
    print(f"Cost of adding 10 shares to outcome 0: {cost:.4f}")

    new_q = [11.0, 1.0, 1.0]
    new_prices = [math_lib.lmsr_price(new_q, b_param, i) for i in range(len(new_q))]
    print(f"New Prices after trade: {new_prices}")
