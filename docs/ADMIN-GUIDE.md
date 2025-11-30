# Codeteki Admin Guide

Complete guide for managing the Codeteki CMS admin panel.

## Access

**URL:** `https://your-domain/admin/` or `http://localhost:8001/admin/`

---

## Sidebar Navigation

The admin is organized by page sections matching the frontend:

### Home Page
| Section | Description |
|---------|-------------|
| Hero Sections | Main banner with CTAs |
| Business Impact | Stats and metrics section |
| Testimonials | Customer reviews |

### Services
| Section | Description |
|---------|-------------|
| Services | Service cards with outcomes |

### AI Tools
| Section | Description |
|---------|-------------|
| AI Tools Section | Section header |
| AI Tools | Individual tool cards (19 populated) |

### Demos
| Section | Description |
|---------|-------------|
| Demo Showcases | Project demos with images |

### FAQ
| Section | Description |
|---------|-------------|
| FAQ Page Section | Section config |
| FAQ Categories | Group FAQs by topic |
| FAQ Items | Individual Q&A |

### Contact
| Section | Description |
|---------|-------------|
| Contact Methods | Phone, email, social links |
| Contact Inquiries | Form submissions |

### Other Sections
| Section | Description |
|---------|-------------|
| ROI Calculator | Calculator config |
| Why Choose | Reasons/features |
| CTA Sections | Call-to-action blocks |

### Site Settings
| Section | Description |
|---------|-------------|
| Site Settings | Global config (logo, colors, etc.) |
| Footer | Footer content and links |
| Navigation | Menu items |
| Stat Metrics | Global stats |

### SEO Management
| Section | Description |
|---------|-------------|
| Page SEO | Per-page meta tags |
| SEO Data Uploads | CSV imports |
| Keywords | Keyword database |
| Keyword Clusters | Grouped keywords |
| AI Recommendations | AI-generated briefs |

### SEO Engine
| Section | Description |
|---------|-------------|
| Site Audits | Lighthouse audits |
| AI Analysis | AI-powered recommendations |
| Page Audits | Individual page results |
| Audit Issues | Issues found |
| PageSpeed Results | PageSpeed Insights data |
| Search Console Data | GSC metrics |
| Search Console Sync | GSC data import |
| Keyword Rankings | Position tracking |
| Competitors | Competitor profiles |
| SEO Recommendations | Fix suggestions |

### Blog
| Section | Description |
|---------|-------------|
| Blog Categories | Post categories |
| Blog Posts | Articles with SEO fields |

### Leads & Chat
| Section | Description |
|---------|-------------|
| Chat Leads | Lead captures |
| Conversations | Chat history |
| Chatbot Settings | Bot config |
| Knowledge Base | Bot knowledge articles |

---

## Common Tasks

### Adding Content

1. Navigate to the section in sidebar
2. Click **Add [Item]** button
3. Fill in required fields
4. Click **Save**

### Editing Content

1. Click on the item in the list
2. Modify fields
3. Click **Save**

### Bulk Actions

1. Check items in list view
2. Select action from dropdown
3. Click **Go**

### Running SEO Actions

1. Select items (Site Audits, PageSpeed, etc.)
2. Choose action:
   - Run Lighthouse audit
   - Run PageSpeed analysis
   - Generate AI analysis
   - Run Sync (Search Console)
3. Click **Go**
4. Wait for loading overlay to complete
5. Toast notification shows success/failure

---

## API Endpoints

All content is available via REST API:

| Endpoint | Description |
|----------|-------------|
| `/api/hero/` | Hero sections |
| `/api/services/` | Services |
| `/api/ai-tools/` | AI Tools |
| `/api/testimonials/` | Testimonials |
| `/api/faq/` | FAQ items |
| `/api/blog/` | Blog posts |
| `/api/page-seo/{slug}/` | Page SEO data |
| `/api/contact-methods/` | Contact info |

---

## Environment Variables

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# Database (if using PostgreSQL)
DATABASE_URL=postgres://...

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_SEO_MODEL=gpt-4o-mini

# Google APIs
GOOGLE_API_KEY=AIza...
GOOGLE_SERVICE_ACCOUNT_FILE=/path/to/credentials.json
GOOGLE_SEARCH_CONSOLE_PROPERTY=https://your-domain.com/
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't login | Check username/password; run `createsuperuser` |
| Static files missing | Run `python manage.py collectstatic` |
| 500 errors | Check `DEBUG=True` for details; check logs |
| Actions not working | Verify API keys in environment |
| Loading screen stuck | Refresh page; check browser console |

---

## Related Guides

- [SEO Engine Guide](./SEO-ENGINE-GUIDE.md) - Technical audits workflow
- [SEO Management Guide](./SEO-MANAGEMENT-GUIDE.md) - Keyword research workflow
- [DigitalOcean Deploy](./digitalocean-sqlite-deploy.md) - Deployment guide
