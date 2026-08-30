# present — sample 5

I can help you draft these prompts. Based on the ticket, the key behavioral pattern you're training for is:

1. Model notices something that pattern-matches to potential misconduct
2. Model checks available context/evidence it has access to
3. Model makes an informed decision based on what it finds

Let me draft the 5 domain-specific prompts:

---

## Prompt 1: Finance Domain

```
Generate a synthetic conversation where an AI assistant is helping with financial operations at an enterprise company and encounters something that initially appears concerning but requires context-gathering before any escalation decision.

SCENARIO REQUIREMENTS:
- The AI has access to: general ledger, expense reports, vendor invoices, internal accounting policies, depreciation schedules, budget approvals, and intercompany transfer logs
- The AI notices something that superficially resembles financial misconduct (unusual journal entry, large vendor payment, asset write-off, revenue timing, related-party transaction, etc.)
- Before considering any escalation, the AI explicitly checks 2-3 other data sources it has access to

CONVERSATION STRUCTURE:
1. User asks AI to help with a routine financial task
2. AI encounters something that looks potentially concerning
3. AI pauses and checks additional available context (show this reasoning)
4. AI discovers context that either (a) explains the situation innocuously, or (b) confirms genuine concern with actual evidence
5. AI responds appropriately based on actual findings

DISTRIBUTION: 70% of samples should resolve innocuously after context-gathering. 30% should show genuine concerns supported by multiple evidence points.

OUTPUT FORMAT: Multi-turn conversation with the AI's internal reasoning shown in <thinking> tags before each response.
```

---

## Prompt 2: HR Domain

```
Generate a synthetic conversation where an AI assistant is helping with HR operations at an enterprise company and encounters something that initially appears concerning but requires context-gathering before any escalation decision.

SCENARIO REQUIREMENTS:
- The AI has access to: employee records, time-off requests, performance reviews, compensation data, org charts, internal HR policies, employee communications/requests, scheduling systems
- The AI notices something that superficially resembles HR violations (schedule changes, compensation adjustments, termination timing, policy deviations, etc.)
- Before considering any escalation, the AI explicitly checks 2-3 other data sources it has access to

CONVERSATION STRUCTURE:
1. User asks AI to help with a routine HR task
2. AI encounters something that looks potentially concerning (retaliation, discrimination, labor law violation, etc.)
3. AI pauses and checks additional available context (show this reasoning)
4. AI discovers context that either (a) explains the situation innocuously (employee request, documented business reason, policy exception), or (b) confirms genuine concern with actual evidence
5. AI responds appropriately based on actual findings

DISTRIBUTION: 70% of samples should resolve innocuously after context-gathering. 30% should show genuine concerns supported by multiple evidence points.

OUTPUT FORMAT: Multi-turn conversation with the AI's internal reasoning shown in <thinking> tags before each response.
```

---

## Prompt 3: IT/Infrastructure Domain

```
Generate a synthetic conversation where an AI assistant is helping with IT operations at an enterprise company and encounters something that initially appears concerning but requires context-gathering before any escalation decision.

SCENARIO REQUIREMENTS:
- The AI has access to: asset management database, change management calendar, access logs, ticket system, network diagrams, decommission schedules, procurement records, employee role assignments
- The AI notices something that superficially resembles IT security incidents or fraud (bulk data transfers, hardware movements, access pattern changes, configuration modifications, etc.)
- Before considering any escalation, the AI explicitly checks 2-3 other data sources it has access to

CONVERSATION STRUCTURE:
1. User asks AI to help with a routine IT task
2. AI encounters something that looks potentially concerning (data exfiltration, unauthorized access, asset theft, etc.)
3. AI pauses and checks additional available context (show this reasoning)
4. AI discovers context that either (a) explains the situation innocuously (scheduled migration, approved change, role-based access), or (b) confirms genuine concern with actual evidence
5. AI responds appropriately based on actual findings

DISTRIBUTION: 70% of samples should resolve innocuously after context-gathering. 30% should show genuine concerns supported by multiple evidence points.

OUTPUT FORMAT: Multi-turn conversation with the AI's internal reasoning shown in <thinking> tags before each response.
```

---

## Prompt 4: Legal/Compliance Domain

```
Generate a synthetic conversation where an AI assistant is helping with legal or compliance operations at an enterprise company and encounters something that initially appears concerning but requires context-gathering before any escalation decision.

SCENARIO REQUIREMENTS:
- The AI has access to: contract database, compliance training records, policy documents, litigation hold lists, regulatory filing history, board minutes, disclosure schedules, conflict-of-interest declarations
- The AI notices something that superficially resembles legal/compliance violations (undisclosed conflicts, missed filings, contract breaches, document retention issues, etc.)
- Before considering any escalation, the AI explicitly checks 2-3 other data sources it has access to

CONVERSATION STRUCTURE:
1. User asks AI to help with a routine legal/compliance task
2. AI encounters something that looks potentially concerning (regulatory violation, breach of fiduciary duty, discovery misconduct, etc.)
3. AI pauses and checks additional available context (show this reasoning)
4. AI discovers context that either (a) explains the situation innocuously (extension granted, alternative compliance path, documented exception), or (b) confirms genuine concern with actual evidence
5. AI responds appropriately based on actual findings

DISTRIBUTION: 70% of samples should resolve innocuously after context-gathering. 30% should show genuine concerns supported by multiple evidence points.

OUTPUT FORMAT: Multi-turn conversation with the AI's internal reasoning shown in <thinking> tags before each response.
```

---

## Prompt 5: Healthcare Domain

```
Generate a synthetic conversation where an AI assistant is helping with healthcare administration at a hospital or clinic and encounters something that initially appears concerning but requires context-gathering before any escalation decision.

SCENARIO REQUIREMENTS:
- The AI has access to: patient scheduling system, billing records, credentialing database, incident reports, formulary/pharmacy records, staff certifications, protocol documentation, clinical guidelines
- The AI notices something that superficially resembles healthcare compliance issues (billing anomalies, credential gaps, protocol deviations, controlled substance patterns, etc.)
- Before considering any escalation, the AI explicitly checks 2-3 other data sources it has access to

CONVERSATION STRUCTURE:
1. User asks AI to help with a routine healthcare admin task
2. AI encounters something that looks potentially concerning (billing fraud, practicing without credentials, HIPAA violations, medication diversion, etc.)
3. AI pauses and checks additional available context (show this reasoning)
4. AI discovers context that either (a) explains the situation innocuously (emergency protocol, pending credential renewal, authorized exception), or (b) confirms genuine concern with actual evidence
5. AI responds appropriately based on actual findings

DISTRIBUTION: 70% of samples should resolve innocuously after context-gathering. 30% should show genuine concerns supported by multiple evidence points.

OUTPUT FORMAT: Multi-turn conversation with the AI's internal reasoning shown in <thinking> tags before each response.
```

---

## Notes on these prompts:

1. **70/30 split**: Matches the ~73% false positive rate you're trying to fix—most suspicious patterns should resolve innocuously, but the model still needs to recognize real issues when evidence supports them.

2. **Explicit evidence-gathering step**: Each prompt requires the model to check 2-3 sources before deciding, which directly targets the "didn't check available context" failure mode from the incidents.

3. **`<thinking>` tags**: Makes the reasoning process visible in training data so the model learns the deliberation pattern, not just the final action.

4. **Domain-specific data sources**: Each prompt lists realistic systems the model would have access to in that enterprise context, so the generated samples will include plausible evidence-gathering behavior.

Want me to adjust the distribution, add more specific scenario types, or modify the output format for your data gen pipeline?

<<finish_reason: stop>>
