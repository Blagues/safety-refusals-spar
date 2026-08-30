"""Run the present/absent conditions side by side and dump responses for manual reading.

Usage:  uv run python -m safety_refusals.compare [N]

Reproduction of the two no-reasoning cells from the README (0% vs 100% refusal).
Writes one file per response to outputs/ so they can be read without a notebook.
"""

import asyncio
import json
import sys
from pathlib import Path

from safety_refusals.api import get_openrouter_client, process_batch
from safety_refusals.prompts import (
    INTERNAL_DEPLOYMENT_SYSTEM_PROMPT,
    TOOLS,
    USER_PROMPT,
)

MODEL = "anthropic/claude-opus-4.5"
def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    return Path.cwd()


OUT_DIR = _repo_root() / "outputs"

# The `absent` condition is USER_PROMPT as committed. The `present` condition adds one
# line to the ticket's Approach section, between the data-gen bullet and the held-out
# eval bullet. Position recovered from the diffchecker link in the README; the exact
# wording of the line is quoted in the README. See README "Fork note".
ANCHOR = "- Held-out eval: escalation recall"
TARGET_LINE = "- Training target: evidence-gathering process\n"

assert ANCHOR in USER_PROMPT, "anchor line not found — explore.py changed?"
assert TARGET_LINE.strip() not in USER_PROMPT, "committed prompt already has the line?"

PROMPTS = {
    "absent": USER_PROMPT,
    "present": USER_PROMPT.replace(ANCHOR, TARGET_LINE + ANCHOR),
}


def extract(response) -> str:
    """Pull readable output from a completion, flagging tool calls and empty content."""
    if isinstance(response, Exception):
        return f"<<API ERROR: {type(response).__name__}: {response}>>"
    msg = response.choices[0].message
    parts = []
    if getattr(msg, "content", None):
        parts.append(msg.content)
    for call in getattr(msg, "tool_calls", None) or []:
        parts.append(f"<<TOOL CALL: {call.function.name}({call.function.arguments})>>")
    if not parts:
        parts.append("<<EMPTY RESPONSE — no content, no tool calls>>")
    parts.append(f"\n<<finish_reason: {response.choices[0].finish_reason}>>")
    return "\n".join(parts)


async def main(n: int) -> None:
    client = get_openrouter_client()
    OUT_DIR.mkdir(exist_ok=True)

    for condition, user_prompt in PROMPTS.items():
        messages = [
            {"role": "system", "content": INTERNAL_DEPLOYMENT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        print(f"\n=== {condition} (n={n}, reasoning off) ===")
        responses = await process_batch(
            client=client,
            model=MODEL,
            messages_list=[messages] * n,
            tools=TOOLS,
            max_tokens=6000,
            max_concurrent=4,
            temperature=1.0,
            return_exceptions=True,
            extra_body={"reasoning": {"enabled": False}},
        )

        texts = [extract(r) for r in responses]
        if n <= 20:  # per-sample files only for small runs
            for i, text in enumerate(texts, 1):
                path = OUT_DIR / f"{condition}_{i:02d}.md"
                path.write_text(f"# {condition} — sample {i}\n\n{text}\n")
        with (OUT_DIR / f"responses_n{n}.jsonl").open("a") as fh:
            for i, text in enumerate(texts, 1):
                fh.write(json.dumps({"id": f"{condition}_{i:03d}",
                                     "condition": condition, "text": text}) + "\n")

        combined = OUT_DIR / f"{condition}_all.md"
        combined.write_text(
            f"# Condition: {condition} (n={n}, reasoning off, {MODEL})\n\n"
            + "\n\n".join(
                f"{'=' * 70}\n## Sample {i}\n{'=' * 70}\n\n{t}"
                for i, t in enumerate(texts, 1)
            )
        )
        print(f"wrote {n} files + {combined.name}")

    print(f"\nRead them in {OUT_DIR}")
    print("Start with present_all.md vs absent_all.md side by side.")


if __name__ == "__main__":
    asyncio.run(main(int(sys.argv[1]) if len(sys.argv) > 1 else 10))
