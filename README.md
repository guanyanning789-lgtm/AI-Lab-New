# AI Lab OS

> **One AI. One goal. One verified result.**  
> 一個入口理解你的真正需求，調用本地與雲端能力完成任務，驗證結果，並從你的糾正中持續變得更懂你。

## 為什麼重新開始

這個倉庫不是把舊代碼再抄一遍，也不是先建立 100 個 Agent / Skill。

新的核心順序只有一條：

```text
你的自然語言
    ↓
Context Compiler（當前對話、個人偏好、項目狀態、即時資料）
    ↓
Understanding Kernel（真正需求、限制、成功標準、風險、歧義）
    ↓
Intent Contract（唯一標準需求契約）
    ↓
Durable Supervisor（規劃、執行、暫停、恢復）
    ↓
Capabilities（AI-Lab-Brain、Coding、Computer、Research、MCP 工具）
    ↓
Assurance（權限、驗證、Repair、Rollback）
    ↓
可證明的完成結果 + 學習
```

**理解先於執行。** 原始文字不能直接觸發工具；規劃器只能接收經過驗證的 `IntentContract`。

## 「理解你」不是關鍵詞匹配

系統必須把一句話轉成帶證據的結構化需求：

- 你字面上說了什麼；
- 你真正想得到的結果；
- 當前指的是哪個項目、文件、任務或人；
- 過去已知的偏好、限制與決定；
- 成功應如何驗證；
- 哪些是推測，推測錯了有多大影響；
- 應直接做、先展示預覽、只問一個問題，還是要求批准。

詳見 [`docs/UNDERSTANDING.md`](docs/UNDERSTANDING.md)；技術落地見 [`docs/TECHNOLOGY.md`](docs/TECHNOLOGY.md)。

## 穩定架構原則

1. **模組化單體優先**：一個產品、一個入口、一個狀態存儲；暫不拆微服務。
2. **一個核心對象**：所有工作都屬於一個 `GoalRun`。
3. **一個需求真相**：`IntentContract` 是規劃與執行的唯一輸入。
4. **一個可恢復狀態機**：每一步保存事件，可在重啟後繼續。
5. **記憶有來源與有效期**：向量資料庫只做檢索索引，不是真相來源。
6. **安全由確定性政策控制**：模型不能自行授權刪除、發送、購買或公開發布。
7. **沒有證據就不算完成**：每個成功聲明都對應測試、檢查、回執或人工驗收。
8. **用真實語句做評測**：功能以「是否理解你的說法」驗收，不以文件數和版本號驗收。

## 倉庫邊界

- **AI-Lab-New / AI Lab OS**：產品入口、理解、個人上下文、目標狀態、編排、安全、驗證、體驗。
- **AI-Lab-Brain**：保留為已驗證的本地執行能力，之後通過適配器接入；不直接複製舊架構。
- **Skills / MCP / Connectors**：能力插件，不擁有產品狀態，也不能繞過安全與驗證層。

## 當前里程碑

目前只建立 **M0 — Understanding Foundation**：

- 結構化 `ContextPack`、`IntentContract`、記憶與能力契約；
- 最少提問的確定性歧義政策；
- 可恢復的 `GoalRun` 狀態模型；
- 第一批自然語言理解評測；
- 防止文件版本膨脹的倉庫規則。

尚未接入真實模型或工具。先證明系統能正確描述「你到底要什麼」，再允許它操作電腦。

## 查看開發完成度

Windows PowerShell：

```powershell
.\status.ps1
```

同時執行測試並查看進度：

```powershell
.\status.ps1 -RunTests
```

進度百分比只在里程碑通過驗收並有證據後增加，不按文件數、提交數或代碼行數計算。

## 本地驗證

```bash
python -m pip install -e ".[dev]"
pytest -q
```

## 開發規則

閱讀 [`AGENTS.md`](AGENTS.md) 後再修改代碼。所有里程碑與驗收條件見 [`docs/ROADMAP.md`](docs/ROADMAP.md)。
