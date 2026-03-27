import logging, time
from datetime import datetime, timedelta
import anthropic, config
from data.competitors import COMPETITOR_DOMAIN_KEYWORDS, DIRECT_COMPETITOR_NAMES, INDIRECT_COMPETITOR_NAMES

logger = logging.getLogger(__name__)

_SEARCH_SYSTEM = """\
You are a competitive intelligence analyst for AppFolio (APPF), \
the leading cloud property management software platform for residential property managers.

DIRECT competitors: Yardi, RealPage, MRI Software, Entrata, Buildium, Rent Manager, \
ResMan, Propertyware, Doorloop, TurboTenant, Hemlane.

INDIRECT competitors: EliseAI, BetterBot, Knock CRM, Funnel Leasing, LeadSimple, \
Rentvine, SmartRent, Latch.

For each finding output one line:
FINDING|||[Company]|||[investment|product|metrics|partnership|platform_shift|vc_signal]|||[HIGH|MEDIUM]|||[VC firm or N/A]|||[One sentence description]|||[Source URL]

HIGH: direct competitor raises funding/launches AI product/major customer win;
large PM group migrating away from AppFolio; AI leasing tool raises significant capital.
MEDIUM: proptech raises Series B+ for leasing/PM automation; VC thesis on rental housing tech.
Skip LOW. When done: BLOCK_COMPLETE
"""

def _date_range():
    today = datetime.now()
    return f"{(today - timedelta(days=7)).strftime('%B %d')}-{today.strftime('%B %d, %Y')}"

_SEARCH_BLOCKS = [
    {"name": "direct_competitors", "prompt_template": "Search for news from the past 7 days ({date_range}) about AppFolio direct competitors:\n- Yardi Systems: new product launches, AI features, customer wins, Yardi Breeze updates\n- RealPage: product news, AI pricing tool updates, new features\n- MRI Software: funding, acquisitions, new product announcements\n- Entrata: funding, product launches, multifamily customer wins\n- Buildium: product updates, pricing changes, new features\n- Rent Manager: product news, customer announcements\n- Doorloop: funding rounds, product launches, customer growth metrics\nOutput all HIGH and MEDIUM FINDING||| lines, then: BLOCK_COMPLETE"},
    {"name": "ai_proptech_and_vc", "prompt_template": "Search for news from the past 7 days ({date_range}) about:\nPART A - AI leasing and property management technology:\n- EliseAI: funding, product expansion, new property management customers\n- BetterBot: funding, new features, customer wins\n- Knock CRM: funding, product updates, multifamily leasing news\n- Funnel Leasing: funding, partnerships, product launches\n- SmartRent: earnings, new products, property management integrations\n- AI property management software: new startup funding 2026\nPART B - VC investments in proptech:\n- Search: Andreessen Horowitz OR Sequoia proptech OR property management investment 2026\n- Search: Khosla OR General Catalyst rental housing technology investment 2026\n- Search: Bessemer OR Insight Partners property management OR leasing software 2026\n- Search: Fifth Wall OR Metaprop proptech portfolio news 2026\nOutput all HIGH and MEDIUM FINDING||| lines, then: BLOCK_COMPLETE"},
    {"name": "market_signals", "prompt_template": "Search for news from the past 7 days ({date_range}) about broader property management technology market signals:\n- property management software Series B OR C OR D 2026\n- leasing automation OR AI leasing assistant raised funding 2026\n- multifamily technology replaced OR migrated from AppFolio 2026\n- new property management platform startup raised funding {month_year}\n- AppFolio competitor announcement {month_year}\n- VC blog proptech OR rental housing technology investment thesis 2026\nAlso: ResMan, Rentvine, LeadSimple, Hemlane, TurboTenant, Latch smart home property management news.\nOutput all HIGH and MEDIUM FINDING||| lines, then: BLOCK_COMPLETE"},
]

def _parse_findings(text):
    findings = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("FINDING|||"):
            continue
        parts = line.split("|||")
        if len(parts) < 7:
            continue
        findings.append({"company": parts[1].strip(), "type": parts[2].strip().lower(), "relevance": parts[3].strip().upper(), "vc_firm": parts[4].strip(), "description": parts[5].strip(), "source": parts[6].strip(), "found_at": datetime.now().isoformat()})
    return findings

def _run_block(client, block):
    user_prompt = block["prompt_template"].format(date_range=_date_range(), month_year=datetime.now().strftime("%B %Y"))
    messages = [{"role": "user", "content": user_prompt}]
    accumulated = ""
    continuations = 0
    while continuations <= 3:
        response = client.messages.create(model="claude-sonnet-4-6", max_tokens=3000, system=_SEARCH_SYSTEM, tools=[{"type": "web_search_20260209", "name": "web_search"}], messages=messages)
        for cb in response.content:
            if hasattr(cb, "text"):
                accumulated += cb.text + "\n"
        if response.stop_reason == "end_turn":
            break
        elif response.stop_reason == "pause_turn":
            messages.append({"role": "assistant", "content": response.content})
            continuations += 1
        else:
            break
    return _parse_findings(accumulated)

BLOCK_PAUSE_SECONDS = 15

def run_research():
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY, timeout=180.0)
    all_findings = []
    for i, block in enumerate(_SEARCH_BLOCKS):
        logger.info("Search block %d/%d - %s", i + 1, len(_SEARCH_BLOCKS), block["name"])
        try:
            findings = _run_block(client, block)
            all_findings.extend(findings)
            logger.info("  -> %d finding(s)", len(findings))
        except anthropic.RateLimitError:
            logger.warning("Rate limit on '%s' - waiting 60s", block["name"])
            time.sleep(60)
        except Exception as exc:
            logger.error("Block '%s' failed: %s", block["name"], exc)
        if i < len(_SEARCH_BLOCKS) - 1:
            time.sleep(BLOCK_PAUSE_SECONDS)
    seen = set()
    deduped = []
    for f in all_findings:
        key = f"{f['company'].lower()}|{f['type'].lower()}"
        if key not in seen:
            seen.add(key)
            deduped.append(f)
    deduped.sort(key=lambda f: (0 if f.get("relevance") == "HIGH" else 1))
    logger.info("Research complete - %d unique findings", len(deduped))
    return deduped
