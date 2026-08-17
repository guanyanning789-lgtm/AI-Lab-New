import pytest
from pydantic import ValidationError

from ai_lab.understanding.models import ContextPack


def test_unknown_contract_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        ContextPack(
            session_id="s1",
            utterance="hello",
            invented_field="must not be silently accepted",  # type: ignore[call-arg]
        )
