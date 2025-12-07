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
import { getIcon } from "../lib/iconMap";

// Icon map for capabilities
const iconMap = {
  Bot, Mic, Cog, Globe, Building, Zap, Shield, TrendingUp, Target, Sparkles,
  Code, Search, BarChart, MessageSquare, Rocket, Layers, RefreshCw, Database,
  Lock, Wrench, Repeat, Cable, FileText, Eye, Settings, LineChart, PieChart,
  Activity, Users, Award, Headphones, Clock, MapPin, Mail, Phone, CheckCircle, Calendar
};

// Fallback static data (used when API data is incomplete)
const fallbackServiceData = {
  "ai-workforce": {
    tagline: "Enterprise Ready",
    subtitle: "Domain-trained AI agents that collaborate with your team",
    fullDescription: "Deploy domain-trained AI agents that collaborate with your team, manage workflows, and eliminate repetitive busy work. Our AI workforce solutions include intelligent chatbots, voice agents, and automation tools that work 24/7.",
    heroImage: "https://images.unsplash.com/photo-1531746790731-6c087fecd65a?auto=format&fit=crop&w=1200&q=80",
    gradient: "from-purple-600 to-indigo-600",
  },
  "custom-tools": {
    tagline: "Tailored Builds",
    subtitle: "Bespoke internal tools, portals, and dashboards",
    fullDescription: "Design and ship bespoke internal tools, portals, and dashboards that plug straight into your existing ecosystem.",
    heroImage: "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=1200&q=80",
    gradient: "from-orange-500 to-red-600",
  },
  "automation": {
    tagline: "Process Automation",
    subtitle: "Orchestrated workflows that automate approvals and operations",
    fullDescription: "Automate approvals, reporting, compliance, and daily operations with orchestrated workflows across your entire tech stack.",
    heroImage: "https://images.unsplash.com/photo-1518186285589-2f7649de83e0?auto=format&fit=crop&w=1200&q=80",
    gradient: "from-amber-500 to-orange-600",
  },
  "daily-ai": {
    tagline: "Personal Copilots",
    subtitle: "Personalized AI copilots for sales, support, HR, and finance",
    fullDescription: "Personalized AI copilots for sales, support, HR, and finance that meet your policies and tone of voice from day one.",
    heroImage: "https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=1200&q=80",
    gradient: "from-cyan-500 to-blue-600",
  },
  "mcp-integration": {
    tagline: "MCP Experts",
    subtitle: "Connect Model Context Protocol to your knowledge bases",
    fullDescription: "Connect the Model Context Protocol to your proprietary knowledge bases and tooling to unlock trustworthy automation.",
    heroImage: "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80",
    gradient: "from-violet-600 to-purple-700",
  },
  "web-dev": {
    tagline: "Full Stack",
    subtitle: "Full-stack teams delivering marketing sites and web apps",
    fullDescription: "Full-stack product teams that deliver marketing sites, customer portals, and high-performance web applications.",
    heroImage: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&q=80",
    gradient: "from-blue-600 to-cyan-600",
  },
  "seo-engine": {
    tagline: "New",
    subtitle: "Comprehensive SEO auditing with AI recommendations",
    fullDescription: "Comprehensive SEO auditing platform with Lighthouse, PageSpeed Insights, Search Console integration, and AI-powered recommendations.",
    heroImage: "https://images.unsplash.com/photo-1432888622747-4eb9a8efeb07?auto=format&fit=crop&w=1200&q=80",
    gradient: "from-emerald-600 to-teal-600",
  }
};

// Default fallback
const defaultFallback = {
  tagline: "Professional Solutions",
  subtitle: "Melbourne-based AI and digital solutions",
  fullDescription: "Professional AI and digital solutions tailored to your business needs.",
  heroImage: "https://images.unsplash.com/photo-1551434678-e076c223a692?auto=format&fit=crop&w=1200&q=80",
  gradient: "from-[#f9cb07] to-[#ffcd3c]",
};

export default function ServiceDetail() {
  const [, params] = useRoute("/services/:serviceId");
  const serviceId = params?.serviceId;
  const [bookingOpen, setBookingOpen] = useState(false);
  const { settings } = useSiteSettings();

  // Fetch service detail from API
  const { data: serviceData, isLoading } = useQuery({
    queryKey: [`/api/services/${serviceId}/`],
    enabled: !!serviceId,
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

  // Build service object from API data with fallbacks
  const service = useMemo(() => {
    const apiService = serviceData?.data?.service || serviceData?.service;
    if (!apiService && !serviceId) return null;

    // Get fallback data for this service
    const fallback = fallbackServiceData[serviceId] || defaultFallback;

    // If we have API data, merge with fallbacks for missing fields
    if (apiService) {
      const gradient = apiService.gradient || fallback.gradient;

      return {
        id: apiService.id,
        title: apiService.title,
        badge: apiService.badge,
        description: apiService.description,
        icon: apiService.icon,
        // Detail fields - use API data or fallback
        tagline: apiService.tagline || fallback.tagline,
        subtitle: apiService.subtitle || apiService.description?.substring(0, 150) || fallback.subtitle,
        fullDescription: apiService.fullDescription || apiService.description || fallback.fullDescription,
        heroImage: apiService.heroImage || fallback.heroImage,
        gradient: gradient,
        // Related content from API
        outcomes: apiService.outcomes || [],
        features: apiService.features || apiService.outcomes || [],
        capabilities: apiService.capabilities || [],
        benefits: apiService.benefits || [],
        process: apiService.process || [],
      };
    }

    // No API data yet but we have serviceId - show fallback
    if (serviceId && fallback !== defaultFallback) {
      return {
        id: serviceId,
        title: serviceId.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
        badge: fallback.tagline,
        tagline: fallback.tagline,
        subtitle: fallback.subtitle,
        fullDescription: fallback.fullDescription,
        heroImage: fallback.heroImage,
        gradient: fallback.gradient,
        features: [],
        capabilities: [],
        benefits: [],
        process: [],
      };
    }

    return null;
  }, [serviceData, serviceId]);

  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-white">
        <div className="text-center px-4">
          <div className="w-16 h-16 mx-auto mb-4 border-4 border-[#f9cb07] border-t-transparent rounded-full animate-spin" />
          <p className="text-gray-600">Loading service details...</p>
        </div>
      </div>
    );
  }

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

  // Helper to get icon component
  const getIconComponent = (iconName) => {
    if (!iconName) return Sparkles;
    return iconMap[iconName] || getIcon(iconName) || Sparkles;
  };

  return (
    <div className="min-h-screen bg-white">
      <SEOHead
        title={`${service.title} | Codeteki Melbourne`}
        description={service.fullDescription || service.description}
        page={`service-${serviceId}`}
      />

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-gray-900 via-gray-800 to-black py-20 lg:py-28">
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
                {service.tagline || service.badge}
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
              {service.fullDescription}
            </p>
          </div>
        </div>
      </section>

      {/* Features Grid - Only show if we have features */}
      {service.features && service.features.length > 0 && (
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
      )}

      {/* Capabilities Section - Only show if we have capabilities */}
      {service.capabilities && service.capabilities.length > 0 && (
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
                const IconComponent = getIconComponent(capability.icon);
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
      )}

      {/* Process Section - Only show if we have process steps */}
      {service.process && service.process.length > 0 && (
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
      )}

      {/* Benefits Section - Only show if we have benefits */}
      {service.benefits && service.benefits.length > 0 && (
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
      )}

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
