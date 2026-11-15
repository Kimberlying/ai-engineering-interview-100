# en_build_header.py

en_header = """# 100 Questions That Haunt AI Engineering Interviews in 2026

<p align="center">
  <b>From Production Incidents to Scalable System Architecture Design</b><br>
  Covering LLM Foundations, RAG, Autonomous Agents, Fine-tuning, Inference & Serving, Production Reliability, Governance, and 7 End-to-End System Designs.
</p>

<p align="center">
  <a href="README.md"><b>🇨🇳 简体中文</b></a> | 
  <a href="README_EN.md"><b>🇬🇧 English</b></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
  <img src="https://img.shields.io/badge/Status-Complete-success.svg" alt="Status">
  <img src="https://img.shields.io/badge/Focus-Production%20Incidents-blue.svg" alt="Focus">
  <img src="https://img.shields.io/badge/License-MIT-orange.svg" alt="License">
</p>

---

## 📌 Why This Handbook Exists

In 2026, AI engineering interviews have undergone a fundamental shift: **The era of memorizing theoretical textbook concepts is dead.**

Interviewers no longer ask you *"What is self-attention?"* or *"Can you derive the LoRA backward pass?"*. Instead, they drop you straight into **real-world production outages and architectural fire drills**:
- *"Your support agent called the same order lookup tool 40 times in a row until it timed out and blew the token budget. How do you detect and intercept this at runtime?"*
- *"Your evaluation dashboard shows a Faithfulness of 0.92, yet users and stakeholders are screaming that the assistant is completely useless. What broke?"*
- *"Monthly user traffic only grew by 40%, but your LLM API invoice tripled. How do you diagnose root causes and present an actionable cost-reduction plan to the CFO by Friday?"*
- *"At 2 AM on Halloween, your multi-tenant platform begins leaking another enterprise customer's confidential contract clauses. How do you lead incident response and redesign the system?"*

This repository compiles all **100 production-grounded questions**, enriched with **core conceptual breakdowns, step-by-step diagnostic paths, industry-grade answers**, and **7 comprehensive end-to-end system designs**.

---

## 💡 The Two "Muscle Memories" of Senior AI Architects

### Golden Rule #1: Divide & Conquer — Retrieval or Generation?
> When an AI system produces an incorrect response, never blindly tweak prompt instructions. First ask:
> **"Did the correct evidence ever make it in front of the model?"**
> - **NO (Not present)**: It is strictly a **retrieval/ingestion failure** (poor recall, fragmented chunking, outdated indexing, ACL filters). No amount of prompt engineering will ever fix missing context.
> - **YES (Present, yet still failed)**: It is a **generation/reasoning failure** (needle-in-a-haystack attention dilution, reasoning weakness, weak instruction following). Upgrading to a more expensive vector database will not save you.

### Golden Rule #2: Commit to the Right Contract (Engineering SLA/SLO)
> When facing stochastic systems (e.g., non-determinism even at `temperature = 0`), senior engineers never make vague promises like *"I guarantee the model will output the exact same wording every time."* 
> Instead, they establish **hard engineering contracts**:
> - Commit to **decision stability** (deterministic state machine transitions, exact JSON schema compliance), rather than verbatim textual phrasing.
> - Enforce critical paths via structured outputs and deterministic downstream validation code.
> - Maintain an active Golden Benchmark (e.g., 1,000 edge cases) with CI/CD regression gates and quantitative thresholds (e.g., `>= 99.8% decision consistency`).

---

## 📑 Table of Contents

- [Part 1: LLM Foundations & Prompt Engineering (Q1–Q15)](#part-1-llm-foundations--prompt-engineering-q1q15)
- [Part 2: RAG Architectures & Retrieval (Q16–Q35)](#part-2-rag-architectures--retrieval-q16q35)
  - 🌟 **Q35 System Design**: Enterprise Multi-Source Knowledge Assistant for 50,000 Employees
- [Part 3: RAG Evaluation, Hallucination & Grounding (Q36–Q50)](#part-3-rag-evaluation-hallucination--grounding-q36q50)
  - 🌟 **Q50 System Design**: High-Stakes Clinical / Legal Grounding & Safety Architecture
- [Part 4: AI Agents, Tool Calling & Multi-Agent Systems (Q51–Q65)](#part-4-ai-agents-tool-calling--multi-agent-systems-q51q65)
  - 🌟 **Q65 System Design**: Production Support Agent for 100,000 Daily E-Commerce Conversations
- [Part 5: Fine-Tuning, Model Adaptation & Model Selection (Q66–Q75)](#part-5-fine-tuning-model-adaptation--model-selection-q66q75)
  - 🌟 **Q75 System Design**: Regulated Financial Multi-Model Tiering Strategy
- [Part 6: LLM Inference, Deployment & Scaling (Q76–Q85)](#part-6-llm-inference-deployment--scaling-q76q85)
  - 🌟 **Q85 System Design**: Unified Multi-Tenant LLM Serving & Inference Platform
- [Part 7: AI System Design & Production Reliability (Q86–Q95)](#part-7-ai-system-design--production-reliability-q86q95)
  - 🌟 **Q95 System Design**: Automated Pull Request AI Code Reviewer for 2,000 Engineers
- [Part 8: Security, Privacy, Governance & Cost Control (Q96–Q100)](#part-8-security-privacy-governance--cost-control-q96q100)
  - 🌟 **Q100 Ultimate War Room**: 2 AM Cross-Tenant Data Leak & Cost Surge Remediation

---
"""
