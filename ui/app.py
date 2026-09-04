from pathlib import Path
import sys
from textwrap import dedent

import pandas as pd
import plotly.express as px
import streamlit as st

from demo.investor_demo import run_investor_demo


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
UI_DIR = ROOT_DIR / "ui"

for path in [ROOT_DIR, SRC_DIR, UI_DIR]:

    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


# ============================================================
# UI IMPORTS
# ============================================================

from data import (
    load_predictions,
    calculate_metrics,
    action_distribution,
    failure_distribution,
    recent_events,
)

from theme import (
    configure_page,
    apply_theme,
    render_brand,
)


# ============================================================
# PAGE SETUP
# ============================================================

configure_page()
apply_theme()


# ============================================================
# LOAD DATA
# ============================================================

df = load_predictions()

metrics = calculate_metrics(df)
actions = action_distribution(df)
failures = failure_distribution(df)
recent = recent_events(df)


# ============================================================
# HELPERS
# ============================================================

def money(value):

    try:
        return f"₹{float(value):,.0f}"

    except Exception:
        return "₹0"


def pct(value):

    try:
        return f"{float(value) * 100:.1f}%"

    except Exception:
        return "0.0%"


def section(title, note=None):

    note_html = ""

    if note:

        note_html = f"""
        <div class="section-note">
            {note}
        </div>
        """

    st.html(
        dedent(
            f"""
            <div class="section-header">

                <div class="section-title">
                    {title}
                </div>

                {note_html}

            </div>
            """
        ),
    )


def metric_card(
    label,
    value,
    detail="",
    variant="",
):

    st.html(
        dedent(
            f"""
            <div class="metric {variant}">

                <div class="metric-label">
                    {label}
                </div>

                <div class="metric-value">
                    {value}
                </div>

                <div class="metric-detail">
                    {detail}
                </div>

            </div>
            """
        ),
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    render_brand()

    st.html(
        '<div class="sidebar-section">Operations</div>',
    )

    page = st.radio(
        "Navigation",
        [
            "Overview",
            "Investor Demo",
            "Recovery Operations",
            "Payment Events",
            "AI Agent",
            "MLOps",
        ],
        label_visibility="collapsed",
    )

    st.html(
        '<div class="sidebar-section">Environment</div>',
    )

    st.html(
        dedent(
            """
            <div class="sidebar-env">
                <div class="sidebar-env-label">Gateway</div>
                <div class="sidebar-env-name">● Razorpay Test Mode</div>
                <div class="sidebar-env-detail">Connected · Test environment</div>
            </div>
            """
        ),
    )

    st.html("<br>")

    if st.button(
        "Refresh data",
        use_container_width=True,
    ):

        st.cache_data.clear()
        st.rerun()


# ============================================================
# HEADER
# ============================================================

header_left, header_right = st.columns(
    [7, 2]
)

with header_left:

    st.html(
        dedent(
            """
            <div class="page-kicker">
                REVENUE OPERATIONS · COMMAND CENTER
            </div>

            <div class="page-title">
                Payment recovery, driven by decisions
            </div>

            <div class="page-description">
                Detect revenue at risk → choose the right intervention → measure what was recovered.
            </div>
            """
        ),
    )


with header_right:

    st.html(
        dedent(
            """
            <div class="environment-label">

                <div class="environment-name">
                    <span class="environment-dot"></span>
                    Razorpay Test Mode
                </div>

                <div class="environment-detail">
                    Gateway connected
                </div>

            </div>
            """
        ),
    )


# ============================================================
# OVERVIEW
# ============================================================

if page == "Overview":

    section(
        "Recovery performance",
        "Current prediction and outcome log",
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:

        metric_card(
            "FAILED PAYMENTS",
            f"{metrics['failed_payments']:,}",
            "Payment failures observed",
        )

    with c2:

        metric_card(
            "INTERVENTIONS",
            f"{metrics['interventions']:,}",
            f"{pct(metrics['intervention_rate'])} of failures",
            "metric-accent",
        )

    with c3:

        metric_card(
            "RECOVERED",
            f"{metrics['recovered_transactions']:,}",
            f"{pct(metrics['recovery_rate'])} overall",
            "metric-success",
        )

    with c4:

        metric_card(
            "EXPECTED REVENUE",
            money(metrics["expected_revenue"]),
            "Model-estimated recovery",
            "metric-warning",
        )

    with c5:

        metric_card(
            "RECOVERED REVENUE",
            money(metrics["recovered_revenue"]),
            "Observed recovered value",
            "metric-success",
        )


    # --------------------------------------------------------
    # ANALYSIS
    # --------------------------------------------------------

    section(
        "Recovery analysis",
        "Where the agent is directing recovery effort",
    )

    left, right = st.columns(
        [1.25, 1]
    )

    with left:

        if not actions.empty:

            chart_df = actions.copy()

            fig = px.bar(
                chart_df,
                x="recommended_action",
                y="count",
                text="count",
            )

            fig.update_traces(
                marker_color="#2F5BEA",
                textposition="outside",
                textfont=dict(color="#172033", size=11),
            )

            fig.update_layout(
                template="plotly_white",
                height=300,
                margin=dict(
                    l=20,
                    r=20,
                    t=25,
                    b=20,
                ),
                paper_bgcolor="white",
                plot_bgcolor="white",
                font=dict(
                    family="Segoe UI",
                    color="#172033",
                    size=11,
                ),
                xaxis_title=None,
                yaxis_title=None,
                xaxis=dict(
                    tickfont=dict(color="#172033", size=10),
                    showgrid=False,
                    zeroline=False,
                    linecolor="#E4E7EC",
                ),
                yaxis=dict(
                    tickfont=dict(color="#667085", size=10),
                    showgrid=True,
                    gridcolor="#EEF0F3",
                    zeroline=False,
                ),
                showlegend=False,
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    "displayModeBar": False
                },
            )


    with right:

        if not failures.empty:

            fig = px.pie(
                failures,
                names="failure_category",
                values="count",
                hole=0.62,
            )

            fig.update_traces(
                textfont=dict(color="#172033", size=11),
                textposition="inside",
                hovertemplate="%{label}: %{percent}<extra></extra>",
            )

            fig.update_layout(
                template="plotly_white",
                height=300,
                margin=dict(
                    l=20,
                    r=20,
                    t=25,
                    b=20,
                ),
                paper_bgcolor="white",
                font=dict(
                    family="Segoe UI",
                    color="#172033",
                    size=11,
                ),
                legend=dict(
                    font=dict(color="#172033", size=10),
                ),
                showlegend=True,
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    "displayModeBar": False
                },
            )


    # --------------------------------------------------------
    # RECENT ACTIVITY
    # --------------------------------------------------------

    section(
        "Recent activity",
        "Latest recovery decisions",
    )

    if recent.empty:

        st.info(
            "No prediction events have been logged yet."
        )

    else:

        display = recent.copy()

        preferred_columns = [
            "timestamp",
            "amount",
            "failure_category",
            "recovery_probability",
            "recommended_action",
            "confidence",
            "outcome_status",
        ]

        columns = [
            c
            for c in preferred_columns
            if c in display.columns
        ]

        display = display[columns]

        if "amount" in display.columns:

            display["amount"] = (
                display["amount"]
                .apply(money)
            )

        if "recovery_probability" in display.columns:

            display["recovery_probability"] = (
                display["recovery_probability"]
                * 100
            ).round(1).astype(str) + "%"

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# INVESTOR DEMO
# ============================================================

elif page == "Investor Demo":

    st.html(dedent("""
        <div class="demo-hero">
            <div class="demo-kicker">RECLAIM · DECISION ENGINE</div>
            <div class="demo-title">
                Recovery isn't the hard part.<br>
                Knowing when <em>not</em> to recover is.
            </div>
            <div class="demo-description">
                A controlled three-payment walkthrough of the real RECLAIM inference and
                decision path: diagnose the failure, estimate recovery probability,
                calculate expected revenue, choose a bounded action, and observe the outcome.
            </div>
        </div>
    """))

    st.html(dedent("""
        <div class="demo-explanation">
            <div class="demo-explanation-item">
                <div class="demo-explanation-number">01 · DETECT</div>
                <div class="demo-explanation-title">Payment fails</div>
                <div class="demo-explanation-text">Gateway event enters the recovery workflow.</div>
            </div>
            <div class="demo-explanation-item">
                <div class="demo-explanation-number">02 · PREDICT</div>
                <div class="demo-explanation-title">AI scores recovery</div>
                <div class="demo-explanation-text">ML estimates the probability of successful recovery.</div>
            </div>
            <div class="demo-explanation-item">
                <div class="demo-explanation-number">03 · VALUE</div>
                <div class="demo-explanation-title">Revenue is estimated</div>
                <div class="demo-explanation-text">Probability × payment value gives expected revenue.</div>
            </div>
            <div class="demo-explanation-item">
                <div class="demo-explanation-number">04 · DECIDE</div>
                <div class="demo-explanation-title">Policy selects action</div>
                <div class="demo-explanation-text">Recovery is bounded by failure type and stopping rules.</div>
            </div>
            <div class="demo-explanation-item">
                <div class="demo-explanation-number">05 · LEARN</div>
                <div class="demo-explanation-title">Outcome closes loop</div>
                <div class="demo-explanation-text">Recovered value becomes measurable feedback.</div>
            </div>
        </div>
    """))

    run_demo = st.button(
        "▶  Run RECLAIM Investor Demo",
        type="primary",
        use_container_width=True,
    )

    if run_demo:
        st.session_state["reclaim_demo"] = run_investor_demo()

    if "reclaim_demo" not in st.session_state:
        st.html(dedent("""
            <div class="demo-start-card">
                <div class="demo-start-left">
                    <div class="demo-start-icon">▶</div>
                    <div>
                        <div class="demo-start-title">Three decisions. One revenue story.</div>
                        <div class="demo-start-text">
                            Run the controlled scenarios to see the actual model prediction,
                            policy decision and bounded recovery execution.
                        </div>
                    </div>
                </div>
                <div class="badge badge-blue">READY</div>
            </div>
        """))
    else:
        demo = st.session_state["reclaim_demo"]
        summary = demo.get("summary", {})
        results = demo.get("results", [])

        st.html(dedent(f"""
            <div class="demo-status">
                <div class="demo-status-left">
                    <span class="demo-status-dot"></span>
                    <span class="demo-status-text">MODEL EXECUTED · DECISIONS COMPLETE</span>
                </div>
                <div class="demo-status-meta">Logistic Regression · v1 · threshold 0.35</div>
            </div>
        """))

        for idx, result in enumerate(results, start=1):
            action = str(result.get("recommended_action", "NO_ACTION"))
            outcome = str(result.get("outcome_status", "NOT_RECOVERED"))
            recovered = float(result.get("recovered_amount", 0) or 0)
            probability = float(result.get("recovery_probability", 0) or 0)
            expected = float(result.get("expected_revenue", 0) or 0)
            amount = float(result.get("amount", 0) or 0)
            failure = str(result.get("failure_category", "unknown"))
            failure_code = str(result.get("failure_code", ""))
            reason = str(result.get("reason", ""))
            confidence = str(result.get("confidence", ""))
            scenario = str(result.get("scenario", f"Scenario {idx}"))
            card_class = "no-action" if action == "NO_ACTION" else "recovered"
            action_class = "no-action" if action == "NO_ACTION" else ""
            outcome_label = "RECOVERED" if outcome == "RECOVERED" else "NOT RECOVERED"
            outcome_badge = "badge-green" if outcome == "RECOVERED" else "badge-amber"

            st.html(dedent(f"""
                <div class="demo-scenario {card_class}">
                    <div class="demo-scenario-top">
                        <div>
                            <div class="demo-scenario-number">SCENARIO {idx:02d}</div>
                            <div class="demo-scenario-title">{scenario}</div>
                            <div class="demo-scenario-failure">{failure} · {failure_code}</div>
                        </div>
                        <div>
                            <div class="demo-amount">₹{amount:,.0f}</div>
                            <div style="text-align:right;margin-top:5px;">
                                <span class="badge {outcome_badge}">{outcome_label}</span>
                            </div>
                        </div>
                    </div>

                    <div class="demo-decision-grid">
                        <div class="demo-decision-cell">
                            <div class="demo-cell-label">Recovery probability</div>
                            <div class="demo-cell-value">{probability*100:.0f}%</div>
                        </div>
                        <div class="demo-decision-cell">
                            <div class="demo-cell-label">Expected revenue</div>
                            <div class="demo-cell-value">₹{expected:,.0f}</div>
                        </div>
                        <div class="demo-decision-cell">
                            <div class="demo-cell-label">Decision</div>
                            <div class="demo-cell-value demo-action {action_class}">{action}</div>
                        </div>
                        <div class="demo-decision-cell">
                            <div class="demo-cell-label">Confidence</div>
                            <div class="demo-cell-value">{confidence}</div>
                        </div>
                        <div class="demo-decision-cell">
                            <div class="demo-cell-label">Revenue recovered</div>
                            <div class="demo-cell-value">₹{recovered:,.0f}</div>
                        </div>
                    </div>

                    <div class="demo-reason"><strong>Why:</strong> {reason}</div>
                    {f'<div class="demo-recovered">✓ Synthetic outcome: ₹{recovered:,.2f} recovered after the selected action.</div>' if outcome == "RECOVERED" else ''}
                </div>
            """))

        no_action = next((r for r in results if r.get("recommended_action") == "NO_ACTION"), None)
        if no_action:
            st.html(dedent(f"""
                <div class="killer-card">
                    <div class="killer-label">THE IMPORTANT DECISION</div>
                    <div class="killer-title">RECLAIM chose NOT to intervene.</div>
                    <div class="killer-text">
                        The payment is valuable, but the failure is merchant-side. A retry or
                        customer intervention is unlikely to solve the underlying problem.
                        RECLAIM therefore stops the recovery loop instead of blindly spending effort.
                    </div>
                    <div class="killer-reason">{no_action.get("reason", "Merchant-side failure → intervention stopped")}</div>
                    <div class="killer-line">
                        Knowing when <strong>NOT</strong> to intervene is part of revenue optimization.
                    </div>
                </div>
            """))

        total_value = float(summary.get("total_payment_value", 0) or 0)
        expected_revenue = float(summary.get("expected_revenue", 0) or 0)
        recovered_revenue = float(summary.get("recovered_revenue", 0) or 0)
        recovery_rate = float(summary.get("recovery_rate", 0) or 0)

        st.html(dedent(f"""
            <div class="revenue-impact">
                <div class="revenue-impact-title">Revenue impact · closed-loop result</div>
                <div class="revenue-grid">
                    <div class="revenue-cell">
                        <div class="revenue-label">Payment value analyzed</div>
                        <div class="revenue-value">₹{total_value:,.0f}</div>
                    </div>
                    <div class="revenue-cell">
                        <div class="revenue-label">Expected recovery</div>
                        <div class="revenue-value">₹{expected_revenue:,.0f}</div>
                    </div>
                    <div class="revenue-cell">
                        <div class="revenue-label">Recovered revenue</div>
                        <div class="revenue-value">₹{recovered_revenue:,.0f}</div>
                    </div>
                    <div class="revenue-cell">
                        <div class="revenue-label">Recovery rate</div>
                        <div class="revenue-value">{recovery_rate*100:.1f}%</div>
                    </div>
                </div>
            </div>
        """))

        ledger = pd.DataFrame(results)
        if not ledger.empty:
            ledger = ledger[[
                c for c in [
                    "scenario", "amount", "recovery_probability",
                    "expected_revenue", "recommended_action",
                    "outcome_status", "recovered_amount"
                ] if c in ledger.columns
            ]].copy()
            rename = {
                "scenario":"Scenario", "amount":"Amount", "recovery_probability":"Recovery probability",
                "expected_revenue":"Expected revenue", "recommended_action":"Decision",
                "outcome_status":"Outcome", "recovered_amount":"Recovered"
            }
            ledger = ledger.rename(columns=rename)
            if "Amount" in ledger: ledger["Amount"] = ledger["Amount"].map(lambda x: f"₹{float(x):,.0f}")
            if "Expected revenue" in ledger: ledger["Expected revenue"] = ledger["Expected revenue"].map(lambda x: f"₹{float(x):,.0f}")
            if "Recovered" in ledger: ledger["Recovered"] = ledger["Recovered"].map(lambda x: f"₹{float(x):,.0f}")
            if "Recovery probability" in ledger: ledger["Recovery probability"] = ledger["Recovery probability"].map(lambda x: f"{float(x)*100:.0f}%")
            st.dataframe(ledger, use_container_width=True, hide_index=True)

        st.html("""
            <div class="demo-disclosure">
                <strong>Demo disclosure:</strong> the three payment events and their final outcomes
                are controlled synthetic scenarios. The recovery prediction and policy decision
                are executed by the RECLAIM system; production outcomes would be supplied by
                Razorpay payment/webhook events. Recovery actions are represented through the
                bounded action layer in this demo.
            </div>
        """)


# ============================================================
# RECOVERY OPERATIONS
# ============================================================

elif page == "Recovery Operations":

    section(
        "Recovery Operations",
        "Interventions selected by the recovery policy",
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        metric_card(
            "PAYMENTS AT RISK",
            f"{metrics['failed_payments']:,}",
            "Failed payment events",
        )

    with c2:

        metric_card(
            "INTERVENTION RATE",
            pct(metrics["intervention_rate"]),
            "Failures receiving an action",
            "metric-accent",
        )

    with c3:

        metric_card(
            "INTERVENTION SUCCESS",
            pct(
                metrics.get(
                    "intervention_success_rate",
                    0,
                )
            ),
            "Interventions resulting in recovery",
            "metric-success",
        )

    with c4:

        metric_card(
            "REVENUE AT RISK",
            money(metrics["revenue_at_risk"]),
            "Value of failed payments",
            "metric-warning",
        )


    section(
        "Action distribution",
        "Current recovery policy output",
    )

    if not actions.empty:

        action_display = actions.copy()

        if "count" in action_display.columns:

            action_display["share"] = (
                action_display["count"]
                / action_display["count"].sum()
            )

        if "share" in action_display.columns:

            action_display["share"] = (
                action_display["share"]
                * 100
            ).round(1).astype(str) + "%"

        st.dataframe(
            action_display,
            use_container_width=True,
            hide_index=True,
        )


    section(
        "Recovery event ledger",
        "Prediction → decision → outcome",
    )

    if df.empty:

        st.info(
            "No recovery events available."
        )

    else:

        ledger = df.copy()

        preferred = [
            "timestamp",
            "amount",
            "failure_category",
            "attempt_number",
            "recovery_probability",
            "expected_revenue",
            "recommended_action",
            "confidence",
            "outcome_status",
            "recovered_amount",
        ]

        cols = [
            c
            for c in preferred
            if c in ledger.columns
        ]

        ledger = ledger[cols]

        for column in [
            "amount",
            "expected_revenue",
            "recovered_amount",
        ]:

            if column in ledger.columns:

                ledger[column] = (
                    ledger[column]
                    .apply(money)
                )

        if "recovery_probability" in ledger.columns:

            ledger["recovery_probability"] = (
                ledger["recovery_probability"]
                * 100
            ).round(1).astype(str) + "%"

        st.dataframe(
            ledger,
            use_container_width=True,
            hide_index=True,
            height=430,
        )


# ============================================================
# PAYMENT EVENTS
# ============================================================

elif page == "Payment Events":

    section(
        "Payment Events",
        "Failure-level transaction intelligence",
    )

    if df.empty:

        st.info(
            "No payment events have been logged."
        )

    else:

        f1, f2, f3 = st.columns(
            [1, 1, 2]
        )

        categories = ["All"]

        if "failure_category" in df.columns:

            categories += sorted(
                df["failure_category"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

        with f1:

            category_filter = st.selectbox(
                "Failure category",
                categories,
            )


        actions_list = ["All"]

        if "recommended_action" in df.columns:

            actions_list += sorted(
                df["recommended_action"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

        with f2:

            action_filter = st.selectbox(
                "Recovery action",
                actions_list,
            )


        with f3:

            search = st.text_input(
                "Search",
                placeholder=(
                    "Transaction, failure code, customer..."
                ),
            )


        filtered = df.copy()

        if (
            category_filter != "All"
            and "failure_category"
            in filtered.columns
        ):

            filtered = filtered[
                filtered["failure_category"]
                .astype(str)
                == category_filter
            ]


        if (
            action_filter != "All"
            and "recommended_action"
            in filtered.columns
        ):

            filtered = filtered[
                filtered["recommended_action"]
                .astype(str)
                == action_filter
            ]


        if search.strip():

            mask = pd.Series(
                False,
                index=filtered.index,
            )

            for column in [
                "transaction_id",
                "customer_id",
                "failure_category",
                "failure_code",
                "recommended_action",
            ]:

                if column in filtered.columns:

                    mask = mask | (
                        filtered[column]
                        .astype(str)
                        .str.contains(
                            search,
                            case=False,
                            na=False,
                        )
                    )

            filtered = filtered[mask]


        st.html(
            dedent(
                f"""
                <div style="
                    color:#667085;
                    font-size:11px;
                    margin:10px 0;
                ">
                    {len(filtered):,} events
                </div>
                """
            ),
        )


        event_columns = [
            "timestamp",
            "transaction_id",
            "customer_id",
            "amount",
            "payment_method",
            "failure_category",
            "failure_code",
            "attempt_number",
            "recovery_probability",
            "recommended_action",
            "confidence",
            "outcome_status",
        ]

        cols = [
            c
            for c in event_columns
            if c in filtered.columns
        ]

        event_table = filtered[cols].copy()

        if "amount" in event_table.columns:

            event_table["amount"] = (
                event_table["amount"]
                .apply(money)
            )

        if "recovery_probability" in event_table.columns:

            event_table[
                "recovery_probability"
            ] = (
                event_table[
                    "recovery_probability"
                ]
                * 100
            ).round(1).astype(str) + "%"

        st.dataframe(
            event_table,
            use_container_width=True,
            hide_index=True,
            height=550,
        )


# ============================================================
# AI AGENT
# ============================================================

elif page == "AI Agent":

    section(
        "Recovery Agent",
        "Closed-loop payment recovery workflow",
    )

    # --------------------------------------------------------
    # PIPELINE
    # --------------------------------------------------------

    st.html(
        dedent(
            """
            <div class="panel">

                <div class="panel-title">
                    Decision workflow
                </div>

                <div class="panel-description">
                    A failed payment is diagnosed, scored,
                    assigned a recovery action and observed
                    for its outcome.
                </div>

                <div class="pipeline">

                    <div class="pipeline-stage">
                        <div class="pipeline-number">01</div>
                        <div class="pipeline-name">
                            Payment failure
                        </div>
                        <div class="pipeline-detail">
                            Event received
                        </div>
                    </div>

                    <div class="pipeline-stage">
                        <div class="pipeline-number">02</div>
                        <div class="pipeline-name">
                            Diagnose
                        </div>
                        <div class="pipeline-detail">
                            Failure analysis
                        </div>
                    </div>

                    <div class="pipeline-stage">
                        <div class="pipeline-number">03</div>
                        <div class="pipeline-name">
                            Predict
                        </div>
                        <div class="pipeline-detail">
                            Recovery probability
                        </div>
                    </div>

                    <div class="pipeline-stage">
                        <div class="pipeline-number">04</div>
                        <div class="pipeline-name">
                            Estimate
                        </div>
                        <div class="pipeline-detail">
                            Expected revenue
                        </div>
                    </div>

                    <div class="pipeline-stage">
                        <div class="pipeline-number">05</div>
                        <div class="pipeline-name">
                            Decide
                        </div>
                        <div class="pipeline-detail">
                            Policy selection
                        </div>
                    </div>

                    <div class="pipeline-stage">
                        <div class="pipeline-number">06</div>
                        <div class="pipeline-name">
                            Act
                        </div>
                        <div class="pipeline-detail">
                            Recovery action
                        </div>
                    </div>

                    <div class="pipeline-stage">
                        <div class="pipeline-number">07</div>
                        <div class="pipeline-name">
                            Observe
                        </div>
                        <div class="pipeline-detail">
                            Outcome feedback
                        </div>
                    </div>

                </div>

            </div>
            """
        ),
    )


    # --------------------------------------------------------
    # DECISION FEED
    # --------------------------------------------------------

    section(
        "Decision feed",
        "Most recent recovery decisions",
    )

    if df.empty:

        st.info(
            "No agent decisions recorded yet."
        )

    else:

        feed = df.head(10).copy()

        st.html(
            '<div class="panel decision-feed">',
        )

        for _, row in feed.iterrows():

            transaction_id = row.get(
                "transaction_id",
                "TXN",
            )

            category = row.get(
                "failure_category",
                "unknown",
            )

            action = row.get(
                "recommended_action",
                "NO_ACTION",
            )

            probability = row.get(
                "recovery_probability",
                0,
            )

            confidence = row.get(
                "confidence",
                "LOW",
            )

            amount = row.get(
                "amount",
                0,
            )

            status = row.get(
                "outcome_status",
                "PENDING",
            )

            try:

                probability_text = (
                    f"{float(probability) * 100:.1f}%"
                )

            except Exception:

                probability_text = "—"


            action_class = "badge-blue"

            if action == "PAYMENT_LINK":

                action_class = "badge-purple"

            elif action == "PAYMENT_METHOD_UPDATE":

                action_class = "badge-amber"

            elif action == "NO_ACTION":

                action_class = "badge-red"


            confidence_class = "badge-green"

            if str(confidence).upper() == "MEDIUM":

                confidence_class = "badge-amber"

            elif str(confidence).upper() == "LOW":

                confidence_class = "badge-red"


            st.html(
                dedent(
                    f"""
                    <div class="decision-row">

                        <div>
                            <div class="decision-id">
                                {transaction_id}
                            </div>

                            <div class="decision-sub">
                                {money(amount)}
                            </div>
                        </div>

                        <div>
                            <div class="decision-main">
                                {str(category)
                                    .replace("_", " ")
                                    .title()}
                            </div>

                            <div class="decision-sub">
                                {status}
                            </div>
                        </div>

                        <div>
                            <span class="badge {action_class}">
                                {str(action)
                                    .replace("_", " ")}
                            </span>
                        </div>

                        <div>
                            <div class="decision-prob">
                                {probability_text}
                            </div>

                            <div style="
                                text-align:right;
                                margin-top:4px;
                            ">
                                <span class="
                                    badge
                                    {confidence_class}
                                ">
                                    {confidence}
                                </span>
                            </div>
                        </div>

                    </div>
                    """
                ),
            )

        st.html(
            "</div>",
        )


# ============================================================
# MLOPS
# ============================================================

elif page == "MLOps":

    section(
        "MLOps Control Plane",
        "Model registry, evaluation and lifecycle",
    )


    # --------------------------------------------------------
    # MODEL METRICS
    # --------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        metric_card(
            "MODEL",
            "RECLAIM v1",
            "Production registry version",
        )

    with c2:

        metric_card(
            "F1",
            "0.699",
            "Held-out evaluation",
            "metric-success",
        )

    with c3:

        metric_card(
            "ROC-AUC",
            "0.734",
            "Ranking performance",
            "metric-accent",
        )

    with c4:

        metric_card(
            "PR-AUC",
            "0.688",
            "Imbalanced-data ranking",
            "metric-accent",
        )


    # --------------------------------------------------------
    # MODEL LIFECYCLE
    # --------------------------------------------------------

    section(
        "Model lifecycle",
        "Current registry state",
    )

    st.html(
        dedent(
            """
            <div class="panel lifecycle-table">

                <div class="lifecycle-row">

                    <div class="lifecycle-label">
                        Registered model
                    </div>

                    <div class="lifecycle-value">
                        RECLAIM-Recovery-Model
                    </div>

                    <div>
                        <span class="badge badge-green">
                            ACTIVE
                        </span>
                    </div>

                </div>


                <div class="lifecycle-row">

                    <div class="lifecycle-label">
                        Production version
                    </div>

                    <div class="lifecycle-value">
                        Version 1
                    </div>

                    <div>
                        <span class="badge badge-green">
                            SERVING
                        </span>
                    </div>

                </div>


                <div class="lifecycle-row">

                    <div class="lifecycle-label">
                        Prediction logging
                    </div>

                    <div class="lifecycle-value">
                        logs/predictions.csv
                    </div>

                    <div>
                        <span class="badge badge-green">
                            ACTIVE
                        </span>
                    </div>

                </div>


                <div class="lifecycle-row">

                    <div class="lifecycle-label">
                        Drift monitoring
                    </div>

                    <div class="lifecycle-value">
                        PSI and distribution monitoring
                    </div>

                    <div>
                        <span class="badge badge-green">
                            ACTIVE
                        </span>
                    </div>

                </div>


                <div class="lifecycle-row">

                    <div class="lifecycle-label">
                        Retraining
                    </div>

                    <div class="lifecycle-value">
                        Triggered by significant drift
                    </div>

                    <div>
                        <span class="badge badge-amber">
                            CONDITIONAL
                        </span>
                    </div>

                </div>


                <div class="lifecycle-row">

                    <div class="lifecycle-label">
                        Promotion gate
                    </div>

                    <div class="lifecycle-value">
                        F1 ≥ 0.65 · ROC-AUC ≥ 0.70 ·
                        PR-AUC ≥ 0.65
                    </div>

                    <div>
                        <span class="badge badge-green">
                            PASSED
                        </span>
                    </div>

                </div>

            </div>
            """
        ),
    )


    # --------------------------------------------------------
    # MODEL QUALITY
    # --------------------------------------------------------

    section(
        "Model quality",
        "Frozen production evaluation",
    )

    quality = pd.DataFrame(
        {
            "Metric": [
                "Accuracy",
                "Precision",
                "Recall",
                "F1",
                "ROC-AUC",
                "PR-AUC",
                "Brier Score",
                "Log Loss",
            ],

            "Value": [
                "0.657",
                "0.601",
                "0.834",
                "0.699",
                "0.734",
                "0.688",
                "0.209",
                "0.608",
            ],

            "Purpose": [
                "Overall classification",
                "Positive prediction quality",
                "Recovery capture",
                "Balance",
                "Ranking quality",
                "Imbalanced-data ranking",
                "Calibration",
                "Probability quality",
            ],
        }
    )

    st.dataframe(
        quality,
        use_container_width=True,
        hide_index=True,
    )


    # --------------------------------------------------------
    # ARCHITECTURE
    # --------------------------------------------------------

    section(
        "Architecture",
        "Closed-loop ML lifecycle",
    )

    st.html(
        dedent(
            """
            <div class="panel">

                <div class="architecture-flow">

                    <span class="architecture-node">
                        Payment event
                    </span>

                    <span class="architecture-arrow">
                        →
                    </span>

                    <span class="architecture-node">
                        Features
                    </span>

                    <span class="architecture-arrow">
                        →
                    </span>

                    <span class="architecture-node">
                        ML inference
                    </span>

                    <span class="architecture-arrow">
                        →
                    </span>

                    <span class="architecture-node">
                        Recovery policy
                    </span>

                    <span class="architecture-arrow">
                        →
                    </span>

                    <span class="architecture-node">
                        Action
                    </span>

                    <span class="architecture-arrow">
                        →
                    </span>

                    <span class="architecture-node">
                        Outcome
                    </span>

                    <span class="architecture-arrow">
                        →
                    </span>

                    <span class="architecture-node">
                        Monitoring
                    </span>

                    <span class="architecture-arrow">
                        →
                    </span>

                    <span class="architecture-node">
                        Retraining
                    </span>

                </div>

            </div>
            """
        ),
    )