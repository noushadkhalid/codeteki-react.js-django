# SEO Engine Guide

The SEO Engine provides automated website auditing with Lighthouse, PageSpeed Insights, and AI-powered analysis.

## Overview

| Feature | Description |
|---------|-------------|
| Site Audits | Run Lighthouse audits on multiple URLs |
| AI Analysis | ChatGPT-powered SEO recommendations |
| PageSpeed Results | Google PageSpeed Insights integration |
| Search Console | Google Search Console data sync |

---

## Quick Start Workflow

### Step 1: Create a Site Audit

1. Go to **Admin > SEO Engine > Site Audits**
2. Click **Add Site Audit**
3. Fill in:
   - **Name**: Descriptive name (e.g., "Codeteki Homepage Audit")
   - **Domain**: Target domain (e.g., `codeteki.au`)
   - **Strategy**: Mobile or Desktop
   - **URLs to Audit**: Enter URLs (one per line)
4. Click **Save**

### Step 2: Run Lighthouse Audit

1. Select the audit from the list
2. Choose **Action**: "Run Lighthouse audit"
3. Click **Go**
4. Wait for the loading screen to complete (30-60 seconds per URL)
5. Results appear in Page Audits and Audit Issues

### Step 3: Run PageSpeed Analysis

1. Select the audit
2. Choose **Action**: "Run PageSpeed analysis"
3. Click **Go**
4. View results in **SEO Engine > PageSpeed Results**

### Step 4: Generate AI Analysis

**Option A - Single Audit Analysis:**
1. Select one audit
2. Choose **Action**: "Generate AI analysis"
3. Click **Go**

**Option B - Combined Multi-Source Analysis (Recommended):**
1. Select one or more audits (same domain recommended)
2. Choose **Action**: "Generate COMBINED AI analysis (multi-source)"
3. Click **Go**
4. The system will automatically include:
   - All selected Lighthouse audits
   - PageSpeed Insights data for the same domain
   - Search Console data for the same domain
5. Analysis is saved to the first selected audit

View results in **SEO Engine > AI Analysis** tab.

---

## Combined Analysis Data Sources

| Source | Data Included |
|--------|---------------|
| Site Audits | Scores, page data, issues from selected audits |
| PageSpeed Insights | Performance scores, Core Web Vitals |
| Search Console | Clicks, impressions, CTR, top queries |

The combined analysis provides:
- Cross-source insights (correlating technical issues with search rankings)
- Trend analysis (if multiple audit dates)
- More accurate prioritization based on real traffic impact

---

## Cost-Effective AI Analysis Strategy

AI Analysis uses OpenAI's `gpt-4o-mini` model (~$0.01-0.02 per analysis). To minimize costs:

### When to Run AI Analysis

| Scenario | Recommended Action | Est. Cost |
|----------|-------------------|-----------|
| First audit of a site | Run **Combined Analysis** once | ~$0.01-0.02 |
| Weekly monitoring | Skip AI, just review scores | $0.00 |
| Scores dropped significantly | Run **Combined Analysis** | ~$0.01-0.02 |
| After fixing issues | Run **Single Analysis** to verify | ~$0.005-0.01 |
| Monthly review | Run **Combined Analysis** | ~$0.01-0.02 |

### Recommended Workflow

```
1. Create Site Audit → Run Lighthouse → Run PageSpeed (no AI cost)
         ↓
2. Review scores manually first (free)
         ↓
3. Only run AI Analysis if:
   - First time auditing the site
   - Scores are poor (<70 in any category)
   - You need actionable fix recommendations
         ↓
4. Use COMBINED Analysis (not single) - one API call covers everything
```

### What NOT to Do (Wastes Tokens)

| Wasteful Practice | Better Alternative |
|-------------------|-------------------|
| Running AI on every audit | Run only when scores need investigation |
| Running AI on each page separately | Use Site Audit level analysis |
| Re-running AI after minor changes | Wait until multiple fixes are done |
| Running both Single AND Combined | Just use Combined |

### Cost Summary

- **Lighthouse audit**: Free (runs locally)
- **PageSpeed Insights**: Free (Google API)
- **Search Console Sync**: Free (Google API)
- **AI Analysis**: ~$0.01-0.02 per run

---

## Using AI Analysis with Claude Code

### Export and Fix Issues

1. Go to **SEO Engine > AI Analysis**
2. Select your report
3. Choose **Action**: "Export as Markdown"
4. Download the `.md` file

### In Claude Code

```bash
# Navigate to your project
cd /path/to/your/project

# Start Claude Code
claude

# Paste the analysis
"Here's my SEO analysis. Please fix these issues starting with critical ones:

[Paste markdown content]"
```

### Example Prompts

| Issue Type | Claude Code Prompt |
|------------|-------------------|
| Meta Tags | "Fix missing meta descriptions on these pages: [list]" |
| Images | "Add alt tags and optimize images for LCP" |
| Performance | "Implement lazy loading for below-fold images" |
| Accessibility | "Fix the accessibility issues: [list from report]" |

### Verify Fixes

After Claude Code makes changes:
1. Create a new Site Audit
2. Run Lighthouse audit on the same URLs
3. Compare scores

---

## Components

### Site Audits
Main audit configuration. Stores domain, URLs, and aggregated scores.

**Fields:**
- Name, Domain, Strategy (mobile/desktop)
- URLs to Audit (one per line)
- Scores: Performance, SEO, Accessibility, Best Practices
- Issue counts

**Actions:**
- Run Lighthouse audit
- Run PageSpeed analysis
- Generate AI analysis

### AI Analysis
Separate view for audits with AI-generated recommendations.

**Features:**
- Preview column in list view
- Full formatted analysis display
- Regenerate AI Analysis action
- Export as Markdown action

### Page Audits
Individual page results from Lighthouse.

**Metrics:**
- Performance, SEO, Accessibility, Best Practices scores
- Core Web Vitals: LCP, CLS, FCP, TBT, SI

### Audit Issues
Specific issues found during audits.

**Fields:**
- Severity: Critical, Warning, Info
- Category: Performance, SEO, Accessibility, Best Practices
- Title, Description, Display Value
- Potential savings (ms)

### PageSpeed Results
Google PageSpeed Insights API results.

**Actions:**
- Run PageSpeed Analysis (from list view)
- Results include Core Web Vitals and recommendations

### Search Console Data
Google Search Console metrics.

**Metrics:**
- Clicks, Impressions, CTR, Position
- Query data by date range

### Search Console Sync
Automates Search Console data import.

**Actions:**
- Run Sync action to fetch latest data

---

## Configuration

### Required Environment Variables

```env
# OpenAI for AI Analysis
OPENAI_API_KEY=sk-...
OPENAI_SEO_MODEL=gpt-4o-mini

# Google PageSpeed Insights
GOOGLE_API_KEY=AIza...

# Google Search Console (optional)
GOOGLE_SERVICE_ACCOUNT_FILE=/path/to/credentials.json
GOOGLE_SEARCH_CONSOLE_PROPERTY=https://codeteki.au/
```

### Lighthouse CLI
Installed globally via npm:
```bash
npm install -g lighthouse
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Lighthouse fails | Ensure Chrome is installed; check URL is accessible |
| PageSpeed 403 | Verify GOOGLE_API_KEY is valid |
| AI Analysis empty | Check OPENAI_API_KEY; ensure audit has completed |
| Search Console 403 | Verify property URL matches exactly |
| Loading not showing | Clear browser cache; check JS is loading |

---

## Workflow Summary

```
Site Audits → Run Lighthouse → Generate AI Analysis → AI Analysis tab → Export Markdown → Claude Code → Fix Issues → Re-audit
```
