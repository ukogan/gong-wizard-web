#!/usr/bin/env python3
"""
Analyze Gong call transcripts for customer objections.
Reads transcript files and extracts objections with metadata.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Objection indicator phrases
OBJECTION_PHRASES = [
    r"concerned about",
    r"worried",
    r"not sure",
    r"what about",
    r"how do we know",
    r"the problem is",
    r"we can't",
    r"that's expensive",
    r"challenge",
    r"issue",
    r"concern",
    r"hesitat",
    r"risk",
    r"difficult",
    r"complicated",
    r"limitation",
    r"doesn't work",
    r"won't work",
    r"can't do",
    r"unable to",
    r"struggle",
    r"problem with"
]

# Filter patterns for partner/consultant calls
PARTNER_INDICATORS = [
    r"newcomb[\s&]+boyd",
    r"gridium",
    r"consultant",
    r"advising r[\-\s]?zero",
    r"channel partner",
    r"shared account",
    r"joint opportunit"
]


def parse_transcript(file_path: str) -> List[Dict[str, Any]]:
    """Parse transcript file and extract call information."""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into individual calls
    calls = re.split(r'\nCALL: ', content)

    results = []

    for call_text in calls[1:]:  # Skip header
        call_data = parse_call(call_text)
        if call_data:
            results.append(call_data)

    return results


def parse_call(call_text: str) -> Dict[str, Any]:
    """Parse individual call data."""

    # Extract metadata
    call_id_match = re.search(r"^'?([^\n]+)", call_text)
    date_match = re.search(r"DATE:\s*([^\n]+)", call_text)
    account_match = re.search(r"ACCOUNT:\s*([^\n]+)", call_text)
    industry_match = re.search(r"INDUSTRY:\s*([^\n]+)", call_text)
    org_type_match = re.search(r"ORG TYPE:\s*([^\n]+)", call_text)

    if not call_id_match or not date_match or not account_match:
        return None

    call_id = call_id_match.group(1).strip()
    date = date_match.group(1).strip()
    account = account_match.group(1).strip()
    industry = industry_match.group(1).strip() if industry_match else ""
    org_type = org_type_match.group(1).strip() if org_type_match else ""

    # Extract speakers
    speakers_section = re.search(r"SPEAKERS:\s*\n(.*?)\n---", call_text, re.DOTALL)
    speakers = []
    external_speakers = []

    if speakers_section:
        speaker_lines = speakers_section.group(1).strip().split('\n')
        for line in speaker_lines:
            speakers.append(line.strip())
            if '[E]' in line:
                external_speakers.append(line.strip())

    # Check if this is a partner/consultant call
    is_partner_call = is_partner_or_consultant(call_text, account, speakers)

    # Extract transcript lines
    transcript_match = re.search(r'\n---\s*\n(.*)', call_text, re.DOTALL)
    transcript = transcript_match.group(1).strip() if transcript_match else ""

    # Find objections
    objections = find_objections(transcript, external_speakers)

    return {
        'call_id': call_id,
        'date': date,
        'account': account,
        'industry': industry,
        'org_type': org_type,
        'speakers': speakers,
        'external_speakers': external_speakers,
        'is_partner_call': is_partner_call,
        'objections': objections
    }


def is_partner_or_consultant(call_text: str, account: str, speakers: List[str]) -> bool:
    """Determine if this is a partner/consultant call to filter out."""

    # Be conservative - only filter if there's clear evidence
    # Check if account is an explicit partner
    explicit_partners = [
        r"newcomb[\s&]+boyd",
        r"gridium",
        r"distech"
    ]

    for pattern in explicit_partners:
        if re.search(pattern, account, re.IGNORECASE):
            # Additional check - is this a call WITH them or TO them?
            # If external speaker includes consultant title and discussing R-Zero introduction
            if re.search(r"consultant", " ".join(speakers), re.IGNORECASE):
                if re.search(r"advising.*r[\-\s]?zero|introducing.*r[\-\s]?zero", call_text, re.IGNORECASE):
                    return True

    # Check for explicit language indicating partner/channel relationship
    partner_phrases = [
        r"channel partner.*discuss",
        r"shared account.*joint",
        r"advising r[\-\s]?zero on",
        r"consulting.*for r[\-\s]?zero"
    ]

    for pattern in partner_phrases:
        if re.search(pattern, call_text, re.IGNORECASE):
            return True

    return False


def find_objections(transcript: str, external_speakers: List[str]) -> List[Dict[str, Any]]:
    """Find objections in transcript from external speakers."""

    objections = []

    # Split into individual utterances
    utterances = re.split(r'\n\n', transcript)

    for utterance in utterances:
        # Parse timestamp and speaker
        match = re.match(r'(\d+:\d+)\s*\|\s*([^\n]+)\n(.*)', utterance, re.DOTALL)
        if not match:
            continue

        timestamp = match.group(1).strip()
        speaker = match.group(2).strip()
        text = match.group(3).strip()

        # Only process external speaker utterances (ALL CAPS)
        if not re.match(r'^[A-Z\s,\.\!\?\'\"\-\(\)]+$', text[:100]) and text:
            continue

        # Look for objection phrases
        for phrase_pattern in OBJECTION_PHRASES:
            if re.search(phrase_pattern, text, re.IGNORECASE):
                objection = extract_objection(timestamp, speaker, text, phrase_pattern)
                objections.append(objection)
                break  # Only count once per utterance

    return objections


def extract_objection(timestamp: str, speaker: str, text: str, trigger_phrase: str) -> Dict[str, Any]:
    """Extract objection details."""

    # Truncate quote to 200 chars
    quote = text[:200]
    if len(text) > 200:
        quote += "..."

    # Classify objection type
    obj_type = classify_objection_type(text)

    # Infer persona from context
    persona = infer_persona(speaker, text)

    # Assess resolution status
    resolution_status = "lingered"  # Default, would need context to determine

    # Assess severity
    severity = assess_severity(text)

    # Extract topic
    topic = extract_topic(text)

    return {
        'timestamp': timestamp,
        'speaker': speaker,
        'quote': quote,
        'type': obj_type,
        'persona': persona,
        'resolution_status': resolution_status,
        'severity': severity,
        'topic': topic,
        'trigger_phrase': trigger_phrase
    }


def classify_objection_type(text: str) -> str:
    """Classify objection as technical, business, or process."""

    technical_keywords = [
        r"integrat", r"protocol", r"bacnet", r"wireless", r"sensor",
        r"system", r"data", r"architecture", r"API", r"compatibility"
    ]

    business_keywords = [
        r"cost", r"expensive", r"budget", r"savings", r"ROI",
        r"value", r"pricing", r"contract"
    ]

    process_keywords = [
        r"install", r"implement", r"deploy", r"timeline", r"approval",
        r"pilot", r"test", r"validation", r"stakeholder"
    ]

    for pattern in technical_keywords:
        if re.search(pattern, text, re.IGNORECASE):
            return "technical"

    for pattern in business_keywords:
        if re.search(pattern, text, re.IGNORECASE):
            return "business"

    for pattern in process_keywords:
        if re.search(pattern, text, re.IGNORECASE):
            return "process"

    return "technical"  # Default


def infer_persona(speaker: str, text: str) -> str:
    """Infer speaker role/persona."""

    if re.search(r"director|VP|executive|chief", speaker, re.IGNORECASE):
        return "executive"
    elif re.search(r"engineer|technical|architect", speaker, re.IGNORECASE):
        return "engineer"
    elif re.search(r"manager|facility|operations", speaker, re.IGNORECASE):
        return "facilities_manager"
    elif re.search(r"consultant", speaker, re.IGNORECASE):
        return "consultant"
    else:
        return "unknown"


def assess_severity(text: str) -> str:
    """Assess objection severity."""

    blocker_keywords = [
        r"can't", r"won't work", r"impossible", r"deal breaker",
        r"must have", r"required", r"critical"
    ]

    concern_keywords = [
        r"concerned", r"worried", r"hesitant", r"uncertain"
    ]

    for pattern in blocker_keywords:
        if re.search(pattern, text, re.IGNORECASE):
            return "blocker"

    for pattern in concern_keywords:
        if re.search(pattern, text, re.IGNORECASE):
            return "concern"

    return "question"


def extract_topic(text: str) -> str:
    """Extract 2-5 word topic label."""

    # Look for key domain terms
    if re.search(r"integrat|bacnet|API|protocol", text, re.IGNORECASE):
        return "system integration"
    elif re.search(r"wireless|sensor|device|battery", text, re.IGNORECASE):
        return "sensor technology"
    elif re.search(r"data|layer|cloud|on[\-\s]prem", text, re.IGNORECASE):
        return "data architecture"
    elif re.search(r"install|deploy|implementation", text, re.IGNORECASE):
        return "deployment process"
    elif re.search(r"cost|expensive|pricing|budget", text, re.IGNORECASE):
        return "cost concerns"
    elif re.search(r"control|sequence|logic|BMS", text, re.IGNORECASE):
        return "control sequences"
    elif re.search(r"lab|research|space", text, re.IGNORECASE):
        return "lab operations"
    elif re.search(r"occupancy|people counting|utilization", text, re.IGNORECASE):
        return "occupancy detection"
    else:
        return "general inquiry"


def main():
    input_file = "/Users/urikogan/code/GongGPT/runs/run_20260114_140045_2025-12-01_to_2026-01-14/EaaS_rank_6.txt"
    output_file = "/Users/urikogan/code/GongGPT/runs/run_20260114_140045_2025-12-01_to_2026-01-14/objections_rank_6.json"

    print(f"Analyzing transcript: {input_file}")

    calls = parse_transcript(input_file)

    # Filter and process results
    results = {
        'analysis_date': datetime.now().isoformat(),
        'source_file': input_file,
        'total_calls': len(calls),
        'filtered_calls': [],
        'prospect_calls': []
    }

    for call in calls:
        if call['is_partner_call']:
            results['filtered_calls'].append({
                'call_id': call['call_id'],
                'date': call['date'],
                'account': call['account'],
                'reason': 'Partner/consultant call'
            })
        else:
            results['prospect_calls'].append({
                'call_id': call['call_id'],
                'date': call['date'],
                'account': call['account'],
                'industry': call['industry'],
                'org_type': call['org_type'],
                'external_speakers': call['external_speakers'],
                'objection_count': len(call['objections']),
                'objections': call['objections']
            })

    # Write results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nAnalysis complete!")
    print(f"Total calls analyzed: {results['total_calls']}")
    print(f"Filtered (partner/consultant): {len(results['filtered_calls'])}")
    print(f"Prospect calls: {len(results['prospect_calls'])}")
    print(f"\nTotal objections found: {sum(c['objection_count'] for c in results['prospect_calls'])}")
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
