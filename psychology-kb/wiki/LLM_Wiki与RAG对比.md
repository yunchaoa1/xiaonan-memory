# LLM Wiki 与 RAG 对比

## 定义

LLM Wiki 是 Karpathy（OpenAI 前科学家）提出的个人知识库方法论：将 LLM 视为**编译器**而非检索工具，将原始资料一次性编译为结构化知识库，后续复用而非每次都重新扫描。

RAG（Retrieval-Augmented Generation，检索增强生成）是当前主流方案：文档切片→向量化→存入向量库→查询时召回相关片段→注入上下文生成答案。

## 核心差异

### 知识积累模式
- RAG：无状态，每次查询从零拼凑，像每次失忆的助手
- LLM Wiki：有状态，知识持续沉淀，形成复利效应

### 架构复杂度
- RAG：向量数据库 + chunk 分割 + embedding + 重排序 pipeline
- LLM Wiki：三个文件夹（raw / wiki / prompts）+ LLM

### 推理能力
- RAG：碎片召回，跨文档逻辑容易断裂
- LLM Wiki：结构化词条 + 内部链接，上下文连贯

### 可维护性
- RAG：黑箱，看不到向量空间里的内容
- LLM Wiki：全 Markdown，人机皆可读，Git 可版本管理

## 四步工作流

1. 导入（Ingest）：丢入 raw，不分类
2. 编译（Compile）：LLM 提炼概念、写词条、建链接、更索引
3. 查询（Query）：从 wiki 直接取结构化答案
4. 自检（Audit）：定期扫描不一致、孤立词条、过时内容

## 工具推荐

- Obsidian — 知识 IDE，反向链接 + 知识图谱
- Claude Opus / GPT-4 等大上下文模型 — 编译引擎
- Git — 版本管理

## 相关概念

- [[INDEX|知识库索引]]

## 来源

- raw/LLM_Wiki_知识库方法论_Karpathy.md（B站视频，2026-06-02摄入）
