from policy import decide_recovery_action


def run_test(name, **kwargs):
    decision = decide_recovery_action(**kwargs)

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    print(
        f"Recovery probability: "
        f"{decision.recovery_probability:.2%}"
    )

    print(
        f"Expected revenue: "
        f"₹{decision.expected_revenue:,.2f}"
    )

    print(
        f"Confidence: "
        f"{decision.confidence}"
    )

    print(
        f"Recommended action: "
        f"{decision.recommended_action}"
    )

    print("Reasons:")

    for reason in decision.reason:
        print(f"  • {reason}")


# --------------------------------------------------
# Test 1 — Strong transient failure
# --------------------------------------------------

run_test(
    "TEST 1 — Strong transient failure",
    recovery_probability=0.82,
    amount=5000,
    failure_category="transient",
    attempt_number=1,
    customer_failure_rate=0.08,
)


# --------------------------------------------------
# Test 2 — Insufficient funds
# --------------------------------------------------

run_test(
    "TEST 2 — Insufficient funds",
    recovery_probability=0.65,
    amount=3000,
    failure_category="insufficient_funds",
    attempt_number=1,
    customer_failure_rate=0.15,
)


# --------------------------------------------------
# Test 3 — Expired payment method
# --------------------------------------------------

run_test(
    "TEST 3 — Expired payment method",
    recovery_probability=0.72,
    amount=8000,
    failure_category="expired_payment_method",
    attempt_number=1,
    customer_failure_rate=0.10,
)


# --------------------------------------------------
# Test 4 — Merchant error
# --------------------------------------------------

run_test(
    "TEST 4 — Merchant error",
    recovery_probability=0.75,
    amount=10000,
    failure_category="merchant_error",
    attempt_number=1,
    customer_failure_rate=0.05,
)


# --------------------------------------------------
# Test 5 — Low probability
# --------------------------------------------------

run_test(
    "TEST 5 — Low recovery probability",
    recovery_probability=0.12,
    amount=2500,
    failure_category="transient",
    attempt_number=1,
    customer_failure_rate=0.40,
)


# --------------------------------------------------
# Test 6 — Repeated attempts
# --------------------------------------------------

run_test(
    "TEST 6 — Repeated failed attempts",
    recovery_probability=0.55,
    amount=15000,
    failure_category="transient",
    attempt_number=3,
    customer_failure_rate=0.35,
)