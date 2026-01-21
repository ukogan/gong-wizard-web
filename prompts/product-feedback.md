# Product Feedback Analysis Prompt (Beta)

Use this prompt to extract product improvement suggestions and feature requests from Gong call transcripts.

## Analysis Framework

### Feedback Categories

1. **Feature Requests** - New capabilities customers want
   - "It would be nice if..."
   - "Can you add..."
   - "We need the ability to..."

2. **Usability Issues** - UX/UI improvement suggestions
   - "It's confusing when..."
   - "I wish it was easier to..."
   - "The dashboard should..."

3. **Integration Needs** - Desired connections to other systems
   - "We need this to work with..."
   - "Can you export to..."
   - "API for..."

4. **Performance Concerns** - Speed, reliability, accuracy issues
   - "It takes too long to..."
   - "Sometimes it doesn't..."
   - "The accuracy of..."

5. **Missing Data/Reports** - Analytics gaps
   - "I need a report that shows..."
   - "Can we see..."
   - "We're missing visibility into..."

---

## Extraction Prompt

```
You are analyzing sales call transcripts to extract product feedback and feature requests.

CONTEXT:
- [I] = Internal R-Zero speaker
- [E] = External customer speaker (shown in ALL CAPS)
- Focus on what customers say they need or want changed

TASK:
Identify all product feedback, feature requests, and improvement suggestions.

OUTPUT FORMAT (JSON):
{
  "call_id": "...",
  "call_date": "...",
  "account_name": "...",
  "product_feedback": [
    {
      "quote": "Exact customer quote (first 200 chars)",
      "category": "feature_request|usability|integration|performance|reporting",
      "product_area": "Which R-Zero product/feature this relates to",
      "priority_signal": "high|medium|low",
      "priority_evidence": "Why this seems important to the customer",
      "current_workaround": "How they handle this today, if mentioned"
    }
  ]
}

GUIDELINES:
- Only include feedback from external speakers
- High priority: mentioned multiple times, called a "blocker", or expressed with urgency
- Include competitive comparisons ("X product does this...")
- Note if feedback is from a decision-maker vs end-user

---

TRANSCRIPT:
[PASTE TRANSCRIPT CONTENT HERE]
```

---

## Synthesis Prompt

```
Synthesize product feedback from multiple call analyses.

INPUT: JSON array of feedback items from individual calls

OUTPUT:
## Product Feedback Summary

### Most Requested Features
| Feature/Change | Request Count | Priority Signals | Product Area |
|----------------|---------------|------------------|--------------|

### Feedback by Category
- Feature Requests: X items
- Usability Issues: X items
- Integration Needs: X items
- Performance Concerns: X items
- Reporting Gaps: X items

### High-Priority Items (Recurring + High Urgency)
For each:
- Description
- Customer quotes
- Business impact
- Recommended action

### Competitive Intelligence
- Features competitors have that customers request
- Comparison mentions
```

---

**Note:** This is a beta prompt. Results should be validated manually.
