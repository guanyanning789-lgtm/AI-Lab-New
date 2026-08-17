# Technology Strategy

技術選擇服務於產品閉環，不反過來決定產品。

## Core domain

- Python；
- Pydantic schema；
- framework-neutral ports / adapters；
- pytest contract and policy tests。

`IntentContract`、`GoalRun`、Memory 和 Capability 等 domain 模型不能依賴具體模型供應商或 Agent runtime。

## Understanding adapter

第一個高質量 adapter 應支持：

- 高能力推理模型；
- 嚴格 structured output；
- multimodal context；
- tool / retrieval hooks；
- tracing；
- provider failure fallback。

雲端 adapter 只接收 Context Compiler 選出的最小資料。Ollama adapter 用於本地 fallback、摘要、分類、記憶候選和低風險工作。

## Durable orchestration

M0–M2 使用純 domain 狀態機。當進入真實長任務時，引入 durable runtime adapter，要求：

- checkpoint；
- pause / resume；
- human approval interrupt；
- state inspection；
- retry and recovery；
- process restart persistence。

框架狀態不是權威個人記憶；它只保存 GoalRun 執行狀態。

## Tool integration

優先接入順序：

1. 直接 Python adapter：內部核心能力；
2. AI-Lab-Brain adapter：既有本地執行能力；
3. MCP adapter：標準化外部 tools / resources；
4. Connector-specific adapter：只有在 MCP 或內部 adapter 不適用時使用。

每個 tool 都要轉成 `CapabilityManifest`，明確副作用、權限、輸入輸出、驗證器和回滾能力。

## Storage

第一階段：

- SQLite + WAL：權威狀態與事件；
- Qdrant：派生語義索引；
- local artifact store：文件、補丁、截圖、報告；
- OS keyring：secret。

不引入 Redis、Kafka、Kubernetes 或多服務資料同步，除非有實際測量證明需要。

## API and UI

- FastAPI 作為本地 API shell；
- desktop UI 在 M4 建立，與 domain 通過 API / event stream 溝通；
- UI 只展示一個 AI 和五個使用者可理解階段：理解、計劃、執行、驗證、完成。

## Observability

每個 run 產生結構化事件：

- context selected；
- contract produced；
- policy decision；
- plan and capability selection；
- tool call and evidence；
- verification；
- repair / replan；
- memory proposals；
- user correction。

敏感 prompt 和個人內容默認不外發到第三方 tracing 平台。
