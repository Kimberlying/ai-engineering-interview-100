# en_parts_5_6.py

part5 = r"""
## Part 5: Fine-Tuning, Model Adaptation & Model Selection (Q66–Q75)

#### Q66 A product manager says: "Let's fine-tune a model on our company data so it knows our products." Walk through how you decide between prompt engineering, RAG, and fine-tuning. `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Core Industry Consensus**: **Fine-tuning teaches models *form, tone, syntax, and task behavior*—it is notoriously ineffective and unsafe for teaching *dynamic facts, knowledge, and business data*.**
- **Decision Matrix (Prompting vs RAG vs Fine-Tuning)**:
  1. **Prompt Engineering**:
     - *Use When*: Rapid prototyping, logic exploration, zero-budget initial MVP, tasks where general knowledge suffices.
  2. **RAG (Retrieval-Augmented Generation)**:
     - *Use When*: **Injecting proprietary company products, rapidly evolving policies, and factual knowledge**.
     - *Advantages*: Zero retraining cost, real-time knowledge freshness, strict verifiable citations, and immediate ACL access enforcement.
  3. **Fine-Tuning (SFT / LoRA)**:
     - *Use When*: Teaching a complex internal DSL, enforcing strict JSON schemas with 0% format errors, mimicking specialized brand voice, or **distilling a 70B model into a fast 8B model** to slash latency by 70% and costs by 80%.
  4. **The Winning Production Pattern**: Combine RAG with a fine-tuned small model (RAG retrieves current facts, fine-tuned 8B model structures output with flawless precision).
</details>

#### Q67 You have one 80GB GPU, an open-weights 7B–13B model, and one month to adapt it to your domain. Compare full fine-tuning, LoRA, and QLoRA, and outline your training schedule. `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Comparison on Single 80GB GPU (A100/H100)**:
  - *Full Fine-Tuning*: Infeasible for 13B on a single card. Storing weights (26GB in FP16), gradients (26GB), optimizer states (AdamW takes 8–16 bytes/param = ~104GB), and activation memory exceeds 80GB (OOM). Requires multi-GPU DeepSpeed ZeRO-3.
  - *LoRA (Low-Rank Adaptation)*: Freezes base model in BF16 (~26GB). Injects trainable rank-decomposition matrices into linear layers (rank 16–64, adding $< 1\%$ trainable parameters). Runs comfortably on 80GB with large batch sizes, stable convergence, and zero added inference latency post-merge.
  - *QLoRA (Quantized LoRA)*: Quantizes base weights to 4-bit NormalFloat (NF4, taking only ~8GB VRAM). Enables massive context windows and large batches on single card; slight 20% training speed penalty due to on-the-fly dequantization.
- **One-Month Engineering Training Plan**:
  - *Week 1 (Data Engineering - 70% of Success)*: Clean, curate, and deduplicate 3,000–5,000 high-quality domain input-output pairs.
  - *Week 2 (LoRA Baseline & Hyperparameter Sweep)*: Train BF16 LoRA (rank 32, alpha 64, target all linear modules), lr = $2\times 10^{-4}$, FlashAttention-2, gradient checkpointing.
  - *Week 3 (Automated Evaluation & Ablation)*: Track validation loss, run automated domain accuracy tests and general capability regression benchmarks.
  - *Week 4 (Weight Merging, Quantization & Serving)*: Merge LoRA weights into base model, export to AWQ / FP8, deploy on vLLM, and run load testing.
</details>

#### Q68 You have 8,000 customer support transcripts collected over two years to use for fine-tuning. Before training, how do you evaluate and improve data quality? `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **"Garbage In, Garbage Out" Systematic Data Cleansing**:
  1. **Temporal & Policy Audit**: Policies from 18–24 months ago are often obsolete. Filter transcripts against historical policy deprecation dates; purge invalid answers.
  2. **Semantic Clustering & Deduplication**: Embed all 8,000 samples. Cluster to detect redundant conversational filler (e.g., 2,500 repetitive "Where is my tracking number?" variants) and downsample to a diverse, balanced subset.
  3. **Automated PII Scrubbing**: Run Presidio / regex sanitizers to mask names, credit cards, emails, and phone numbers (`[CUSTOMER_NAME]`, `[PHONE]`).
  4. **Quality Scoring & LLM-Assisted Filtering**: Use an advanced LLM to score transcripts on resolution completeness, logical clarity, and tone. Filter out unresolved tickets, angry rants, or confusing agent workarounds.
  5. **Curate the Top 3,000 Golden Samples**: 3,000 flawless, diverse instruction pairs outperform 8,000 noisy, contradictory transcripts every time.
</details>

#### Q69 After domain fine-tuning, domain accuracy increases, but the model's ability to follow general instructions degrades, and it exhibits strange refusals. Diagnose and prevent this. `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Root Cause: Catastrophic Forgetting and Alignment Tax**: The narrow domain dataset overfits the network, warping the high-dimensional representation space learned during pre-training and RLHF.
- **Prevention and Remediation**:
  1. **General Data Replay (Experience Replay)**:
     - Mix in **15%–25% high-quality general-purpose instruction data** (e.g., OpenHermes, ShareGPT, or UltraChat subsets) into the domain dataset. This acts as an anchor preserving general conversational capability.
  2. **Constrain LoRA Scope**:
     - Avoid full fine-tuning; lower LoRA rank (e.g., from 128 to 32) and tune only key projection layers rather than all linear layers.
  3. **KL-Divergence Loss Penalty**:
     - Penalize divergence between the fine-tuned model's token distribution and the frozen base model's distribution on general tasks.
  4. **CI General Regression Testing**:
     - Mandate that fine-tuned checkpoints pass general benchmarks (e.g., IFEval, MMLU subset) with $< 2\%$ degradation before release approval.
</details>

#### Q70 The company must decide between managed frontier APIs and self-hosted open-weights models for a high-volume internal assistant. Detail your decision framework and evaluation plan. `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Five Pillars Decision Framework**:
  1. **Data Sovereignty & Compliance**: Is data legally permitted to traverse public cloud APIs? If handling classified defense, healthcare, or strict banking secrets, self-hosting is non-negotiable.
  2. **TCO Economic Crossover Point**:
     - At low-to-medium volumes (< 2M tokens/day), managed commercial APIs are drastically cheaper.
     - At sustained high volumes (> 50M tokens/day with steady load), self-hosting on dedicated GPUs (e.g., 8x H100 serving 70B models) achieves a lower marginal cost per million tokens.
  3. **Operational Overhead & Mental Taxes**: Factor in hardware procurement lead times, GPU driver updates, Kubernetes HPA, and 24/7 on-call engineering salaries.
  4. **Model Capability Gap**: Frontier proprietary models (Claude 3.5 Sonnet, GPT-4o) still outperform open 70B models on nuanced reasoning, coding, and multi-turn instruction adherence.
- **Execution Plan**: Run a 3-week dual-track PoC benchmarking real task accuracy, p95 latency under concurrent load, and true annual TCO (hardware depreciation + engineers vs API bills).
</details>

#### Q71 Your assistant uses a large foundation model, but costs are unsustainable at scale. Describe how you distill its behavior into a smaller model, and how you know the small model is good enough. `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **End-to-End Distillation Pipeline**:
  1. **Teacher Dataset Generation (CoT Distillation)**:
     - Pass 50,000 real domain user queries through the teacher model (e.g., GPT-4o / Claude 3.5 Sonnet).
     - Require the teacher to output step-by-step reasoning (Chain-of-Thought) followed by the final structured action/answer.
  2. **Student SFT Training**:
     - Fine-tune an open-weights 8B student model (e.g., Llama-3.1-8B or Qwen-2.5-7B) on the teacher's input-reasoning-output triplets using full-context supervised fine-tuning.
- **Verification of "Good Enough"**:
  1. **Concordance Rate (Teacher-Student Agreement)**: Measure whether the student's final decisions match the teacher's on a holdout test set (target $\ge 95\%$).
  2. **Task Resolution & Business Metrics**: Run an A/B test verifying that customer task completion rates and CSAT scores show no statistically significant drop.
  3. **Economic Validation**: Confirm inference latency drops by $\ge 60\%$ and serving costs drop by $\ge 80\%$.
</details>

#### Q72 Customers report that your assistant's tone is inconsistent and overly verbose. You have thousands of production responses with thumbs-up and thumbs-down feedback. Would you use preference tuning (DPO or RLHF)? How do you do it safely? `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Decision: Direct Preference Optimization (DPO)**: Choose DPO over traditional PPO-RLHF. DPO is mathematically equivalent to RLHF but optimizes the policy directly via implicit reward formulation, eliminating the instability of training a separate reward model and managing complex reinforcement learning loops.
- **Safe Implementation Blueprint**:
  1. **Preference Pair Construction ($Y_w, Y_l$)**:
     - Formulate pairs for the exact same prompt: $Y_w$ (Chosen: concise, helpful thumbs-up response) and $Y_l$ (Rejected: verbose, rambling thumbs-down response).
     - Filter out pairs where downvotes were caused by backend 500 errors or incorrect retrieval data; isolate purely stylistic and tonal variance.
  2. **Conservative Regularization ($\beta$)**:
     - Set DPO temperature parameter $\beta = 0.1$, preventing the policy from drifting too far from the reference model to avoid linguistic collapse.
  3. **Verbosity Guardrails**:
     - Monitor average completion token length during evaluation. Prevent the model from swinging to the opposite extreme—becoming so curt that it omits necessary context.
</details>

#### Q73 Your Agent must generate valid tool calls and structured JSON, but a prompt-driven model has a ~6% failure rate on complex nested schemas. Would you fine-tune for this? How do you evaluate the outcome? `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Hierarchy of Interventions: Constrained Decoding First, Fine-Tuning Second**:
  - *Step 1*: Before fine-tuning, enable **Grammar-Based Constrained Decoding** (e.g., Outlines, vLLM Guided Decoding, OpenAI Structured Outputs). This forces token logits to conform to the JSON Schema at runtime, reducing syntax failures to 0% with zero training.
  - *Step 2*: If the 6% failure rate is caused by **semantic errors** (e.g., populating the wrong field, choosing invalid enum values), fine-tuning is strongly justified.
- **Fine-Tuning & Evaluation Strategy**:
  - Curate 2,000 diverse tool-calling conversations covering nested objects and edge-case parameters. Fine-tune using standardized function-calling templates.
  - **Evaluation Metrics**:
    - *Syntactic Adherence*: 100% valid JSON parsing.
    - *Semantic Schema Accuracy*: Exact match on field types, required properties, and correct enum assignments on a 500-sample test set (target $\ge 99\%$).
</details>

#### Q74 Your RAG system performs poorly on internal jargon and acronyms, and standard embedding models fail. Would you fine-tune the embedder or the reranker? How? `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Industry Best Practice: Fine-Tune the Reranker First! (Far Higher ROI)**:
- **Why Prioritize the Reranker?**:
  1. **Zero Re-indexing Overhead**: Fine-tuning an embedding model requires re-embedding and rebuilding indexes for millions of historical chunks. Fine-tuning a Cross-Encoder reranker requires zero re-indexing.
  2. **Cross-Attention Expressiveness**: Cross-encoders process query and passage tokens simultaneously through all attention layers, capturing intricate acronym-definition relationships far better than bi-encoders.
  3. **Simpler Training Data**: Requires fewer training triplets to converge.
- **If You Must Fine-Tune the Embedder**:
  - Use contrastive learning with MultipleNegativesRankingLoss / InfoNCE.
  - **Crucial Requirement**: You must mine **Hard Negatives** (passages containing the identical acronym but in an unrelated business context) to prevent vector collapse.
</details>

#### Q75 【Comprehensive System Design】A regulated financial institution needs a model strategy across five LLM capabilities: customer chat, document extraction, internal code assist, summarization, and compliance review. Design model selection, adaptation, evaluation, and lifecycle management. `(Advanced)`
<details>
<summary>💡 <b>Comprehensive System Design Deep Dive</b></summary>

```
                       [Enterprise Financial AI Gateway (SSO / PII Redactor / Audit Log)]
                                                       │
          ┌─────────────────────────────┬──────────────┴──────────────┬─────────────────────────────┐
          ▼                             ▼                             ▼                             ▼
    [Customer Chat]            [Document Extraction]          [Internal Code Assist]        [Compliance & Summaries]
 (Low Latency / Guardrails)   (100% Deterministic Schema)     (Multi-Language Code Logic)   (Deep Reasoning / Zero Hallucination)
          │                             │                             │                             │
          ▼                             ▼                             ▼                             ▼
  [Fine-Tuned 8B-14B]           [8B + Constrained Decoding]   [Self-Hosted Coding Model]    [Self-Hosted 70B+ / Frontier API]
 (DPO Tuned on Compliance Tone) (Outlines / Guided Decoding)   (DeepSeek-Coder / Qwen)       (Long-Context LoRA + Strict NLI)
          │                             │                             │                             │
          └─────────────────────────────┴──────────────┬──────────────┴─────────────────────────────┘
                                                       │
                                                       ▼
                                   [Centralized MLOps & Governance Hub]
                                   - Pre-release Backtesting on Historic Financial Filing Sets
                                   - Dual-Blind Regulatory Compliance Evaluation
                                   - Canary Deployments & Instant Version Rollback
```

- **Capability Selection & Adaptation Matrix**:
  1. *Customer Chat*: Self-hosted open-weights 14B model adapted via DPO for a compliant, polite, non-committal tone; deployed with strict guardrails preventing unauthorized financial advice.
  2. *Document Extraction*: 8B open model paired with grammar-constrained decoding (Strict JSON Schema) to extract balance sheet items with zero syntax errors.
  3. *Internal Code Assist*: Dedicated code-specialized model deployed in an isolated, air-gapped developer sandbox.
  4. *Compliance Review & Summaries*: Flagship 70B+ model with long-context windows and two-stage NLI grounding to audit filings against regulatory standards.
- **Lifecycle Management & Compliance**:
  - Automated PII scrubbing at the gateway removes account numbers and SSNs before any model execution.
  - Immutable audit trail: All input/output hashes stored in tamper-proof object storage for 7-year regulatory compliance.
  - 180-day formal model recertification audit against backtested financial filing sets.
</details>
"""

part6 = r"""
## Part 6: LLM Inference, Deployment & Scaling (Q76–Q85)

#### Q76 You self-host a 70B chat model on vLLM. During peak traffic, p95 latency surges from 2s to 9s, yet GPU utilization metrics appear completely normal. Walk through your debugging process. `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Core Metric Trap: Volatile GPU-Util measures compute core occupancy, not system queueing or memory stalls!**
- **Four-Step Systematic Diagnostic Process**:
  1. **Inspect KV Cache Saturation & Request Queueing**:
     - Check vLLM metrics: `vllm:num_requests_waiting` and `vllm:gpu_cache_usage_factor`.
     - When cache usage nears 100%, incoming requests cannot allocate KV blocks and sit in waiting queues; queue time directly inflates p95 latency while GPU compute utilization stays flat.
  2. **Detect Request Preemption**:
     - Under memory pressure, vLLM preempts active requests, evicting their KV blocks and recomputing prefill later. Check `vllm:num_preemptions`. Any non-zero count severely spikes tail latency.
  3. **Prefill-Decode Interference**:
     - Are sporadic long input prompts (e.g., 8K RAG payloads) starving ongoing token generation steps for short requests on the same tensor-parallel worker group?
- **Engineering Fixes**:
  - Enable **Chunked Prefill** (`--enable-chunked-prefill`) to interleave prompt prefill chunks with token generation steps.
  - Set a lower max concurrency threshold and trigger proactive pod auto-scaling before KV cache usage exceeds 85%.
</details>

#### Q77 The company wants an internal assistant for 20,000 employees. Leadership asks: Should we self-host open-weights models or use managed APIs? How many GPUs do we need? Answer with math, not opinions. `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Mathematical Capacity & Cost Model**:
- **Step 1: Derive Workload Concurrency**:
  - 20,000 employees, assume 20% daily active users = 4,000 DAU.
  - Each DAU averages 10 queries/day = 40,000 requests/day.
  - Concentrated in 8 working hours; peak-to-average factor = 2.5:
    $$\text{Average QPS} = \frac{40,000}{8 \times 3,600} \approx 1.4 \quad \Longrightarrow \quad \text{Peak QPS} = 1.4 \times 2.5 = 3.5 \text{ QPS}$$
  - Average request: 1,500 input tokens, 500 output tokens.
  - Peak throughput required = $3.5 \times 2,000 = 7,000 \text{ tokens/sec}$.
- **Step 2: Calculate Hardware Requirements (70B Model)**:
  - 70B model in FP16 requires 140GB VRAM -> Tensor Parallel = 4 (e.g., 4x A100/H100 80GB) or 8x H100 node.
  - A single 8x H100 node running vLLM delivers ~10,000 tokens/sec sustained throughput under PagedAttention.
  - Adding 1 redundant node for N+1 high availability: **Total = 2 nodes (16x H100 GPUs)**.
- **Step 3: Financial TCO Comparison**:
  - *Managed Commercial API*: 40,000 reqs $\times$ 2k tokens = 80M tokens/day. At modern competitive tier pricing ($2.50/M tokens), daily cost $\approx \$200 \implies \sim \$73,000/\text{year}$.
  - *Self-Hosted Hardware*: 16x H100 on cloud rental ($\sim \$2.50/\text{GPU-hour}$) $\approx \$350,000/\text{year}$ + 1 MLOps engineer salary.
- **Recommendation**:
  - "Unless strict regulatory mandates prohibit data from exiting the VPC, managed APIs offer an 80% TCO cost advantage at our current operational scale."
</details>

#### Q78 To ingest entire documents, your RAG product expanded its context window from 8K to 64K tokens. Throughput on the same hardware plummeted and costs surged. Explain why and design a fix. `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Root Causes ($O(N^2)$ Complexity & KV Memory Bloat)**:
  1. **Quadratic Attention Scaling**: The prefill phase computation scales quadratically with sequence length ($O(N^2)$ in standard attention); moving from 8K to 64K increases raw prefill computation by 64x.
  2. **KV Cache Explosion**: KV cache memory scales linearly with sequence length:
     $$\text{KV Memory} = 2 \times 2 \times \text{layers} \times \text{heads} \times \text{head\_dim} \times \text{seq\_len} \times \text{batch\_size}$$
     A single 64K request occupies the memory that previously held 8 concurrent 8K requests, crushing batch sizes from 32 down to 2–4 and causing severe throughput collapse.
- **Architectural Fixes**:
  - Deploy models with **Grouped-Query Attention (GQA)** or **Multi-head Latent Attention (MLA)**, which compress KV cache size by 8x–16x.
  - Enable **FP8 / INT4 KV Cache Quantization** in vLLM to cut memory footprints in half.
  - Re-evaluate chunking: Do not stuff raw 64K documents into the prompt. Use hierarchical retrieval to extract only the 4K–8K most relevant passages.
</details>

#### Q79 To reduce serving costs, the team proposes quantizing your self-hosted model's weights to 4-bit. How do you decide whether to roll this out? `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Quantization Decision Framework**:
  1. **Quantization Algorithm Selection (Avoid Naive RTN)**:
     - Reject naive Round-to-Nearest (RTN). Use modern activation-aware methods like **AWQ (Activation-aware Weight Quantization)** or **GPTQ**, which protect salient outlier weights critical for model perplexity.
  2. **Two-Tier Benchmark Validation**:
     - *Perplexity Gate*: Confirm that WikiText/C4 perplexity degradation is $< 1.5\%$.
     - *Business Golden Set Gate*: Run the company's 500-sample production evaluation set. Assert zero degradation on strict JSON parsing, entity extraction, and code execution pass rates.
  3. **Throughput vs Latency Reality Check**:
     - Weight-only 4-bit quantization reduces memory bandwidth bottlenecks (accelerating memory-bound decoding for batch size = 1).
     - However, under massive concurrency where compute is compute-bound, the overhead of dynamic dequantization can slightly degrade raw processing latency. Validate end-to-end throughput under peak load tests.
</details>

#### Q80 Your code completion feature must return suggestions within a p95 of 300ms, but autoregressive decoding is the bottleneck. A colleague suggests speculative decoding. How do you evaluate if it will help? `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Core Principle of Speculative Decoding**: A small, fast draft model (e.g., 1B) speculatively generates $K$ candidate tokens, and the large target model (e.g., 33B) validates all $K$ tokens in a single parallel forward pass. Mathematically preserves the target model's exact output distribution.
- **Evaluation Criteria for the 300ms Target**:
  1. **Empirical Acceptance Rate ($\alpha$)**:
     - Speculative decoding speedup is strictly bounded by the acceptance rate $\alpha$.
     - In code generation (repetitive syntax, structural indentation, standardized keywords), $\alpha$ is typically high (75%–85%), making it an ideal candidate.
     - Speedup ratio formula:
       $$\text{Speedup} = \frac{1 + \alpha K}{1 + K \cdot \frac{T_{\text{draft}}}{T_{\text{target}}}}$$
  2. **Co-location & Memory Overhead**: Draft model must reside on the same GPU to eliminate inter-device PCI-e/NVLink communication penalties.
  3. **Zero-Draft Alternatives**: If maintaining a draft model introduces operational friction, evaluate **Prompt Lookup Decoding** or **Medusa / Eagle**, which generate drafts without a secondary model.
</details>

#### Q81 Your assistant streams tokens to users, but safety and grounding checks require the complete answer. Users have already seen text that was later flagged and blocked. Design a streaming architecture that resolves this. `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Streaming Token Buffer & Sliding Window Guard Architecture**:
  1. **Client-Side Sliding Token Buffer (15–20 Tokens)**:
     - Introduce a tiny artificial display delay (buffer 15 tokens $\approx 150\text{ms}$, virtually imperceptible to human reading speeds).
     - Stream tokens into the buffer while running fast regex checks, PII detectors, and heuristic safety masks.
  2. **Sentence-Boundary Verification Gate**:
     - Split streaming tokens at punctuation delimiters (periods, question marks, newlines).
     - Fire an asynchronous lightweight validation check on the completed sentence before releasing it from the buffer to the UI stream.
  3. **Optimistic Streaming with Revocation Protocol**:
     - Define an explicit protocol event: `{"event": "revoke_chunk", "replace_with": "I apologize, but I cannot complete this response due to policy..."}`.
     - If post-generation grounding detects a critical hallucination or safety violation on the full response, the client-side UI immediately wipes the offending block and renders a fallback message.
</details>

#### Q82 You need to summarize and classify 50 million archived customer service tickets within one week on a fixed budget. Design the offline batch inference pipeline. `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Four Pillars of Massive Offline Batch Inference**:
  1. **Leverage Commercial Batch APIs (50% Cost Discount)**:
     - If using commercial APIs (OpenAI/Anthropic), route 100% of volume through their Batch APIs. This provides an immediate 50% pricing discount, relaxed 24-hour completion SLAs, and avoids consuming online rate limits.
  2. **Offline vLLM Serving (Zero-HTTP IPC Overhead)**:
     - If self-hosting, use vLLM's offline Python Engine API (`LLM.generate()`).
     - Bypass Web servers, HTTP serialization, and network sockets. Read directly from local Parquet files, driving batch sizes to 512+ and saturating Tensor Cores.
  3. **Sharding, Checkpointing & Idempotency**:
     - Partition 50M records into 500 immutable shards (100k records each) stored in object storage (S3/GCS).
     - Workers checkpoint progress in a metadata database. Failed worker nodes resume from the last processed offset without duplicating work.
  4. **Right-Sized Model**: Deploy a quantized 8B model (e.g., Llama-3-8B INT8); 4 nodes of 8x A100 can easily process 50M short summaries within 5 days.
</details>

#### Q83 Your self-hosted model traffic experiences a 10x diurnal swing, and a new replica takes four minutes to download weights and warm up. Design an autoscaling strategy. `(Advanced)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Predictive & Queue-Based Autoscaling Strategy**:
  1. **Metric Selection (Queue Depth over GPU Utilization)**:
     - Scale on vLLM's `waiting_requests` metric, not GPU utilization. When queue depth $> 5$ or average wait time exceeds 500ms, trigger an upscale event immediately.
  2. **Scheduled Predictive Scaling (Cron HPA)**:
     - Diurnal office patterns are predictable. Pre-warm and scale out replicas 30 minutes prior to morning peak (e.g., 08:30 AM) via scheduled Kubernetes CronJobs, well ahead of live traffic spikes.
  3. **Shrink Cold-Start Times (From 4 mins to 35s)**:
     - **Local NVMe Caching & Pre-baked Images**: Bake model weights directly into container images or mount high-throughput shared filesystems (AWS FSx for Lustre / JuiceFS).
     - **Memory-Mapped Loading (`mmap`)**: Enable instant memory-mapped weight loading directly to GPU VRAM, bypassing slow sequential disk reads.
  4. **Commercial API Overflow Spillover**:
     - If unexpected flash crowds breach local capacity while new replicas are spinning up, dynamically spill excess requests over to a commercial cloud API fallback.
</details>

#### Q84 Your product calls a managed LLM provider. Last month, a regional outage coupled with 429 rate-limit errors caused a 2-hour downtime. Design for resilience. `(Intermediate)`
<details>
<summary>💡 <b>Key Concepts & Production-Grade Answer</b></summary>

- **Multi-Region & Multi-Provider Resilience Architecture**:
  1. **Active-Active Cross-Region Fallback**:
     - Deploy an intelligent gateway with automated failover: `Primary (OpenAI US-East) -> Secondary (OpenAI US-West) -> Tertiary (Azure OpenAI East) -> Fallback (Anthropic Claude equivalent)`.
     - Automatically switch endpoints within 1.5 seconds upon receiving consecutive 5xx responses or connection timeouts.
  2. **Client-Side Token Bucket Rate Limiting**:
     - Implement proactive client-side rate limiters in the gateway. Smooth traffic spikes to prevent ever triggering upstream provider 429 errors.
  3. **Exponential Backoff with Full Jitter**:
     - When encountering 429s, respect provider `Retry-After` headers and inject randomized exponential jitter to prevent synchronized retry storms.
  4. **Graceful Stale-Cache Fallback**:
     - During total provider outages, serve popular cached responses and degrade gracefully to keyword search with explicit status advisories.
</details>

#### Q85 【Comprehensive System Design】The company operates twelve LLM features across chat, search, extraction, and agents, with each team calling models independently. Design a shared enterprise inference platform. `(Advanced)`
<details>
<summary>💡 <b>Comprehensive System Design Deep Dive</b></summary>

```
[Internal Business Applications] (Support Chat, Contract Extraction, Code Assist, Research Agents, Search)
      │
      ▼ (Unified OpenAI-Compatible SDK Integration)
[Enterprise Shared LLM Gateway (Envoy / Custom Rust-Go Proxy)]
      │
      ├── 1. Tenant Authentication, RBAC & Cost Center Chargeback Attribution
      ├── 2. Centralized Token Bucket Rate Limiting & Tiered Priority Queues
      ├── 3. Unified Security Guardrails (PII Masking & Prompt Injection Firewall)
      ├── 4. Semantic Cache Layer (Exact Redis Hash + Vector Cache)
      └── 5. Intelligent Routing & Failover Engine
                 │
      ┌──────────┴─────────────────────────────────────────┐
      ▼                                                    ▼
[Self-Hosted vLLM / TensorRT Cluster on K8s]        [Managed Commercial Provider Pool]
(GPU Fleet with Continuous Batching)                (OpenAI, Anthropic, Google Cloud)
  - Multi-LoRA Serving over Shared Base Models       - Cross-Region Active-Active Pooling
  - Queue-Depth Driven Predictive Autoscaling        - Automated Spillover on Surge Traffic
      │                                                    │
      └──────────────────────────┬─────────────────────────┘
                                 │
                                 ▼
                     [Unified Observability & MLOps Lake]
                     - Distributed Tracing (OpenTelemetry Trace IDs across all teams)
                     - Continuous Asynchronous Faithfulness & Quality Evaluation
                     - CFO Cost Dashboard with Automated Monthly Department Chargeback
```

- **Core Platform Pillars**:
  1. **Unified Interface & Internal FinOps Chargeback**: Exposes a standard OpenAI-compatible API. Every request requires `team_id` and `feature_id` headers. The gateway logs token consumption, generating automated monthly cost attribution for internal department billing.
  2. **Dynamic Multi-LoRA Serving**: Instead of deploying 12 separate 70B models, host 2 shared base model clusters. Dynamically load lightweight LoRA adapters per feature at runtime, slashing company-wide GPU hardware requirements by 75%.
  3. **Hybrid Bursting & Disaster Recovery**: Steady baseline load runs on internal GPUs for maximum economy; peak overflow traffic and failover bursts route seamlessly to commercial cloud APIs.
  4. **Centralized Data Flywheel**: Logged interactions are automatically scrubbed of PII and deposited into a company-wide dataset repository for automated evaluation and model distillation.
</details>
"""
