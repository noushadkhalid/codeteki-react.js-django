# Codeteki Admin - Quick Reference Guide

## 🚀 Quick Access

**Admin URL:** `https://www.codeteki.au/admin/`

---

## 📄 Page Content Management

### 🏠 Home Page
| Section | What it controls | Key fields |
|---------|------------------|------------|
| **Hero Section** | Top banner, main headline | Title, CTA buttons, background |
| **Services Overview** | Service cards grid | Title, description, icon, order |
| **Business Impact** | Metrics, stats section | Metrics, logos, description |
| **ROI Calculator** | Calculator tool section | Stats, tool configuration |
| **Why Choose Us** | Benefits/features list | Reasons with icons |
| **Testimonials** | Customer reviews | Name, company, rating, content |
| **Stats & Metrics** | Number highlights | Value, label, icon |
| **CTA Sections** | Call-to-action banners | Title, buttons, placement |

### 🤖 AI Tools Page
| Section | What it controls |
|---------|------------------|
| **AI Tools Section** | Page header/intro |
| **AI Tools** | Individual tool cards |

### 📞 Contact Page
| Section | What it controls |
|---------|------------------|
| **Contact Methods** | Email, phone, address cards |
| **Contact Inquiries** | Form submissions (inbox) |
| **FAQ Categories** | FAQ sections and questions |

### 🎬 Demos Page
| Section | What it controls |
|---------|------------------|
| **Demo Showcases** | Project portfolio items |

---

## 🔍 SEO Tools - Workflow at a Glance

### Quick Upload
**📤 Upload Ubersuggest Data** → Direct upload form

### 3-Step Process
1. **Upload CSV** → SEO Data Uploads → Add new
2. **Wait for processing** → Auto-creates keywords & clusters
3. **Generate content** → Actions → "Generate AI playbooks"

### View Results
- **AI Recommendations** → Content briefs, meta tags, FAQs
- **Keyword Clusters** → Thematic keyword groups
- **Keywords** → Individual keyword data
- **Page SEO Settings** → Meta tags per page

---

## 📝 Content Publishing

### Blog Posts
1. Go to **Blog & Content → Blog Posts**
2. Click **Add Blog Post**
3. Fill in: Title, content, excerpt, featured image
4. Set **Is Published = True**
5. Set publish date
6. Save

**Auto-slugs:** Slugs auto-generate from title

### Knowledge Articles
Similar to blog posts but organized by category
- Used for help docs, guides, tutorials
- Can be referenced by chatbot

---

## 💬 Lead Management

### Contact Inquiries
**📞 Contact Page → Contact Inquiries**
- View all form submissions
- Filter by status: New, Reviewed, Contacted
- Reply via email from inquiry details

### Chat Leads
**💬 Chatbot & Leads → Chat Leads**
- Leads captured via chatbot
- Includes conversation context
- Filter by status: New, Contacted, Qualified

---

## ⚙️ Global Settings

### Site Settings
**⚙️ Global Settings → Site Settings**
- Site name, tagline, description
- Logo, favicon
- Contact information
- Social media links
- Google Analytics ID

### Footer Section
**⚙️ Global Settings → Footer Section**
- Company info
- Footer links (3 columns)
- Social media icons
- Copyright text

### Navigation Menus
**⚙️ Global Settings → Navigation Menus**
- Header navigation
- Footer navigation
- Menu items with icons

---

## 🎯 Common Tasks

### Update Home Page Hero
1. **🏠 Home Page Content → Hero Section**
2. Click on active hero section
3. Edit: Title, description, CTA buttons
4. Upload new background image if needed
5. Save changes

### Add New Service
1. **🏠 Home Page Content → Services Overview**
2. Click **Add Service**
3. Fill in:
   - Title
   - Slug (auto-generates)
   - Description
   - Icon (lucide icon name)
   - Order (display order)
4. Add outcomes (click + to add more)
5. Save

### Update Page SEO
1. **🔍 SEO Tools → Page SEO Settings**
2. Select page (Home, Services, AI Tools, etc.)
3. Update:
   - Meta title (<60 chars)
   - Meta description (<155 chars)
   - Keywords
   - Open Graph image
4. Save

### Add Testimonial
1. **🏠 Home Page Content → Testimonials**
2. Click **Add Testimonial**
3. Fill in:
   - Name, position, company
   - Rating (1-5 stars)
   - Content (review text)
   - Upload image (optional)
   - Is Featured (shows first)
   - Is Active (published)
4. Save

---

## 🔐 User Management

### Create New Admin User
1. **Authentication → Users**
2. Click **Add User**
3. Enter username and password
4. Save and continue
5. Check:
   - **Staff status** (can access admin)
   - **Superuser status** (full permissions)
6. Fill in email and other details
7. Save

---

## 📊 Monitoring

### Recent Activity
- Admin home shows recent changes
- Filter by user and date

### Logs
- Server logs: `sudo journalctl -u gunicorn -f`
- Nginx logs: `sudo tail -f /var/log/nginx/error.log`

---

## ⚡ Power User Tips

### Bulk Actions
Select multiple items → Choose action → Click "Go"
- Delete selected
- Process uploads (SEO)
- Generate AI content (SEO)
- Update status (inquiries)

### Search & Filters
- Use search bar at top of list pages
- Apply filters on right sidebar
- Combine filters for precision

### Inline Editing
Many sections support inline editing:
- Hero metrics
- Service outcomes
- FAQ items
- Pricing features
- Footer links

### Keyboard Shortcuts
- `Ctrl/Cmd + S` - Save
- `Ctrl/Cmd + K` - Search (if enabled)

---

## 🎨 Content Organization Philosophy

Content is organized by **where it appears** on the website:
- **🏠 Home Page Content** - Everything visible on homepage
- **🤖 AI Tools Page** - AI tools page components
- **📞 Contact Page** - Contact page elements
- **🎬 Demos Page** - Portfolio/showcase items
- **📝 Blog & Content** - Published content
- **🔍 SEO Tools** - Behind-the-scenes optimization
- **💬 Chatbot** - Visitor interactions
- **⚙️ Global** - Site-wide settings

**Why this structure?**
- Easy to find what you want to edit
- Mirrors the actual website structure
- No confusion about where things live
- Logical grouping reduces clicks

---

## 🆘 Troubleshooting

### Can't find a section
- Check the appropriate page group
- Use the search bar (top right)
- Ask: "Which page does this appear on?"

### Changes not visible on site
1. Clear browser cache (`Ctrl/Cmd + Shift + R`)
2. Check if item is "Active" or "Published"
3. Restart Gunicorn: `sudo systemctl restart gunicorn`

### Upload failed
- Check file size (<10MB recommended)
- Verify file format (CSV for SEO, image for media)
- Check server disk space: `df -h`

### Image not displaying
- Ensure image is uploaded in correct field
- Check file permissions on server
- Run collectstatic: `python manage.py collectstatic`

---

## 📞 Support Contacts

**Technical Issues:**
- Check logs first
- Review error messages
- Server access: SSH to droplet

**Content Questions:**
- Refer to SEO Workflow Guide for SEO tools
- Check this guide for page organization

---

**Version:** 1.0
**Last Updated:** November 2024
