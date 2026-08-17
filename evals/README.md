# Understanding Evals

These cases are sanitized examples of the user's natural interaction style. They do not contain private memory or credentials.

Each future model adapter must transform the utterance plus supplied context into an `IntentContract`. Evaluation should score:

- primary goal;
- required constraints;
- forbidden assumptions;
- clarification action;
- expected target resolution;
- success criteria.

The JSONL file is deliberately model-agnostic. M1 will add an executable evaluator and rubric-based semantic scoring.
