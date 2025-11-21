# Codeteki CMS - Complete Admin Guide

## 📋 Table of Contents
1. [Accessing the Admin](#accessing-the-admin)
2. [Dashboard Overview](#dashboard-overview)
3. [Website Pages Management](#website-pages-management)
4. [SEO Management](#seo-management)
5. [Leads & Chatbot](#leads--chatbot)
6. [Site Settings](#site-settings)

---

## 🔐 Accessing the Admin

1. Navigate to: `http://yourdomain.com/admin/`
2. Login with your superuser credentials
3. You'll see the Codeteki CMS dashboard

---

## 📊 Dashboard Overview

The admin is organized into clear sections:

### 📄 WEBSITE PAGES
- **🏠 Home Page** - All home page sections
- **⚙️ Services Page** - Service listings and process steps
- **🤖 AI Tools Page** - AI tool management
- **🎬 Demos Page** - Project demos and showcases
- **❓ FAQ Page** - FAQ categories and items
- **📞 Contact Page** - Contact methods and inquiries

### 🔧 TOOLS & SEO
- **🔍 SEO Management** - Complete SEO control
- **💬 Leads & Chat** - Lead management and chatbot
- **📝 Blog & Content** - Blog posts

### ⚙️ SITE SETTINGS
- Global site settings, footer, navigation, etc.

---

## 🏠 Website Pages Management

### Home Page Sections

#### 1. Hero Section
**Location:** Home Page → Hero Section

**What it controls:** The first thing visitors see on your homepage

**Fields to edit:**
- **Badge** - Small tag above title (e.g., "AI-Powered Business Solutions")
- **Badge Emoji** - Emoji for the badge (e.g., 🚀)
- **Title** - Main heading
- **Highlighted Text** - Text to highlight in gradient
- **Subheading** - Secondary heading
- **Description** - Main description text
- **Gradient Colors** - Customcolors for highlighted text
- **Media/Image** - Upload hero image OR provide image URL
- **CTAs** - Primary and secondary button text and links
- **Is Active** - Toggle to show/hide this section

**Inline Sections:**
- **Metrics** - Add stats like "210% Avg ROI", "6 Weeks Delivery"
- **Partner Logos** - Add client/partner logos

---

#### 2. Business Impact Section
**Location:** Home Page → Business Impact

**What it controls:** Showcase business impact metrics and trusted brands

**Fields:**
- Title, Description, CTA Label & Link

**Inline Sections:**
- **Metrics** - Add impact stats with icons and colors
- **Logos** - Add company logos

---

#### 3. ROI Calculator Section
**Location:** Home Page → ROI Calculator

**What it controls:** Smart business calculator section

**Fields:**
- Badge, Title, Highlighted Text, Description

**Inline Sections:**
- **Stats** - Add calculator statistics
- **Tools** - Add calculator tools/features

---

#### 4. Why Choose Us
**Location:** Home Page → Why Choose Us

**What it controls:** Why customers should choose Codeteki

**Fields:**
- Badge, Title, Description

**Inline Sections:**
- **Reasons** - Add reasons with icons and descriptions

---

#### 5. Testimonials
**Location:** Home Page → Testimonials

**What it controls:** Customer reviews and testimonials

**Fields per testimonial:**
- Name, Title, Company, Avatar
- Testimonial Text
- Rating (1-5 stars)
- Is Featured, Is Active
- Order (display order)

---

### ⚙️ Services Page

#### Services
**Location:** Services Page → All Services

**What you can manage:**
- Service Title
- Badge (e.g., "Enterprise Ready", "Tailored Builds")
- Description
- Icon (e.g., "Bot", "Wrench", "Zap")
- Order (display order)

**Inline Sections:**
- **Outcomes** - Add service outcomes/benefits

**Note:** The badge field is what appears in the yellow tag on service cards!

---

#### Process Steps
**Location:** Services Page → Process Steps

**What it controls:** The service delivery process/workflow

**Fields:**
- Title, Description
- Icon, Accent Color
- Order

---

### 🤖 AI Tools Page

**Location:** AI Tools Page

**Section Management:**
- Click on "AI Tools Section" to edit the section header
- Individual tools are managed as inline items

**Per Tool Fields:**
- Title, Slug, Description
- Icon, Emoji, Color, Badge
- Category, Status, Is Coming Soon
- Credits & Pricing
- External URL, Preview URL
- CTAs (primary and secondary)
- Is Active, Order

---

### 🎬 Demos Page

**Location:** Demos Page

**What you can manage:**
- Demo Title, Industry, Short & Full Description
- Status (Completed, In Progress, Planning)
- Icon, Color, Highlight Badge
- Thumbnail, Screenshot
- Features (JSON array)
- Demo URL, Video URL
- Client Name, Logo, Technologies
- Completion Date
- Is Featured, Is Active, Order

**Inline Sections:**
- **Gallery Images** - Add multiple demo images

---

### ❓ FAQ Page

**Location:** FAQ Page

**Structure:** Categories → Items

**How to use:**
1. Create FAQ Categories (e.g., "General", "Pricing", "Technical")
2. Add FAQ Items to each category
3. Set order for both categories and items

**Per Category:**
- Title, Order

**Per Item (inline):**
- Question, Answer, Order

---

### 📞 Contact Page

#### Contact Methods
**Location:** Contact Page → Contact Methods

**What to add:**
- Contact method title (e.g., "Call Us", "Email", "Visit Us")
- Value (phone number, email, address)
- Icon
- Description
- CTA text and link
- Order

**Examples:**
```
Title: Call Us
Value: +61 469 754 386
Icon: Phone
Description: Melbourne-based support team
Order: 1
```

#### Contact Inquiries
**Location:** Contact Page → Contact Inquiries

**What it shows:** All contact form submissions

**You can:**
- View inquiry details
- Mark as Contacted/Converted
- Filter by status and service
- Search by name/email

---

## 🔍 SEO Management

### Page SEO Tags
**Location:** SEO Management → Page SEO Tags

**What it controls:** SEO for each page (Home, Services, Contact, etc.)

**Per Page:**
- Meta Title
- Meta Description
- Meta Keywords
- Canonical URL
- Open Graph Title & Description
- OG Image (for social sharing)

---

### SEO Data Uploads
**Location:** SEO Management → Upload SEO Data

**What it does:** Upload keyword data from Ubersuggest/other tools

**How to use:**
1. Export keywords from Ubersuggest as CSV
2. Click "Upload SEO Data"
3. Fill in:
   - Name (e.g., "Q1 2025 Keywords")
   - Source (Ubersuggest, Ahrefs, etc.)
   - Upload CSV file
   - Notes (optional)
4. Click Save
5. Select the upload and use actions:
   - ✅ Process selected CSV uploads
   - 🤖 Generate AI playbooks
   - 📝 Generate blog drafts from clusters

**What you get:**
- Automatic keyword clustering
- AI-generated content recommendations
- Blog post drafts
- Priority scores

---

### Keywords
**Location:** SEO Management → Keywords

**What it shows:** All SEO keywords from uploads

**You can:**
- View search volume, difficulty, CPC
- Filter by intent (informational, commercial, etc.)
- See priority scores
- Link to keyword clusters

---

### Keyword Clusters
**Location:** SEO Management → Keyword Clusters

**What it shows:** Grouped keywords by topic

**Use for:**
- Content planning
- Blog topic ideas
- Service page optimization

---

### AI Recommendations
**Location:** SEO Management → AI Recommendations

**What it shows:** AI-generated SEO content ideas

**Includes:**
- Title suggestions
- Content outlines
- Meta descriptions
- Blog post ideas

---

## 💬 Leads & Chatbot

### Chat Leads
**Location:** Leads & Chat → Chat Leads

**What it shows:** Leads captured via chatbot

**Per Lead:**
- Name, Email, Phone, Company
- Intent, Budget, Timeline
- Notes
- Status (New, Contacted, Qualified, Converted, Lost)

**Actions:**
- Mark as Contacted
- Mark as Qualified

---

### Chat Conversations
**Location:** Leads & Chat → Chat Conversations

**What it shows:** Full chat conversation history

**You can:**
- View all messages in a conversation
- See visitor information
- Check conversation status
- Review metadata

---

### Chatbot Settings
**Location:** Leads & Chat → Chatbot Settings

**What you can configure:**
- Bot Name & Persona Title
- Brand Voice
- Accent Color
- Hero Image
- Messages:
  - Intro Message
  - Fallback Message
  - Lead Capture Prompt
  - Success Message
  - Quick Replies (JSON array)
- Escalation:
  - Escalation Threshold (number of messages)
  - Contact Email
  - Meeting Link

---

### Knowledge Base
**Location:** Leads & Chat → Knowledge Base

**What it controls:** Articles for chatbot training

**Per Article:**
- Category, Title, Slug
- Summary, Content
- Status, Published Date
- Persona (who it's for)
- Keywords, Tags
- Call to Action
- Cover Image
- Is Featured

**Inline Sections:**
- **FAQs** - Add related Q&As

---

## 📝 Blog & Content

**Location:** Blog & Content

**What you can manage:**
- Blog Post Title, Slug
- Author, Category
- Excerpt, Content
- Featured Image
- Publishing Status & Date
- Is Featured
- Tags
- SEO (Meta Title, Description)
- Reading Time
- Views Count

---

## ⚙️ Site Settings

### Site Settings
**Location:** Site Settings → Site Settings

**IMPORTANT:** Only ONE site settings instance exists!

**Tabs:**

#### 1. Site Information
- Site Name
- Site Tagline
- Site Description

#### 2. Logos & Branding
- Logo (light)
- Logo Dark (for dark backgrounds)
- Favicon

#### 3. Contact Information
- Primary Email, Secondary Email
- Primary Phone, Secondary Phone
- Physical Address

#### 4. Business Hours
Format as JSON:
```json
[
  {"day": "Monday - Friday", "hours": "9:00 AM - 6:00 PM AEDT"},
  {"day": "Saturday", "hours": "10:00 AM - 4:00 PM AEDT"},
  {"day": "Sunday", "hours": "By appointment"}
]
```

#### 5. Social Media
- Facebook, Twitter, LinkedIn
- Instagram, YouTube, GitHub

#### 6. Support & SLA
- Support Badge
- Response Value & Label (e.g., "2-6 hrs", "Response time")
- Helper Text
- Response Message
- Confirmation Message

#### 7. Business Details
- ABN

#### 8. Analytics & Tracking
- Google Analytics ID
- Facebook Pixel ID

---

### Footer
**Location:** Site Settings → Footer

**What you can manage:**
- Company Name
- Tagline
- Description
- ABN

**Inline Sections:**
- **Footer Links** - Add footer navigation links

---

### Navigation Menus
**Location:** Site Settings → Navigation Menus

**What it controls:** Header and footer navigation

**Structure:**
1. Create Menu (Header/Footer/Sidebar)
2. Add Navigation Items to menu
3. Set hierarchy (parent/child relationships)

**Per Menu:**
- Name, Location, Is Active

**Per Item (inline):**
- Title, URL
- Icon (optional)
- Parent (for dropdowns)
- Open in New Tab
- Is Active, Order

---

### Statistics
**Location:** Site Settings → Statistics

**What it controls:** Stats displayed on various pages

**Per Stat:**
- Section (Home, About, Services)
- Value (e.g., "100+", "$2M", "95%")
- Label
- Icon, Color
- Is Active, Order

---

### CTA Sections
**Location:** Site Settings → CTA Sections

**What it controls:** Call-to-action sections across the site

**Per CTA:**
- Title, Subtitle, Description
- Placement (where it appears)
- Primary Button (text & URL)
- Secondary Button (text & URL)
- Is Active, Order

---

### Pricing Plans
**Location:** Site Settings → Pricing Plans

**What you can manage:**
- Plan Name, Slug, Tagline
- Description
- Price, Currency, Billing Period
- Button Text & URL
- Is Popular, Is Active
- Order

**Inline Sections:**
- **Features** - Add pricing features (with checkmarks/crosses)

---

## 🎯 Quick Tips

### Making Content Changes
1. **Always check "Is Active"** - Inactive items won't appear on site
2. **Use Order fields** - Lower numbers appear first
3. **Save often** - Changes are immediate
4. **Preview on site** - Open site in new tab to check changes

### Working with Images
1. Upload images via media fields
2. OR provide image URLs for external hosting
3. Images are automatically optimized

### SEO Best Practices
1. Fill out Page SEO for ALL pages
2. Keep meta descriptions under 160 characters
3. Use relevant keywords naturally
4. Upload Open Graph images (1200x630px recommended)

### Chatbot Training
1. Add knowledge articles regularly
2. Review chat conversations for gaps
3. Update quick replies based on common questions
4. Set appropriate escalation threshold

### Managing Leads
1. Check Contact Inquiries daily
2. Review Chat Leads weekly
3. Use status updates to track progress
4. Export data periodically for CRM

---

## 🆘 Troubleshooting

### Content not appearing on site?
- Check "Is Active" checkbox
- Clear browser cache (Cmd+Shift+R)
- Check if section is enabled

### Images not loading?
- Verify image URL is correct
- Check file was uploaded successfully
- Ensure image is not too large (< 5MB recommended)

### SEO changes not reflecting?
- Changes may take time to index
- Verify meta tags using browser inspector
- Check search console

---

## 📞 Support

For technical issues or questions:
- Email: info@codeteki.au
- Phone: +61 469 754 386 or +61 424 538 777

---

## 🚀 Pro Tips

1. **Use "Is Featured"** to highlight important items
2. **Leverage AI recommendations** for content ideas
3. **Monitor chat conversations** to improve chatbot
4. **Regular SEO uploads** keep content fresh
5. **Update testimonials** monthly
6. **Review analytics** in Google Analytics

---

*Last Updated: 2025-01-18*
*Version: 2.0 - Complete CMS Revamp*
