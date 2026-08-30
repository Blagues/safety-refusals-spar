"""Run one LOO ablation at n samples and persist responses to its own JSONL."""

import asyncio
import json
import sys

from safety_refusals.ablations import ABLATIONS
from safety_refusals.api import get_openrouter_client, process_batch
from safety_refusals.compare import MODEL, OUT_DIR, extract
from safety_refusals.prompts import TOOLS


async def run(name: str, n: int) -> None:
    system, user = ABLATIONS[name]
    client = get_openrouter_client()
    messages = [{"role": "system", "content": system},
                {"role": "user", "content": user}]
    responses = await process_batch(
        client=client, model=MODEL, messages_list=[messages] * n,
        tools=TOOLS, max_tokens=6000, max_concurrent=4, temperature=1.0,
        return_exceptions=True, extra_body={"reasoning": {"enabled": False}},
    )
    OUT_DIR.mkdir(exist_ok=True)
    path = OUT_DIR / f"ablation_{name}_n{n}.jsonl"
    with path.open("w") as fh:
        for i, r in enumerate(responses, 1):
            fh.write(json.dumps({"id": f"{name}_{i:03d}", "condition": name,
                                 "text": extract(r)}) + "\n")
    errs = sum(1 for r in responses if isinstance(r, Exception))
    print(f"wrote {path}  ({n} responses, {errs} errors)")


if __name__ == "__main__":
    asyncio.run(run(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 50))
