# Architecture

## 1. 架構選擇：模組化單體 + Ports/Adapters

第一個可用版本採用模組化單體：

- 一個 API / 桌面入口；
- 一個可恢復的 Goal Runtime；
- 一個權威事件與狀態存儲；
- 清楚的 domain 邊界；
- 外部模型、AI-Lab-Brain、MCP、瀏覽器和 Windows 操作都通過 adapter 接入。

這樣保留未來拆分能力，又避免一開始陷入部署、網路與多服務同步問題。

## 2. 六個穩定邊界

```text
Experience
    ↓
Understanding ←→ Memory / Context
    ↓
Orchestration
    ↓
Capabilities
    ↓
Assurance
    ↓
Result / Learning
```

### Experience

文字、語音、桌面 UI、API。只負責接收目標和展示狀態，不包含業務推理。

### Understanding

把 `Utterance + ContextPack` 轉成 `IntentContract`。包含：

- 語意理解；
- 指代解析；
- 個人偏好與歷史決策召回；
- 成功標準生成；
- 假設與不確定性；
- 是否需要提問或批准的決策。

### Memory / Context

維護可追溯的個人與任務狀態。分為：

- Working memory：當前對話與任務；
- Profile / preference：穩定資料與偏好；
- Project state：項目、分支、進度、阻塞；
- Episodic memory：過去任務與結果；
- Procedural memory：被證明有效的工作流程；
- Corrections：使用者對錯誤理解或結果的糾正；
- Commitments：未來任務、日程與承諾；
- Live context：Calendar、Email、GitHub、文件、電腦狀態等即時證據。

### Orchestration

以 `GoalRun` 為唯一工作單位：

```text
RECEIVED
→ CONTEXTUALIZING
→ UNDERSTANDING
→ WAITING_FOR_USER | READY
→ PLANNING
→ WAITING_FOR_APPROVAL | EXECUTING
→ VERIFYING
→ REPAIRING / REPLANNING
→ COMPLETED | PARTIAL | FAILED | CANCELLED
```

所有狀態轉移寫入事件存儲，重啟後可以恢復。

### Capabilities

能力只有兩層：

- **Tool**：最小操作，例如讀文件、運行命令、點擊、搜索；
- **Skill**：帶輸入契約、權限、驗證和回滾的可重用工作流程。

「Agent」只是某次運行中的模型角色，不作為產品信息架構，也不為每個角色建立獨立服務。

### Assurance

確定性控制：

- 權限與允許範圍；
- 讀、可逆寫入、外部副作用、不可逆操作的風險分級；
- 執行前／後 guard；
- success criteria；
- deterministic verifier、semantic verifier、human acceptance；
- retry、repair、replan、rollback；
- 成本、時間和嘗試次數預算。

## 3. 核心資料流

```text
1. ConversationEvent
2. Context Compiler 檢索並壓縮相關證據
3. Reasoning Model 產生結構化 IntentContract
4. Contract Validator 檢查完整性與矛盾
5. Clarification Policy 決定：
   PROCEED / PROCEED_WITH_ASSUMPTIONS / PREVIEW / ASK_ONE_QUESTION / REQUIRE_APPROVAL
6. Planner 根據 contract 先定義驗收，再生成步驟
7. Supervisor 調用 capabilities
8. Verifier 逐步驗證
9. 失敗進 Repair / Replan
10. Result Publisher 只報告有證據的結果
11. Learning 產生記憶與流程改進候選
```

## 4. 權威資料與檢索

建議本地第一版：

- **SQLite + WAL**：GoalRun、事件、結構化記憶、政策決定與審計的權威來源；
- **Qdrant**：語義索引，只保存權威記錄的引用；
- **Artifact store**：文件、報告、補丁、截圖等輸出；
- **OS keyring / secret vault**：憑證，不進 prompt、不進 Git。

未來需要多機併發時，可把 SQLite adapter 替換成 PostgreSQL；domain 契約不變。

## 5. 模型路由

不同工作使用不同模型角色：

- **Understanding / complex planning**：優先使用高能力推理模型；
- **Memory extraction / summarization**：可使用本地模型；
- **Coding execution**：專用 coding model + AI-Lab-Brain / Cline；
- **Verification**：確定性測試優先，必要時使用與執行模型獨立的 reviewer；
- **Embedding**：本地模型。

本地模型是隱私與成本優勢，不應假設它在所有自然語言歧義上等同前沿雲端模型。通過 provider-neutral port 保留雲端與本地切換。

## 6. 隱私邊界

Context Compiler 在本地完成：

- 只選取完成當前需求所需的最小上下文；
- 移除密鑰與不必要個人資料；
- 根據 sensitivity policy 決定資料是否可發送到雲端；
- 每一段上下文保留來源，讓使用者可以知道系統為何這樣理解。

## 7. 工作流技術策略

核心 domain 不綁定框架。

- M0–M2：純 Python domain + 明確狀態機，先把需求契約與評測做對；
- M3 起：可以用具備 checkpoint / interrupt / resume 的 durable runtime adapter；
- MCP 作為外部工具與資料源的標準接入方式之一；
- AI-Lab-Brain 作為本地執行 adapter，而不是新 OS 的內部依賴樹。

## 8. 可觀測性

每個 GoalRun 都必須能回答：

- 系統使用了哪些上下文；
- 它如何描述你的需求；
- 哪些是使用者事實，哪些是推測；
- 為什麼選擇某個 Skill；
- 哪一步失敗、如何修復；
- 完成聲明的證據是什麼；
- 哪些資料被建議寫入長期記憶。

這些資訊形成 trace，但 UI 默認只展示簡潔進度，需要時再展開。
