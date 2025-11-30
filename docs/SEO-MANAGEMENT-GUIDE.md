# SEO Management Guide

The SEO Management section handles keyword research, page-level SEO settings, and AI recommendations from CSV data uploads.

## Overview

| Feature | Description |
|---------|-------------|
| Page SEO | Meta tags, OG data, canonical URLs per page |
| SEO Data Upload | Import CSV from Ubersuggest, Ahrefs, SEMrush |
| Keywords | Track keywords with volume, difficulty, CPC |
| Keyword Clusters | Group related keywords by topic |
| AI Recommendations | ChatGPT-generated content briefs |

---

## Quick Start Workflow

### Step 1: Set Up Page SEO

1. Go to **Admin > SEO Management > Page SEO**
2. Add entries for each important page:
   - **Page Identifier**: Unique slug (e.g., `home`, `services`, `contact`)
   - **Meta Title**: 50-60 characters
   - **Meta Description**: 150-160 characters
   - **Canonical URL**: Full URL
   - **OG Image**: Social sharing image

### Step 2: Upload Keyword Data

1. Export CSV from your SEO tool (Ubersuggest, Ahrefs, etc.)
2. Go to **SEO Management > SEO Data Uploads**
3. Click **Add SEO Data Upload**
4. Select source (Ubersuggest, Ahrefs, SEMrush, Generic)
5. Upload CSV file
6. Select the upload and run **Process upload** action

### Step 3: Review Keywords

1. Go to **SEO Management > Keywords**
2. View imported keywords with:
   - Search Volume
   - Keyword Difficulty
   - CPC
   - Trend data
3. Filter by difficulty or volume

### Step 4: Create Keyword Clusters

1. Go to **SEO Management > Keyword Clusters**
2. Group related keywords by topic
3. Assign primary and secondary keywords

### Step 5: Generate AI Recommendations

1. Select keywords or clusters
2. Run **Generate AI playbooks** action
3. View recommendations in **SEO Management > AI Recommendations**

---

## Components

### Page SEO
Per-page SEO configuration used by the frontend.

**Fields:**
- Page Identifier (slug)
- Meta Title, Meta Description
- Canonical URL
- OG Title, OG Description, OG Image
- Robots directive (index/noindex)
- Schema markup (JSON-LD)

**API Endpoint:**
```
GET /api/page-seo/{page_identifier}/
```

### SEO Data Upload
Import keyword data from various sources.

**Supported Sources:**
- Ubersuggest
- Ahrefs
- SEMrush
- Generic CSV

**CSV Requirements:**
| Column | Description |
|--------|-------------|
| keyword | The search term |
| volume | Monthly search volume |
| difficulty | Keyword difficulty (0-100) |
| cpc | Cost per click |
| trend | Search trend data |

**Actions:**
- Process upload (imports keywords)
- Generate AI playbooks (creates recommendations)

### Keywords
Individual keyword records.

**Fields:**
- Keyword text
- Search Volume
- Keyword Difficulty (0-100)
- CPC (cost per click)
- Trend data
- Source (which upload)

**Filters:**
- By difficulty range
- By volume range
- By source

### Keyword Clusters
Group keywords by topic/intent.

**Fields:**
- Cluster Name
- Primary Keyword
- Secondary Keywords (many-to-many)
- Topic category

**Use Cases:**
- Content planning
- Page targeting
- Internal linking strategy

### AI SEO Recommendations
ChatGPT-generated content strategies.

**Fields:**
- Keyword/Cluster reference
- Recommendation type
- Content brief
- Title suggestions
- Outline/structure
- Target word count

**Actions:**
- Generate AI playbooks
- Generate blog drafts

---

## Integration with Frontend

### Using Page SEO in React

```jsx
// Fetch page SEO data
const response = await fetch('/api/page-seo/home/');
const seo = await response.json();

// Apply to page
<Helmet>
  <title>{seo.meta_title}</title>
  <meta name="description" content={seo.meta_description} />
  <meta property="og:title" content={seo.og_title} />
  <meta property="og:description" content={seo.og_description} />
  <meta property="og:image" content={seo.og_image} />
  <link rel="canonical" href={seo.canonical_url} />
</Helmet>
```

---

## Configuration

### Required Environment Variables

```env
# OpenAI for AI Recommendations
OPENAI_API_KEY=sk-...
OPENAI_SEO_MODEL=gpt-4o-mini
```

---

## Best Practices

### Page SEO
1. Every page should have unique meta title and description
2. Include target keyword in meta title
3. Keep meta descriptions actionable (include CTA)
4. Set canonical URLs to prevent duplicate content

### Keyword Research
1. Import data regularly (monthly)
2. Focus on keywords with:
   - High volume + Low difficulty
   - High intent (transactional/commercial)
3. Create clusters around topic themes

### AI Recommendations
1. Use AI briefs as starting points, not final copy
2. Review and customize for your brand voice
3. Validate recommendations against actual SERP results

---

## Workflow Summary

```
Export CSV from SEO Tool → Upload to SEO Data Uploads → Process Upload → Review Keywords → Create Clusters → Generate AI Recommendations → Create Content → Update Page SEO
```

---

## Comparison: SEO Management vs SEO Engine

| Aspect | SEO Management | SEO Engine |
|--------|---------------|------------|
| Purpose | Keyword research & page config | Technical audits |
| Data Source | CSV imports, manual entry | Lighthouse, PageSpeed, Search Console |
| AI Use | Content briefs & strategies | Technical fix recommendations |
| Output | Page SEO settings, content ideas | Audit scores, issue lists |
| Frequency | Ongoing content planning | Periodic site audits |

**Use Both Together:**
1. SEO Engine audits identify technical issues
2. SEO Management plans content strategy
3. AI Analysis (Engine) + AI Recommendations (Management) = Full SEO coverage
