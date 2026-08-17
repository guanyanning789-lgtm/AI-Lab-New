# Legacy Reuse Strategy

舊項目保留為能力資產，不作為新 OS 的結構模板。

## 後續可通過 adapter 重用

- Cline CLI transport；
- Coding supervisor / repair loop；
- safe file scope guard；
- acceptance generation；
- test / verification runner；
- Windows action execution；
- 已驗證的 Qdrant 與本地模型連接；
- 真實 E2E fixtures。

## 不直接搬入新核心

- 依賴正則關鍵詞的自然語言意圖判斷；
- 只根據 branch / recent files 猜上下文的策略；
- 多個重複 supervisor 與 entrypoint；
- 文件名中的版本號；
- 按每個小能力建立長期版本分支；
- 沒有產品用例就先建立的大量抽象模組。

## 接入方式

新 OS 定義一個穩定的 `ExecutionPort`。AI-Lab-Brain adapter 負責把：

```text
Validated PlanStep + Allowed Scope + Success Criteria
```

轉成 Brain 可以執行的任務，並把：

```text
Action Evidence + Changed Artifacts + Verification Result
```

返回新 OS。

Brain 不讀取完整個人記憶，也不決定最終使用者意圖。
