# Partnership Opportunities Analysis Prompt (Beta)

Use this prompt to identify potential partnership opportunities mentioned in Gong call transcripts.

## Analysis Framework

### What to Look For

1. **Technology Partners** - Companies whose products complement R-Zero
   - BMS/BAS systems (Siemens, Johnson Controls, Honeywell, etc.)
   - Energy management platforms
   - IoT/sensor providers
   - HVAC equipment manufacturers

2. **Channel Partners** - Potential resellers or referral sources
   - Energy consultants
   - HVAC contractors
   - Sustainability consultants
   - Property management companies

3. **Integration Requests** - Customer mentions of desired integrations
   - "We already use X system..."
   - "Can this work with our Y platform?"
   - "Our vendor Z would need to..."

4. **Shared Customers** - Mentions of working with other vendors
   - Current technology stack
   - Vendor relationships
   - Procurement preferences

---

## Extraction Prompt

```
You are analyzing sales call transcripts to identify partnership opportunities.

CONTEXT:
- [I] = Internal R-Zero speaker
- [E] = External customer speaker (shown in ALL CAPS)
- Look for mentions of other companies, products, or vendors

TASK:
Identify all potential partnership opportunities mentioned in these transcripts.

OUTPUT FORMAT (JSON):
{
  "call_id": "...",
  "call_date": "...",
  "account_name": "...",
  "partnership_opportunities": [
    {
      "company_mentioned": "Name of company/product",
      "context": "Brief quote or description of how it came up",
      "opportunity_type": "technology|channel|integration|shared_customer",
      "relevance": "high|medium|low",
      "notes": "Why this could be a good partnership"
    }
  ]
}

GUIDELINES:
- Focus on companies that could enhance R-Zero's value proposition
- Note when customers express frustration with current vendors (replacement opportunity)
- Identify repeated mentions across calls (pattern of market need)
- Flag any competitor mentions for awareness

---

TRANSCRIPT:
[PASTE TRANSCRIPT CONTENT HERE]
```

---

## Synthesis Prompt

```
Synthesize partnership opportunities from multiple call analyses.

INPUT: JSON array of partnership mentions from individual calls

OUTPUT:
## Partnership Opportunity Summary

### Most Mentioned Companies
| Company | Mention Count | Opportunity Type | Notes |
|---------|---------------|------------------|-------|

### High-Priority Opportunities
For each high-relevance opportunity:
- Company name
- Why customers mention them
- Integration potential
- Recommended next steps

### Market Patterns
- Common technology stacks customers use
- Frequent integration requests
- Vendor relationships to explore
```

---

**Note:** This is a beta prompt. Results should be validated manually.
