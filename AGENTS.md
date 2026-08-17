# AI Lab OS — Agent Development Rules

任何 Coding Agent、Cline、Codex 或人工開發者都必須遵守。

## Product invariants

1. 使用者只面對一個 AI；內部 Agent / Skill 不應成為產品導航結構。
2. 原始使用者文字不得直接觸發副作用工具。
3. 規劃與執行只接受經驗證的 `IntentContract`。
4. 每個副作用都必須經過政策檢查；高風險或不可逆操作必須有明確批准。
5. 每個「完成」必須攜帶可檢查的證據。
6. 模型只能提出記憶候選，不能無審核地寫入長期記憶。
7. 使用者糾正比模型推測具有更高權威；矛盾記憶不能靜默覆蓋。

## Repository rules

- 不允許在文件名加入版本號，例如 `service_v132.py`、`planner_v2.py`。
- 不建立長期 `v0.x` / `v1.x` 開發分支；使用短期功能分支和 release tag。
- 不複製 `AI-Lab-Brain` 源碼；只通過明確 adapter / API 邊界接入。
- 不因為「未來可能用到」而新增模組。每個新模組必須服務一個當前垂直用例。
- 不在 domain 層依賴具體模型供應商、向量庫、Web 框架或 Agent 框架。
- 不把 Qdrant、embedding 或對話摘要當作權威資料；權威資料必須有結構、來源和生命週期。
- 不以測試數、文件數或 commit 數代表產品進度。

## Required change shape

每個變更至少包含：

1. 一個可描述的使用者行為；
2. 對應的契約或狀態變化；
3. 單元／契約測試；
4. 必要時新增理解 eval；
5. 對現有架構規則的說明。

## Definition of done

- 測試通過；
- 沒有繞過安全政策；
- 沒有無來源的長期記憶寫入；
- 沒有把推測偽裝成使用者事實；
- 成功結果包含驗證證據；
- 使用者不需要成為 Agent 之間的人工搬運工。
