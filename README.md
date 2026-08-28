````markdown
# RECLAIM AI

### Autonomous Revenue Recovery Agent

> An AI-powered revenue recovery system that identifies at-risk revenue, diagnoses payment failures, chooses the safest recovery action, executes it through Razorpay Test Mode, and measures the revenue actually recovered.

---

## 🎯 Problem

Payment failures and other revenue-leakage events can cause merchants to lose otherwise recoverable revenue.

A failed payment does not always mean lost revenue. The appropriate response depends on factors such as:

- Failure reason
- Transaction amount
- Customer payment history
- Number of previous attempts
- Payment method
- Timing
- Likelihood of successful recovery
- Merchant-defined recovery policies

RECLAIM aims to move beyond fixed recovery rules by combining **machine learning, agentic decision-making, deterministic guardrails, and measurable business outcomes**.

---

## 💡 Solution

RECLAIM continuously evaluates revenue-at-risk events and determines the most appropriate recovery strategy.

### Core workflow

```text
Payment Event
      ↓
Revenue-at-Risk Detection
      ↓
ML Recovery Prediction
      ↓
AI Diagnosis
      ↓
Recovery Agent
      ↓
Policy & Safety Guardrails
      ↓
Recovery Action
      ↓
Outcome Verification
      ↓
Revenue Recovered
      ↓
Monitoring & Learning
````

The system can choose from bounded actions such as:

* 🔄 Retry payment
* 🔗 Create payment link
* 📩 Send payment reminder
* 💳 Request payment-method update
* 👤 Escalate to human
* 🛑 Stop recovery attempts

The LLM does **not** have unrestricted control over financial actions. Agent decisions pass through deterministic policies and guardrails before execution.

---

## 🤖 AI + ML Architecture

RECLAIM combines multiple components:

### Machine Learning

Predicts the probability that a revenue-at-risk event can be successfully recovered.

Potential models include:

* Logistic Regression
* Random Forest
* Gradient Boosting / XGBoost

### Agentic AI

Uses transaction context, ML predictions, merchant policies, and available tools to determine an appropriate recovery strategy.

### Guardrails

Ensure that recovery actions remain within predefined limits.

Examples:

```text
Maximum retry attempts
Minimum recovery probability
Maximum intervention cost
Merchant policy restrictions
Escalation conditions
```

### Razorpay Integration

Razorpay Test Mode is used to simulate payment workflows and execute test transactions without moving real money.

---

## 📊 Key Metrics

### Business Metrics

* **Revenue at Risk**
* **Revenue Recovered**
* **Revenue Recovery Rate**
* Intervention Success Rate
* Average Recovery Time
* Human Escalation Rate
* Unnecessary Intervention Rate

### ML Metrics

* Precision
* Recall
* F1 Score
* ROC-AUC
* Model Calibration

### MLOps Metrics

* Model version
* Prediction distribution
* Data drift
* Model performance over time
* Retraining performance

---

## 🧪 Evaluation Strategy

RECLAIM will be compared against simpler recovery strategies.

### Baselines

1. Always retry once
2. Always send a payment reminder
3. ML-only recovery decision

### Proposed System

**ML + Agent + Guardrails**

The goal is to demonstrate that intelligent, context-aware recovery can improve revenue recovery while reducing unnecessary interventions.

---

## 🔄 MLOps

RECLAIM is designed as an end-to-end ML system rather than a standalone model.

Planned components include:

```text
Data
 ↓
Validation
 ↓
Feature Engineering
 ↓
Model Training
 ↓
Experiment Tracking
 ↓
Model Registry
 ↓
Deployment
 ↓
Monitoring
 ↓
Drift Detection
 ↓
Retraining
```

Potential tools:

* MLflow
* GitHub Actions
* Docker
* scikit-learn
* Python

---

## 🛡️ Safety & Reliability

Financial actions require strict control.

RECLAIM follows a **bounded-agent architecture**:

```text
LLM Agent
    ↓
Proposed Action
    ↓
Policy Engine
    ↓
Guardrail Validation
    ↓
Allowed? ───── No → Reject / Escalate
    │
   Yes
    ↓
Razorpay Test Mode
    ↓
Outcome Verification
```

The system should also gracefully handle failures.

For example:

```text
Payment Failed
      ↓
Retry Attempt
      ↓
Retry Failed
      ↓
Maximum Attempts Reached
      ↓
STOP
      ↓
Human Escalation
```

---

## 🧰 Technology Stack

| Component     | Technology                 |
| ------------- | -------------------------- |
| Language      | Python                     |
| ML            | scikit-learn / XGBoost     |
| LLM           | Groq / Gemini              |
| Agent         | LangGraph                  |
| Vector Search | FAISS / Chroma             |
| Backend       | FastAPI                    |
| Database      | SQLite / Supabase          |
| Payments      | Razorpay Test Mode         |
| MLOps         | MLflow                     |
| CI/CD         | GitHub Actions             |
| Frontend      | Streamlit / Next.js        |
| Deployment    | Vercel + free-tier backend |
| Data          | Synthetic / Kaggle         |

All development is designed around **free-tier or open-source tooling**.

---

## 🗺️ Project Roadmap

* [ ] Phase 0 — Product Definition & Repository Setup
* [ ] Phase 1 — Dataset & Data Pipeline
* [ ] Phase 2 — Baseline ML Model
* [ ] Phase 3 — MLOps Foundation
* [ ] Phase 4 — Revenue Recovery Decision Engine
* [ ] Phase 5 — Agentic Layer
* [ ] Phase 6 — Razorpay Test Mode Integration
* [ ] Phase 7 — Revenue & Outcome Measurement
* [ ] Phase 8 — Monitoring & Drift Detection
* [ ] Phase 9 — CI/CD & Automated Retraining
* [ ] Phase 10 — Merchant Dashboard
* [ ] Phase 11 — Failure Handling & Guardrails
* [ ] Phase 12 — Evaluation & Ablation
* [ ] Phase 13 — Deployment
* [ ] Phase 14 — Final Demo & Presentation

---

## 🚧 Current Status

**Phase 0 — Product Definition**

The project is currently in the product-definition and architecture stage.

---

## ⚠️ Disclaimer

RECLAIM is a hackathon/research prototype.

All payment operations are performed using **Razorpay Test Mode** and no real financial transactions are processed.

```
```
