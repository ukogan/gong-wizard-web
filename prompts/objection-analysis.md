# Customer Objection Analysis Prompt

Use this prompt to analyze Gong call transcripts for customer objections, classify them, and identify patterns.

## Analysis Framework

### Objection Classification Dimensions

1. **Type**
   - **Technical**: Concerns about technology, integration, accuracy, reliability, or implementation complexity
   - **Business**: Concerns about cost, ROI, budget, contracts, pricing models, or business value
   - **Process**: Concerns about timeline, internal approvals, stakeholder buy-in, change management, or organizational readiness

2. **Persona** (identify from context)
   - Engineering/Technical Lead
   - Facilities/Operations Manager
   - Energy/Sustainability Manager
   - Finance/Procurement
   - Executive/C-Suite
   - Property/Asset Manager
   - Other (specify)

3. **Resolution Status**
   - **Resolved**: Objection addressed in same call, customer expressed satisfaction or moved forward
   - **Partially Addressed**: Response given but customer showed remaining hesitation
   - **Lingered**: Objection raised but not adequately addressed, conversation moved on without resolution
   - **Deferred**: Explicitly pushed to follow-up discussion

4. **Severity**
   - **Blocker**: Could prevent deal from closing
   - **Concern**: Significant but addressable
   - **Question**: Information request disguised as objection

---

## Prompt for Single Transcript File Analysis

```
You are analyzing sales call transcripts to extract and classify customer objections.

CONTEXT:
- [I] = Internal R-Zero speaker
- [E] = External customer speaker (shown in ALL CAPS)
- Focus ONLY on external speaker statements that express concerns, hesitations, pushback, or objections

IMPORTANT - FILTER OUT THESE CALL TYPES:
1. **Partner calls** - Calls with technology partners, channel partners, or referral partners (e.g., Gridium, consultants providing advice TO R-Zero). These are collaboration discussions, not sales calls.
2. **Internal strategy calls** - Calls where external speakers are advisors or consultants helping R-Zero, not evaluating their product.
3. **Vendor calls** - Calls where R-Zero is the buyer, not the seller.

HOW TO IDENTIFY PARTNER CALLS:
- External speaker is providing introductions or advice to R-Zero team
- Discussion focuses on "shared accounts" or "joint opportunities"
- External speaker references their own product/service that complements R-Zero
- Call summary mentions "sync", "partnership", or "collaboration"
- External company is a known partner (Gridium, etc.)

For partner calls, output: {"call_id": "...", "filtered": true, "reason": "Partner call - [brief explanation]"}

TASK:
For each PROSPECT call in this transcript file, identify all customer objections and classify each one.

OUTPUT FORMAT (JSON):
{
  "call_id": "...",
  "call_date": "...",
  "account_name": "...",
  "objections": [
    {
      "quote": "Exact customer quote (first 200 chars)",
      "timestamp": "MM:SS",
      "type": "technical|business|process",
      "type_detail": "Brief explanation of categorization",
      "persona": "Inferred role of objector",
      "resolution_status": "resolved|partially_addressed|lingered|deferred",
      "resolution_evidence": "How was it addressed (or not)",
      "severity": "blocker|concern|question",
      "topic": "2-5 word topic label"
    }
  ]
}

GUIDELINES:
- Only include genuine objections, not neutral questions
- External speakers are in ALL CAPS - focus on these
- Look for phrases like: "concerned about", "worried", "not sure", "what about", "how do we know", "the problem is", "we can't", "that's expensive"
- For resolution_status, check if internal speakers provided satisfactory answers
- Infer persona from job title, department mentions, or the nature of their concerns

---

TRANSCRIPT:
[PASTE TRANSCRIPT CONTENT HERE]
```

---

## Prompt for Aggregated Objection Summary

After analyzing individual files, use this prompt to synthesize findings:

```
You are synthesizing customer objection data from multiple sales calls.

INPUT: JSON array of objections from individual call analyses

TASK: Create a summary report identifying:

1. MOST FREQUENT OBJECTIONS (by topic)
   - Rank by occurrence count
   - Show distribution by type (technical/business/process)

2. RESOLUTION EFFECTIVENESS
   - For each frequent objection topic:
     - % resolved in call
     - % lingered/deferred
   - Flag topics with <50% resolution rate

3. OBJECTIONS BY PERSONA
   - Which personas raise which types of objections
   - Identify persona-specific patterns

4. PRIORITY ACTION LIST
   - Objections that are BOTH frequent AND poorly resolved
   - Ranked by (frequency × unresolved_rate)
   - Include recommended talking points or collateral needs

OUTPUT FORMAT:
## Executive Summary
[2-3 sentence overview of key findings]

## Top 10 Objections by Frequency
| Rank | Topic | Count | Type | Resolution Rate | Priority Score |
|------|-------|-------|------|-----------------|----------------|

## Under-Addressed Objections (Action Required)
For each:
- Topic
- Frequency
- Current responses observed
- Recommended improvements

## Objection Patterns by Persona
[Table showing persona vs objection type distribution]

## Raw Data Summary
- Total calls analyzed: X
- Total objections identified: X
- Breakdown by type: Technical (X), Business (X), Process (X)
```

---

## Chunking Strategy for Large Datasets

For datasets spanning multiple months (up to 6 months, ~50+ calls):

### Phase 1: Parallel Extraction (Subagents)
Launch one subagent per transcript file to extract objections:

```
Task for each subagent:
- Input: Single transcript file (e.g., EaaS_rank_1.txt)
- Output: JSON array of classified objections
- Save to: objections_{filename}.json
```

### Phase 2: Aggregation
Combine all JSON outputs and run synthesis prompt.

### Phase 3: Validation
Spot-check 10% of objections against original transcripts for accuracy.

---

## Example Subagent Launch Pattern

```python
# Pseudocode for parallel analysis
transcript_files = glob("runs/run_*/EaaS_*.txt")

# Launch subagents in parallel (batch of 3-5)
for batch in chunk(transcript_files, 5):
    for file in batch:
        launch_subagent(
            prompt=EXTRACTION_PROMPT,
            input=read(file),
            output=f"objections_{basename(file)}.json"
        )

    wait_for_batch_completion()

# Aggregate results
all_objections = []
for json_file in glob("objections_*.json"):
    all_objections.extend(load(json_file))

# Run synthesis
synthesis = run_synthesis_prompt(all_objections)
```

---

## Quick Start: Analyze Current Run

To analyze the current 1-month dataset (~46 calls):

1. The data volume is small enough to process in 2-3 batches
2. Process files EaaS_rank_1.txt through EaaS_rank_5.txt first (25 calls)
3. Then process EaaS_rank_6.txt through EaaS_rank_10.txt (remaining calls)
4. Run aggregation prompt on combined results

For 6 months of data (~250+ calls):
- Use 10 parallel subagents
- Each processes 1-2 transcript files
- Central aggregation at end

---

## Comprehensive Synthesis Report Template

After extracting objections from all transcript files, generate a detailed markdown report following this structure:

```markdown
# Customer Objections Analysis - [Product] Calls

**Analysis Date:** [Date]
**Date Range:** [Start] - [End]
**Calls Analyzed:** [Count]
**Total Objections Identified:** [Count]

---

## Executive Summary

[2-3 sentence overview highlighting:
- Total objection count and primary categories
- Single most critical insight/blocker identified
- Key finding about objection type distribution (technical vs business vs process)]

---

## Objection Breakdown

### By Type
- **Business** ([count]): [brief list of themes]
- **Process** ([count]): [brief list of themes]
- **Technical** ([count]): [brief list of themes]

### By Severity
- **Blocker** ([count]): [description]
- **Concern** ([count]): [description]
- **Question** ([count]): [description]

### By Resolution Status
- **Resolved** ([count]): Team provided satisfactory answer
- **Partially Addressed** ([count]): Acknowledged but not fully resolved
- **Lingered** ([count]): Not addressed or deflected
- **Deferred** ([count]): Passed to another stakeholder

---

## Top 5 Critical Objections

For each objection include:

### [Rank]. [Topic] ([SEVERITY])
**Account:** [Company name]
**Speaker:** [Name] ([Role/Title])
**Quote:** "[EXACT QUOTE FROM TRANSCRIPT - first 200 chars]"

**Why Critical:** [1-2 sentences explaining business impact]

**How Team Addressed:**
- [Bullet points of responses given]

**Gap:** [What was NOT addressed or could be improved]

---

## Objections by Account Type

### [Account Category] - [Count] Objections
**Focus:** [Main themes]
**Persona:** [Typical buyer role]

**Key Insight:** [1-2 sentences on what matters to this segment]

[Repeat for each account category]

---

## Patterns and Themes

### What Customers DON'T Object To:
- [List of accepted/unquestioned aspects]

### What Customers DO Object To:
- [List of recurring concerns]

---

## Resolution Effectiveness

### What Worked Well (Resolved Objections):
1. [Topic] - [How it was resolved]

### What Needs Improvement (Lingered/Deferred):
1. [Topic] - [What's missing]

---

## Files Generated
1. `[path]/objections_analysis.json` - Structured data format
2. `[path]/objections_summary.md` - This summary document
```

---

## Output File Naming Convention

For each analysis run, generate:
- `objections_[product]_[ranks].json` - Raw extraction data
- `OBJECTION_SYNTHESIS_REPORT.md` - Comprehensive markdown report

Save all files to the same run directory as the source transcripts.
