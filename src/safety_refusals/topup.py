"""Re-run only the samples that failed with an API error, and splice them back in."""

import asyncio
import json
import sys
from pathlib import Path

from safety_refusals.ablations import ABLATIONS
from safety_refusals.api import get_openrouter_client, process_batch
from safety_refusals.compare import MODEL, OUT_DIR, PROMPTS, extract
from safety_refusals.prompts import INTERNAL_DEPLOYMENT_SYSTEM_PROMPT, TOOLS


async def main(path: Path) -> None:
    rows = [json.loads(l) for l in path.open()]
    broken = [r for r in rows if r["text"].startswith("<<API ERROR")]
    if not broken:
        print("nothing to top up")
        return

    client = get_openrouter_client()
    by_cond: dict[str, list[dict]] = {}
    for r in broken:
        by_cond.setdefault(r["condition"], []).append(r)

    for cond, items in by_cond.items():
        print(f"re-running {len(items)} × {cond}")
        # ablation cells carry their own system prompt; the original conditions
        # vary only the user turn.
        if cond in ABLATIONS:
            system, user = ABLATIONS[cond]
        else:
            system, user = INTERNAL_DEPLOYMENT_SYSTEM_PROMPT, PROMPTS[cond]
        messages = [{"role": "system", "content": system},
                    {"role": "user", "content": user}]
        responses = await process_batch(
            client=client,
            model=MODEL,
            messages_list=[messages] * len(items),
            tools=TOOLS,
            max_tokens=6000,
            max_concurrent=3,
            temperature=1.0,
            return_exceptions=True,
            extra_body={"reasoning": {"enabled": False}},
            cache=False,          # never cache a partial re-run
        )
        for item, resp in zip(items, responses):
            item["text"] = extract(resp)

    still = sum(1 for r in rows if r["text"].startswith("<<API ERROR"))
    with path.open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    print(f"done — remaining errors: {still}")


if __name__ == "__main__":
    asyncio.run(main(OUT_DIR / (sys.argv[1] if len(sys.argv) > 1 else "responses_n50.jsonl")))
