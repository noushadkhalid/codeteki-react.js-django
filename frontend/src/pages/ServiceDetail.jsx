import { useRoute } from "wouter";
import { useQuery } from "@tanstack/react-query";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import {
  CheckCircle, ArrowLeft, Phone, Mail, MapPin, Clock,
  Users, Award, Headphones, Bot, Mic, Cog, Globe, Building, Zap,
  Shield, TrendingUp, Target, Sparkles, Code, Search, BarChart,
  MessageSquare, Rocket, Layers, RefreshCw, Database, Lock,
  Calendar
} from "lucide-react";
import { Link } from "wouter";
import SEOHead from "../components/SEOHead";
import { useMemo, useState } from "react";
import BookingModal from "../components/BookingModal";
import { useSiteSettings } from "../hooks/useSiteSettings";

// Comprehensive service details - NO PRICING
const serviceDetails = {
  "ai-workforce": {
    title: "AI Workforce Solutions",
    subtitle: "Complete AI workforce with voice agents, chatbots, and intelligent automation",
    tagline: "Your 24/7 AI Team",
    description: "Deploy our complete AI workforce including AI-powered voice agents and intelligent chatbots that work around the clock to engage customers, qualify leads, and handle routine inquiries with human-like conversations. Transform how your business communicates.",
    heroImage: "https://images.unsplash.com/photo-1531746790731-6c087fecd65a?auto=format&fit=crop&w=1200&q=80",
    gradient: "from-purple-600 to-indigo-600",
    accentColor: "purple",
    features: [
      "24/7 automated customer engagement",
      "Intelligent lead qualification & scoring",
      "Multi-language support (English + South Asian languages)",
      "Custom training on your business data",
      "Seamless CRM & system integration",
      "Real-time analytics and insights",
      "Natural conversation flows",
      "Instant response times"
    ],
    capabilities: [
      { icon: Bot, title: "Smart Chatbots", description: "AI chatbots that understand context, sentiment, and provide meaningful responses across all channels" },
      { icon: Mic, title: "Voice AI Agents", description: "Natural-sounding AI voice agents for phone support, appointment booking, and outbound calls" },
      { icon: Users, title: "Lead Qualification", description: "Automatically qualify, score, and route leads based on your criteria before human handoff" },
      { icon: Globe, title: "Multilingual", description: "Communicate fluently with customers in English and major South Asian languages" },
      { icon: MessageSquare, title: "Omnichannel", description: "Unified experience across website, phone, SMS, WhatsApp, and social media" },
      { icon: TrendingUp, title: "Smart Analytics", description: "Deep insights into customer interactions, sentiment trends, and conversion metrics" }
    ],
    benefits: [
      "Reduce customer response time from hours to seconds",
      "Handle unlimited simultaneous conversations",
      "Capture and convert leads outside business hours",
      "Free up your team for high-value strategic activities",
      "Consistent brand voice across all interactions",
      "Scale customer service without scaling costs"
    ],
    process: [
      { step: 1, title: "Discovery", description: "We analyze your customer journey and communication needs" },
      { step: 2, title: "Design", description: "Custom AI personality and conversation flows for your brand" },
      { step: 3, title: "Training", description: "AI trained on your business data, FAQs, and processes" },
      { step: 4, title: "Launch", description: "Deployment with ongoing optimization and support" }
    ]
  },
  "web-development": {
    title: "Professional Web Development",
    subtitle: "Modern, responsive websites that convert visitors into customers",
    tagline: "Your Digital Storefront",
    description: "Get a professional website built with cutting-edge technologies, optimized for mobile devices and search engines. We create stunning digital experiences that showcase your business, build trust, and drive conversions.",
    heroImage: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&q=80",
    gradient: "from-blue-600 to-cyan-600",
    accentColor: "blue",
    features: [
      "Mobile-first responsive design",
      "Search engine optimization (SEO)",
      "Lightning-fast performance",
      "Intuitive content management",
      "Contact forms & lead capture",
      "Social media integration",
      "Analytics & tracking setup",
      "SSL security included"
    ],
    capabilities: [
      { icon: Building, title: "Modern Design", description: "Contemporary, brand-aligned designs that appeal to your target audience and build credibility" },
      { icon: Zap, title: "Performance", description: "Blazing-fast websites optimized for Core Web Vitals and search engine rankings" },
      { icon: Search, title: "SEO Ready", description: "Built-in SEO best practices to help you rank higher and attract organic traffic" },
      { icon: Cog, title: "Easy Updates", description: "Simple content management so you can update your site without technical knowledge" },
      { icon: Shield, title: "Secure", description: "SSL certificates, security headers, and best practices to protect your business" },
      { icon: BarChart, title: "Analytics", description: "Track visitor behavior, conversions, and ROI with integrated analytics" }
    ],
    benefits: [
      "Professional online presence that builds instant trust",
      "Mobile-friendly design reaches customers everywhere",
      "SEO optimization improves your search visibility",
      "Lead capture forms grow your customer base automatically",
      "Fast loading speeds reduce bounce rates",
      "Easy updates keep your content fresh"
    ],
    process: [
      { step: 1, title: "Strategy", description: "Define goals, target audience, and key messaging" },
      { step: 2, title: "Design", description: "Create stunning mockups aligned with your brand" },
      { step: 3, title: "Develop", description: "Build with modern tech for speed and reliability" },
      { step: 4, title: "Launch", description: "Go live with training and ongoing support" }
    ]
  },
  "automation": {
    title: "Custom Automation Solutions",
    subtitle: "Streamline repetitive tasks and supercharge productivity",
    tagline: "Work Smarter, Not Harder",
    description: "Eliminate repetitive manual tasks with custom automation solutions tailored to your business processes. Save hours every week, reduce errors, and let your team focus on what matters most - growing your business.",
    heroImage: "https://images.unsplash.com/photo-1518186285589-2f7649de83e0?auto=format&fit=crop&w=1200&q=80",
    gradient: "from-amber-500 to-orange-600",
    accentColor: "amber",
    features: [
      "Custom workflow automation",
      "Data entry & processing",
      "Automated report generation",
      "Email & communication flows",
      "Inventory management",
      "Invoice & billing automation",
      "Social media scheduling",
      "CRM synchronization"
    ],
    capabilities: [
      { icon: Cog, title: "Process Automation", description: "Automate complex multi-step business processes from trigger to completion" },
      { icon: Database, title: "Data Processing", description: "Automatically collect, validate, transform, and organize data from multiple sources" },
      { icon: Mail, title: "Communication", description: "Automated email sequences, reminders, follow-ups, and customer notifications" },
      { icon: RefreshCw, title: "Integrations", description: "Connect your tools - CRM, accounting, marketing, and more - for seamless data flow" },
      { icon: BarChart, title: "Reporting", description: "Automated dashboards and reports delivered on schedule without manual effort" },
      { icon: Lock, title: "Reliable", description: "Built-in error handling, logging, and alerts ensure your automations run smoothly" }
    ],
    benefits: [
      "Save 10-20+ hours per week on manual tasks",
      "Eliminate human errors in repetitive processes",
      "Scale operations without hiring additional staff",
      "Focus your team on strategic, revenue-generating activities",
      "Faster turnaround on routine business processes",
      "Complete audit trail of all automated actions"
    ],
    process: [
      { step: 1, title: "Audit", description: "Map your current processes and identify automation opportunities" },
      { step: 2, title: "Design", description: "Create optimized workflows and integration architecture" },
      { step: 3, title: "Build", description: "Develop, test, and refine your custom automations" },
      { step: 4, title: "Optimize", description: "Continuous improvement based on performance data" }
    ]
  },
  "seo": {
    title: "SEO & Digital Marketing",
    subtitle: "Get found by customers actively searching for your services",
    tagline: "Dominate Search Results",
    description: "Comprehensive SEO and digital marketing strategies that drive organic traffic, increase visibility, and convert searchers into customers. Data-driven approach with transparent reporting and measurable results.",
    heroImage: "https://images.unsplash.com/photo-1432888622747-4eb9a8efeb07?auto=format&fit=crop&w=1200&q=80",
    gradient: "from-emerald-600 to-teal-600",
    accentColor: "emerald",
    features: [
      "Technical SEO audit & fixes",
      "Keyword research & strategy",
      "On-page optimization",
      "Content strategy & creation",
      "Local SEO for Melbourne businesses",
      "Google Business Profile optimization",
      "Monthly performance reporting",
      "Competitor analysis"
    ],
    capabilities: [
      { icon: Search, title: "Technical SEO", description: "Comprehensive audits and fixes for site speed, crawlability, and Core Web Vitals" },
      { icon: Target, title: "Keyword Strategy", description: "Research-driven keyword targeting to capture high-intent search traffic" },
      { icon: Layers, title: "Content Optimization", description: "Strategic content creation and optimization that ranks and converts" },
      { icon: MapPin, title: "Local SEO", description: "Dominate local search results and Google Maps for Melbourne area searches" },
      { icon: BarChart, title: "Analytics", description: "Transparent reporting with actionable insights on rankings, traffic, and conversions" },
      { icon: TrendingUp, title: "Growth Focus", description: "Continuous optimization based on data to drive sustainable organic growth" }
    ],
    benefits: [
      "Increase organic traffic from qualified searchers",
      "Higher rankings for valuable keywords",
      "Better visibility in local Melbourne searches",
      "Transparent monthly reporting and insights",
      "Long-term sustainable growth strategy",
      "Competitive edge in your industry"
    ],
    process: [
      { step: 1, title: "Audit", description: "Comprehensive analysis of your current SEO standing" },
      { step: 2, title: "Strategy", description: "Custom roadmap based on your goals and competition" },
      { step: 3, title: "Execute", description: "Implement technical fixes, content, and optimizations" },
      { step: 4, title: "Report", description: "Monthly insights with clear metrics and next steps" }
    ]
  },
  "integration": {
    title: "System Integration",
    subtitle: "Connect your tools and eliminate data silos",
    tagline: "Unified Business Systems",
    description: "Seamlessly connect your business tools and platforms for smooth data flow and unified operations. Custom API integrations, data synchronization, and middleware solutions that make your tech stack work as one.",
    heroImage: "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80",
    gradient: "from-indigo-600 to-purple-600",
    accentColor: "indigo",
    features: [
      "Custom API development",
      "CRM integration (Salesforce, HubSpot, etc.)",
      "Accounting sync (Xero, MYOB, QuickBooks)",
      "E-commerce platform connections",
      "Payment gateway integration",
      "Real-time data synchronization",
      "Legacy system modernization",
      "Webhook & event automation"
    ],
    capabilities: [
      { icon: Code, title: "API Development", description: "Custom APIs and integrations built to your exact specifications" },
      { icon: RefreshCw, title: "Real-time Sync", description: "Automatic data synchronization between all your business systems" },
      { icon: Database, title: "Data Migration", description: "Safe, accurate migration of data between platforms with validation" },
      { icon: Shield, title: "Secure", description: "Enterprise-grade security for all data transfers and API connections" },
      { icon: Layers, title: "Middleware", description: "Custom middleware solutions to bridge incompatible systems" },
      { icon: Zap, title: "Event-Driven", description: "Webhook integrations that trigger actions across your tech stack" }
    ],
    benefits: [
      "Eliminate manual data entry between systems",
      "Single source of truth for business data",
      "Reduce errors from duplicate data entry",
      "Real-time visibility across all platforms",
      "Faster workflows with connected tools",
      "Future-proof integration architecture"
    ],
    process: [
      { step: 1, title: "Discovery", description: "Map your current systems and integration requirements" },
      { step: 2, title: "Architecture", description: "Design robust, scalable integration architecture" },
      { step: 3, title: "Develop", description: "Build and test integrations with comprehensive QA" },
      { step: 4, title: "Monitor", description: "Ongoing monitoring and support for reliability" }
    ]
  },
  "consulting": {
    title: "AI & Digital Consulting",
    subtitle: "Strategic guidance for your digital transformation journey",
    tagline: "Expert Guidance",
    description: "Navigate the AI and digital landscape with expert consulting tailored to your business. From strategy development to technology selection and implementation planning, we help you make informed decisions that drive real results.",
    heroImage: "https://images.unsplash.com/photo-1553028826-f4804a6dba3b?auto=format&fit=crop&w=1200&q=80",
    gradient: "from-slate-700 to-slate-900",
    accentColor: "slate",
    features: [
      "AI readiness assessment",
      "Digital transformation strategy",
      "Technology stack evaluation",
      "Process optimization analysis",
      "ROI & business case development",
      "Vendor selection guidance",
      "Implementation roadmap",
      "Change management support"
    ],
    capabilities: [
      { icon: Target, title: "Strategy", description: "Clear, actionable digital transformation strategies aligned with your business goals" },
      { icon: BarChart, title: "Assessment", description: "Comprehensive analysis of your current state and opportunities for improvement" },
      { icon: Rocket, title: "Roadmap", description: "Prioritized implementation plans with realistic timelines and milestones" },
      { icon: Award, title: "Best Practices", description: "Industry insights and proven methodologies for successful transformation" },
      { icon: Users, title: "Change Support", description: "Guidance on change management and team adoption strategies" },
      { icon: TrendingUp, title: "ROI Focus", description: "Business case development with clear metrics and expected returns" }
    ],
    benefits: [
      "Make informed technology decisions",
      "Avoid costly implementation mistakes",
      "Accelerate your digital transformation",
      "Clear roadmap with prioritized initiatives",
      "Vendor-agnostic recommendations",
      "Ongoing strategic partnership"
    ],
    process: [
      { step: 1, title: "Discover", description: "Deep dive into your business, goals, and challenges" },
      { step: 2, title: "Analyze", description: "Assessment of current state and opportunity identification" },
      { step: 3, title: "Recommend", description: "Strategic recommendations with business case" },
      { step: 4, title: "Plan", description: "Detailed implementation roadmap and support" }
    ]
  }
};

// Default service template for services not in the detailed list
const defaultServiceTemplate = (service) => ({
  title: service.title,
  subtitle: service.description?.substring(0, 100) + "...",
  tagline: "Professional Solutions",
  description: service.description,
  heroImage: "https://images.unsplash.com/photo-1551434678-e076c223a692?auto=format&fit=crop&w=1200&q=80",
  gradient: "from-[#f9cb07] to-[#ffcd3c]",
  accentColor: "yellow",
  features: service.outcomes || [
    "Professional implementation",
    "Melbourne-based support",
    "Tailored to your needs",
    "Ongoing optimization"
  ],
  capabilities: [
    { icon: Sparkles, title: "Custom Solutions", description: "Tailored specifically to your business requirements and goals" },
    { icon: Users, title: "Expert Team", description: "Melbourne-based specialists with industry experience" },
    { icon: Shield, title: "Quality Assured", description: "Rigorous testing and quality control processes" },
    { icon: Headphones, title: "Dedicated Support", description: "Responsive support team available during business hours" }
  ],
  benefits: [
    "Tailored solution for your specific needs",
    "Melbourne-based team with local understanding",
    "Ongoing support and optimization",
    "Transparent communication throughout"
  ],
  process: [
    { step: 1, title: "Consult", description: "Free consultation to understand your needs" },
    { step: 2, title: "Propose", description: "Detailed proposal with clear deliverables" },
    { step: 3, title: "Deliver", description: "Professional implementation and testing" },
    { step: 4, title: "Support", description: "Ongoing optimization and assistance" }
  ]
});

export default function ServiceDetail() {
  const [, params] = useRoute("/services/:serviceId");
  const serviceId = params?.serviceId;
  const [bookingOpen, setBookingOpen] = useState(false);
  const { settings } = useSiteSettings();

  // Fetch services from API
  const { data: servicesData } = useQuery({
    queryKey: ["/api/services/"],
  });

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

  // Get service data - first check static details, then fall back to API data
  const service = useMemo(() => {
    const staticService = serviceDetails[serviceId];
    if (staticService) return staticService;

    // Check if service exists in API data
    const services = servicesData?.data?.services || servicesData?.services || [];
    const apiService = services.find(s => s.id === serviceId);
    if (apiService) {
      return defaultServiceTemplate(apiService);
    }

    return null;
  }, [serviceId, servicesData]);

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
      <section className="relative overflow-hidden bg-gradient-to-br from-gray-900 via-gray-800 to-black py-24 lg:py-32">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-30">
          <div className={`absolute top-0 right-0 w-[800px] h-[800px] bg-gradient-to-br ${service.gradient} rounded-full blur-[150px] -translate-y-1/2 translate-x-1/3`} />
          <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-[#f9cb07]/30 rounded-full blur-[120px] translate-y-1/2 -translate-x-1/3" />
        </div>

        <div className="relative container mx-auto px-4">
          <Link href="/services">
            <Button variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10 mb-8">
              <ArrowLeft className="mr-2 h-4 w-4" />
              All Services
            </Button>
          </Link>

          <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
            <div className="text-white">
              <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r ${service.gradient} text-white text-sm font-semibold mb-6`}>
                <Sparkles className="w-4 h-4" />
                {service.tagline}
              </div>
              <h1 className="text-4xl lg:text-6xl font-bold mb-6 leading-tight">
                {service.title}
              </h1>
              <p className="text-xl text-white/80 mb-8 leading-relaxed">
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

            <div className="relative">
              <div className="relative rounded-2xl overflow-hidden shadow-2xl shadow-black/50">
                <img
                  src={service.heroImage}
                  alt={service.title}
                  className="w-full h-[400px] lg:h-[500px] object-cover"
                />
                <div className={`absolute inset-0 bg-gradient-to-t ${service.gradient} opacity-20`} />
              </div>
              {/* Floating Stats */}
              <div className="absolute -bottom-6 -left-6 bg-white rounded-xl shadow-xl p-4 hidden lg:block">
                <div className="flex items-center gap-3">
                  <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${service.gradient} flex items-center justify-center`}>
                    <CheckCircle className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-gray-900">100+</p>
                    <p className="text-sm text-gray-600">Projects Delivered</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Description Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl lg:text-4xl font-bold text-black mb-6">Overview</h2>
            <p className="text-lg text-gray-600 leading-relaxed">
              {service.description}
            </p>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <span className="inline-block px-4 py-1.5 rounded-full bg-[#f9cb07]/20 text-[#8a7000] text-sm font-semibold mb-4">
              What's Included
            </span>
            <h2 className="text-3xl lg:text-4xl font-bold text-black">Key Features</h2>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 max-w-6xl mx-auto">
            {service.features.map((feature, index) => (
              <div
                key={index}
                className="group flex items-center p-5 bg-white rounded-xl border border-gray-100 hover:border-[#f9cb07]/50 hover:shadow-lg hover:shadow-[#f9cb07]/10 transition-all duration-300"
              >
                <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-[#f9cb07]/10 flex items-center justify-center mr-4 group-hover:bg-[#f9cb07]/20 transition-colors">
                  <CheckCircle className="h-5 w-5 text-[#f9cb07]" />
                </div>
                <span className="text-gray-700 font-medium">{feature}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Capabilities Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <span className="inline-block px-4 py-1.5 rounded-full bg-[#f9cb07]/20 text-[#8a7000] text-sm font-semibold mb-4">
              Our Expertise
            </span>
            <h2 className="text-3xl lg:text-4xl font-bold text-black">Capabilities</h2>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {service.capabilities.map((capability, index) => {
              const IconComponent = capability.icon;
              return (
                <Card key={index} className="group border-0 shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden">
                  <CardContent className="p-8">
                    <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${service.gradient} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                      <IconComponent className="h-7 w-7 text-white" />
                    </div>
                    <h3 className="text-xl font-bold text-black mb-3">
                      {capability.title}
                    </h3>
                    <p className="text-gray-600 leading-relaxed">
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
      <section className="py-20 bg-gray-900 text-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <span className="inline-block px-4 py-1.5 rounded-full bg-[#f9cb07]/20 text-[#f9cb07] text-sm font-semibold mb-4">
              How We Work
            </span>
            <h2 className="text-3xl lg:text-4xl font-bold">Our Process</h2>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
            {service.process.map((step, index) => (
              <div key={index} className="relative">
                <div className="text-center">
                  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-[#f9cb07] to-[#ffcd3c] flex items-center justify-center mx-auto mb-6 shadow-lg shadow-yellow-500/30">
                    <span className="text-2xl font-bold text-black">{step.step}</span>
                  </div>
                  <h3 className="text-xl font-bold mb-3">{step.title}</h3>
                  <p className="text-white/70">{step.description}</p>
                </div>
                {index < service.process.length - 1 && (
                  <div className="hidden lg:block absolute top-8 left-[60%] w-[80%] border-t-2 border-dashed border-white/20" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <span className="inline-block px-4 py-1.5 rounded-full bg-[#f9cb07]/20 text-[#8a7000] text-sm font-semibold mb-4">
              The Codeteki Advantage
            </span>
            <h2 className="text-3xl lg:text-4xl font-bold text-black">Why Choose Us</h2>
          </div>
          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {service.benefits.map((benefit, index) => (
              <div
                key={index}
                className="flex items-start p-6 bg-gradient-to-br from-gray-50 to-white rounded-xl border border-gray-100"
              >
                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-green-100 flex items-center justify-center mr-4">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                </div>
                <span className="text-gray-700 leading-relaxed pt-2">{benefit}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Melbourne Support Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center mb-16">
            <span className="inline-block px-4 py-1.5 rounded-full bg-[#f9cb07]/20 text-[#8a7000] text-sm font-semibold mb-4">
              Local Expertise
            </span>
            <h2 className="text-3xl lg:text-4xl font-bold text-black mb-4">Melbourne-Based Support</h2>
            <p className="text-lg text-gray-600">
              Work with a local team who understands Australian business needs
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-6 max-w-5xl mx-auto">
            {[
              { icon: Clock, title: "Quick Turnaround", desc: "Fast delivery without compromising quality" },
              { icon: Users, title: "Expert Team", desc: "Specialists in AI and digital solutions" },
              { icon: Headphones, title: "Responsive Support", desc: "Available during AEDT business hours" },
              { icon: MapPin, title: "Local Team", desc: "Melbourne-based with Australia-wide service" }
            ].map((item, index) => (
              <Card key={index} className="text-center border-0 shadow-md hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="w-14 h-14 rounded-2xl bg-[#f9cb07]/10 flex items-center justify-center mx-auto mb-4">
                    <item.icon className="h-7 w-7 text-[#f9cb07]" />
                  </div>
                  <h3 className="font-bold text-black mb-2">{item.title}</h3>
                  <p className="text-sm text-gray-600">{item.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-br from-gray-900 via-gray-800 to-black relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-[#f9cb07]/20 rounded-full blur-[150px]" />
          <div className={`absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-gradient-to-br ${service.gradient} opacity-30 rounded-full blur-[120px]`} />
        </div>

        <div className="relative container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center text-white">
            <h2 className="text-3xl lg:text-5xl font-bold mb-6">
              Ready to Get Started?
            </h2>
            <p className="text-xl text-white/80 mb-10">
              Book a free consultation and discover how {service.title.toLowerCase()} can transform your business.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Button
                size="lg"
                onClick={() => setBookingOpen(true)}
                className="bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] hover:from-[#e6b800] hover:to-[#f9cb07] text-black font-semibold px-10 py-6 text-lg shadow-2xl shadow-yellow-500/30"
              >
                <Calendar className="mr-2 h-5 w-5" />
                Book Free Consultation
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="border-2 border-white/30 text-white hover:bg-white hover:text-black font-semibold px-10 py-6 text-lg"
                onClick={() => window.location.href = `tel:${contactInfo.phone.replace(/\s+/g, "")}`}
              >
                <Phone className="mr-2 h-5 w-5" />
                Call Us Now
              </Button>
            </div>

            {/* Contact Info */}
            <div className="grid md:grid-cols-3 gap-8 pt-8 border-t border-white/10">
              <div className="flex flex-col items-center">
                <div className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center mb-3">
                  <Phone className="h-5 w-5 text-[#f9cb07]" />
                </div>
                <a href={`tel:${contactInfo.phone.replace(/\s+/g, "")}`} className="text-white hover:text-[#f9cb07] transition-colors">
                  {contactInfo.phone}
                </a>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center mb-3">
                  <Mail className="h-5 w-5 text-[#f9cb07]" />
                </div>
                <a href={`mailto:${contactInfo.email}`} className="text-white hover:text-[#f9cb07] transition-colors">
                  {contactInfo.email}
                </a>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center mb-3">
                  <MapPin className="h-5 w-5 text-[#f9cb07]" />
                </div>
                <span className="text-white">{contactInfo.address}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <BookingModal open={bookingOpen} onOpenChange={setBookingOpen} />
    </div>
  );
}
