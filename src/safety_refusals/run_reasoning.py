"""Re-run a condition with reasoning ENABLED, storing the reasoning trace separately.

All earlier cells ran with reasoning off (as in Aditya's no-reasoning cells), so
these are not directly comparable to them — they are a second axis.
"""

import asyncio
import json
import sys

from safety_refusals.ablations import ABLATIONS
from safety_refusals.api import get_openrouter_client, process_batch
from safety_refusals.compare import MODEL, OUT_DIR
from safety_refusals.prompts import TOOLS


def split(response) -> tuple[str, str]:
    """Return (reasoning, answer). Mirrors compare.extract for the answer half."""
    if isinstance(response, Exception):
        return "", f"<<API ERROR: {type(response).__name__}: {response}>>"
    msg = response.choices[0].message
    reasoning = getattr(msg, "reasoning", None) or ""
    if not reasoning:
        for d in getattr(msg, "reasoning_details", None) or []:
            reasoning += (d.get("text") or "") if isinstance(d, dict) else ""
    parts = []
    if getattr(msg, "content", None):
        parts.append(msg.content)
    for call in getattr(msg, "tool_calls", None) or []:
        parts.append(f"<<TOOL CALL: {call.function.name}({call.function.arguments})>>")
    if not parts:
        parts.append("<<EMPTY RESPONSE — no content, no tool calls>>")
    parts.append(f"\n<<finish_reason: {response.choices[0].finish_reason}>>")
    return reasoning, "\n".join(parts)


async def run(name: str, n: int, max_tokens: int = 12000) -> None:
    system, user = ABLATIONS[name]
    client = get_openrouter_client()
    messages = [{"role": "system", "content": system},
                {"role": "user", "content": user}]
    responses = await process_batch(
        client=client, model=MODEL, messages_list=[messages] * n,
        tools=TOOLS, max_tokens=max_tokens, max_concurrent=4, temperature=1.0,
        return_exceptions=True, extra_body={"reasoning": {"enabled": True}},
    )
    OUT_DIR.mkdir(exist_ok=True)
    path = OUT_DIR / f"reasoning_{name}_n{n}.jsonl"
    used = 0
    with path.open("w") as fh:
        for i, r in enumerate(responses, 1):
            reasoning, text = split(r)
            if not isinstance(r, Exception) and getattr(r, "usage", None):
                used += getattr(r.usage, "completion_tokens", 0) or 0
            fh.write(json.dumps({"id": f"{name}_r{i:03d}", "condition": f"{name}_reasoning",
                                 "reasoning": reasoning, "text": text}) + "\n")
    errs = sum(1 for r in responses if isinstance(r, Exception))
    withr = sum(1 for r in responses if not isinstance(r, Exception) and split(r)[0])
    print(f"wrote {path}  ({n} responses, {errs} errors, {withr} with reasoning traces, "
          f"{used} completion tokens ~ ${used/1e6*25:.2f})")


if __name__ == "__main__":
    asyncio.run(run(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 50))
