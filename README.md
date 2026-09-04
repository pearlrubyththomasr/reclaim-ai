# RECLAIM — Autonomous Revenue Recovery Agent

> **Recovery isn't the hard part. Knowing when not to recover is.**

RECLAIM is an AI-driven revenue recovery system designed to identify failed payments worth recovering, estimate the probability of successful recovery, choose the most appropriate intervention, execute a bounded recovery action, observe the outcome, and feed operational data back into an MLOps lifecycle.

The project is built for the **Razorpay AI Buildathon 2026 — Track 3: AI Revenue Recovery**.

---

## 1. Problem

A failed payment does not automatically mean that another retry is the right answer.

Different failure causes require different responses:

- A transient gateway/network failure may be worth retrying.
- An insufficient-funds failure may be better handled with an alternate payment path.
- An expired payment method may require the customer to update their payment method.
- A merchant configuration error may not be worth retrying at all.

A naive recovery system can waste retries, create unnecessary customer friction, and spend operational effort on payments that have little chance of recovery.

### RECLAIM's objective

Instead of asking:

> "Can we retry this payment?"

RECLAIM asks:

> **"Is intervention economically justified, and if so, what is the best bounded action?"**

---

# 2. Solution

RECLAIM combines:

1. Failure diagnosis
2. ML-based recovery probability prediction
3. Expected revenue estimation
4. Deterministic recovery policy
5. Bounded recovery execution
6. Outcome observation
7. Revenue measurement
8. MLOps monitoring and conditional retraining

### Core decision loop

```text
Failed Payment
      |
      v
Failure Diagnosis
      |
      v
Recovery Probability
      |
      v
Expected Revenue
(probability × amount)
      |
      v
Deterministic Policy
      |
      +----------+-------------+-------------+
      |          |             |             |
      v          v             v             v
    RETRY   PAYMENT LINK   METHOD UPDATE   NO ACTION
      |          |             |             |
      +----------+-------------+-------------+
                         |
                         v
                      Outcome
                         |
                         v
                 Revenue Recovered
                         |
                         v
                  MLOps Monitoring
                         |
                +--------+--------+
                |                 |
              Stable            Drift
                                  |
                                  v
                              Retraining
                                  |
                                  v
                            Promotion Gate
```

---

# 3. Why RECLAIM is different

The central design principle is:

> **The best recovery system is not the one that intervenes most. It is the one that allocates intervention effort where the expected value is highest.**

RECLAIM therefore separates **intelligence** from **control**.

### AI / ML provides

- Failure understanding
- Recovery probability
- Expected recoverable value

### Deterministic policy provides

- Allowed actions
- Failure-specific intervention rules
- Retry boundaries
- Stopping conditions
- No-action decisions

This prevents an LLM or probabilistic model from directly making unrestricted payment decisions.

---

# 4. Architecture

```text
                    +-----------------------+
                    |   Razorpay Test Mode  |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    |   Payment Event       |
                    |   Normalization        |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    | Failure Diagnostics   |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    | Recovery ML Model     |
                    | Logistic Regression   |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    | Expected Revenue      |
                    | P(recovery) × amount  |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    | Deterministic Policy  |
                    +-----------+-----------+
                                |
              +-----------------+-----------------+
              |                 |                 |
              v                 v                 v
            RETRY         PAYMENT LINK      NO ACTION
              |                 |                 |
              +-----------------+-----------------+
                                |
                                v
                    +-----------------------+
                    | Outcome / Feedback    |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    | Revenue Metrics       |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    | MLOps Monitoring      |
                    | Drift / Lifecycle     |
                    +-----------------------+
```

---

# 5. Machine Learning

## Dataset

The project uses a synthetic transaction dataset containing:

- 50,000 transaction records
- Payment amount
- Payment method
- Merchant category
- Subscription status
- Payment status
- Failure category and failure code
- Attempt number
- Customer transaction history
- Customer failure rate
- Previous recovery history
- Temporal features
- Recovery outcome

After validation and temporal splitting:

| Split | Rows | Recovery Rate |
|---|---:|---:|
| Train | 11,200 failed payments | 44.76% |
| Validation | 1,400 failed payments | 47.64% |
| Test | 1,401 failed payments | 47.75% |

The split is temporal so that future observations are not used to train the model.

---

# 6. Model selection

Several models were evaluated:

- Majority baseline
- Logistic Regression
- Random Forest
- XGBoost

The final model is **Logistic Regression** because it provided strong validation performance while remaining simple, interpretable, and easy to monitor.

### Validation comparison

| Model | Accuracy | F1 | ROC-AUC | PR-AUC |
|---|---:|---:|---:|---:|
| Logistic Regression | 67.21% | 63.19% | 0.729 | 0.689 |
| Random Forest | 66.07% | 64.31% | 0.722 | 0.689 |
| XGBoost | 65.57% | 61.75% | 0.708 | 0.676 |

The recovery policy threshold was selected using validation data.

### Final recovery threshold

**0.35**

The threshold was chosen as a revenue-aware operating point rather than simply assuming a 0.50 classification threshold.

---

# 7. Final test performance

The frozen model was evaluated on the held-out temporal test set.

| Metric | Test |
|---|---:|
| Accuracy | 65.67% |
| Precision | 60.13% |
| Recall | 83.41% |
| F1 | **69.88%** |
| ROC-AUC | **0.734** |
| PR-AUC | **0.688** |
| Brier Score | 0.209 |
| Log Loss | 0.608 |

The model is used as a decision input rather than as the final authority over payment actions.

---

# 8. Explainability

The model provides interpretable feature coefficients.

Important learned signals include:

- Failure category
- Failure code
- Attempt number
- Customer failure rate
- Merchant configuration errors
- Gateway/network failures
- Insufficient funds
- Authentication failures
- Expired payment methods

This helps RECLAIM explain why a recovery action was recommended.

---

# 9. Recovery Decision Policy

The policy converts model output into a bounded action.

### Example rules

```text
Recovery probability < 20%
        |
        v
     NO ACTION

20% - 35%
        |
        +--> insufficient funds -> PAYMENT LINK
        |
        +--> expired/authentication -> METHOD UPDATE
        |
        +--> otherwise -> NO ACTION

Recovery probability >= 35%
        |
        +--> transient/network + low attempts -> RETRY
        |
        +--> insufficient funds -> PAYMENT LINK
        |
        +--> expired/authentication -> METHOD UPDATE
        |
        +--> merchant error -> NO ACTION
        |
        +--> otherwise -> RETRY
```

Repeated attempts are bounded to avoid indefinite retry behavior.

---

# 10. Expected Revenue

RECLAIM converts prediction into an economic signal:

```text
Expected Revenue =
Recovery Probability × Payment Amount
```

For example:

```text
Payment amount       = ₹4,999
Recovery probability = 82%

Expected recovery ≈ ₹4,099
```

This allows the system to reason about **money at risk**, rather than only classification accuracy.

---

# 11. The key RECLAIM decision

A central demonstration scenario is a merchant configuration failure.

```text
Payment amount:       ₹6,999
Failure:              Merchant configuration error
Recovery probability: Low
Decision:             NO ACTION
```

RECLAIM deliberately avoids intervention because retrying does not address the underlying failure.

This demonstrates the project's core principle:

> **Knowing when NOT to intervene is part of intelligent revenue recovery.**

---

# 12. MLOps

RECLAIM is designed as an MLOps system rather than a one-time ML application.

## Experiment tracking

**MLflow** is used for:

- Experiment tracking
- Parameters
- Metrics
- Model artifacts
- Model registry
- Model versioning

Registered model:

```text
RECLAIM-Recovery-Model
```

Current candidate:

```text
Version 1
```

## Promotion gate

A model must satisfy minimum quality requirements before promotion.

Current gates:

```text
F1     >= 0.65
ROC-AUC >= 0.70
PR-AUC  >= 0.65
```

The current validation candidate passes the promotion gate.

---

# 13. Production monitoring

RECLAIM records prediction and action events including:

- Timestamp
- Payment amount
- Failure category
- Failure code
- Attempt number
- Customer failure rate
- Model version
- Recovery probability
- Expected revenue
- Recommended action
- Confidence
- Outcome status
- Recovered amount

Monitoring compares production behavior against the validation reference distribution.

### Drift monitoring includes

#### Numeric features

- Amount
- Attempt number
- Customer failure rate

#### Categorical features

- Failure category
- Failure code

#### Behavioral monitoring

- Intervention rate
- Action distribution
- Prediction probability distribution
- Outcome status
- Recovered revenue

---

# 14. Conditional retraining

RECLAIM does not retrain blindly.

The retraining pipeline checks:

1. Whether enough production observations exist.
2. Whether significant distribution drift is present.
3. Whether retraining is justified.

Conceptually:

```text
Production Data
      |
      v
Enough Data?
   /       \
 NO         YES
 |           |
Stop      Drift Check
             |
       +-----+-----+
       |           |
     Stable      Drift
       |           |
     Keep       Retrain
                   |
                   v
              Validate Model
                   |
                   v
             Promotion Gate
                   |
                   v
                Promote
```

---

# 15. Razorpay integration

RECLAIM is connected to **Razorpay Test Mode**.

The project validates the gateway connection through test-order creation and normalizes payment failure information into the internal RECLAIM event model.

The current build intentionally distinguishes between:

- **Real gateway connectivity**
- **Real ML inference and policy decisions**
- **Controlled/synthetic recovery outcomes for the demo**

Recovery outcomes shown in the investor demonstration are simulated and clearly labeled. A production deployment would replace the outcome simulator with real gateway/webhook outcome events.

---

# 16. Investor Demo

The Streamlit interface contains a dedicated **Investor Demo** page.

### Demo scenarios

#### Scenario 1 — Network failure

```text
Amount:              ₹4,999
Failure:             Network / transient failure
Recovery probability: High
Action:              RETRY
Outcome:             Recovered
```

#### Scenario 2 — Insufficient funds

```text
Amount:              ₹3,247
Failure:             Insufficient funds
Recovery probability: Meaningful
Action:              PAYMENT LINK
Outcome:             Recovered
```

#### Scenario 3 — Merchant configuration error

```text
Amount:              ₹6,999
Failure:             Merchant configuration error
Recovery probability: Low
Action:              NO ACTION
Outcome:             Not recovered
```

The first two scenarios demonstrate recovery.

The third demonstrates intelligent restraint.

---

# 17. Dashboard

The RECLAIM Command Center provides:

### Overview

- Failed payments
- Interventions
- Recovered transactions
- Expected revenue
- Recovered revenue
- Recovery analysis
- Recent activity

### Investor Demo

- End-to-end decision demonstration
- Recovery probability
- Expected revenue
- Recommended action
- Recovery outcome
- Revenue impact
- NO_ACTION decision

### Recovery Operations

- Recovery action distribution
- Recovery event ledger
- Operational outcomes

### Payment Events

- Failed payment records
- Failure categories
- Failure codes
- Attempt information
- Customer context

### AI Agent

```text
Payment Failure
      ↓
Diagnose
      ↓
Predict
      ↓
Estimate
      ↓
Decide
      ↓
Act
      ↓
Observe
```

### MLOps

- Model quality
- Model version
- Promotion status
- Monitoring
- Drift
- Retraining status
- Architecture

---

# 18. Project Structure

```text
reclaim-ai/
│
├── data/
│   ├── raw/
│   │   └── transactions_raw.csv
│   │
│   └── processed/
│       ├── train.csv
│       ├── validation.csv
│       └── test.csv
│
├── models/
│
├── logs/
│   └── predictions.csv
│
├── src/
│   ├── agent/
│   │   ├── agent.py
│   │   ├── diagnostics.py
│   │   ├── feedback.py
│   │   └── retraining_decision.py
│   │
│   ├── decision/
│   │   └── policy.py
│   │
│   ├── mlops/
│   │   ├── train_tracked.py
│   │   ├── promotion_gate.py
│   │   ├── model_loader.py
│   │   ├── inference.py
│   │   ├── prediction_logger.py
│   │   ├── model_monitor.py
│   │   ├── monitor.py
│   │   ├── revenue_metrics.py
│   │   ├── retraining_pipeline.py
│   │   └── model_lifecycle.py
│   │
│   ├── payments/
│   │   ├── razorpay_client.py
│   │   ├── payment_event.py
│   │   ├── recovery_actions.py
│   │   ├── reclaim_payment_flow.py
│   │   ├── sandbox_demo.py
│   │   └── test_razorpay.py
│   │
│   └── demo/
│       └── investor_demo.py
│
├── ui/
│   ├── app.py
│   └── theme.py
│
├── .env
├── .gitignore
├── requirements.txt
├── mlflow.db
└── README.md
```

---

# 19. Running the project

## 1. Create/activate environment

```powershell
conda create -n reclaim python=3.11
conda activate reclaim
```

Or use an existing Python virtual environment.

## 2. Install dependencies

```powershell
pip install -r requirements.txt
```

## 3. Configure Razorpay Test Mode

Create a `.env` file:

```env
RAZORPAY_KEY_ID=rzp_test_your_key
RAZORPAY_KEY_SECRET=your_secret
```

**Never commit `.env` or payment credentials.**

## 4. Start the dashboard

From the project root:

```powershell
$env:PYTHONPATH="src"
streamlit run ui/app.py
```

## 5. Start MLflow

```powershell
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
```

Then open:

```text
http://127.0.0.1:5000
```

---

# 20. Useful commands

### Test Razorpay connection

```powershell
$env:PYTHONPATH="src"
python -m payments.test_razorpay
```

### Run payment-flow demo

```powershell
$env:PYTHONPATH="src"
python -m payments.sandbox_demo
```

### Run agent demo

```powershell
$env:PYTHONPATH="src"
python -m agent.demo
```

### Run investor demo

```powershell
$env:PYTHONPATH="src"
python -m demo.investor_demo
```

# 21. Safety and operational boundaries

RECLAIM intentionally uses bounded deterministic policies around payment actions.

Important safeguards include:

- Failure-specific action selection
- Retry limits
- NO_ACTION paths
- Model promotion gates
- Production drift monitoring
- Versioned models
- Prediction/action logging
- Outcome feedback
- Separation between probabilistic prediction and deterministic execution

The current demonstration uses controlled synthetic outcomes for recovery execution. It does not claim that a test-mode order creation itself constitutes successful payment recovery.

---

# 22. Technology Stack

| Layer | Technology |
|---|---|
| Language | Python |
| ML | scikit-learn |
| Model | Logistic Regression |
| Experiment Tracking | MLflow |
| API | FastAPI |
| Dashboard | Streamlit |
| Visualization | Plotly |
| Data | pandas / NumPy |
| Payments | Razorpay Test Mode |
| Storage | SQLite / CSV |
| Environment | Python / Conda |

---

# 23. Key takeaway

RECLAIM treats payment recovery as a **closed-loop revenue optimization problem**:

```text
Predict
  ↓
Value
  ↓
Decide
  ↓
Act
  ↓
Measure
  ↓
Monitor
  ↓
Learn
```

The system is not optimized to maximize intervention volume.

It is designed to maximize **justified recovery effort and recovered revenue while avoiding unnecessary intervention**.

> ## Recovery isn't the hard part.
> ## Knowing when not to recover is.
