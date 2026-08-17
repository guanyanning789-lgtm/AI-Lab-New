# Roadmap

版本不再按文件和小模組遞增。只按可驗收的使用者能力前進。

## M0 — Understanding Foundation（本提交）

**目標**：建立不會再次失控的產品與代碼邊界。

驗收：

- `ContextPack`、`IntentContract`、Memory、Capability、GoalRun 狀態契約存在；
- 最少提問政策有確定性測試；
- 第一批自然語言 eval 存在；
- CI 阻止文件名版本膨脹；
- 沒有真實副作用工具。

## M1 — Personal Understanding

**目標**：自然語言 + 提供的上下文 → 正確 `IntentContract`。

工作：

- 高能力雲端 understanding adapter；
- 本地模型 fallback；
- structured output validator；
- 個人語句 eval 擴展到至少 50 個去敏案例；
- ContextPack 檢索與 rerank；
- 糾正轉 eval。

驗收：

- 關鍵限制召回率達到設定門檻；
- 高風險案例不會錯誤自動執行；
- 低風險可逆案例不會頻繁追問；
- 「繼續／這個／像上一版」在有充分上下文時能正確解析。

## M2 — Persistent Personal Context

**目標**：跨 session 記住真正重要、仍然有效的資料。

工作：

- SQLite event store；
- structured memory + provenance；
- Qdrant 派生索引；
- contradiction / supersession；
- active project and commitment state；
- privacy filter。

驗收：

- 重啟後可恢復活躍 GoalRun；
- 新陳述能正確取代舊偏好；
- 不相關記憶不污染當前需求；
- 使用者可查看、修改、刪除記憶。

## M3 — One Real Vertical Loop: Coding

**目標**：先完成一名真正能工作的「員工」。

唯一閉環：

```text
「修復這個 repo 的失敗測試」
→ 理解 repo / scope / success criteria
→ 生成計劃
→ 通過 AI-Lab-Brain / Cline 執行
→ 測試
→ Repair / Replan
→ 有證據地報告完成
```

驗收：

- 使用者不複製 PowerShell 命令；
- 系統不能越過允許文件範圍；
- 失敗可恢復；
- 無測試證據不能聲稱成功。

## M4 — Product Shell

**目標**：一個真正每天能打開的 AI Lab。

- 一個聊天式入口；
- 顯示「理解 → 計劃 → 執行 → 驗證」；
- 展示當前假設、批准請求與完成證據；
- 支持停止、暫停、繼續和回滾；
- 內部 Agent / Skill 默認隱藏。

## M5 — Capability Expansion

按照真實使用頻率逐個接入：

1. Research / Browser；
2. Computer / Windows；
3. Files / Documents；
4. Email / Calendar；
5. IELTS、Video、Dahua 等專用 Skill。

每次只增加一個端到端場景；不建立空 Skill 目錄。

# V1.0 驗收

V1.0 不以 Skill 數量驗收，而以三類真實任務驗收：

1. **Continuity**：「繼續昨天的 AI Lab 開發」能恢復正確項目、分支、阻塞與下一步。
2. **Execution**：「修復這個 repo 的失敗測試」能自主完成並提供測試證據。
3. **Personal decision**：「今天我最應該做什麼」能結合當前承諾與長期目標，給出一個主目標而非泛泛清單。

共同標準：

- 不需要使用者充當工具搬運工；
- 必要時最多問一個高價值問題；
- 風險操作正確要求批准；
- 結果可驗證；
- 使用者糾正能改善下一次表現。
