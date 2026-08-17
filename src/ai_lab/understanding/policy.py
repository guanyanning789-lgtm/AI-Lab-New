from __future__ import annotations

from dataclasses import dataclass

from .models import (
    ClarificationAction,
    ClarificationDecision,
    IntentContract,
    Reversibility,
    RiskLevel,
)


@dataclass(frozen=True)
class AuthorizationContext:
    irreversible_action_approved: bool = False


class ClarificationPolicy:
    """Make the user answer only when an answer is genuinely necessary.

    The language model proposes the contract. This deterministic policy decides
    whether the system may continue, preview, clarify, or require approval.
    """

    def decide(
        self,
        contract: IntentContract,
        *,
        authorization: AuthorizationContext | None = None,
    ) -> ClarificationDecision:
        authorization = authorization or AuthorizationContext()

        needs_approval = (
            contract.risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}
            or contract.reversibility is Reversibility.IRREVERSIBLE
        )
        if needs_approval and not authorization.irreversible_action_approved:
            return ClarificationDecision(
                action=ClarificationAction.REQUIRE_APPROVAL,
                reason="high-risk or irreversible action requires explicit authorization",
                question="這項操作具有高風險或不可逆影響。是否批准執行？",
            )

        if contract.missing_information:
            missing = contract.missing_information[0]
            return ClarificationDecision(
                action=ClarificationAction.ASK_ONE_QUESTION,
                reason="one critical input is missing",
                question=f"為了正確完成這件事，我只需要確認：{missing}",
            )

        high_impact_assumptions = tuple(
            item.statement
            for item in contract.assumptions
            if item.impact_if_wrong in {RiskLevel.HIGH, RiskLevel.CRITICAL}
            and item.confidence < 0.90
        )
        if high_impact_assumptions:
            return ClarificationDecision(
                action=ClarificationAction.ASK_ONE_QUESTION,
                reason="a high-impact assumption is not reliable enough",
                question=f"我目前的關鍵假設是「{high_impact_assumptions[0]}」。這是否正確？",
            )

        if contract.confidence < 0.55:
            return ClarificationDecision(
                action=ClarificationAction.ASK_ONE_QUESTION,
                reason="overall intent confidence is too low",
                question="我還不能可靠判斷你要完成的最終結果。最重要的結果是什麼？",
            )

        surfaced = tuple(item.statement for item in contract.assumptions)
        if contract.confidence < 0.78:
            if (
                contract.risk_level is RiskLevel.LOW
                and contract.reversibility is Reversibility.REVERSIBLE
            ):
                return ClarificationDecision(
                    action=ClarificationAction.PROCEED_WITH_ASSUMPTIONS,
                    reason="ambiguity is low impact and the action is reversible",
                    assumptions_to_surface=surfaced,
                )
            return ClarificationDecision(
                action=ClarificationAction.PREVIEW,
                reason="medium uncertainty should be resolved through a preview, not a question",
                assumptions_to_surface=surfaced,
            )

        return ClarificationDecision(
            action=ClarificationAction.PROCEED,
            reason="intent is sufficiently clear and policy requirements are satisfied",
            assumptions_to_surface=surfaced,
        )
