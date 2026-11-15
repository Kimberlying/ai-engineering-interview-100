# en_parts_3_4.py

part3 = """
## Part 3: RAG Evaluation, Hallucination & Grounding (Q36–Q50)

#### Q36 Your team relies on a single metric—"thumbs-up rate"—to measure the RAG assistant. Design a tiered evaluation framework so that when quality degrades, you know exactly what to fix. `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Failure of Thumbs-Up Rate**: Lagging indicator, subject to severe survivor bias (only extremely delighted or infuriated users vote), and provides zero diagnostic attribution.
- **Tiered Evaluation Funnel (Four Pillars)**:
  1. **Tier 1: Retrieval Quality (Search Layer)**
     - *Metrics*: HitRate@K, Recall@K, Mean Reciprocal Rank (MRR), nDCG@K.
     - *Diagnostics*: Did the retriever fetch the true positive chunks into the candidate pool?
  2. **Tier 2: Context Precision & Noise Ratio (Context Layer)**
     - *Metrics*: Context Relevance, Noise Chunk Ratio.
     - *Diagnostics*: Are injected chunks diluting the prompt with irrelevant content?
  3. **Tier 3: Generation Faithfulness / Grounding (Truthfulness Layer)**
     - *Metrics*: Faithfulness Score (fraction of output claims strictly entailed by context).
     - *Diagnostics*: Is the LLM hallucinating beyond the provided context, or is the context itself wrong?
  4. **Tier 4: Answer Relevance & Task Resolution (Business Layer)**
     - *Metrics*: Answer Quality, Task Completion Rate, Escalation Rate.
     - *Diagnostics*: Did the answer actually resolve the user's specific problem?
</details>

#### Q37 Build an automated faithfulness checker for an HR policy RAG assistant. How do you ensure this checker itself is trustworthy? `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Faithfulness Checker Architecture (Atomic Claim Decomposition)**:
  1. Decompose the generated response into atomic, independent factual claims.
  2. For each atomic claim, run Natural Language Inference (NLI) against retrieved context to classify entailment: `Entailed`, `Contradicted`, or `Neutral (Unproven)`.
  3. Compute $\text{Faithfulness} = \frac{\text{Count of Entailed Claims}}{\text{Total Claims}}$.
- **Trust Calibration for the Checker**:
  - **Expert Human Golden Dataset**: Have HR and legal specialists curate 300 audited responses with intentional subtle factual errors.
  - **Inter-Annotator Agreement (IAA)**: Measure Cohen’s Kappa ($\kappa \ge 0.85$) between the checker and human legal auditors.
  - **Ensemble Validation**: Cross-verify outputs using a fine-tuned NLI model (e.g., DeBERTa-v3) alongside an advanced LLM judge (Claude 3.5 Sonnet / GPT-4o).
  - **Mandatory Quote Extraction**: The checker must output the exact sentence in the context that proves or disproves each claim.
</details>

#### Q38 Your enterprise RAG assistant has a 12% error rate. Leadership asks: "Is this a search problem or a model problem?" Show how you find the answer. `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Attribution Methodology: Dual-Blind Context Isolation**:
  1. Sample 200 failed interactions representing the 12% error rate.
  2. **Audit 1: Oracle Context Audit (Knowledge Base Coverage)**:
     - Search the raw knowledge base manually. Does the knowledge base actually contain the correct answer?
     - If NO -> **Knowledge Ingestion Deficit** (Missing content).
  3. **Audit 2: Retrieval Slice Isolation (Search vs Model)**:
     - Inspect the exact Top-K chunks injected into the prompt for that failed request:
     - **Case A: The correct evidence was NOT in the context** -> **Search Failure** (responsible for ~70% of real-world bugs: chunking splits, missing keywords, ranking drops).
     - **Case B: The correct evidence WAS in the context, yet the model produced an error** -> **Model Generation Failure** (attention dilution, reasoning collapse, or prompt instruction conflicts).
  4. Present findings to leadership with a quantified attribution pie chart: *"Of the 12% errors: 60% retrieval misses, 25% missing KB docs, 15% model hallucination."*
</details>

#### Q39 Your assistant appends source citations to every sentence, but an audit shows ~20% of citations do not support the claim they are attached to. How do you fix and measure citation quality? `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Root Cause**: Hallucinatory citation attribution. Models append footnotes out of stylistic habit during generation without verifying strict semantic entailment.
- **Architectural Fix (Two-Stage Post-Hoc Attribution)**:
  1. Remove citation generation from the initial text generation prompt. Let the model write the factual response first.
  2. Run a fast, dedicated NLI attribution pass: For each generated sentence, evaluate entailment against each retrieved chunk. Attach footnote `[K]` only if the claim achieves a high entailment confidence score against Chunk $K$.
  3. If a sentence has no supporting chunk, either redact it or flag it with an explicit disclaimer.
- **Metrics**:
  - **Citation Precision**: $\frac{\text{Citations that strictly entail the attached sentence}}{\text{Total citations displayed}}$
  - **Citation Recall**: $\frac{\text{Factual assertions supported by citations}}{\text{Total factual assertions in response}}$
</details>

#### Q40 When the knowledge base lacks an answer, your assistant must say "I don't know." Currently, it either hallucinates answers or refuses valid questions. Design and evaluate an abstention mechanism. `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Three-Tier Abstention Defense**:
  1. **Retrieval-Score Hard Gate (Pre-Generation Gating)**: If the top reranker score is below an absolute relevance threshold (e.g., `score < 0.40`), do not call the generation LLM at all. Short-circuit immediately to a canned fallback message.
  2. **Explicit Negative Exemplars**: Inject 3 few-shot examples into the system prompt showcasing out-of-domain queries and modeling the ideal concise refusal response.
  3. **Structured Verification Gate**: Instruct the model to emit a verification tag before generating text: `<has_sufficient_evidence>true/false</has_sufficient_evidence>`. If `false`, truncate generation immediately.
- **Evaluation Strategy**:
  - Build an adversarial dataset: 50% answerable questions + 50% deliberately out-of-domain / unanswerable questions.
  - Plot the Precision-Recall curve for abstention: optimize for False Acceptance (hallucination on unanswerable) $< 1\%$ while keeping False Rejection (refusing valid questions) $< 5\%$.
</details>

#### Q41 Production traffic lacks ground-truth labels. How do you detect hallucinations and quality regressions in production within hours rather than weeks? `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Near-Real-Time Observability Pyramid**:
  1. **Implicit User Behavioral Signals**:
     - Immediate query reformulation (< 15s between near-identical queries).
     - Rapid copy-paste vs instant regeneration clicks.
     - Sudden spikes in "Transfer to Human Agent" requests.
  2. **Asynchronous Weak-Supervision Sampling**:
     - Route a continuous 5% stratified sample of production interactions to an asynchronous evaluation worker.
     - Run reference-free checks: Faithfulness (NLI entailment between output and retrieved context) and Self-Consistency (sample 3 completions at `temperature=0.7`; divergence signals hallucination).
  3. **Semantic Drift & Cluster Monitoring**:
     - Embed incoming user queries and monitor embedding space centroid drift. If a cluster of negative feedback emerges around a specific topic, trigger an automated Slack alert.
</details>

#### Q42 Design a CI regression gate for your RAG pipeline so that changes to prompts, chunking, embeddings, or retrievers cannot ship if quality degrades. How do you handle noise and cost? `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Tiered CI Test Suite Architecture**:
  - *Tier 1: Deterministic Unit Tests (ms, $0)*: Fast regression tests on chunkers, tokenizers, metadata filters, and regex parsing.
  - *Tier 2: Retrieval Snapshot Gate (30s, minimal cost)*: 100 benchmark queries evaluated strictly on retrieval metrics (HitRate@5, MRR). Block PR if retrieval metrics drop $> 0.5\%$.
  - *Tier 3: End-to-End Golden Eval (5 mins, run on PR merge / nightly)*: 200 representative queries evaluated by an LLM judge for Faithfulness and Correctness.
- **Managing Noise and Cost**:
  - Run eval models with `seed` and `temperature = 0` to reduce variance.
  - Cache intermediate retrieval results: do not re-embed unedited documents.
  - Implement a **Tolerance Band**: Allow $\pm 1\%$ statistical noise for stylistic scores, but enforce zero tolerance on hard constraints (e.g., zero regression on safety, schema parsing, and ACL checks).
</details>

#### Q43 You have a new reranker that shows a small offline nDCG@10 lift. Design an online experiment to decide whether to ship it to production. `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Two-Phase Experimentation Framework**:
  1. **Phase 1: Shadow Traffic Run (Days 1–3)**:
     - Asynchronously mirror 10% of live traffic through the new reranker without returning results to users.
     - Measure production infrastructure impact: p95/p99 latency delta, GPU memory utilization, and failure/timeout rates.
  2. **Phase 2: Split A/B Test (Days 4–14, 50/50 Traffic Split)**:
     - User assignment by persistent `user_id` hash to prevent UX flapping.
     - **Primary Business Metrics**: First-Contact Resolution (FCR), Session Length (fewer turns indicate higher precision), Thumbs-up/down ratio, Escalation-to-human rate.
     - **Guardrail Metrics**: End-to-end response timeouts must not increase; zero increase in client-side error codes.
  3. **Decision Criteria**: Ship only if primary business metrics demonstrate statistically significant improvements ($p < 0.05$) without breaching latency SLAs.
</details>

#### Q44 The retrieved context contains a 2022 policy and a 2024 revised policy that directly contradict each other, and the model blends them into an incoherent answer. How do you handle conflicting evidence? `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Four-Pillar Resolution Framework**:
  1. **Temporal Metadata Injection**: Prepend explicit temporal state to every retrieved chunk header: `[Effective Date: 2024-01-01 | Status: ACTIVE]` vs `[Effective Date: 2022-03-01 | Status: SUPERSEDED]`.
  2. **Explicit Temporal Precedence Prompting**: Mandate: *"When policies contradict, the document with the most recent effective date supersedes older versions. Explicitly acknowledge that the older policy has been replaced."*
  3. **Recency Decay at Reranking**: Apply exponential recency weighting to decay older documents during the cross-encoder rerank phase.
  4. **NLI Conflict Detection**: Run a lightweight conflict checker on top-ranked chunks; when contradiction is detected, instruct the model to output a comparative timeline instead of merging contradictory facts.
</details>

#### Q45 Your RAG evaluation dashboard displays a faithfulness of 0.92 and answer relevance of 0.90, but users and support reps report that the assistant is completely useless. What broke in your measurement? How do you fix it? `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Four Fatal Evaluation Blind Spots**:
  1. **Evaluation Dataset Distribution Skew**: The evaluation benchmark is flooded with 80% trivial queries ("What is the office Wi-Fi?"), masking failures on the 20% complex, high-stakes edge cases that real users struggle with.
  2. **Faithful but Unhelpful (Vacuous Compliance)**: The model faithfully summarizes irrelevant context snippets. Because it didn't hallucinate, Faithfulness is 1.0, but the user's question remains completely unanswered.
  3. **Critical Negative Omissions**: The model answers accurately but omits a single vital constraint ("Refunds are only valid within 7 days"), invalidating the response.
- **Remediation**:
  - Shift from academic text-matching to **Task Actionability & Resolution Rate**.
  - **Stratified Hard-Slice Benchmarking**: Break the test suite into distinct difficulty slices (e.g., Multi-hop queries, Conflicting documents, Edge-case complaints) and report scores per slice.
  - Establish monthly calibration sessions with support representatives to audit real-world failures.
</details>

#### Q46 Design a human-in-the-loop (HITL) review workflow for a customer-facing RAG assistant. What gets reviewed, who reviews it, and how does feedback flow back into the system? `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Closed-Loop HITL Architecture**:
  1. **Trigger Criteria (Selective Routing)**:
     - Automated triggers: Faithfulness score $< 0.8$, low retrieval confidence, safety guardrail alerts, transactions exceeding $\$100$.
     - User triggers: Explicit thumbs-down or rapid support escalation.
  2. **Tiered Reviewers**:
     - *Tier 1 (Customer Support Specialists)*: Triage operational and conversational quality daily.
     - *Tier 2 (Legal / Domain Experts)*: Bi-weekly audit of compliance-sensitive responses.
  3. **Data Flywheel Feedback Loops**:
     - *Short-Term*: Human-corrected answers are instantly upserted into an FAQ Cache for immediate lookup.
     - *Medium-Term*: Retrieval failures are used to optimize chunking boundaries and fine-tune the cross-encoder reranker.
     - *Long-Term*: Verified question-answer pairs are added to the Golden CI Regression Benchmark.
</details>

#### Q47 Your financial assistant occasionally generates incorrect numbers (e.g., citing revenue growth as 14% when the retrieved 10-K report states 12.4%), even when the correct table was retrieved. How do you detect and eradicate numerical hallucinations? `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Root Cause**: Spatial token misalignment when parsing complex tables, coupled with standard autoregressive next-token sampling errors on dense numerical digits.
- **Eradication Strategy**:
  1. **Structured Input Ingestion**: Ingest financial tables as structured Markdown or JSON with explicit column/row headers prepended to every cell.
  2. **Offload Arithmetic to Code Execution**: Prohibit the LLM from performing math in natural language. Route calculation queries to a sandboxed Python (Pandas) interpreter.
  3. **Deterministic Numerical Post-Processor**:
     - Regex-extract all numbers and percentages from the model's generated response.
     - Verify that every extracted number exists either verbatim in the retrieved context or matches the output of a deterministic tool execution.
     - Intercept and regenerate any response containing ungrounded numbers.
</details>

#### Q48 Design an observability architecture for a RAG system so that any bad response can be debugged in minutes, and business stakeholders can track quality trends. `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **End-to-End Observability Stack (OpenTelemetry / OpenInference)**:
  1. **Unified Trace Graph**:
     - Every request generates a unique `Trace_ID` tracking: `Raw Query` -> `Rewritten Query` -> `Retrieved Chunk IDs & Scores` -> `Reranked Chunks` -> `Prompt Payload` -> `LLM Tokens` -> `Guardrail Verdict`.
  2. **Rapid 3-Minute Triage Workflow**:
     - Step 1: Open the trace; inspect top 3 reranked chunks. Did retrieval capture the answer? (30 seconds to isolate search vs model).
     - Step 2: Check prompt token counts to verify context wasn't truncated.
     - Step 3: Check generation log-probabilities to detect model uncertainty.
  3. **Executive & Operational Dashboards**:
     - Track business trends: Daily Query Volume, First-Contact Resolution, p95 Latency, Thumbs-Down Rate, and Top-10 Drifted Topics.
</details>

#### Q49 Design a guardrail framework for a customer-facing RAG assistant: what runs pre-retrieval, between retrieval and generation, and post-generation? How do you control latency and false positives? `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Three-Stage Guardrail Lifecycle**:
  1. **Pre-Retrieval Guard (< 30ms)**:
     - PII Masking (redact SSNs, credit cards).
     - Adversarial Prompt Injection & Jailbreak Detection (heuristic regex + lightweight ONNX classifier).
     - Topic / Out-of-Bounds Rejection.
  2. **Mid-Retrieval Guard (< 40ms)**:
     - Document Security Scrubbing (ensure retrieved context contains no leaked internal secrets).
     - Context Relevance Threshold Gate (trigger graceful refusal if retrieval confidence $< 0.4$).
  3. **Post-Generation Guard (< 80ms)**:
     - Output Grounding & Hallucination Check.
     - Brand / Competitor Keyword Filtering & PII De-anonymization.
- **Latency & False-Positive Controls**:
  - Run small, quantized guard models (e.g., Llama-Guard-1B) resident in GPU memory.
  - Implement an enterprise whitelist for verified internal terminology to minimize false-positive refusals.
</details>

#### Q50 【Comprehensive System Design】You are building a RAG assistant for clinicians or lawyers where wrong answers have severe real-world consequences. Design the end-to-end grounding, evaluation, and safety architecture, and state what you would refuse to automate. `(Advanced)`
<details>
<summary>💡 <b>Comprehensive System Design Deep Dive</b></summary>

```
[Peer-Reviewed Clinical / Legal Repositories] (Clinical Guidelines, Statutes, Case Law)
      │
      ▼ (Cryptographic Version Signing & Daily Auditing)
[Strict Layout Ingestion & Knowledge Graph] ──> [Entity Alignment (UMLS / Legal Lexicon)]
                                                        │
[Verified Professional User] ──> [MFA & Role-Based Access Control Gate]
      │
      ▼
[Pre-Retrieval Guard (Emergency / Acute Hazard Blocker)]
      │
      ▼
[Deterministic Multi-Hop Search] (Knowledge Graph Traversal + Dense/Lexical Hybrid Search)
      │
      ▼
[Evidence-Grade Reranker] (Prioritizes Level-1 Double-Blind Trials / Supreme Court Precedents)
      │
      ▼
[Constrained Generation Engine]
- Strict Grounding: Citations required for every clinical/legal assertion
- Abstention Mandate: Prohibits speculative extrapolations beyond provided evidence
      │
      ▼
[Post-Generation Dual Verification (Deterministic Checker + NLI Validator)]
- 100% Entailment required
- Numerical & Dosage zero-tolerance audit
      │
      ▼
[Copilot Interface Display]
- Highlights source passages side-by-side
- Explicit confidence scores displayed
- MANDATORY HUMAN EXPERT SIGN-OFF REQUIRED
```

- **Core Architectural Pillars**:
  1. **Evidence-Grade Grounding**: Chunks are tagged with formal evidence tiers (e.g., Level A: Systematic Reviews vs Level D: Expert Opinion). The model must cite the evidence tier alongside every recommendation.
  2. **Zero-Tolerance Regression Testing**: 500 multi-specialty cases audited by medical/legal boards with a strict 0% tolerance for ungrounded assertions.
- **What to Refuse to Automate (Non-Negotiable Red Lines)**:
  1. **Direct Prescription Issuance & Autonomous Filings**: The AI must operate strictly in **Copilot Mode**. Final actions require verified human practitioner digital signatures.
  2. **Emergency Triage Decisions**: Queries indicating acute life-threatening symptoms (e.g., chest pain, suicidal ideation) must instantly bypass the LLM and display direct emergency hotline dispatch information.
  3. **Off-Label Extrapolations**: The system must refuse to deduce novel drug combinations or unverified legal loopholes not explicitly documented in verified literature.
</details>
"""

part4 = """
## Part 4: AI Agents, Tool Calling & Multi-Agent Systems (Q51–Q65)

#### Q51 The team wants to "turn our customer support bot into an Agent." Currently, it follows a fixed pipeline: classify, retrieve, answer. How do you evaluate whether you actually need an autonomous agent loop? `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Deterministic Workflows vs Autonomous Agent Loops**:
  - *Keep the Fixed Pipeline (Say NO to Agents)*:
    - If task branches are predictable (e.g., FAQ lookup, track package, issue refund under fixed rules).
    - If strict latency (<2s), low token cost, and 100% predictability are paramount. Turning this into a ReAct loop adds 3x–5x latency and token overhead with the risk of uncontrolled tool flapping.
  - *Adopt an Autonomous Agent Loop (Say YES to Agents)*:
    - **Dynamic Discovery**: The next action depends entirely on the unpredictable output of the previous action (e.g., query user account -> inspect 3 flagged transactions -> query fraud scoring API -> decide whether to pull shipping logs).
    - **Self-Correcting Tool Recovery**: The system must inspect API error responses, adapt parameters, and retry alternate pathways autonomously.
</details>

#### Q52 Your Agent has 12 tools, but ~15% of the time it picks the wrong tool or hallucinates malformed parameters. How do you diagnose and fix this? `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Diagnostic Root Causes**: Overlapping tool descriptions, missing parameter typing/enums, and attention dilution caused by stuffing 12 tool schemas into every prompt.
- **Production Remediation**:
  1. **High-Contrast Tool Descriptions**: Rewrite docstrings to clearly contrast boundaries: specify *"When to use"*, *"When NOT to use"*, and provide canonical parameter examples.
  2. **Strict Pydantic / JSON Schema Constraints**: Enable Strict Mode in tool calling. Enforce explicit Enums for categorical arguments (e.g., `status: Literal['pending', 'shipped']`), mathematically eliminating malformed arguments.
  3. **Two-Stage Hierarchical Tool Selection**: Do not provide all 12 tools at once. First run a fast classifier to select the tool domain (e.g., `Order Management`), then inject only the 3 tools relevant to that domain.
  4. **Self-Correction Interceptor**: When parameter validation fails, pass the Pydantic `ValidationError` directly back into the agent loop for single-turn parameter repair.
</details>

#### Q53 A customer support Agent repeatedly calls the same `lookup_order` tool with identical parameters, burning tokens until it times out. How do you debug this and guarantee loops can never run out of control? `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Root Cause**: The tool returned an empty payload or a generic error string. The LLM misinterprets this as an intermittent failure rather than "record not found," repeatedly retrying. Alternatively, context management bugs failed to append the tool's previous observation into the conversation history.
- **Three-Tier Hard Runtime Circuit Breakers**:
  1. **Action Fingerprinting**:
     - Maintain an in-memory hash ring of recent actions: `hash(tool_name + sorted_args)`.
     - If the identical action is observed **twice in succession**, the execution runtime intercepts the call and injects a hard observation: *"System Warning: You have executed this exact tool call twice with no new result. Do not call this tool again. Ask the user for more details or escalate."*
  2. **Hard Step and Token Budget**: Impose an inviolable ceiling (e.g., maximum 6 tool iterations and a $0.15 token budget per turn).
  3. **Graceful Escalation Fallback**: Catch budget exhaustion exceptions and automatically trigger a graceful handover to a human support agent.
</details>

#### Q54 How would you evaluate an AI Agent that books travel, fills out forms, and sends emails on behalf of users? Evaluating only the final answer is obviously insufficient. `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Comprehensive 4-Dimensional Agent Evaluation Matrix**:
  1. **Trajectory & Step Efficiency**:
     - Measure path optimality: Did the agent take 4 steps when 2 were sufficient? Ratio of redundant or failed tool invocations.
  2. **Side-Effect Safety & Invariance**:
     - Evaluate adherence to authorization boundaries: Did the agent execute irreversible actions (e.g., charge card, send public email) without explicit user confirmation?
  3. **Resilience & Error Recovery**:
     - Inject simulated API failures (429s, 500s, malformed responses) into a sandbox environment; test if the agent retries gracefully or crashes.
  4. **State Machine Goal Completion**:
     - Measure deterministic state verification in a mock sandbox: Was the flight actually booked with the requested parameters in the database?
</details>

#### Q55 Your Agent can issue refunds, modify subscriptions, and send emails. Design a permission model and approval workflow so that model mistakes or prompt injections cannot cause catastrophic harm. `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Principle of Least Agency & Two-Phase Execution**:
  1. **Operation Tiering**:
     - *Tier 1 (Read-Only)*: Search orders, view policies -> Fully autonomous.
     - *Tier 2 (Low-Risk Reversible)*: Address update, small refund $< \$25$ -> Autonomous within daily account rate limits.
     - *Tier 3 (High-Risk Irreversible)*: Refunds $> \$25$, cancellation, external emails -> **Human-in-the-Loop (HITL) Approval Required**.
  2. **Proposal-Execution Pattern (Two-Phase Commit)**:
     - The Agent can only draft a **Proposal Object** (e.g., `RefundProposal(amount=75, reason="late")`).
     - The proposal triggers an interactive UI approval card for the user or human agent.
     - Only upon human cryptographic confirmation does the trusted backend execute the actual API transaction.
  3. **Credential Sandboxing**: The LLM runtime never possesses database write keys or payment gateway tokens.
</details>

#### Q56 A research Agent executing 10+ step workflows consistently fails around step 7: either drifting from the goal or compounding earlier errors. How do you redesign it? `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Root Causes**:
  - *Goal Drift*: As intermediate tool outputs fill the context window, the original user goal is pushed out of active attention.
  - *Error Compounding*: An unverified assumption in step 3 becomes accepted as ground truth in step 6.
- **Architectural Redesign (Plan-and-Solve / Supervisor Pattern)**:
  1. **Decouple Planning from Execution**:
     - **Planner Agent**: Generates a structured execution DAG (Directed Acyclic Graph) of independent sub-tasks.
     - **Worker Agent**: Dispatched to execute one atomic step at a time with clean, scoped context.
  2. **State & Goal Anchoring**: Permanently anchor the primary objective, current step index, and verified outputs in a fixed system banner injected on every turn.
  3. **Independent Verifier / Critic Node**: After each milestone step, a dedicated Critic agent validates outputs against ground truth before allowing the workflow to advance.
</details>

#### Q57 Your personal assistant Agent must remember user preferences across sessions, track progress across long tasks, and avoid recalling obsolete facts. Design its memory architecture. `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Three-Tier Hybrid Memory Architecture (Mem0 / LangMem Principles)**:
  1. **Short-Term Working Memory**: Active conversation buffer with rolling summarization and explicit scratchpad tracking.
  2. **Long-Term Semantic & Episodic Memory**:
     - Asynchronously extract structured entity-relationship facts: `<User, DietPreference, Vegan>` with creation timestamps and confidence scores, indexed in a vector store and relational graph.
  3. **Memory Invalidation & Temporal Decay**:
     - When a user states *"I started eating meat again"*, run contradiction detection to locate existing conflicting memories and mark the older memory as `deprecated`.
     - Apply an Ebbinghaus decay function to deprioritize infrequently accessed non-core memories during retrieval.
</details>

#### Q58 A colleague proposes building a multi-agent system with Planning, Research, Coding, and Reviewing agents for an analytics tool. How do you evaluate whether this is superior to a single agent with tools? `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **The Multi-Agent Tax**: Multi-agent setups exponentially increase token consumption, introduce inter-agent communication latency, complicate debugging, and risk deadlocks.
- **When Multi-Agent is Truly Justified**:
  1. **Disjoint Model Specialization**: The coder requires a dedicated fine-tuned coding model, while the reviewer requires a long-reasoning model with strict compliance prompts.
  2. **Unbiased Adversarial Auditing**: The reviewer must evaluate code without being biased by the coder's intermediate scratchpad rationale.
  3. **Parallelizable Sub-tasks**: Multiple research agents can explore 5 disjoint data sources concurrently, reducing wall-clock time.
- **Evaluation Methodology**: Benchmark the multi-agent system against a single-agent baseline on identical tasks, measuring: Task Success Rate, End-to-End Latency, Total Token Cost, and Failure Modes. Only adopt if success gains substantially outweigh the cost and latency overhead.
</details>

#### Q59 Your Agent's per-task cost varies wildly: median is $0.04, but p95 is $1.20. Finance demands predictable spend. How do you rein in long-tail costs without degrading task success? `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Root Causes of p95 Cost Spikes**: Unchecked tool iteration loops, overly verbose tool payloads, and aggressive reflection cycles.
- **Cost-Containment Engineering**:
  1. **Dynamic Task Step Budgets**: Cap total iterations at 5 steps for standard queries; require explicit user confirmation to continue if an agent projects exceeding budget thresholds.
  2. **Early-Exit Information Gain Heuristics**: If consecutive tool calls yield $< 15\%$ novel tokens, terminate retrieval and force the agent to summarize existing findings.
  3. **Model Cascading**: Execute initial planning and simple queries using cost-effective models (e.g., GPT-4o-mini / Claude 3.5 Haiku). Escalate to frontier models only when task complexity scores or validation failures trigger an escalation.
  4. **Tool Output Payload Compression**: Filter and truncate verbose JSON API payloads before returning observations back into the agent context.
</details>

#### Q60 An Agent execution fails at step 14 with a confident but completely wrong answer. Walk through your investigation using traces and outline the required observability prerequisites. `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Observability Prerequisites**:
  - Full execution DAG tracing (e.g., LangSmith, Phoenix, Langfuse) capturing: `Step Index`, `Agent State Snapshot`, `Prompt & Completion Tokens`, `Tool Invocation Parameters`, `Tool Raw Output`, and `Latency per Step`.
- **Four-Step Post-Mortem Investigation**:
  1. *Locate the Divergence Point*: Step backward from Step 14 to locate the exact step where the agent formed an incorrect premise or invoked an irrelevant tool.
  2. *Inspect Tool Observation Payload*: Determine whether the tool returned corrupted/misleading data or if the tool output was accurate but misinterpreted by the LLM.
  3. *Audit Context Management*: Verify whether critical user constraints were truncated or dropped from the prompt prior to the point of divergence.
  4. *Codify into Regression Test*: Convert the failure trace into a deterministic replay test to validate architectural or prompt fixes.
</details>

#### Q61 Your email-sorting Agent reads incoming emails and can forward, label, and reply. A security researcher shows that an email with hidden text causes the Agent to forward sensitive threads to an external address. How do you defend against indirect prompt injection? `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Core Threat: Indirect Prompt Injection**: Untrusted external data (email body) hijacks the control flow of the privileged LLM.
- **Defense-in-Depth Architecture**:
  1. **Privilege Separation (Dual-LLM Architecture)**:
     - *Reader LLM (Untrusted)*: Reads the raw email and extracts purely structured, non-executable data fields (sender, sanitized summary). It has zero access to tools.
     - *Controller LLM (Privileged)*: Receives the sanitized structured data and decides on actions. It never inspects the raw untrusted email text directly.
  2. **Deterministic Action Egress Whitelist**: Hardcode programmatic checks: the forward tool enforces a strict company domain whitelist (`@company.com`), blocking external forwarding attempts regardless of LLM instructions.
  3. **Syntactic Isolation**: Wrap untrusted email bodies in explicit isolation tags: `<untrusted_content>` with strict system instructions treating enclosed tokens strictly as string data.
  4. **Mandatory Human-in-the-Loop Confirmation**: High-risk actions (forwarding threads externally) require explicit user sign-off.
</details>

#### Q62 Your Agent depends on five internal and third-party APIs. Last week, one API experienced intermittent timeouts, causing the Agent to hang or execute duplicate transactions. Design the tool reliability layer. `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Tool Execution Reliability Middleware**:
  1. **Strict Idempotency Keys**:
     - Generate a deterministic idempotency key for all state-mutating actions: `key = hash(session_id + step_index + action_name)`.
     - Downstream APIs reject duplicate requests, preventing double-billing or duplicate shipments.
  2. **Circuit Breakers & Timeouts**:
     - Wrap external tool calls with strict per-tool timeouts (e.g., 3s).
     - Implement a circuit breaker (e.g., open after 3 consecutive failures); when open, short-circuit immediately with a structured error: `{"status": "SERVICE_UNAVAILABLE"}`.
  3. **Exponential Backoff with Jitter**: Implement automatic retries for transient HTTP errors (429, 503) at the tool execution middleware layer without consuming LLM agent turns.
  4. **Compensating Transactions (Saga Pattern)**: Provide compensating rollback tools (e.g., `cancel_reservation`) if a multi-step sequence fails midway.
</details>

#### Q63 The company wants to expose 200 internal tools to Agents via the Model Context Protocol (MCP). Stuffing all 200 definitions into every prompt is impossible. Design tool discovery, selection, and governance. `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Three-Tier Dynamic Tool Discovery & Governance Architecture**:
  1. **Tool Registry & Semantic Index**:
     - Maintain an enterprise MCP Tool Registry with rich metadata, capability docstrings, and query exemplars per tool.
     - Embed tool descriptions into a semantic vector store.
  2. **Two-Stage Dynamic Tool Retrieval**:
     - Upon receiving a user request, query the tool vector index to select the top 3–5 most relevant tools.
     - Dynamically bind only these selected schemas into the LLM prompt for that turn.
  3. **Hierarchical Specialist Sub-Agents**:
     - Partition 200 tools across domain-specific agents (e.g., DevOps Agent, HR Agent, Billing Agent), each managing 10–15 tools. A top-level Router Agent classifies intent and delegates to the appropriate specialist.
  4. **Role-Based Access Control (RBAC)**: Filter tool availability dynamically based on the verified user JWT, ensuring unauthorized tools are never exposed.
</details>

#### Q64 You are building a data analysis Agent that writes and executes Python code against customer data. Design an execution environment and evaluation framework that is both useful and secure. `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Secure Sandboxed Execution Environment**:
  1. **MicroVM / Container Isolation**: Run code in ephemeral, isolated sandboxes (e.g., gVisor, Firecracker, or Docker with seccomp profiles). Destroy sandboxes after execution.
  2. **Zero Network Egress (Air-Gapping)**: Block all outbound internet access (`--network none`) to prevent data exfiltration.
  3. **Resource & Execution Quotas**: Enforce strict cgroup limits (e.g., 1 CPU core, 1GB RAM, 10s execution timeout) to neutralize infinite loops or fork bombs.
  4. **Static AST Analysis**: Parse generated Python AST before execution to ban dangerous modules (`os`, `sys`, `subprocess`, `socket`, `eval`).
  5. **Ephemeral Read-Only Data Mounts**: Mount data files as read-only volumes, writing temporary outputs to a transient in-memory `tmpfs`.
- **Evaluation Framework**: Measure code generation accuracy on a sandboxed benchmark evaluating syntactic correctness, execution success rate, and statistical accuracy.
</details>

#### Q65 【Comprehensive System Design】Design a production customer support Agent for an e-commerce company handling 100,000 daily conversations. It can check orders, issue refunds under defined limits, and escalate to human agents. Detail architecture, evaluation, rollout, and ops. `(Advanced)`
<details>
<summary>💡 <b>Comprehensive System Design Deep Dive</b></summary>

```
[Customer Inbound Message] (Web / Mobile App / Messaging Channels)
      │
      ▼
[API Gateway & Rate Limiter] ──> [Pre-Flight Security: PII Redaction & Fraud Check]
      │
      ▼
[Session State Store (Postgres / Redis)] ──> Ingest History + User Profile + Active Order
      │
      ▼
[Customer Support Agent Brain (vLLM / Frontier LLM Engine)]
      │
      ├──> [Secure Tool Orchestration Runtime]
      │         │
      │         ├── Order Lookup (Cached Read Replica)
      │         ├── Issue Refund (Strict Policy: Amount <= $50 & Window <= 7 days)
      │         └── Policy RAG (Returns Verified Knowledge Passages)
      │
      ├──> [Runtime Safety Guardrails (Max 4 Steps, Action Fingerprint Deduplication)]
      │
      ▼
[Output Routing & Dispatcher]
      │
      ├──> [Autonomous Resolution (Streamed to Customer via SSE)]
      │
      └──> [Escalation Trigger Met (Refund > $50 / Sentiment Alert / Loop Break)]
                 │
                 ▼
      [Human Agent Console (Pre-filled with Context, Summary & Draft Actions)]
```

- **Architectural Pillars**:
  1. **Bounded Agency & Financial Guardrails**: The Agent can autonomously issue refunds up to $\$50$ for delivered items within a 7-day window. All requests $> \$50$ or involving flagged fraud profiles automatically route to human queues with pre-filled investigation summaries.
  2. **Loop Prevention & Circuit Breakers**: Actions are fingerprinted; duplicate consecutive calls are rejected. Strict 4-step execution limit per turn before graceful human handoff.
  3. **Four-Stage Safe Rollout Strategy**:
     - *Shadow Mode (Week 1–2)*: Agent monitors live human support chats, generating draft responses in the background to benchmark resolution concordance.
     - *Internal Dogfooding (Week 3)*: Deployed exclusively to internal employee test accounts.
     - *Canary Traffic (Week 4–5)*: Route 5% -> 20% of low-risk categories (e.g., "Where is my order?").
     - *Full Rollout with Circuit Breakers (Week 6+)*: 100% enablement with automated kill-switches.
  4. **Operational SLAs**: p95 TTFT $< 1.2\text{s}$, Autonomous Resolution Rate $\ge 72\%$, Unintended Escalation Rate $< 10\%$.
</details>
"""
