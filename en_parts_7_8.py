# en_parts_7_8.py

part7 = r"""
## Part 7: AI System Design & Production Reliability (Q86–Q95)

#### Q86 No one deployed anything for three weeks, but thumbs-down feedback on your RAG assistant has been steadily climbing. Management wants to know what broke. How do you investigate? `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Core Invariant: Zero code deployments does NOT mean zero system changes!**
- **Four Diagnostic Vectors for Silent Degradation**:
  1. **Knowledge Base Drift & Corpus Churn**:
     - Did upstream data synchronization scripts ingest corrupted documents, delete critical reference pages, or introduce orphan vector chunks? Inspect vector database changelogs.
  2. **User Query Distribution Shift**:
     - Has the business launched a new product, updated pricing, or changed promotions? Users are asking about new concepts that do not yet exist in the knowledge base, triggering silent factual refusals or hallucinations. Cluster thumbs-down queries to surface novel intent topics.
  3. **Silent Provider Model Updates**:
     - If using a floating commercial model alias (e.g., `gpt-4o` rather than a pinned snapshot like `gpt-4o-2024-08-06`), provider-side updates frequently shift alignment behavior, verbosity, and refusal thresholds without warning.
  4. **Infrastructure & Index Degradation**:
     - Check if vector database index segmentation or memory fragmentation caused retrieval recall drops.
</details>

#### Q87 Define SLOs for an LLM-powered customer service assistant. Management wants a one-page report they can trust. What do you measure? When "quality" is part of the SLO, how does the error budget work? `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **One-Page Trustworthy AI SLO Specification**:
  1. **Operational Availability & Latency SLOs**:
     - *Availability*: $\ge 99.9\%$ HTTP success rate (status 200 within timeout).
     - *Latency*: p95 Time-To-First-Token (TTFT) $< 1.2\text{s}$; p95 Total Response Time $< 4.0\text{s}$.
  2. **Quality & Grounding SLOs**:
     - *Faithfulness*: $\ge 98.0\%$ of generated assertions grounded in retrieved context (audited weekly via stratified sample).
     - *Schema Validity*: $100\%$ valid JSON schema output for automated actions.
     - *First-Contact Resolution (FCR)*: $\ge 80\%$ of sessions resolved without human escalation within 24 hours.
     - *High-Severity Safety Violations*: $0\%$ tolerance.
- **How the "Quality Error Budget" Operates**:
  - The team is allocated a monthly budget for quality degradation (e.g., 2% defect rate on factual grounding or up to 50 bad-case escalations).
  - **Automated Freeze Policy**: If the quality error budget is exhausted ($100\%$ spent before month-end), all feature deployments and prompt updates are frozen. The team shifts 100% of engineering bandwidth to root-cause remediation, retrieval tuning, and updating the golden evaluation suite.
</details>

#### Q88 Your AI assistant depends on a vector DB, a reranker service, an LLM provider, and two internal APIs. Design graceful degradation when each dependency fails. `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Graceful Degradation Matrix**:
  - *Dependency 1: Reranker Service Fails*
    - **Fallback**: Bypass cross-encoder reranking entirely. Take the Top-5 results directly from the hybrid retrieval (BM25 + Dense) merged via Reciprocal Rank Fusion (RRF). Accuracy drops slightly (~3%), but latency actually improves by 100ms.
  - *Dependency 2: Vector Database Fails*
    - **Fallback**: Fall back to pure lexical search (Elasticsearch / PostgreSQL full-text search) using BM25. Continues serving exact keyword and SKU queries seamlessly.
  - *Dependency 3: Internal Order API Fails*
    - **Fallback**: The Agent catches the timeout, sets conversational state, and politely responds: *"I'm currently unable to access our order fulfillment database. Please check back in a few minutes, or reply with your tracking number and I will notify you."*
  - *Dependency 4: Primary LLM Provider Outage*
    - **Level 1**: Automatic failover at the gateway to a secondary backup provider within 1.5s.
    - **Level 2**: If all providers fail, degrade to static FAQ search with direct escalation queue links.
</details>

#### Q89 Eight product teams are running fragmented, ad-hoc LLM evaluations in notebooks. You are tasked with building a shared evaluation platform. What does it contain, and how do you prove it actually works? `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Enterprise Shared Evaluation Platform Core**:
  1. **Centralized Asset Hub**:
     - Versioned repository of Golden Datasets organized by domain and tagged with risk tiers.
     - Standardized evaluator library: Faithfulness (NLI), Context Recall, Semantic Similarity, and LLM-as-a-judge rubrics.
  2. **CI/CD Integration & Automation**:
     - CLI and GitHub Actions plugins: every PR changing a prompt or model config triggers an automated evaluation run, generating a side-by-side diff report directly on the pull request.
  3. **Human Calibration & Alignment Suite**:
     - Interactive annotation UI allowing domain experts to grade sample runs and track human-judge correlation ($\kappa$).
- **How to Prove the Platform Works (Impact Metrics)**:
  - *Adoption Rate*: Percentage of product teams integrating the CI gate into production deployments.
  - *Incident Reduction*: 50%+ reduction in production P1/P2 incidents caused by prompt or model regressions.
  - *Velocity*: Model upgrade evaluation cycle time reduced from 2 weeks of manual testing to 45 minutes of automated execution.
</details>

#### Q90 Design an insurance claim document pipeline: an LLM extracts fields and recommends approvals, with humans reviewing only cases that require review. Management wants high straight-through processing, but errors are expensive. `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Selective Classification & High-Confidence Straight-Through Pipeline**:
  1. **Dual Extraction Pipeline (Consensus Verification)**:
     - Medical bills and accident reports are processed concurrently by two distinct architectures: a multimodal visual document parser and an OCR + structured LLM extractor.
     - Any discrepancy in critical fields (Claim Amount, ICD-10 Diagnosis Codes, Policy ID) results in an immediate confidence score of 0, forcing human review.
  2. **Deterministic Business Rule Hard Gates**:
     - Extracted structured data is evaluated by a rules engine: Policy active status, claim within deductible boundaries, no duplicate claim hash within 90 days.
  3. **Calibrated Confidence Scoring Model**:
     - Compute composite confidence: $\text{Confidence} = \text{Token Log-Likelihood} \times \text{OCR Clarity Score} \times \text{Cross-Document Consistency}$.
     - **Straight-Through Threshold**: Automated approval is executed ONLY when $\text{Confidence} \ge 0.99$ AND $\text{Claim Amount} < \$500$.
  4. **Continuous Quality Sampling**: Randomly sample 5% of automated straight-through approvals for post-hoc human auditing to continuously calibrate confidence thresholds.
</details>

#### Q91 A screenshot of your assistant giving a confident, harmful, and incorrect response is going viral on social media. You are the Incident Commander. Detail your response during the first hour and the following week. `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **First 60 Minutes (Emergency Triage & Containment)**:
  - *0–15 mins (Triage)*: Locate the exact request trace via Trace ID or timestamp; verify whether the screenshot is authentic or fabricated.
  - *15–30 mins (Containment)*: Push an immediate hotfix blocklist rule at the API Gateway WAF/Guardrail layer to intercept the specific adversarial prompt pattern across all instances.
  - *30–45 mins (Blast Radius Audit)*: Query production logs to determine if this vulnerability was exploited by other sessions. If a widespread jailbreak vector is identified, toggle the feature to safe-refusal mode.
  - *45–60 mins (Communications)*: Provide PR and Legal with verified technical facts: root-cause trigger, impact scope, and confirmation that the vulnerability is actively mitigated.
- **The Following Week (Systemic Hardening & Root-Cause Remediation)**:
  - *Days 2–3*: Conduct a deep-dive technical investigation: Why did the system prompt, retrieval guardrails, and output moderation layers all fail?
  - *Days 4–5*: Add the exploit and 200 adversarial variations to the automated Red Teaming regression test suite; update output safety classifiers.
  - *Days 6–7*: Publish an internal Blameless Post-Mortem (COE) detailing timeline, architectural gaps, and preventative action items.
</details>

#### Q92 Your LLM application launches to 2 million users next month. How do you conduct load testing and capacity forecasting prior to launch? `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Realistic Load Testing & Capacity Planning**:
  1. **Construct a Representative Workload Distribution**:
     - Never load test with static "Hello world" requests! LLM latency is dominated by input prompt length and output token generation counts.
     - Synthesize a test pool mirroring real usage: 20% short single-turn queries, 50% medium RAG queries (2k input / 300 output), 30% complex multi-turn/code generations.
  2. **Stepped Load Testing (Locust / K6)**:
     - Ramp up concurrent users: 50 -> 200 -> 1,000 -> 3,000 users.
     - Monitor the "Knee Point": The saturation point where throughput plateaus and p95 TTFT and inter-token latency spike exponentially.
     - Track GPU KV cache utilization factor and provider 429 rate limit thresholds.
  3. **Capacity Forecasting & Quota Reservation**:
     - Model peak QPS based on diurnal traffic curves.
     - If using commercial APIs, submit enterprise quota increase requests and negotiate Provisioned Throughput (PTUs) 3 weeks in advance.
     - If self-hosting, provision GPU nodes with an N+2 redundancy buffer and configure predictive autoscaling.
</details>

#### Q93 Management wants to leverage production conversations to improve the assistant, curating golden evaluation sets and fine-tuning data. Design the data flywheel without introducing privacy or quality regressions. `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Privacy-Preserving Production Data Flywheel Pipeline**:
  1. **Explicit User Consent & Opt-In**: Embed clear data improvement policies into Terms of Service; provide an effortless opt-out toggle in user settings.
  2. **Automated Multi-Stage PII Sanitization**:
     - Production logs pass through high-precision NER models (e.g., Presidio) and custom regex rules to strip names, emails, credit cards, and addresses before entering the data lake.
  3. **Quality Curation & Stratified Sampling**:
     - Discard trivial pleasantries and uninformative 1-turn interactions.
     - Sample from high-signal interactions: sessions with explicit positive user feedback, conversations resolving complex multi-turn issues, and transcripts corrected by human agents.
  4. **Expert Audit & Golden Baseline Promotion**:
     - Route 10% of curated samples to human domain experts for quality and safety verification.
     - Verified samples are divided into two isolated tracks: **Automated CI/CD Evaluation Benchmarks** and **SFT/DPO Fine-Tuning Corpora**.
</details>

#### Q94 Your "Deep Research Report" feature runs an LLM workflow taking 5 to 15 minutes, calling multiple tools. Workflows frequently crash midway, losing all progress. Design a reliable execution architecture. `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Core Rule: Never manage long-running multi-step workflows over fragile synchronous HTTP connections!**
- **Durable Execution Engine Architecture (Temporal / Cadence Pattern)**:
  1. **Asynchronous Task Dispatch & Durable Execution**:
     - The client triggers the research job and receives an immediate `task_id`; client communication switches to WebSocket / polling.
     - Orchestrate the workflow using a durable execution framework (e.g., Temporal).
     - Each research phase (Search, Scrape, Analyze, Outline, Draft) is modeled as a discrete, idempotent Activity.
  2. **Automatic State Checkpointing**:
     - The inputs, outputs, and intermediate scratchpad states of every step are persisted to reliable storage.
  3. **Checkpoint Resumption & Retries**:
     - If a tool times out at step 7, the system **never re-runs steps 1 through 6**.
     - Temporal automatically executes exponential backoff retries on step 7 alone; once resolved, the workflow resumes execution smoothly.
  4. **Transparent Progress Telemetry**: Stream structured milestone events to the user interface: `{"status": "Synthesizing competitor matrix (Step 4/8)"}`.
</details>

#### Q95 【Comprehensive System Design】Design an AI code review assistant that comments on pull requests for 2,000 software engineers. Cover architecture, evaluation, rollout, and how to maintain engineer trust. `(Advanced)`
<details>
<summary>💡 <b>Comprehensive System Design Deep Dive</b></summary>

```
[GitHub / GitLab Webhook] (PR Opened / Synchronize Event)
      │
      ▼
[PR Context Assembler Service]
      │
      ├── 1. Filter trivial files (lockfiles, generated code, minified assets, markdown)
      ├── 2. Extract git diff + 15 lines of surrounding context
      ├── 3. Fetch static analysis outputs (Linter, SonarQube, Compiler errors)
      └── 4. Retrieve internal architectural style guides via RAG
                 │
                 ▼
[AI Review Orchestration Engine]
      │
      ├──> [Specialized Coding LLM (DeepSeek-Coder / Claude 3.5 Sonnet)]
      │         │
      │         ▼
      │    [Candidate Review Comments Generated]
      │         │
      │         ▼
      └──> [High-Precision Verifier Gate (CRITICAL FOR TRUST)]
           - Precision over Recall filter: Discard low-confidence suggestions
           - Ban nitpicks: Reject comments on variable names, formatting, personal taste
           - Focus exclusively on: Concurrency bugs, Security vulnerabilities, Resource leaks
                 │
                 ▼
[GitHub API Commenter Service] ──> Posts inline comments on specific diff lines
```

- **How to Earn and Defend Engineer Trust (The Ultimate Battle)**:
  1. **"Precision over Recall" (Zero Tolerance for Nitpicks)**:
     - Engineers despise noisy bots that comment on whitespace, minor naming preferences, or generate false positives.
     - It is 10x better to miss 5 minor bugs than to post 1 hallucinated or pedantic critique.
     - Hardcode an exclusion list: formatting, variable names, and stylistic opinions are banned.
  2. **Focus Exclusively on High-Severity Flaws**:
     - Concurrency hazards (race conditions, unbuffered channels).
     - Security vulnerabilities (SQL injection, unescaped parameters, leaked secrets).
     - Performance anti-patterns (unindexed database queries inside loops, unclosed file descriptors).
  3. **Interactive Feedback & Self-Correction**:
     - Every PR comment features inline buttons: `[Helpful 👍]` and `[False Positive 👎]`.
     - Clicking "False Positive" instantly hides the comment and automatically deposits the code snippet into the engineering regression benchmark for model re-tuning.
</details>
"""

part8 = r"""
## Part 8: Security, Privacy, Governance & Cost Control (Q96–Q100)

#### Q96 Before launch, security mandates a threat model for your customer-facing LLM application. It uses RAG, renders Markdown, and calls three internal tools. What threats do you cover, and how do you test your defenses? `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Four Primary Threat Vectors (OWASP Top 10 for LLMs)**:
  1. **Indirect Prompt Injection**: Malicious instructions embedded inside retrieved documents hijack the LLM to execute unauthorized actions.
  2. **Data Exfiltration & Broken Object-Level Authorization (BOLA)**: The model is tricked into querying and returning data belonging to another user.
  3. **Excessive Agency / Parameter Tampering**: The LLM invokes tools with arbitrary, unvalidated arguments (e.g., passing another user's ID to issue a refund).
  4. **Stored Client-Side XSS via Markdown**: The model outputs unescaped HTML/JavaScript inside Markdown (e.g., `<script>` or `![img](javascript:alert(1))`) executed by the user's browser.
- **Defensive Testing & Verification**:
  - **Automated Adversarial Red Teaming**: Use tools like Garak and PyRIT to launch thousands of automated jailbreak and injection probes.
  - **DOMPurify Sanitization**: Enforce DOMPurify on the frontend before rendering Markdown, disabling raw HTML execution.
  - **Session-Bound Tool Authorization**: The tool layer must extract the `user_id` strictly from the cryptographically signed session token, completely ignoring any identity arguments passed by the LLM.
</details>

#### Q97 You are building an HR assistant that answers questions based on policy documents and lets employees query their personal profiles. A user submits a GDPR "Right to be Forgotten" deletion request. Design privacy controls across the entire system. `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **End-to-End Privacy & GDPR Erasure Compliance Architecture**:
  1. **Zero Personal Data in Model Weights (No PII in Weights)**:
     - Machine unlearning is mathematically unproven and unreliable in production. **Never train, pre-train, or fine-tune models on employee personal records.**
  2. **Single Source of Truth in Relational Database**:
     - Employee personal profile records live exclusively in an encrypted, ACID-compliant relational database accessed via read-only tools.
     - When a deletion request is processed, execute an immediate hard delete in the relational DB; subsequent tool queries return empty.
  3. **Vector Database Dynamic Filtering & Deletion**:
     - If internal knowledge base documents mention specific individuals, all vector chunks must carry an `employee_id` metadata tag.
     - Execute a `delete_by_filter: employee_id == target_id` to purge related vectors within seconds.
  4. **Log & Cache Scrubbing**:
     - Purge user conversation history from Postgres, flush cached conversation turns from Redis, and anonymize user identifiers in OpenTelemetry trace logs.
</details>

#### Q98 The company runs 30 distinct LLM features with zero centralized oversight. The board demands an AI governance framework that satisfies audits without crippling developer velocity. What is your proposal? `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Lightweight "Four Pillars" AI Governance Proposal**:
  1. **Centralized AI Gateway Architecture**:
     - Mandate that all 30 features route traffic through a unified internal AI Gateway.
     - Gateway centralizes compliance: PII masking, token logging, rate limiting, and security guardrails without burdening individual product teams.
  2. **Tiered Risk-Based Approval Matrix**:
     - *Tier 1 (Low Risk - Internal code assist, meeting summarizer)*: Zero human gatekeeping; automated CI security scan suffices for instant deployment.
     - *Tier 2 (Medium Risk - Read-only customer support)*: Requires passing standard automated Golden Evaluation benchmarks and security red-teaming.
     - *Tier 3 (High Risk - Automated financial actions, legal/medical advice)*: Requires formal cross-functional sign-off (Legal, Security, AI Staff Architect).
  3. **Living Model & Data Registry (Model Cards)**:
     - Maintain an automated catalog of all active models, data sources, prompt versions, and team owners.
  4. **Executive Compliance Dashboard**:
     - Real-time audit dashboard for leadership displaying company-wide spend, safety intercept counts, and SLA compliance.
</details>

#### Q99 Your monthly LLM bill tripled in six weeks, while user traffic only grew by 40%. The CFO demands an explanation by Friday, along with a plan to cut costs without hurting quality. What do you do? `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Phase 1: 48-Hour Forensic Accounting Investigation**:
  - *Vector 1: Prompt Caching Eviction*: Check if a recent commit added a dynamic variable (e.g., timestamp or random UUID) to the beginning of the system prompt, causing prompt cache hit rates to collapse from 85% to 0%.
  - *Vector 2: Unchecked Context Accumulation*: Inspect average input tokens per turn; did a team remove multi-turn context truncation limits, allowing chat histories to expand to 20k tokens?
  - *Vector 3: Runaway Agent Retry Storms*: Inspect trace logs for automated background jobs looping indefinitely.
- **Phase 2: The Friday Action Plan for the CFO (Commit to a 50% Reduction)**:
  1. **Quantified Explanation**: *"Our invoice tripled because a recent release broke prompt caching, causing a 6x surge in billable input tokens, alongside an unconstrained context window on Feature X."*
  2. **Four Concrete Cost-Cutting Remediations**:
     - **Restore Prompt Caching**: Move all dynamic variables to the end of prompts, restoring 85% cache hit rates (immediate 60% savings on input tokens).
     - **Multi-Tier Model Routing**: Route 70% of simple classifications to lightweight models costing 1/10th the price.
     - **Context Window Pruning**: Enforce sliding window truncation and rolling summarization.
     - **Hard Quotas & Budget Kill-Switches**: Assign departmental budget caps with automated Slack alerts at 80% spend and hard throttles at 100%.
</details>

#### Q100 【Comprehensive System Design · The Ultimate Final Boss】It's 2 AM on Halloween. Your multi-tenant Agent platform experiences an alarming cost surge while a client reports that the assistant cited confidential clauses from another company's contract. Lead the incident response and redesign the system so this can never happen again. `(Advanced)`
<details>
<summary>💡 <b>Ultimate War Room System Design & Root-Cause Redesign</b></summary>

```
                                [P0 Emergency War Room (2:00 AM Halloween)]
                                                     │
      ┌──────────────────────────────────────────────┴──────────────────────────────────────────────┐
      ▼                                                                                             ▼
[Immediate Triage: 0–15 Minutes]                                                              [Root-Cause Forensics: 15–60 Minutes]
1. Trigger Global Kill-Switch: Halt all autonomous agent tools                                1. Inspect distributed traces spanning tenant boundaries
2. Purge shared semantic vector caches & Redis cache partitions                               2. Audit vector DB filter query builder parameters
3. Degrade assistant to safe, non-retrieval polite conversational mode                         3. Identify whether Agent was caught in an infinite retry loop
      │                                                                                             │
      └──────────────────────────────────────────────┬──────────────────────────────────────────────┘
                                                     │
                                                     ▼
                             [Zero-Trust Architectural Hardening & Root-Cause Remediation]
                             - Database & Vector Storage Physical/Logical Namespace Isolation
                             - Cryptographic Tenant Binding for all Cache Keys: SHA256(tenant_id + query)
                             - CI/CD Automated Multi-Tenant Penetration Gates with Canary Tokens
```

- **Incident Commander War Room Playbook**:
  1. **First 15 Minutes (Emergency Triage & Bleeding Control)**:
     - *Action 1*: Declare a **P0 Severity Outage**; assemble Security, Platform, and Legal leads.
     - *Action 2*: **Halt Active Risk**: Deploy an immediate gateway configuration disabling all Agent tool execution and zeroing out RAG retrieval (gracefully degrade to basic conversational support).
     - *Action 3*: **Flush Shared Caches**: Evict all shared Redis semantic caches and vector caches to prevent dirty reads from leaking further data.
  2. **15–60 Minutes (Root-Cause Forensic Discovery)**:
     - *Data Breach Root Cause*: Investigate the vector query builder. A recent refactor accidentally omitted the mandatory `filter: {tenant_id: current_tenant}` clause in a concurrent retrieval path, executing cross-tenant searches over the shared index. Alternatively, the semantic cache key was hashed purely on query text without salting with `tenant_id`.
     - *Cost Surge Root Cause*: The Agent received confusing cross-tenant context, failed internal validation assertions, and entered an unconstrained retry storm, burning millions of tokens in minutes.
- **Root-Cause Architectural Hardening (Zero-Trust Multi-Tenancy)**:
  1. **Storage-Level Namespace & Driver Isolation**:
     - Ban weak application-level filtering. Enforce hard storage partitioning: Dedicated vector collections or database connection pools dynamically provisioned with tenant-scoped credentials.
  2. **Cryptographic Cache Key Salting**:
     - Mandate that all cache keys incorporate tenant identity at the driver level:
       $$\text{Cache\_Key} = \text{HMAC}(\text{tenant\_id}, \text{user\_role} + \text{normalized\_query})$$
       Missing tenant identifiers throw a fatal runtime exception.
  3. **Agent Triple-Safety Circuit Breaker**:
     - Hard limit of 5 iterations per task; action fingerprint deduplication; per-task hard financial budget of $\$0.50$ with automatic kill-switch.
  4. **Continuous Multi-Tenant Canary Penetration CI Gate**:
     - Plant synthetic honeytoken documents ("Canary Tokens") in Tenant B. On every build, automated red-team suites attempt to retrieve Tenant B's canary using Tenant A's credentials. Any retrieval match instantly fails the build and sounds critical alerts.
</details>
"""
