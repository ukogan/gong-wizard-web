# Gong Transcript Wizard

A Flask web application that downloads and processes Gong call recordings to extract relevant customer conversation snippets. The tool filters calls by product topics, identifies external vs internal speakers, and generates ranked transcript files optimized for AI analysis.

## Overview

This tool connects to the Gong API to:
1. Download call transcripts within a specified date range
2. Filter calls by product/topic relevance using keywords and Gong trackers
3. Classify speakers as internal (R-Zero) or external (customer)
4. Format transcripts with external speaker content emphasized
5. Rank calls by keyword relevance and generate downloadable files

## Processing Pipeline

### Step 1: Configuration Loading

On startup, the application loads configuration data from a [Google Sheet](https://docs.google.com/spreadsheets/d/1rOzUYCNSrxjwPI5LVUS5D7vWXRN1SIAE0gsiPIgv5l0) containing:

| Sheet | Purpose |
|-------|---------|
| Product Mappings | Regex patterns to identify product mentions in call content |
| Tracker Mappings | Normalize Gong tracker names (e.g., map variations to canonical names) |
| Tracker to Product | Map Gong trackers directly to products |
| Call ID Overrides | Manual account name overrides for specific calls |
| Account Name Mappings | Normalize company name variations |
| Owner Account Names | Accounts classified as "owners" (vs tenants) |
| Target Domains | Website domains for owner organizations |
| Tenant Domains | Website domains for tenant organizations |
| Internal Domains | Email domains considered internal (R-Zero, subdomains) |
| Internal Speakers | Specific individuals always classified as internal |
| Excluded Domains | Domains to filter out entirely |
| Excluded Account Names | Accounts to filter out entirely |
| Always Include Domains | Domains that override filtering for specific products |

### Step 2: User Input

User provides via web form:
- **Gong API Credentials**: Access key and secret key
- **Date Range**: Start and end date (max 6 months)
- **Products**: Which product categories to include:
  - Secure Air
  - EaaS and Savings Measurement
  - ODCV
  - Occupancy Analytics
  - IAQ Monitoring

### Step 3: Gong API Data Fetch

The application makes three types of API calls:

1. **Call List** (`GET /v2/calls`): Retrieve all call IDs in date range
2. **Call Details** (`POST /v2/calls/extensive`): Fetch metadata, parties, trackers, topics, key points, highlights, outlines (batched in groups of 10)
3. **Transcripts** (`POST /v2/calls/transcript`): Fetch full transcripts (batched in groups of 50)

### Step 4: Product Detection

Each call is tagged with relevant products based on:

1. **Content Keyword Matching**: Searches call title, brief, outline, key points, and highlights for product-specific regex patterns defined in Google Sheets
2. **Gong Tracker Matching**: Maps Gong's native trackers to products using the tracker mappings

### Step 5: Account Resolution

Determines the account/customer for each call:

1. Check manual override by call ID
2. Extract from Salesforce context (account name field)
3. Apply account name normalization mappings
4. Fall back to website domain
5. Fall back to most common external email domain

### Step 6: Call Filtering

Calls are included/excluded based on:

- **Exclusions**: Skip calls with excluded account names or email domains
- **Product Match**: Call must match at least one selected product
- **Always Include**: Override to include calls from specific domains for specific products

### Step 7: Speaker Classification

Each speaker is classified as Internal [I] or External [E]:

**Internal Speaker Detection:**
- Email domain matches internal domains list (exact or subdomain)
- Speaker name appears in internal speakers list

This addresses R-Zero domain emails that aren't Gong users—Gong may misclassify them as external, but the app corrects this using the internal domains/speakers configuration.

### Step 8: Transcript Formatting

Transcripts are processed with:

1. **Speaker Grouping**: Consecutive sentences from the same speaker are combined
2. **External Emphasis**: External speaker text is converted to ALL CAPS for visibility
3. **EaaS Tagging**: For EaaS product, keyword matches are tagged with `[ENERGY_SAVINGS: keyword]`
4. **Timestamp Formatting**: Each speaker block shows `MM:SS | Name [I/E]`

**Output Format Example:**
```
0:30 | John [I]
Great question about the implementation timeline.

0:45 | Sarah [E]
WE'RE LOOKING TO DEPLOY THIS ACROSS ALL OUR BUILDINGS BY Q2. THE MAIN CONCERN IS INTEGRATION WITH OUR EXISTING BMS.
```

### Step 9: Call Ranking

Calls are ranked within each product category:

1. **Score Calculation**: Count keyword pattern matches in call content
2. **Owner Bonus**: Calls from "owner" organizations get 1.33x score multiplier
3. **Sorting**: Calls sorted by score (highest first)

### Step 10: File Generation

**Transcript Files:**
- Split into buckets of 5 calls per file
- Named by product abbreviation and rank: `ODCV_rank_1.txt`, `SA_rank_2.txt`, etc.
- Each file contains full formatted transcripts with metadata headers

**Product Abbreviations:**
| Product | Abbreviation |
|---------|--------------|
| Secure Air | SA |
| ODCV | ODCV |
| Occupancy Analytics | Occ |
| IAQ Monitoring | IAQ |
| EaaS and Savings Measurement | EaaS |

**CSV Summary:**
- One row per call with columns:
  - `call_id`, `call_title`, `call_date`
  - `product_tags` (pipe-separated)
  - `org_type` (owner/tenant)
  - `account_name`, `account_website`, `account_industry`
  - `transcript_bucket` (which product file it's in)
  - `call_rank` (ranking within product)
  - `call_summary` (Gong's brief)

## Product Precedence

When a call matches multiple products, it's assigned to one transcript bucket based on precedence order:
1. EaaS and Savings Measurement
2. ODCV
3. Secure Air
4. Occupancy Analytics
5. IAQ Monitoring

## Gong Topic Filtering

The application uses configurable keyword patterns rather than relying solely on Gong's built-in topics. This allows:
- Custom patterns not trainable in Gong's AI
- Filtering out low-value segments (small talk, conversation open/close)
- Product-specific keyword detection

## Development

### Requirements
- Python 3.12+
- Flask
- pandas
- requests
- pytz

### Local Setup
```bash
pip install -r requirements.txt
python3 app.py
```

### Docker
```bash
docker build -t gong-wizard .
docker run -p 10000:10000 gong-wizard
```

### Environment Variables
- `PORT`: Server port (default: 5000)
- `FLASK_SECRET_KEY`: Session secret key (auto-generated if not set)

## API Rate Limits

The application batches API calls to respect Gong's rate limits:
- Call details: 10 calls per request
- Transcripts: 50 calls per request
- Date range: Maximum 6 months per query

## Security Notes

- API credentials are submitted per-session (not stored)
- All API calls proxied through the backend
- Temporary files stored in `/tmp/gong_output`

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
│                    (index.html + form)                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        Flask Server                          │
│                         (app.py)                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              initialize_data()                       │    │
│  │         (Load Google Sheets config)                  │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              GongAPIClient                           │    │
│  │  - fetch_call_list()                                 │    │
│  │  - fetch_call_details()                              │    │
│  │  - fetch_transcript()                                │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Processing Functions                    │    │
│  │  - determine_products()                              │    │
│  │  - resolve_account_name()                            │    │
│  │  - should_include_call()                             │    │
│  │  - is_internal_speaker()                             │    │
│  │  - format_transcript()                               │    │
│  │  - calculate_ranking_score()                         │    │
│  │  - generate_files()                                  │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│      Gong API           │     │    Google Sheets        │
│  (us-11211.api.gong.io) │     │   (Configuration)       │
└─────────────────────────┘     └─────────────────────────┘
```

## Output Files Location

Generated files are stored in timestamped run folders within the `runs/` directory:

```
runs/
  run_20250114_143052_2024-10-01_to_2024-12-31/
    call-summary_2024-10-01_2024-12-31.csv
    ODCV_rank_1.txt
    ODCV_rank_2.txt
    SA_rank_1.txt
    ...
  run_20250115_091523_2025-01-01_to_2025-01-14/
    ...
```

Each run creates a new folder named: `run_{timestamp}_{start_date}_to_{end_date}`

This structure allows:
- Multiple runs to be preserved without overwriting
- Easy syncing to GitHub for analysis (`git add runs/ && git commit`)
- Clear tracking of when each dataset was generated

### Railway Deployment Workflow

When running on Railway (or other cloud hosting), files are saved on the server, not locally. To sync results to GitHub:

1. **Run the wizard** on Railway and process your calls
2. **Download the ZIP** using the "Download All as ZIP" button
3. **Unzip locally** into your `runs/` folder:
   ```bash
   cd /path/to/GongGPT
   unzip ~/Downloads/run_YYYYMMDD_HHMMSS_*.zip -d runs/
   ```
4. **Commit and push**:
   ```bash
   git add runs/
   git commit -m "Add Gong analysis run"
   git push
   ```
