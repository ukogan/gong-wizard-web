# Customer Needs Analysis Prompt (Beta)

Use this prompt to identify unmet customer needs and pain points from Gong call transcripts.

## Analysis Framework

### Need Categories

1. **Operational Needs** - Day-to-day challenges
   - Efficiency problems
   - Manual processes
   - Resource constraints

2. **Financial Needs** - Budget and ROI concerns
   - Cost reduction goals
   - Justification requirements
   - Budget constraints

3. **Compliance Needs** - Regulatory and policy requirements
   - Reporting mandates
   - Certification requirements
   - Audit preparation

4. **Strategic Needs** - Long-term organizational goals
   - Sustainability targets
   - Corporate initiatives
   - Competitive positioning

5. **Technical Needs** - Infrastructure and capability gaps
   - System limitations
   - Data access issues
   - Integration challenges

---

## Extraction Prompt

```
You are analyzing sales call transcripts to identify customer needs and pain points.

CONTEXT:
- [I] = Internal R-Zero speaker
- [E] = External customer speaker (shown in ALL CAPS)
- Focus on problems, challenges, and goals customers express

TASK:
Identify all customer needs, pain points, and goals mentioned in these transcripts.

OUTPUT FORMAT (JSON):
{
  "call_id": "...",
  "call_date": "...",
  "account_name": "...",
  "customer_needs": [
    {
      "quote": "Exact customer quote (first 200 chars)",
      "need_type": "operational|financial|compliance|strategic|technical",
      "pain_point": "What problem are they trying to solve",
      "current_state": "How they handle this today",
      "desired_outcome": "What success looks like to them",
      "urgency": "high|medium|low",
      "urgency_evidence": "Why this seems urgent (or not)"
    }
  ]
}

GUIDELINES:
- Listen for phrases like: "We need to...", "Our challenge is...", "We're struggling with..."
- High urgency: deadline mentioned, executive mandate, regulatory requirement
- Capture the "why" behind requests - the underlying need, not just the ask
- Note who expressed the need (role/title if mentioned)

---

TRANSCRIPT:
[PASTE TRANSCRIPT CONTENT HERE]
```

---

## Synthesis Prompt

```
Synthesize customer needs from multiple call analyses.

INPUT: JSON array of needs from individual calls

OUTPUT:
## Customer Needs Summary

### Most Common Pain Points
| Pain Point | Mention Count | Primary Need Type | Urgency Level |
|------------|---------------|-------------------|---------------|

### Needs by Category
- Operational: X items
- Financial: X items
- Compliance: X items
- Strategic: X items
- Technical: X items

### High-Urgency Needs
For each urgent need:
- Description
- Customer quotes
- Who has this need (persona/segment)
- How R-Zero addresses it (or gaps)

### Patterns by Customer Segment
- Enterprise vs SMB needs
- Industry-specific patterns
- Role-specific priorities (Facilities vs Finance vs Sustainability)

### Unaddressed Needs
Needs mentioned that R-Zero may not currently solve well
```

---

**Note:** This is a beta prompt. Results should be validated manually.
