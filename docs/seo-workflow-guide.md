# SEO Automation Workflow Guide - Codeteki

## Overview
Codeteki's SEO tool integrates **Ubersuggest keyword data** with **ChatGPT-powered content generation** to automate your SEO workflow.

---

## 🎯 Complete Workflow: Ubersuggest → AI Content Generation

### Step 1: Export Keywords from Ubersuggest

1. Go to [Ubersuggest](https://neilpatel.com/ubersuggest/)
2. Enter your target keyword (e.g., "AI automation tools")
3. Navigate to **Keyword Ideas**
4. Click **Export to CSV** button
5. Save the file (e.g., `ai-automation-keywords.csv`)

**What's in the CSV:**
- Keyword
- Search Volume
- SEO Difficulty
- Paid Difficulty
- CPC
- Trend data

---

### Step 2: Upload to Codeteki Admin

1. Login to **Django Admin**: `https://www.codeteki.au/admin/`
2. Navigate to **🔍 SEO Tools & Automation → 📤 Upload Ubersuggest Data**
3. Fill in the form:
   - **Name**: Descriptive name (e.g., "AI Automation Campaign - Nov 2024")
   - **Source**: Select "Ubersuggest Keyword Export" (default)
   - **CSV File**: Upload your exported file
   - **Notes**: Optional campaign notes
4. Click **Save**

**What happens automatically:**
- ✅ System parses the CSV
- ✅ Imports all keywords
- ✅ Calculates priority scores based on:
  - Search volume
  - SEO difficulty
  - Keyword intent (informational, commercial, transactional)
- ✅ Creates keyword clusters (groups related keywords by theme)
- ✅ Generates cluster summaries

---

### Step 3: Process the Upload

**Option A: Automatic processing (recommended)**
The system automatically processes uploads on save.

**Option B: Manual processing**
If status shows "Pending":
1. Go to **SEO Data Uploads** list
2. Select your upload
3. Choose **Actions → Process selected CSV uploads**
4. Click **Go**

**Processing results:**
- Keywords imported: ~500-2000 (depending on export)
- Clusters created: ~10-30 thematic groups
- Status changes to: "Processed"

---

### Step 4: Generate AI Content Recommendations

1. Go to **SEO Data Uploads** list
2. Select your processed upload(s)
3. Choose **Actions → Generate AI playbooks for selected uploads**
4. Click **Go**

**What ChatGPT generates:**
1. **Opportunity Overview**: Quick-win topics + pillar content themes
2. **Content Briefs** (per cluster):
   - Suggested title
   - Hook/intro angle
   - H2/H3 outline
   - CTA ideas
3. **Meta Tag Kits** (per cluster):
   - Page title (<60 chars)
   - Meta description (<155 chars)
   - URL slug
   - FAQ schema questions

**Processing time:** ~30-60 seconds per upload

---

### Step 5: Generate Blog Post Drafts

Want to create actual blog posts from your keywords?

1. Go to **SEO Data Uploads** list
2. Select your upload(s)
3. Choose **Actions → Generate blog drafts from keyword clusters**
4. Click **Go**

**What happens:**
- System selects top 3 keyword clusters (highest priority)
- ChatGPT writes full blog post drafts:
  - SEO-optimized title
  - Complete article content (800-1200 words)
  - Meta description
  - Slug
- Saves as **draft** blog posts in **Blog & Content**

---

## 📊 Viewing & Using Generated Content

### AI Recommendations
1. Navigate to **🔍 SEO Tools & Automation → AI Recommendations**
2. Filter by:
   - **Category**: Opportunity Overview, Content Brief, Meta Tags, FAQ
   - **Status**: Generated, Draft, Error
3. Click any recommendation to view:
   - ChatGPT's response
   - Source keywords
   - Token usage
   - Related cluster

### Blog Drafts
1. Navigate to **📝 Blog & Content → Blog Posts**
2. Filter by **Published = No** to see drafts
3. Review and edit content
4. Set **Is Published = True** when ready
5. Set publish date

### Keyword Clusters
1. Navigate to **🔍 SEO Tools & Automation → Keyword Clusters**
2. View clusters sorted by priority score
3. See:
   - Cluster label (theme)
   - Keyword count
   - Average search volume
   - Average difficulty
   - Intent classification

### Individual Keywords
1. Navigate to **🔍 SEO Tools & Automation → Keywords**
2. Search or filter keywords
3. View detailed metrics:
   - Search volume
   - SEO difficulty
   - CPC
   - Intent
   - Priority score
   - Assigned cluster

---

## 🎨 Applying Content to Your Site

### Use AI Content Briefs for Page Updates

**Example: Update Home Page Hero Section**
1. Go to **AI Recommendations**
2. Find a content brief for your target keyword cluster
3. Copy the suggested title and description
4. Navigate to **🏠 Home Page Content → Hero Section**
5. Paste and customize the content
6. Save changes

**Example: Update Service Descriptions**
1. Find relevant content brief from AI Recommendations
2. Navigate to **🏠 Home Page Content → Services Overview**
3. Update service descriptions using AI-generated outlines
4. Save changes

### Apply Meta Tags to Pages

1. Go to **AI Recommendations → Meta Kits**
2. Copy generated meta title & description
3. Navigate to **🔍 SEO Tools & Automation → Page SEO Settings**
4. Select the target page (Home, Services, AI Tools, etc.)
5. Paste meta tags
6. Save changes

---

## 🔧 Configuration

### ChatGPT Settings

The AI engine uses settings from your `.env` file:

```bash
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_SEO_MODEL=gpt-4o-mini  # Options: gpt-4o-mini, gpt-4o, gpt-3.5-turbo
```

**Models comparison:**
- **gpt-4o-mini**: Fast, cost-effective, good quality (default)
- **gpt-4o**: Best quality, slower, more expensive
- **gpt-3.5-turbo**: Fastest, cheapest, acceptable quality

### Priority Score Calculation

Keywords are scored based on:
- **Search Volume** (40% weight): Higher = better
- **SEO Difficulty** (30% weight): Lower = better
- **Intent Match** (20% weight): Transactional > Commercial > Informational
- **Keyword Type** (10% weight): Long-tail > Mid-tail > Short-tail

Formula:
```
priority_score = (volume_score * 0.4) + (difficulty_score * 0.3) + (intent_score * 0.2) + (type_score * 0.1)
```

---

## 🎯 Best Practices

### 1. Campaign Organization
- Create separate uploads for different topics/campaigns
- Use descriptive names: "AI Tools - Q4 2024" not "keywords.csv"
- Add notes about target audience or goals

### 2. Keyword Selection
- Export 500-1000 keywords per campaign
- Include both short-tail and long-tail keywords
- Mix informational and transactional intent

### 3. Content Review
- **Always review AI-generated content** before publishing
- Customize with your brand voice
- Add specific examples/case studies
- Verify factual accuracy

### 4. Iterative Improvement
- Regenerate recommendations if not satisfied:
  - Select upload → Actions → Generate AI playbooks (with refresh)
- Adjust target keywords based on results
- Track performance of published content

### 5. Content Application Strategy
- **Quick wins**: Start with low-difficulty, high-volume keywords
- **Pillar content**: Use cluster briefs for comprehensive guides
- **Meta tags**: Update all pages with SEO-optimized tags
- **Blog cadence**: Publish 2-3 AI-assisted posts per week

---

## 🔍 Troubleshooting

### Issue: "AI is disabled. Provide OPENAI_API_KEY"
**Solution:**
1. Add `OPENAI_API_KEY=sk-proj-...` to backend/.env
2. Restart Gunicorn: `sudo systemctl restart gunicorn`

### Issue: Upload status stuck on "Pending"
**Solution:**
1. Check upload for errors in admin
2. Manually trigger: Actions → Process selected CSV uploads
3. Check logs: `sudo journalctl -u gunicorn -n 100`

### Issue: CSV upload fails
**Common causes:**
- Wrong CSV format (must be Ubersuggest export)
- Corrupted file
- Missing required columns

**Solution:**
- Re-export from Ubersuggest
- Verify CSV has columns: Keyword, Vol, SD, PD, CPC

### Issue: No clusters created
**Solution:**
- Upload needs at least 10 keywords to create clusters
- Re-export with more keyword variations
- Check that keywords are related (clustering groups similar terms)

---

## 📈 Admin Navigation Guide

Your admin is now organized by pages:

```
🏠 Home Page Content
   ├── Hero Section
   ├── Services Overview
   ├── Business Impact
   ├── ROI Calculator
   ├── Why Choose Us
   ├── Testimonials
   ├── Stats & Metrics
   └── CTA Sections

🤖 AI Tools Page
   ├── AI Tools Section
   └── AI Tools

📞 Contact Page
   ├── Contact Methods
   ├── Contact Inquiries
   └── FAQ Categories

🎬 Demos Page
   └── Demo Showcases

📝 Blog & Content
   ├── Blog Posts
   ├── Knowledge Categories
   └── Knowledge Articles

💰 Pricing
   └── Pricing Plans

🔍 SEO Tools & Automation
   ├── 📤 Upload Ubersuggest Data (quick upload)
   ├── SEO Data Uploads
   ├── Keyword Clusters
   ├── Keywords
   ├── AI Recommendations
   └── Page SEO Settings

💬 Chatbot & Leads
   ├── Chatbot Settings
   ├── Conversations
   └── Chat Leads

⚙️ Global Settings
   ├── Site Settings
   ├── Footer Section
   ├── Navigation Menus
   └── Service Process Steps
```

---

## 💡 Advanced Workflows

### Workflow 1: Topic Cluster Strategy
1. Upload broad keyword (e.g., "digital marketing")
2. Generate AI recommendations
3. Identify top 5 clusters
4. Create 1 pillar page (main cluster) + 4 supporting blog posts
5. Interlink content using suggested keywords

### Workflow 2: Competitor Gap Analysis
1. Export competitor keywords from Ubersuggest
2. Upload to Codeteki
3. Review clusters for gaps in your content
4. Generate blog drafts for missing topics
5. Publish and optimize

### Workflow 3: Seasonal Content Planning
1. Export seasonal keywords (e.g., "black friday ai tools")
2. Upload 4-6 weeks before event
3. Generate content briefs
4. Batch create blog posts
5. Schedule publishing dates

---

## 🎉 Quick Start Checklist

- [ ] Export keywords from Ubersuggest
- [ ] Upload CSV to **SEO Data Uploads**
- [ ] Verify processing completed (check row_count)
- [ ] Run "Generate AI playbooks" action
- [ ] Review AI Recommendations
- [ ] (Optional) Generate blog drafts
- [ ] Apply best content to your pages
- [ ] Update Page SEO meta tags
- [ ] Publish blog posts
- [ ] Monitor performance

---

## Support

For questions or issues:
- Check server logs: `sudo journalctl -u gunicorn -f`
- Review error messages in admin
- Verify OpenAI API key is valid
- Check CSV format matches Ubersuggest export

---

**Last Updated:** November 2024
**Version:** 1.0
