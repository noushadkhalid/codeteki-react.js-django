"""
Prospect Website Intelligence Scanner

Scans prospect websites to detect gaps mapped to Codeteki's service portfolio:
1. Professional Web Development
2. AI Workforce Solutions
3. Business Automation Tools
4. Custom Tool Development (subscription trap detection)
5. SEO AI Tool
6. CRM & Sales Automation
7. MCP Integration Services

Two-part scan:
- PageSpeed API (performance, mobile, SEO scores, Core Web Vitals)
- Content Intelligence (crawl HTML to detect tech stack, missing features, SaaS subscriptions)
"""

import logging
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


# ============================================================================
# Detection pattern dictionaries
# ============================================================================

SAAS_TOOLS = {
    'hubspot': {'domain': 'hubspot.com', 'category': 'CRM', 'est_cost': '$50-800/mo'},
    'salesforce': {'domain': 'salesforce.com', 'category': 'CRM', 'est_cost': '$75-300/mo'},
    'zoho_crm': {'domain': 'zohocrm.com', 'category': 'CRM', 'est_cost': '$20-65/mo'},
    'pipedrive': {'domain': 'pipedrive.com', 'category': 'CRM', 'est_cost': '$15-100/mo'},
    'zendesk': {'domain': 'zendesk.com', 'category': 'Support', 'est_cost': '$55-115/mo'},
    'freshdesk': {'domain': 'freshdesk.com', 'category': 'Support', 'est_cost': '$15-95/mo'},
    'helpscout': {'domain': 'helpscout.com', 'category': 'Support', 'est_cost': '$20-65/mo'},
    'shopify': {'domain': 'shopify.com', 'category': 'E-commerce', 'est_cost': '$39-399/mo + fees'},
    'bigcommerce': {'domain': 'bigcommerce.com', 'category': 'E-commerce', 'est_cost': '$39-399/mo'},
    'mailchimp': {'domain': 'mailchimp.com', 'category': 'Email Marketing', 'est_cost': '$13-350/mo'},
    'klaviyo': {'domain': 'klaviyo.com', 'category': 'Email Marketing', 'est_cost': '$20-150/mo'},
    'activecampaign': {'domain': 'activecampaign.com', 'category': 'Marketing', 'est_cost': '$29-149/mo'},
    'convertkit': {'domain': 'convertkit.com', 'category': 'Email Marketing', 'est_cost': '$15-111/mo'},
    'hotjar': {'domain': 'hotjar.com', 'category': 'Analytics', 'est_cost': '$39-99/mo'},
    'mixpanel': {'domain': 'mixpanel.com', 'category': 'Analytics', 'est_cost': '$25-833/mo'},
}

CHAT_WIDGETS = {
    'tidio': 'tidio.co',
    'intercom': 'intercom.io',
    'drift': 'drift.com',
    'crisp': 'crisp.chat',
    'tawk': 'tawk.to',
    'livechat': 'livechat.com',
    'zendesk_chat': 'zopim.com',
    'freshchat': 'freshchat.com',
    'hubspot_chat': 'js.hs-scripts.com',
    'olark': 'olark.com',
}

BOOKING_SYSTEMS = {
    'calendly': 'calendly.com',
    'acuity': 'acuityscheduling.com',
    'fresha': 'fresha.com',
    'square': 'squareup.com',
    'setmore': 'setmore.com',
    'mindbody': 'mindbody',
    'booksy': 'booksy.com',
    'simplybook': 'simplybook',
    'vagaro': 'vagaro.com',
}

TEMPLATE_PLATFORMS = {
    'wix': {'pattern': 'wix.com', 'meta': 'wix.com'},
    'squarespace': {'pattern': 'squarespace.com', 'meta': 'squarespace'},
    'godaddy': {'pattern': 'godaddy.com', 'meta': 'godaddy'},
    'weebly': {'pattern': 'weebly.com', 'meta': 'weebly'},
    'webflow': {'pattern': 'webflow.io', 'meta': 'webflow'},
}

ANALYTICS_PROVIDERS = {
    'ga4': 'googletagmanager.com',
    'gtm': 'gtm.js',
    'analytics': 'google-analytics.com',
    'facebook_pixel': 'connect.facebook.net',
    'hotjar': 'hotjar.com',
    'mixpanel': 'mixpanel.com',
    'plausible': 'plausible.io',
    'fathom': 'usefathom.com',
}

MARKETING_AUTOMATION = {
    'mailchimp': 'mailchimp.com',
    'klaviyo': 'klaviyo.com',
    'activecampaign': 'activecampaign.com',
    'convertkit': 'convertkit.com',
    'hubspot_marketing': 'js.hs-analytics.net',
    'drip': 'getdrip.com',
}

CMS_PATTERNS = {
    'wordpress': {'generator': r'WordPress\s*([\d.]+)?', 'path': 'wp-content'},
    'joomla': {'generator': r'Joomla', 'path': 'joomla'},
    'drupal': {'generator': r'Drupal', 'path': 'sites/default'},
}

FRAMEWORK_PATTERNS = {
    'bootstrap_3': {'pattern': r'bootstrap[/.]3', 'name': 'Bootstrap 3'},
    'bootstrap_4': {'pattern': r'bootstrap[/.]4', 'name': 'Bootstrap 4'},
    'bootstrap_5': {'pattern': r'bootstrap[/.]5', 'name': 'Bootstrap 5'},
    'jquery_1': {'pattern': r'jquery[/.-]1\.', 'name': 'jQuery 1.x'},
    'jquery_2': {'pattern': r'jquery[/.-]2\.', 'name': 'jQuery 2.x'},
    'jquery_3': {'pattern': r'jquery[/.-]3\.', 'name': 'jQuery 3.x'},
    'react': {'pattern': r'react', 'name': 'React'},
    'vue': {'pattern': r'vue\.', 'name': 'Vue.js'},
    'angular': {'pattern': r'angular', 'name': 'Angular'},
    'tailwind': {'pattern': r'tailwind', 'name': 'Tailwind CSS'},
}


class ProspectAuditor:
    """Scans prospect websites to detect gaps mapped to Codeteki services."""

    def scan(self, url: str) -> dict:
        """
        Full scan: PageSpeed API + HTML crawl.
        Returns raw scan data dict with 'crawl' and 'pagespeed' keys.
        """
        result = {'crawl': {}, 'pagespeed': {}}

        # 1. Crawl homepage HTML
        try:
            result['crawl'] = self._crawl_homepage(url)
        except Exception as e:
            logger.error(f"Crawl failed for {url}: {e}")
            result['crawl'] = {'error': str(e)}

        # 2. PageSpeed API
        try:
            from core.services.pagespeed import PageSpeedService
            ps = PageSpeedService()
            if ps.enabled:
                result['pagespeed'] = ps.analyze_url(url, 'mobile')
            else:
                result['pagespeed'] = {'success': False, 'error': 'PageSpeed API not configured'}
        except Exception as e:
            logger.error(f"PageSpeed failed for {url}: {e}")
            result['pagespeed'] = {'success': False, 'error': str(e)}

        return result

    def _crawl_homepage(self, url: str) -> dict:
        """
        Crawl homepage HTML and detect features.
        Returns a dict of detected features.
        """
        # Ensure URL has scheme
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        resp.raise_for_status()

        html = resp.text
        soup = BeautifulSoup(html, 'html.parser')
        html_lower = html.lower()

        # Collect all script srcs and link hrefs for pattern matching
        script_srcs = [s.get('src', '') for s in soup.find_all('script') if s.get('src')]
        link_hrefs = [l.get('href', '') for l in soup.find_all('link') if l.get('href')]
        all_refs = ' '.join(script_srcs + link_hrefs + [html_lower])

        data = {}

        # --- Chat widgets ---
        data['has_chat_widget'] = False
        data['chat_provider'] = None
        for name, domain in CHAT_WIDGETS.items():
            if domain in all_refs:
                data['has_chat_widget'] = True
                data['chat_provider'] = name
                break

        # --- Booking systems ---
        data['has_booking'] = False
        data['booking_provider'] = None
        for name, domain in BOOKING_SYSTEMS.items():
            if domain in all_refs:
                data['has_booking'] = True
                data['booking_provider'] = name
                break

        # --- Analytics ---
        data['has_analytics'] = False
        data['analytics_providers'] = []
        for name, pattern in ANALYTICS_PROVIDERS.items():
            if pattern in all_refs:
                data['has_analytics'] = True
                data['analytics_providers'].append(name)

        # --- Marketing automation ---
        data['has_marketing_automation'] = False
        data['marketing_provider'] = None
        for name, pattern in MARKETING_AUTOMATION.items():
            if pattern in all_refs:
                data['has_marketing_automation'] = True
                data['marketing_provider'] = name
                break

        # --- E-commerce detection ---
        data['has_ecommerce'] = False
        data['ecommerce_platform'] = None
        if 'shopify' in all_refs or 'cdn.shopify.com' in all_refs:
            data['has_ecommerce'] = True
            data['ecommerce_platform'] = 'shopify'
        elif 'bigcommerce.com' in all_refs:
            data['has_ecommerce'] = True
            data['ecommerce_platform'] = 'bigcommerce'
        elif 'woocommerce' in all_refs or 'wc-' in html_lower:
            data['has_ecommerce'] = True
            data['ecommerce_platform'] = 'woocommerce'

        # --- CRM detection ---
        data['has_crm'] = False
        data['crm_provider'] = None
        for name, info in SAAS_TOOLS.items():
            if info['category'] == 'CRM' and info['domain'] in all_refs:
                data['has_crm'] = True
                data['crm_provider'] = name
                break

        # --- Support tool detection ---
        data['has_support_tool'] = False
        data['support_provider'] = None
        for name, info in SAAS_TOOLS.items():
            if info['category'] == 'Support' and info['domain'] in all_refs:
                data['has_support_tool'] = True
                data['support_provider'] = name
                break

        # --- Schema markup ---
        json_ld = soup.find_all('script', type='application/ld+json')
        microdata = soup.find_all(attrs={'itemscope': True})
        data['has_schema_markup'] = bool(json_ld or microdata)

        # --- Open Graph ---
        og_tags = soup.find_all('meta', attrs={'property': re.compile(r'^og:')})
        data['has_og_tags'] = len(og_tags) > 0

        # --- SSL ---
        data['has_ssl'] = resp.url.startswith('https://')

        # --- Viewport ---
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        data['has_viewport'] = viewport is not None

        # --- Contact form ---
        forms_found = soup.find_all('form')
        data['has_contact_form'] = len(forms_found) > 0

        # --- Lead capture (popup, newsletter, lead magnet) ---
        data['has_lead_capture'] = False
        lead_indicators = ['newsletter', 'subscribe', 'signup', 'sign-up', 'lead-magnet', 'popup', 'modal']
        for indicator in lead_indicators:
            if indicator in html_lower:
                data['has_lead_capture'] = True
                break

        # --- FAQ ---
        data['has_faq'] = False
        faq_indicators = ['faq', 'frequently asked', 'common questions']
        for indicator in faq_indicators:
            if indicator in html_lower:
                data['has_faq'] = True
                break

        # --- CMS detection ---
        data['cms'] = None
        data['cms_version'] = None
        generator = soup.find('meta', attrs={'name': 'generator'})
        generator_content = generator.get('content', '') if generator else ''
        for cms_name, patterns in CMS_PATTERNS.items():
            match = re.search(patterns['generator'], generator_content, re.IGNORECASE)
            if match:
                data['cms'] = cms_name
                data['cms_version'] = match.group(1) if match.lastindex else None
                break
            if patterns['path'] in all_refs:
                data['cms'] = cms_name
                break

        # --- Framework detection ---
        data['framework'] = None
        data['framework_version'] = None
        data['technologies'] = []
        for fw_key, fw_info in FRAMEWORK_PATTERNS.items():
            if re.search(fw_info['pattern'], all_refs, re.IGNORECASE):
                data['technologies'].append(fw_info['name'])
                if not data['framework']:
                    data['framework'] = fw_info['name']

        # --- Template platform detection ---
        data['platform'] = None
        for name, info in TEMPLATE_PLATFORMS.items():
            if info['pattern'] in all_refs or info['meta'] in generator_content.lower():
                data['platform'] = name.title()
                break
        # Also check meta generator for Wix/Squarespace
        if not data['platform']:
            if 'wix.com' in html_lower:
                data['platform'] = 'Wix'
            elif 'squarespace' in html_lower:
                data['platform'] = 'Squarespace'

        # --- SaaS tool detection (all) ---
        data['saas_tools'] = []
        for name, info in SAAS_TOOLS.items():
            if info['domain'] in all_refs:
                data['saas_tools'].append({
                    'name': name.replace('_', ' ').title(),
                    'category': info['category'],
                    'est_cost': info['est_cost'],
                })

        # --- Third-party count ---
        third_party_domains = set()
        parsed_url = urlparse(url)
        site_domain = parsed_url.netloc.replace('www.', '')
        for src in script_srcs:
            try:
                src_domain = urlparse(src).netloc.replace('www.', '')
                if src_domain and src_domain != site_domain:
                    third_party_domains.add(src_domain)
            except Exception:
                pass
        data['third_party_count'] = len(third_party_domains)

        # --- Manual process indicators ---
        data['has_manual_processes'] = False
        manual_indicators = ['mailto:', '.pdf', 'download our form', 'print this form']
        for indicator in manual_indicators:
            if indicator in html_lower:
                data['has_manual_processes'] = True
                break

        # --- Pricing / instant quotes ---
        data['has_instant_quotes'] = False
        quote_indicators = ['instant quote', 'get a quote', 'price calculator', 'estimate calculator', 'cost calculator']
        for indicator in quote_indicators:
            if indicator in html_lower:
                data['has_instant_quotes'] = True
                break

        return data

    def get_service_opportunities(self, scan_data: dict) -> dict:
        """
        Map scan findings to Codeteki services.
        Returns grade, opportunities, subscription trap, roadmap, scores, etc.
        """
        crawl = scan_data.get('crawl', {})
        pagespeed = scan_data.get('pagespeed', {})

        opportunities = []
        scores = {
            'performance_score': pagespeed.get('lab_performance_score'),
            'mobile_score': pagespeed.get('lab_performance_score'),  # Mobile strategy used
            'seo_score': pagespeed.get('seo_score'),
        }

        # === 1. Professional Web Development ===
        web_dev_findings = []
        perf = scores['performance_score']
        if perf is not None and perf < 50:
            lcp = pagespeed.get('lab_lcp')
            lcp_str = f" (loads in {lcp:.1f}s)" if lcp else ""
            web_dev_findings.append(f"Performance score {perf}/100{lcp_str} — half your visitors leave before seeing anything")

        seo = scores['seo_score']
        mobile = scores['mobile_score']
        if mobile is not None and mobile < 50:
            web_dev_findings.append(f"Mobile score {mobile}/100 — most of your customers browse on phones")

        if crawl.get('cms'):
            cms = crawl['cms']
            ver = crawl.get('cms_version', '')
            if cms == 'wordpress' and ver:
                web_dev_findings.append(f"Running WordPress {ver} — may be missing security patches and modern features")
            elif cms in ('joomla', 'drupal'):
                web_dev_findings.append(f"Running {cms.title()} — older CMS with fewer modern features")

        if crawl.get('framework') and any(t in crawl.get('technologies', []) for t in ['Bootstrap 3', 'jQuery 1.x', 'jQuery 2.x']):
            outdated = [t for t in crawl.get('technologies', []) if t in ('Bootstrap 3', 'jQuery 1.x', 'jQuery 2.x')]
            web_dev_findings.append(f"Using {', '.join(outdated)} — site looks and feels dated")

        if not crawl.get('has_ssl'):
            web_dev_findings.append("Site shows 'Not Secure' warning — drives customers away")

        if not crawl.get('has_viewport'):
            web_dev_findings.append("Not optimized for mobile devices at all")

        if crawl.get('platform'):
            plat = crawl['platform']
            web_dev_findings.append(f"Built on {plat} — limited customization, you don't own your site")

        if web_dev_findings:
            opportunities.append({
                'service': 'Professional Web Development',
                'priority': 'high' if len(web_dev_findings) >= 2 else 'medium',
                'findings': web_dev_findings,
                'business_impact': 'Slow, outdated, or limited website drives visitors to competitors',
                'codeteki_solution': 'Custom-built modern website, mobile-first, fast-loading',
            })

        # === 2. AI Workforce Solutions ===
        ai_findings = []
        if not crawl.get('has_chat_widget'):
            ai_findings.append("No live chat — customers who visit after hours have zero way to get help")
        if not crawl.get('has_booking'):
            ai_findings.append("No online booking — customers have to call, many won't bother")
        if not crawl.get('has_instant_quotes'):
            ai_findings.append("No instant quoting — prospects leave for competitors who respond faster")
        if crawl.get('has_contact_form') and not crawl.get('has_chat_widget') and not crawl.get('has_booking'):
            ai_findings.append("Only a contact form — no one wants to wait 24-48 hours for a reply")
        if crawl.get('has_faq') or not crawl.get('has_faq'):
            # If FAQ exists but is static, or no FAQ at all
            if not crawl.get('has_faq'):
                ai_findings.append("No FAQ section — an AI-powered FAQ could answer customer questions 24/7")

        if ai_findings:
            opportunities.append({
                'service': 'AI Workforce Solutions',
                'priority': 'high',
                'findings': ai_findings,
                'business_impact': 'Losing after-hours leads and customers who expect instant responses',
                'codeteki_solution': 'AI chatbot + automated booking + instant quotes',
            })

        # === 3. Business Automation Tools ===
        automation_findings = []
        if crawl.get('has_manual_processes'):
            automation_findings.append("Still using manual processes — PDF downloads, email-only contact")
        if not crawl.get('has_analytics'):
            automation_findings.append("No website analytics — flying blind on what your visitors actually do")
        if not crawl.get('has_marketing_automation'):
            automation_findings.append("No email marketing automation — missing repeat business opportunities")
        if crawl.get('third_party_count', 0) >= 4:
            count = crawl['third_party_count']
            automation_findings.append(f"Using {count} disconnected third-party tools — could be unified into one workflow")

        if automation_findings:
            opportunities.append({
                'service': 'Business Automation Tools',
                'priority': 'medium',
                'findings': automation_findings,
                'business_impact': 'Manual work eating hours, no data on what works, missed follow-ups',
                'codeteki_solution': 'Unified workflow automation, analytics, and marketing tools',
            })

        # === 4. Custom Tool Development (subscription trap) ===
        saas_tools = crawl.get('saas_tools', [])
        custom_findings = []
        if saas_tools:
            for tool in saas_tools:
                if tool['category'] in ('CRM', 'Support'):
                    custom_findings.append(
                        f"Paying {tool['est_cost']} for {tool['name']} — a custom solution built for YOUR workflow costs less long-term"
                    )
                elif tool['category'] == 'E-commerce':
                    custom_findings.append(
                        f"{tool['name']} takes a cut of every sale — a custom store means you keep 100%"
                    )
            if len(saas_tools) >= 3:
                custom_findings.append(
                    f"Paying for {len(saas_tools)} separate subscriptions — a custom-built solution replaces them all"
                )

        if crawl.get('platform') and crawl.get('third_party_count', 0) >= 3:
            custom_findings.append(
                f"Hitting {crawl['platform']}'s limits — you need features they can't provide"
            )

        if custom_findings:
            opportunities.append({
                'service': 'Custom Tool Development',
                'priority': 'medium' if len(saas_tools) < 3 else 'high',
                'findings': custom_findings,
                'business_impact': 'Overpaying for generic SaaS tools that don\'t fit your workflow',
                'codeteki_solution': 'Custom-built tools that replace expensive subscriptions',
            })

        # === 5. SEO AI Tool ===
        seo_findings = []
        if seo is not None and seo < 70:
            seo_findings.append(f"SEO score {seo}/100 — your competitors are ranking above you")

        if not crawl.get('has_schema_markup'):
            seo_findings.append("No schema markup — missing rich results in Google (stars, prices, hours)")
        if not crawl.get('has_og_tags'):
            seo_findings.append("Links shared on social media show no preview image or description")

        # Core Web Vitals
        lcp = pagespeed.get('lab_lcp')
        cls = pagespeed.get('lab_cls')
        if lcp is not None and lcp > 2.5:
            seo_findings.append(f"LCP {lcp:.1f}s (should be under 2.5s) — failing Google's Core Web Vitals, hurts search ranking")
        if cls is not None and cls > 0.1:
            seo_findings.append(f"CLS {cls:.2f} (should be under 0.1) — page elements shift around, bad user experience")

        if seo_findings:
            opportunities.append({
                'service': 'SEO AI Tool',
                'priority': 'high' if (seo is not None and seo < 50) else 'medium',
                'findings': seo_findings,
                'business_impact': 'Invisible to Google, competitors ranking above you',
                'codeteki_solution': 'Self-service SEO management platform with automated audits and AI-powered fixes',
            })

        # === 6. CRM & Sales Automation ===
        crm_findings = []
        if not crawl.get('has_crm'):
            crm_findings.append("No CRM system — leads fall through the cracks")
        if not crawl.get('has_lead_capture'):
            crm_findings.append("No lead capture — visitors leave and you have no way to follow up")
        if crawl.get('has_contact_form') and not crawl.get('has_marketing_automation'):
            crm_findings.append("Contact form submissions probably sit in an inbox — no automated follow-up")

        if crm_findings:
            opportunities.append({
                'service': 'CRM & Sales Automation',
                'priority': 'medium',
                'findings': crm_findings,
                'business_impact': 'Leads falling through the cracks, no systematic follow-up',
                'codeteki_solution': 'Custom CRM with lead management, email automation, pipeline tracking',
            })

        # === 7. MCP Integration / System Connectivity ===
        if crawl.get('third_party_count', 0) >= 5:
            saas_names = [t['name'] for t in saas_tools] if saas_tools else []
            integration_findings = []
            if saas_names:
                integration_findings.append(
                    f"Using {', '.join(saas_names[:4])} separately — data silos mean you're missing the full picture"
                )
            else:
                integration_findings.append(
                    f"Your customer data lives in {crawl['third_party_count']} different places — no single source of truth"
                )
            opportunities.append({
                'service': 'MCP Integration Services',
                'priority': 'low',
                'findings': integration_findings,
                'business_impact': 'Disconnected systems, no single view of customer data',
                'codeteki_solution': 'Connect systems via MCP to a single source of truth',
            })

        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        opportunities.sort(key=lambda x: priority_order.get(x['priority'], 3))

        # === Subscription trap ===
        subscription_trap = {}
        if saas_tools:
            subscription_trap = {
                'detected_tools': [t['name'] for t in saas_tools],
                'estimated_monthly': self._estimate_total_cost(saas_tools),
                'message': f"Paying for {len(saas_tools)} separate subscriptions — custom-built tools could replace them",
            }

        # === Grade calculation ===
        grade = self._calculate_grade(opportunities, scores, crawl)

        # === Roadmap ===
        roadmap = self._generate_roadmap(opportunities, crawl)

        # === Tech stack summary ===
        tech_parts = []
        if crawl.get('cms'):
            ver = crawl.get('cms_version', '')
            tech_parts.append(f"{crawl['cms'].title()} {ver}".strip())
        if crawl.get('platform'):
            tech_parts.append(crawl['platform'])
        tech_parts.extend(crawl.get('technologies', []))
        if crawl.get('ecommerce_platform'):
            tech_parts.append(crawl['ecommerce_platform'].title())
        tech_stack = ' + '.join(tech_parts) if tech_parts else 'Unknown'

        # Top finding (for quick summary)
        top_finding = ''
        if opportunities:
            top = opportunities[0]
            top_finding = top['findings'][0] if top['findings'] else top['business_impact']

        return {
            'grade': grade,
            'opportunities': opportunities,
            'subscription_trap': subscription_trap,
            'roadmap': roadmap,
            'tech_stack': tech_stack,
            'platform': crawl.get('platform', ''),
            'performance_score': scores.get('performance_score'),
            'mobile_score': scores.get('mobile_score'),
            'seo_score': scores.get('seo_score'),
            'top_finding': top_finding,
        }

    def _calculate_grade(self, opportunities: list, scores: dict, crawl: dict) -> str:
        """Calculate A-F digital maturity grade."""
        # Start at 100, deduct points
        points = 100

        # Deduct for each opportunity found
        for opp in opportunities:
            if opp['priority'] == 'high':
                points -= 15
            elif opp['priority'] == 'medium':
                points -= 8
            else:
                points -= 4

        # Deduct for poor scores
        perf = scores.get('performance_score')
        if perf is not None:
            if perf < 30:
                points -= 15
            elif perf < 50:
                points -= 10
            elif perf < 70:
                points -= 5

        seo = scores.get('seo_score')
        if seo is not None:
            if seo < 50:
                points -= 10
            elif seo < 70:
                points -= 5

        # Bonus for good practices
        if crawl.get('has_ssl'):
            points += 3
        if crawl.get('has_viewport'):
            points += 2
        if crawl.get('has_schema_markup'):
            points += 3
        if crawl.get('has_analytics'):
            points += 2

        # Clamp and convert to grade
        points = max(0, min(100, points))
        if points >= 90:
            return 'A'
        elif points >= 80:
            return 'B'
        elif points >= 65:
            return 'C'
        elif points >= 50:
            return 'D'
        else:
            return 'F'

    def _generate_roadmap(self, opportunities: list, crawl: dict) -> dict:
        """Generate a suggested journey: quick win, next step, long term."""
        roadmap = {
            'quick_win': '',
            'next_step': '',
            'long_term': '',
        }

        service_names = [o['service'] for o in opportunities]

        # Quick win: AI chatbot or SEO tool (fastest ROI)
        if 'AI Workforce Solutions' in service_names:
            roadmap['quick_win'] = 'AI chatbot — instant ROI, handles after-hours inquiries automatically'
        elif 'SEO AI Tool' in service_names:
            roadmap['quick_win'] = 'SEO audit and quick fixes — start ranking higher within weeks'
        elif 'Professional Web Development' in service_names:
            roadmap['quick_win'] = 'Website performance optimization — faster loading = more conversions'
        elif opportunities:
            roadmap['quick_win'] = f"{opportunities[0]['codeteki_solution']}"

        # Next step: custom tools or CRM
        if 'Custom Tool Development' in service_names:
            roadmap['next_step'] = 'Custom tools to replace expensive SaaS subscriptions'
        elif 'CRM & Sales Automation' in service_names:
            roadmap['next_step'] = 'Custom CRM to track leads and automate follow-ups'
        elif 'Professional Web Development' in service_names and roadmap['quick_win'] != 'Website performance optimization — faster loading = more conversions':
            roadmap['next_step'] = 'Modern website rebuild with AI integration'
        elif len(opportunities) > 1:
            roadmap['next_step'] = opportunities[1]['codeteki_solution']

        # Long term: full automation platform
        if 'Business Automation Tools' in service_names or 'MCP Integration Services' in service_names:
            roadmap['long_term'] = 'Full business automation platform — unified workflows, reporting, and AI'
        elif len(opportunities) > 2:
            roadmap['long_term'] = opportunities[2]['codeteki_solution']
        else:
            roadmap['long_term'] = 'Ongoing optimization and new feature development as you grow'

        return roadmap

    def _estimate_total_cost(self, saas_tools: list) -> str:
        """Estimate total monthly SaaS spend from detected tools."""
        # Extract the minimum costs and sum them
        total_min = 0
        for tool in saas_tools:
            cost_str = tool['est_cost']
            # Extract first number
            match = re.search(r'\$(\d+)', cost_str)
            if match:
                total_min += int(match.group(1))

        if total_min > 0:
            return f"${total_min}+/mo"
        return "Unknown"
