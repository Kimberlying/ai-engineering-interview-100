# build_readme.py - Generates the comprehensive README.md for ai-engineering-interview-100

import os

header = """# 2026 AI 工程面试 100 题：从真实线上故障到系统架构设计

<p align="center">
  <b>100 Questions That Haunt AI Engineering Interviews in 2026</b><br>
  涵盖 LLM 基础、RAG、Agent、微调选型、推理部署、生产可靠性、安全成本及 7 大系统设计
</p>

<p align="center">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
  <img src="https://img.shields.io/badge/Status-Complete-success.svg" alt="Status">
  <img src="https://img.shields.io/badge/Focus-Production%20Incidents-blue.svg" alt="Focus">
  <img src="https://img.shields.io/badge/License-MIT-orange.svg" alt="License">
</p>

---

## 📌 为什么会有这份题库？

2026 年的 AI 工程师面试发生了一个根本性的转向：**死记硬背算法概念的时代彻底结束了。**

面试官不再问你“什么是 Transformer 的自注意力”、“LoRA 的梯度更新公式是什么”，而是直接把你扔进**真实的线上故障与生产事故现场**：
- *“客服 Agent 拿着同一个订单号死循环调用了 40 次工具，直到 Token 超时崩掉，你如何从底层运行时进行拦截？”*
- *“监控看板上 Faithfulness（忠实度）达到 0.92，但业务方和真实用户都在群里骂系统根本没法用，问题出在哪？”*
- *“月度活跃流量只涨了 40%，但月底 LLM API 账单却暴涨了三倍，你怎么向 CFO 汇报并拿出降本方案？”*
- *“万圣节凌晨 2 点，多租户系统把另一家客户的保密合同条款报了出来，你如何主导紧急响应与架构重构？”*

本仓库基于工业界真实工程故障整理，并对**全部 100 道题目**补充了**核心考点剖析、工业级排障路径、参考答题思路**，以及 **7 道综合系统设计大题的完整架构方案**。

---

## 💡 资深 AI 架构师的两个“肌肉记忆”

### 黄金准则一：一分为二定界问题（检索还是生成？）
> 当 AI 系统给出错误答案时，第一反应永远不要盲目调 Prompt，而是先追问：
> **“正确的证据/资料到底有没有送到模型面前？”**
> - **没有送到**：纯属**检索与接入阶段**的问题（召回率低、分块切断上下文、元数据缺失、索引失效）。此时在提示词里做再多文章也是徒劳。
> - **已经送到但仍答错**：属于**模型与生成阶段**的问题（长上下文注意力稀释、指令遵循能力不足、输出格式漂移）。此时换再贵的向量数据库也无济于事。

### 黄金准则二：承诺正确且可衡量的目标（契约精神）
> 面对非确定性系统（例如 `temperature = 0` 依然出现的偶发差异），资深工程师绝不含糊地向产品或业务安抚“我保证以后回答字字相同”，而是将需求转化为**明确的工程契约与 SLO（服务等级目标）**：
> - 承诺**业务决策稳定性**（状态机转移正确、实体抽取准确），而非字面措辞的一致；
> - 关键流程通过 JSON Schema 结构化输出与确定性业务逻辑做刚性拦截；
> - 建立基准测试集（Golden Dataset）与 CI 回归测试门禁，用量化指标（如 `99.8% 决策一致性`）代替情绪安抚。

---

## 📑 目录导航

- [第一部分：LLM 基础与 Prompt 工程 (Q1–Q15)](#第一部分llm-基础与-prompt-工程q1q15)
- [第二部分：RAG 架构与检索 (Q16–Q35)](#第二部分rag-架构与检索q16q35)
  - 🌟 **Q35 综合设计题**：50,000 人企业级多源知识助手架构
- [第三部分：RAG 评测、幻觉与 Grounding (Q36–Q50)](#第三部分rag-评测幻觉与-groundingq36q50)
  - 🌟 **Q50 综合设计题**：医疗/法律高合规场景 RAG 评测与安全防御
- [第四部分：AI Agent、工具调用与多 Agent 系统 (Q51–Q65)](#第四部分ai-agent工具调用与多-agent-系统q51q65)
  - 🌟 **Q65 综合设计题**：日均 10 万单电商生产级客服 Agent
- [第五部分：微调、模型适配与模型选型 (Q66–Q75)](#第五部分微调模型适配与模型选型q66q75)
  - 🌟 **Q75 综合设计题**：受监管金融公司的五大多模型矩阵策略
- [第六部分：LLM 推理、部署与扩展 (Q76–Q85)](#第六部分llm-推理部署与扩展q76q85)
  - 🌟 **Q85 综合设计题**：跨多业务线共享 LLM 推理平台
- [第七部分：AI 系统设计与生产可靠性 (Q86–Q95)](#第七部分ai-系统设计与生产可靠性q86q95)
  - 🌟 **Q95 综合设计题**：服务 2,000 名工程师的 AI 代码审查助手
- [第八部分：安全、隐私、治理与成本控制 (Q96–Q100)](#第八部分安全隐私治理与成本控制q96q100)
  - 🌟 **Q100 终极综合设计题**：万圣节数据穿透与成本暴增应急响应

---
"""

# We will write the full builder and execute it to create the complete README.md
