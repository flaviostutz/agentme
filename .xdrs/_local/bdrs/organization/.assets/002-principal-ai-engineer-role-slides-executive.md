---
marp: true
paginate: true
---

# Bank Lead AI Engineer

**Chartering the role at NN Bank**
CTO Organization — May 2026

---

# The problem

AI scaling across BUs — but scattered and unconnected

- Scaling AI across multiple BUs needs intention in sharing
- Data science prototypes do not meet production engineering standards
- Teams lack clear direction on which shared baselines to adopt
- Teams unsure what day-two practices their agents require (monitoring, versioning, retraining)
- As this is a fast-moving target, knowledge needs to be governed and continuously evolved
- Agentic tooling for coding, architecture review, and business rule validation adopted ad-hoc rather than governed
- BUs need someone to help translate AI possibilities into concrete initiatives

---

# The gap in the org

```
Data Scientists   Engineers   Architects   Business Analysts   Controls
      |               |            |              |                |
      +-------+-------+------------+--------------+----------------+
              |
       The combined wide+deep knowledge to connect all disciplines
       in professional AI delivery is a challenge
```

Each discipline optimizes locally — the overall system suffers from misalignment.
The org needs a glue role that speaks all these languages and connects them into a coherent whole.

---

# The decision

**Create a Bank Lead AI Engineer role**
Advisory, reporting through the CTO organization

> A connective glue role that bridges data science, software engineering,
> architecture, business analysis, and controls.

---

# Organizational positioning

| Attribute | Detail |
|---|---|
| Reports to | CTO organization |
| Mandate | Across all AI-active business units |
| Influence model | Standards, enablement, direct team support |
| Escalation | CTO sponsorship for cross-BU alignment |

---

# Responsibility domains

1. Strategic alignment
2. Agentic for business
3. Agentic for coding
4. Agentic for architecture and engineering
5. Agentic for governance
6. AI controls advisory
7. Advisory and knowledge transfer

---

# Strategic alignment

- Define the AI engineering vision and roadmap with CTO
- Identify opportunities for AI and agentic systems across BUs
- Prioritize AI initiatives based on business impact and feasibility
- Track AI industry trends; bring relevant innovations to the org

---

# Agentic for business

- Translate BU requirements into agentic system designs
- Define patterns: orchestration, tool use, memory, human-in-the-loop
- Ensure agents meet compliance, auditability, and explainability requirements for financial services
- Guide teams: ideation → prototyping → production → post-launch

---

# Production engineering bridge

```
Data Science          Bank Lead AI Engineer        Engineering
    |                          |                         |
  Prototype  ------>  Package, serve, monitor  ------>  Production
                       Version, track, test              |
                       Day-two: drift, retrain       Scales, monitors
```

The role helps filling the gap between prototype and production.

---

# Governance and controls

**Governance**
- Quality gates at PoC, MVP, production, and post-launch
- Automated validation of business rules and architecture decisions
- Mandatory sign-off before stage progression

**Controls advisory**
- Translate AI-specific risks (hallucination, drift, bias, prompt injection) into operationalizable controls
- Distinguish blocking controls, detective controls, and advisory guidelines
- Enable safe AI adoption — not blanket restriction

---

# Why advisory, not a dedicated team

| | Model A: Embedded | **Model B: Advisory** | Model C: Dedicated team |
|---|---|---|---|
| Influence scope | Single team | All BUs | All BUs |
| Org change needed | No | No | Yes — new team |
| Knowledge transfer | Low | High | Medium |
| Bottleneck risk | Low | Low | High |
| Right for current state | No | **Yes** | At scale (3+ BUs) |

---

# Evolution path

```
Today (2–3 active BUs)          At scale (3+ BUs)
        |                               |
  Advisory Bank Lead AI Engineer  -->  Lightweight AI team
  (Model B)                            led by Bank Lead AI Engineer
                                        (Model C)
```

The advisory model is the right starting point. Plan the transition as AI adoption grows.

---

# What good looks like

**Success metrics**

- Number of teams delivering AI to production
- Time-to-production reduction for AI projects
- Adoption of shared standards across BUs
- Quality of day-two practices (monitoring, drift detection, retraining)

> Every team the role engages with should need **less** support over time, not more.

---

# Profile required

| Category | Key requirements |
|---|---|
| AI/ML depth | 5+ years production AI/ML; agentic frameworks; LLM patterns (RAG, fine-tuning, evaluation) |
| Engineering breadth | Software engineering; cloud; MLOps; data engineering |
| Architecture | System design; reference architecture; AI/agent integration patterns |
| Leadership | Cross-functional influence; mentoring; exec + engineering communication |
| Business | Financial services domain; cost-benefit analysis; regulated environment risk |

*This is a rare wide+deep profile — the combination is intentional and non-negotiable.*

---

# Recommended next steps

1. **Secure CTO sponsorship** — mandate requires explicit executive backing
2. **Define the hiring brief** — wide+deep profile needs a targeted search
3. **Identify a first BU engagement** — visible early win builds organizational credibility
4. **Plan the Model C transition** — set a threshold (e.g. 3+ active BUs) to review team model

---

# References

- [Bank Lead AI Engineer Role Charter](../002-principal-ai-engineer-role.md)
- [Bank Lead AI Engineer Role Research](../researches/001-principal-ai-engineer-role.md)
