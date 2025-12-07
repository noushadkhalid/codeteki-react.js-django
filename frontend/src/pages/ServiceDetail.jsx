import { useRoute } from "wouter";
import { useQuery } from "@tanstack/react-query";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import {
  CheckCircle, ArrowLeft, Phone, Mail, MapPin, Clock,
  Users, Award, Headphones, Bot, Mic, Cog, Globe, Building, Zap,
  Shield, TrendingUp, Target, Sparkles, Code, Search, BarChart,
  MessageSquare, Rocket, Layers, RefreshCw, Database, Lock,
  Calendar, Wrench, Repeat, Cable, FileText, Eye, Settings,
  LineChart, PieChart, Activity
} from "lucide-react";
import { Link } from "wouter";
import SEOHead from "../components/SEOHead";
import { useMemo, useState } from "react";
import BookingModal from "../components/BookingModal";
import { useSiteSettings } from "../hooks/useSiteSettings";

// Comprehensive service details matching API IDs - NO PRICING
const serviceDetails = {
  // AI Workforce Solutions
  "ai-workforce": {
    title: "AI Workforce Solutions",
    subtitle: "Domain-trained AI agents that collaborate with your team and eliminate repetitive work",
    tagline: "Enterprise Ready",
    description: "Deploy domain-trained AI agents that collaborate with your team, manage workflows, and eliminate repetitive busy work. Our AI workforce solutions include intelligent chatbots, voice agents, and automation tools that work 24/7 to engage customers, qualify leads, and handle routine inquiries with human-like conversations. Every solution includes human-in-the-loop guardrails for quality assurance.",
    heroImage: "https://images.unsplash.com/photo-1531746790731-6c087fecd65a?auto=format&fit=crop&w=1200&q=80",
    gradient: "from-purple-600 to-indigo-600",
    features: [
      "Human-in-the-loop guardrails",
      "Secure knowledge base integrations",
      "Real-time analytics and alerts",
      "24/7 automated customer engagement",
      "Intelligent lead qualification",
      "Multi-language support",
      "Custom training on your data",
      "Seamless CRM integration"
    ],
    capabilities: [
      { icon: Bot, title: "Smart AI Agents", description: "Domain-trained agents that understand your business context and communicate naturally" },
      { icon: Shield, title: "Guardrailed Operations", description: "Human oversight built into every workflow for quality and compliance" },
      { icon: Database, title: "Knowledge Integration", description: "Secure connections to your existing knowledge bases and documentation" },
      { icon: Activity, title: "Real-time Monitoring", description: "Live dashboards and instant alerts for complete operational visibility" },
      { icon: Users, title: "Team Collaboration", description: "AI that works alongside your team, not as a replacement" },
      { icon: TrendingUp, title: "Continuous Learning", description: "Agents improve over time based on interactions and feedback" }
    ],
    benefits: [
      "Reduce response time from hours to seconds",
      "Handle unlimited simultaneous conversations",
      "Maintain quality with human oversight",
      "Free your team for strategic work",
      "Scale operations without scaling headcount",
      "24/7 availability for customers"
    ],
    process: [
      { step: 1, title: "Discovery", description: "Understand your workflows and automation opportunities" },
      { step: 2, title: "Design", description: "Create AI agents tailored to your business needs" },
      { step: 3, title: "Deploy", description: "Implement with guardrails and monitoring" },
      { step: 4, title: "Optimize", description: "Continuous improvement based on real data" }
    ]
  },

  // Custom Tool Development
  "custom-tools": {
    title: "Custom Tool Development",
    subtitle: "Bespoke internal tools, portals, and dashboards for your business",
    tagline: "Tailored Builds",
    description: "Design and ship bespoke internal tools, portals, and dashboards that plug straight into your existing ecosystem. We build custom software solutions that solve your specific business challenges, from employee portals to customer-facing applications, all with pixel-perfect interfaces and seamless integrations.",
    heroImage: "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=1200&q=80",
    gradient: "from-orange-500 to-red-600",
    features: [
      "Pixel-perfect UI/UX design",
      "First-party API integrations",
      "Ongoing roadmap partnership",
      "Custom business logic",
      "Role-based access control",
      "Mobile-responsive interfaces",
      "Real-time data sync",
      "Comprehensive documentation"
    ],
    capabilities: [
      { icon: Wrench, title: "Custom Development", description: "Purpose-built tools designed specifically for your unique business requirements" },
      { icon: Layers, title: "Seamless Integration", description: "Direct connections to your existing systems, databases, and third-party services" },
      { icon: Eye, title: "Intuitive Design", description: "User-centered interfaces that your team will actually want to use" },
      { icon: RefreshCw, title: "Roadmap Partnership", description: "We evolve your tools as your business grows and needs change" },
      { icon: Shield, title: "Enterprise Security", description: "Built with security best practices and compliance requirements in mind" },
      { icon: FileText, title: "Documentation", description: "Complete technical documentation and user guides for your team" }
    ],
    benefits: [
      "Tools built exactly for your workflow",
      "Eliminate workarounds and manual processes",
      "Improve team productivity and satisfaction",
      "Own your software - no vendor lock-in",
      "Scale as your business grows",
      "Ongoing partnership for future needs"
    ],
    process: [
      { step: 1, title: "Discovery", description: "Deep dive into your requirements and current pain points" },
      { step: 2, title: "Design", description: "UI/UX mockups and technical architecture planning" },
      { step: 3, title: "Build", description: "Agile development with regular demos and feedback" },
      { step: 4, title: "Launch", description: "Deployment, training, and ongoing support" }
    ]
  },

  // Business Automation Tools
  "automation": {
    title: "Business Automation Tools",
    subtitle: "Orchestrated workflows that automate approvals, reporting, and daily operations",
    tagline: "Process Automation",
    description: "Automate approvals, reporting, compliance, and daily operations with orchestrated workflows across your entire tech stack. Our automation solutions eliminate repetitive manual tasks, reduce errors, and give your team back hours every week. Every automation includes our governance layer for visibility and control.",
    heroImage: "https://images.unsplash.com/photo-1518186285589-2f7649de83e0?auto=format&fit=crop&w=1200&q=80",
    gradient: "from-amber-500 to-orange-600",
    features: [
      "Unified task orchestration",
      "Governance and compliance layer",
      "ROI tracking and reporting",
      "Multi-system workflows",
      "Approval chain automation",
      "Scheduled task execution",
      "Error handling and alerts",
      "Audit trail logging"
    ],
    capabilities: [
      { icon: Cog, title: "Workflow Orchestration", description: "Complex multi-step processes automated across all your business systems" },
      { icon: Shield, title: "Governance Layer", description: "Built-in compliance, approval workflows, and audit trails" },
      { icon: BarChart, title: "ROI Reporting", description: "Track time saved, errors prevented, and return on automation investment" },
      { icon: RefreshCw, title: "System Integration", description: "Connect CRM, accounting, HR, and any system with an API" },
      { icon: Clock, title: "Scheduled Tasks", description: "Automated reports, backups, and maintenance on your schedule" },
      { icon: Lock, title: "Error Handling", description: "Graceful failure recovery with alerts and manual override options" }
    ],
    benefits: [
      "Save 10-20+ hours per week on manual tasks",
      "Eliminate errors in repetitive processes",
      "Complete visibility with audit trails",
      "Scale without adding headcount",
      "Faster turnaround on routine work",
      "Focus your team on strategic activities"
    ],
    process: [
      { step: 1, title: "Audit", description: "Map your processes and identify automation opportunities" },
      { step: 2, title: "Design", description: "Create workflow architecture with governance built in" },
      { step: 3, title: "Build", description: "Implement and test automations thoroughly" },
      { step: 4, title: "Monitor", description: "Ongoing optimization and ROI tracking" }
    ]
  },

  // AI Tools for Daily Tasks
  "daily-ai": {
    title: "AI Tools for Daily Tasks",
    subtitle: "Personalized AI copilots for sales, support, HR, and finance teams",
    tagline: "Personal Copilots",
    description: "Personalized AI copilots for sales, support, HR, and finance that meet your policies and tone of voice from day one. These tools integrate with your existing workspace, provide role-based access, and eliminate context switching so your team can focus on high-value work instead of repetitive tasks.",
    heroImage: "https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=1200&q=80",
    gradient: "from-cyan-500 to-blue-600",
    features: [
      "Secure workspace libraries",
      "Role-based access and auditing",
      "No context switching required",
      "Custom tone and policies",
      "Team-specific training",
      "Privacy-first architecture",
      "Seamless tool integration",
      "Usage analytics dashboard"
    ],
    capabilities: [
      { icon: Repeat, title: "Daily Task Automation", description: "AI handles routine tasks like email drafts, data lookups, and report generation" },
      { icon: Users, title: "Role-Based Tools", description: "Different AI capabilities for sales, support, HR, and finance teams" },
      { icon: Shield, title: "Policy Compliance", description: "AI follows your company policies, tone guidelines, and approval workflows" },
      { icon: Database, title: "Workspace Integration", description: "Works with your existing tools - Slack, Teams, Gmail, and more" },
      { icon: Lock, title: "Privacy First", description: "Your data stays yours - no training on your proprietary information" },
      { icon: BarChart, title: "Usage Insights", description: "See how teams use AI tools and measure productivity gains" }
    ],
    benefits: [
      "Eliminate repetitive daily tasks",
      "Consistent communication that matches your brand",
      "Faster response times across all teams",
      "Reduced context switching",
      "Measurable productivity improvements",
      "Team adoption without steep learning curve"
    ],
    process: [
      { step: 1, title: "Assess", description: "Identify high-impact daily tasks for each team" },
      { step: 2, title: "Configure", description: "Set up AI tools with your policies and tone" },
      { step: 3, title: "Train", description: "Onboard teams with hands-on guidance" },
      { step: 4, title: "Scale", description: "Expand to more teams and use cases" }
    ]
  },

  // MCP Integration Services
  "mcp-integration": {
    title: "MCP Integration Services",
    subtitle: "Connect Model Context Protocol to your knowledge bases and tooling",
    tagline: "MCP Experts",
    description: "Connect the Model Context Protocol to your proprietary knowledge bases and tooling to unlock trustworthy automation. We specialize in MCP implementations that give AI models secure, controlled access to your business data while maintaining strict governance and observability across all interactions.",
    heroImage: "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80",
    gradient: "from-violet-600 to-purple-700",
    features: [
      "Source-of-truth syncing",
      "Guardrailed data pipelines",
      "Observability dashboards",
      "Secure API connections",
      "Real-time data access",
      "Custom MCP servers",
      "Access control policies",
      "Audit logging"
    ],
    capabilities: [
      { icon: Cable, title: "MCP Implementation", description: "Expert setup and configuration of Model Context Protocol for your systems" },
      { icon: Database, title: "Knowledge Base Connection", description: "Secure access to your documentation, databases, and proprietary data" },
      { icon: Shield, title: "Guardrailed Access", description: "Fine-grained permissions and data filtering for safe AI interactions" },
      { icon: Eye, title: "Full Observability", description: "Complete visibility into what data AI accesses and how it's used" },
      { icon: RefreshCw, title: "Real-time Sync", description: "Keep AI models updated with the latest information automatically" },
      { icon: Settings, title: "Custom Servers", description: "Purpose-built MCP servers for your specific integration needs" }
    ],
    benefits: [
      "AI with access to your actual business data",
      "Maintain control over what AI can see and do",
      "Trustworthy automation with audit trails",
      "Eliminate hallucinations with grounded context",
      "Faster AI adoption with proper governance",
      "Future-proof integration architecture"
    ],
    process: [
      { step: 1, title: "Audit", description: "Assess your data sources and integration requirements" },
      { step: 2, title: "Architect", description: "Design secure MCP implementation with guardrails" },
      { step: 3, title: "Build", description: "Implement MCP servers and data pipelines" },
      { step: 4, title: "Monitor", description: "Ongoing observability and optimization" }
    ]
  },

  // Professional Web Development
  "web-dev": {
    title: "Professional Web Development",
    subtitle: "Full-stack teams delivering marketing sites, portals, and web apps",
    tagline: "Full Stack",
    description: "Full-stack product teams that deliver marketing sites, customer portals, and high-performance web applications. We specialize in React and Django development, creating accessible, fast-loading websites that look great on any device. Every project includes comprehensive documentation and training for your team.",
    heroImage: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&q=80",
    gradient: "from-blue-600 to-cyan-600",
    features: [
      "React + Django specialists",
      "Accessibility-grade builds",
      "Training and documentation",
      "Mobile-first responsive design",
      "SEO optimization built-in",
      "Performance optimized",
      "Content management systems",
      "Analytics integration"
    ],
    capabilities: [
      { icon: Code, title: "Full-Stack Development", description: "React frontends with Django backends - a proven, scalable stack" },
      { icon: Eye, title: "Accessibility First", description: "WCAG-compliant builds that work for all users and improve SEO" },
      { icon: Zap, title: "Performance", description: "Fast-loading sites optimized for Core Web Vitals and search rankings" },
      { icon: FileText, title: "Documentation", description: "Comprehensive guides so your team can manage and update content" },
      { icon: Search, title: "SEO Built-in", description: "Technical SEO best practices implemented from the start" },
      { icon: Layers, title: "Scalable Architecture", description: "Built to grow with your business and handle increased traffic" }
    ],
    benefits: [
      "Professional online presence that converts",
      "Fast, accessible sites that rank well",
      "Your team can manage content independently",
      "Modern tech stack with long-term support",
      "Mobile-friendly design for all devices",
      "Ongoing partnership for future features"
    ],
    process: [
      { step: 1, title: "Strategy", description: "Define goals, audience, and key features" },
      { step: 2, title: "Design", description: "Create mockups and get your approval" },
      { step: 3, title: "Build", description: "Develop with regular demos and feedback" },
      { step: 4, title: "Launch", description: "Go live with training and support" }
    ]
  },

  // AI-Powered SEO Engine
  "seo-engine": {
    title: "AI-Powered SEO Engine",
    subtitle: "Comprehensive auditing with Lighthouse, PageSpeed, and AI recommendations",
    tagline: "New",
    description: "Comprehensive SEO auditing platform with Lighthouse, PageSpeed Insights, Search Console integration, and AI-powered recommendations. Get real-time performance audits, actionable insights, and competitor analysis to improve your search rankings and drive more organic traffic to your business.",
    heroImage: "https://images.unsplash.com/photo-1432888622747-4eb9a8efeb07?auto=format&fit=crop&w=1200&q=80",
    gradient: "from-emerald-600 to-teal-600",
    features: [
      "Real-time site performance audits",
      "AI-powered SEO recommendations",
      "Competitor analysis and tracking",
      "Automated reporting and alerts",
      "Core Web Vitals monitoring",
      "Search Console integration",
      "Keyword tracking",
      "Technical SEO checks"
    ],
    capabilities: [
      { icon: Search, title: "SEO Auditing", description: "Comprehensive technical audits using Lighthouse and PageSpeed Insights" },
      { icon: Bot, title: "AI Analysis", description: "Intelligent recommendations prioritized by impact and effort" },
      { icon: LineChart, title: "Performance Tracking", description: "Monitor Core Web Vitals and performance metrics over time" },
      { icon: Target, title: "Competitor Insights", description: "See how you stack up against competitors in search results" },
      { icon: Activity, title: "Real-time Alerts", description: "Get notified when issues arise that could impact rankings" },
      { icon: PieChart, title: "Automated Reports", description: "Regular performance reports delivered to your inbox" }
    ],
    benefits: [
      "Understand exactly what's hurting your rankings",
      "Prioritized recommendations you can action",
      "Track progress over time with clear metrics",
      "Stay ahead of competitor SEO strategies",
      "Automated monitoring saves manual audit time",
      "Data-driven decisions for SEO investment"
    ],
    process: [
      { step: 1, title: "Connect", description: "Link your site and Search Console for full data access" },
      { step: 2, title: "Audit", description: "Comprehensive scan of your site's SEO health" },
      { step: 3, title: "Analyze", description: "AI generates prioritized recommendations" },
      { step: 4, title: "Improve", description: "Implement fixes and track improvements" }
    ]
  }
};

// Fallback for legacy URLs or services not in the list
const legacyIdMap = {
  "web-development": "web-dev",
  "seo": "seo-engine",
  "integration": "mcp-integration",
  "consulting": "ai-workforce"
};

export default function ServiceDetail() {
  const [, params] = useRoute("/services/:serviceId");
  const serviceId = params?.serviceId;
  const [bookingOpen, setBookingOpen] = useState(false);
  const { settings } = useSiteSettings();

  // Fetch contact info
  const { data: contactData } = useQuery({
    queryKey: ["/api/contact/"],
  });

  const contactInfo = useMemo(() => {
    const info = contactData?.data?.info || contactData?.info || {};
    return {
      email: info.primaryEmail || settings?.contact?.email || "info@codeteki.au",
      phone: info.primaryPhone || settings?.contact?.phone || "+61 469 754 386",
      address: info.address || settings?.contact?.address || "Melbourne, Victoria",
    };
  }, [contactData, settings]);

  // Get service data - check static details first, then try legacy mapping
  const service = useMemo(() => {
    // Direct match
    if (serviceDetails[serviceId]) {
      return serviceDetails[serviceId];
    }
    // Try legacy ID mapping
    const mappedId = legacyIdMap[serviceId];
    if (mappedId && serviceDetails[mappedId]) {
      return serviceDetails[mappedId];
    }
    return null;
  }, [serviceId]);

  if (!service) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-white">
        <div className="text-center px-4">
          <div className="w-24 h-24 mx-auto mb-8 bg-[#f9cb07]/20 rounded-full flex items-center justify-center">
            <Sparkles className="w-12 h-12 text-[#f9cb07]" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Service Not Found</h1>
          <p className="text-gray-600 mb-8 max-w-md mx-auto">
            The requested service could not be found. Explore our range of AI and digital solutions.
          </p>
          <Link href="/services">
            <Button className="bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] text-black font-semibold px-8 py-3">
              <ArrowLeft className="mr-2 h-4 w-4" />
              View All Services
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <SEOHead
        title={`${service.title} | Codeteki Melbourne`}
        description={service.description}
        page={`service-${serviceId}`}
      />

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-gray-900 via-gray-800 to-black py-20 lg:py-28">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-30">
          <div className={`absolute top-0 right-0 w-[800px] h-[800px] bg-gradient-to-br ${service.gradient} rounded-full blur-[150px] -translate-y-1/2 translate-x-1/3`} />
          <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-[#f9cb07]/30 rounded-full blur-[120px] translate-y-1/2 -translate-x-1/3" />
        </div>

        <div className="relative container mx-auto px-4">
          <Link href="/services">
            <Button variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10 mb-6">
              <ArrowLeft className="mr-2 h-4 w-4" />
              All Services
            </Button>
          </Link>

          <div className="grid lg:grid-cols-2 gap-10 lg:gap-16 items-center">
            <div className="text-white">
              <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r ${service.gradient} text-white text-sm font-semibold mb-6`}>
                <Sparkles className="w-4 h-4" />
                {service.tagline}
              </div>
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4 leading-tight">
                {service.title}
              </h1>
              <p className="text-lg lg:text-xl text-white/80 mb-8 leading-relaxed">
                {service.subtitle}
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Button
                  size="lg"
                  onClick={() => setBookingOpen(true)}
                  className="bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] hover:from-[#e6b800] hover:to-[#f9cb07] text-black font-semibold px-8 py-6 text-lg shadow-2xl shadow-yellow-500/20"
                >
                  <Calendar className="mr-2 h-5 w-5" />
                  Book Free Consultation
                </Button>
                <Button
                  variant="outline"
                  size="lg"
                  className="border-2 border-white/30 text-white hover:bg-white hover:text-black font-semibold px-8 py-6 text-lg backdrop-blur"
                  onClick={() => window.location.href = `mailto:${contactInfo.email}`}
                >
                  <Mail className="mr-2 h-5 w-5" />
                  Send Inquiry
                </Button>
              </div>
            </div>

            <div className="relative hidden lg:block">
              <div className="relative rounded-2xl overflow-hidden shadow-2xl shadow-black/50">
                <img
                  src={service.heroImage}
                  alt={service.title}
                  className="w-full h-[400px] object-cover"
                />
                <div className={`absolute inset-0 bg-gradient-to-t ${service.gradient} opacity-20`} />
              </div>
              {/* Floating Stats */}
              <div className="absolute -bottom-6 -left-6 bg-white rounded-xl shadow-xl p-4">
                <div className="flex items-center gap-3">
                  <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${service.gradient} flex items-center justify-center`}>
                    <CheckCircle className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-gray-900">Melbourne</p>
                    <p className="text-sm text-gray-600">Based Team</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Overview Section */}
      <section className="py-16 lg:py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <span className="inline-block px-4 py-1.5 rounded-full bg-[#f9cb07]/20 text-[#8a7000] text-sm font-semibold mb-4">
              About This Service
            </span>
            <h2 className="text-2xl lg:text-3xl font-bold text-black mb-6">Overview</h2>
            <p className="text-lg text-gray-600 leading-relaxed">
              {service.description}
            </p>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-16 lg:py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <span className="inline-block px-4 py-1.5 rounded-full bg-[#f9cb07]/20 text-[#8a7000] text-sm font-semibold mb-4">
              What's Included
            </span>
            <h2 className="text-2xl lg:text-3xl font-bold text-black">Key Features</h2>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-6xl mx-auto">
            {service.features.map((feature, index) => (
              <div
                key={index}
                className="group flex items-center p-4 bg-white rounded-xl border border-gray-100 hover:border-[#f9cb07]/50 hover:shadow-lg hover:shadow-[#f9cb07]/10 transition-all duration-300"
              >
                <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-[#f9cb07]/10 flex items-center justify-center mr-3 group-hover:bg-[#f9cb07]/20 transition-colors">
                  <CheckCircle className="h-5 w-5 text-[#f9cb07]" />
                </div>
                <span className="text-gray-700 font-medium text-sm">{feature}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Capabilities Section */}
      <section className="py-16 lg:py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <span className="inline-block px-4 py-1.5 rounded-full bg-[#f9cb07]/20 text-[#8a7000] text-sm font-semibold mb-4">
              Our Expertise
            </span>
            <h2 className="text-2xl lg:text-3xl font-bold text-black">Capabilities</h2>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
            {service.capabilities.map((capability, index) => {
              const IconComponent = capability.icon;
              return (
                <Card key={index} className="group border border-gray-100 shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden">
                  <CardContent className="p-6">
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${service.gradient} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
                      <IconComponent className="h-6 w-6 text-white" />
                    </div>
                    <h3 className="text-lg font-bold text-black mb-2">
                      {capability.title}
                    </h3>
                    <p className="text-gray-600 text-sm leading-relaxed">
                      {capability.description}
                    </p>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Process Section */}
      <section className="py-16 lg:py-20 bg-gray-900 text-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <span className="inline-block px-4 py-1.5 rounded-full bg-[#f9cb07]/20 text-[#f9cb07] text-sm font-semibold mb-4">
              How We Work
            </span>
            <h2 className="text-2xl lg:text-3xl font-bold">Our Process</h2>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8 max-w-5xl mx-auto">
            {service.process.map((step, index) => (
              <div key={index} className="relative">
                <div className="text-center">
                  <div className="w-14 h-14 rounded-full bg-gradient-to-br from-[#f9cb07] to-[#ffcd3c] flex items-center justify-center mx-auto mb-4 shadow-lg shadow-yellow-500/30">
                    <span className="text-xl font-bold text-black">{step.step}</span>
                  </div>
                  <h3 className="text-lg font-bold mb-2">{step.title}</h3>
                  <p className="text-white/70 text-sm">{step.description}</p>
                </div>
                {index < service.process.length - 1 && (
                  <div className="hidden lg:block absolute top-7 left-[60%] w-[80%] border-t-2 border-dashed border-white/20" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-16 lg:py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <span className="inline-block px-4 py-1.5 rounded-full bg-[#f9cb07]/20 text-[#8a7000] text-sm font-semibold mb-4">
              The Codeteki Advantage
            </span>
            <h2 className="text-2xl lg:text-3xl font-bold text-black">Why Choose Us</h2>
          </div>
          <div className="grid md:grid-cols-2 gap-4 max-w-4xl mx-auto">
            {service.benefits.map((benefit, index) => (
              <div
                key={index}
                className="flex items-start p-5 bg-gradient-to-br from-gray-50 to-white rounded-xl border border-gray-100"
              >
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-100 flex items-center justify-center mr-3">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                </div>
                <span className="text-gray-700 leading-relaxed">{benefit}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Melbourne Support Section */}
      <section className="py-16 lg:py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center mb-12">
            <span className="inline-block px-4 py-1.5 rounded-full bg-[#f9cb07]/20 text-[#8a7000] text-sm font-semibold mb-4">
              Local Expertise
            </span>
            <h2 className="text-2xl lg:text-3xl font-bold text-black mb-4">Melbourne-Based Support</h2>
            <p className="text-gray-600">
              Work with a local team who understands Australian business needs
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-5xl mx-auto">
            {[
              { icon: Clock, title: "Quick Turnaround", desc: "Fast delivery without compromising quality" },
              { icon: Users, title: "Expert Team", desc: "Specialists in AI and digital solutions" },
              { icon: Headphones, title: "Responsive Support", desc: "Available during AEDT business hours" },
              { icon: MapPin, title: "Local Team", desc: "Melbourne-based with Australia-wide service" }
            ].map((item, index) => (
              <Card key={index} className="text-center border-0 shadow-sm hover:shadow-lg transition-shadow">
                <CardContent className="p-5">
                  <div className="w-12 h-12 rounded-xl bg-[#f9cb07]/10 flex items-center justify-center mx-auto mb-3">
                    <item.icon className="h-6 w-6 text-[#f9cb07]" />
                  </div>
                  <h3 className="font-bold text-black mb-1">{item.title}</h3>
                  <p className="text-sm text-gray-600">{item.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 lg:py-24 bg-gradient-to-br from-gray-900 via-gray-800 to-black relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-[#f9cb07]/20 rounded-full blur-[150px]" />
          <div className={`absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-gradient-to-br ${service.gradient} opacity-30 rounded-full blur-[120px]`} />
        </div>

        <div className="relative container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center text-white">
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-4">
              Ready to Get Started?
            </h2>
            <p className="text-lg text-white/80 mb-8">
              Book a free consultation and discover how we can help transform your business.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-10">
              <Button
                size="lg"
                onClick={() => setBookingOpen(true)}
                className="bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] hover:from-[#e6b800] hover:to-[#f9cb07] text-black font-semibold px-8 py-6 text-lg shadow-2xl shadow-yellow-500/30"
              >
                <Calendar className="mr-2 h-5 w-5" />
                Book Free Consultation
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="border-2 border-white/30 text-white hover:bg-white hover:text-black font-semibold px-8 py-6 text-lg"
                onClick={() => window.location.href = `tel:${contactInfo.phone.replace(/\s+/g, "")}`}
              >
                <Phone className="mr-2 h-5 w-5" />
                Call Us Now
              </Button>
            </div>

            {/* Contact Info */}
            <div className="grid sm:grid-cols-3 gap-6 pt-8 border-t border-white/10">
              <div className="flex flex-col items-center">
                <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center mb-2">
                  <Phone className="h-4 w-4 text-[#f9cb07]" />
                </div>
                <a href={`tel:${contactInfo.phone.replace(/\s+/g, "")}`} className="text-white hover:text-[#f9cb07] transition-colors text-sm">
                  {contactInfo.phone}
                </a>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center mb-2">
                  <Mail className="h-4 w-4 text-[#f9cb07]" />
                </div>
                <a href={`mailto:${contactInfo.email}`} className="text-white hover:text-[#f9cb07] transition-colors text-sm">
                  {contactInfo.email}
                </a>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center mb-2">
                  <MapPin className="h-4 w-4 text-[#f9cb07]" />
                </div>
                <span className="text-white text-sm">{contactInfo.address}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <BookingModal open={bookingOpen} onOpenChange={setBookingOpen} />
    </div>
  );
}
