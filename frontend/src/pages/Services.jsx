import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import {
  Bot,
  Globe,
  Cog,
  ArrowRight,
  Mic,
  Sparkles,
  Rocket,
  ClipboardCheck,
  Layers,
  Star,
} from "lucide-react";
import { Link } from "wouter";
import SEOHead from "../components/SEOHead";

const serviceIconMap = {
  bot: Bot,
  globe: Globe,
  cog: Cog,
  mic: Mic,
};

const accentStyles = {
  automation: { text: "text-blue-600", bg: "bg-blue-100", gradient: "from-blue-500 to-blue-600" },
  workforce: { text: "text-purple-600", bg: "bg-purple-100", gradient: "from-purple-500 to-purple-600" },
  integration: { text: "text-emerald-600", bg: "bg-emerald-100", gradient: "from-emerald-500 to-emerald-600" },
  tooling: { text: "text-amber-600", bg: "bg-amber-100", gradient: "from-amber-500 to-amber-600" },
  web: { text: "text-slate-600", bg: "bg-slate-100", gradient: "from-slate-500 to-slate-600" },
  ai: { text: "text-indigo-600", bg: "bg-indigo-100", gradient: "from-indigo-500 to-indigo-600" },
};

const processIconMap = {
  sparkles: Sparkles,
  layers: Layers,
  clipboardcheck: ClipboardCheck,
  rocket: Rocket,
};

const fallbackServices = [
  {
    id: 1,
    title: "AI Workforce Solutions",
    description:
      "Deploy intelligent chatbots and voice agents that work 24/7 to engage customers, qualify leads, and handle routine inquiries with human-like conversations.",
    icon: "bot",
    badge: "from $699 setup",
    outcomes: [
      "24/7 automated customer engagement",
      "Intelligent lead qualification",
      "Multi-language support",
      "Custom training on your business data",
    ],
  },
  {
    id: 2,
    title: "Professional Web Development",
    description:
      "Modern, responsive websites built with the latest technologies, optimized for mobile devices and search engines to showcase your business.",
    icon: "globe",
    badge: "from $499",
    outcomes: [
      "Mobile-responsive design",
      "Search engine optimization",
      "Content management system",
      "Contact forms and lead capture",
    ],
  },
  {
    id: 3,
    title: "Custom Automation Solutions",
    description:
      "Eliminate repetitive manual tasks with custom automation solutions tailored to your business processes, saving time and reducing errors.",
    icon: "cog",
    badge: "custom scoped",
    outcomes: [
      "Workflow automation",
      "Data entry + reconciliation",
      "Email + support automation",
      "Reporting + dashboards",
    ],
  },
];

const fallbackStats = [
  { label: "Average delivery", value: "4-6 weeks" },
  { label: "Projects delivered", value: "70+" },
  { label: "Live copilots", value: "20+" },
];

const fallbackProcess = [
  {
    title: "Discovery Lab",
    description: "Workshops + audits to map automation and AI opportunities.",
    icon: "sparkles",
    accent: "blue",
  },
  {
    title: "Design & Build",
    description: "UI, flows, and copilots crafted with our Codeteki system.",
    icon: "layers",
    accent: "purple",
  },
  {
    title: "Launch & Train",
    description: "QA, compliance, and handover with your playbooks.",
    icon: "clipboardcheck",
    accent: "yellow",
  },
  {
    title: "Care Plans",
    description: "Support tiers covering monitoring, improvements, and hosting.",
    icon: "rocket",
    accent: "green",
  },
];

const fallbackReasons = [
  { emoji: "🇦🇺", title: "Melbourne pod", copy: "Designers + engineers in the same time zone." },
  { emoji: "✨", title: "Unlimited capabilities", copy: "Custom copilots, automation, and MCP integration." },
  { emoji: "🚀", title: "Fast iterations", copy: "Concept to launch in weeks, not quarters." },
  { emoji: "🤝", title: "Care plans", copy: "Support tiers covering hosting, analytics, enhancements." },
];

const fallbackCTA = {
  title: "Ready to Transform Your Business?",
  description: "Get started with a free consultation and custom quote.",
  primaryButton: { text: "Start Free Consultation", url: "/contact" },
  secondaryButton: { text: "View Our Portfolio", url: "/ai-tools" },
};

export default function Services() {
  const { data: servicesData, isLoading } = useQuery({
    queryKey: ["/api/services/"],
  });

  const servicesPayload = servicesData?.data || servicesData || {};

  const servicesToDisplay = useMemo(() => {
    const remote = Array.isArray(servicesPayload.services) ? servicesPayload.services : [];
    if (!remote.length) return fallbackServices;
    return remote.map((service, idx) => ({
      id: service.id || service.slug || idx,
      title: service.title,
      description: service.description,
      icon: (service.icon || "bot").toLowerCase(),
      badge: service.badge,
      outcomes: service.outcomes || [],
      slug: service.id || service.slug,
    }));
  }, [servicesPayload.services]);

  const serviceStats = useMemo(() => {
    const stats = Array.isArray(servicesPayload.stats) ? servicesPayload.stats : [];
    if (!stats.length) return fallbackStats;
    return stats;
  }, [servicesPayload.stats]);

  const processSteps = useMemo(() => {
    const steps = Array.isArray(servicesPayload.process) ? servicesPayload.process : [];
    if (!steps.length) return fallbackProcess;
    return steps;
  }, [servicesPayload.process]);

  const { data: whyData } = useQuery({
    queryKey: ["/api/why-choose/"],
  });
  const reasons = useMemo(() => {
    const remote = whyData?.data?.whyChoose?.reasons || whyData?.whyChoose?.reasons;
    if (!remote || !remote.length) return fallbackReasons;
    return remote.map((reason) => ({
      emoji: null,
      title: reason.title,
      copy: reason.description,
      icon: reason.icon,
      color: reason.color,
    }));
  }, [whyData]);

  const { data: ctaData } = useQuery({
    queryKey: ["/api/cta-sections", "services"],
    queryFn: async () => {
      const response = await fetch("/api/cta-sections/?placement=services");
      if (!response.ok) throw new Error("Failed to fetch CTA");
      return response.json();
    },
  });
  const ctaSection = ctaData?.data?.ctaSections?.[0] || fallbackCTA;

  return (
    <div className="min-h-screen bg-white">
      <SEOHead
        title="AI Business Services | Codeteki - Melbourne"
        description="Comprehensive AI-powered business services including chatbots, voice assistants, and custom automation."
        keywords="AI services, business automation, chatbot services, voice AI, Melbourne AI development"
      />

      <section className="relative overflow-hidden bg-gradient-to-br from-[#fff9e6] via-white to-[#eef2ff] py-24">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute -top-20 left-1/4 h-64 w-64 rounded-full bg-[#f9cb07]/30 blur-[140px]" />
          <div className="absolute bottom-0 right-10 h-72 w-72 rounded-full bg-[#c4b5fd]/30 blur-[140px]" />
        </div>
        <div className="relative container mx-auto px-4">
          <div className="text-center max-w-4xl mx-auto">
            <span className="codeteki-pill mb-6">Our Core Services</span>
            <h1 className="text-4xl lg:text-5xl font-bold text-black mb-4">
              From AI workforce to custom tools and MCP integration
            </h1>
            <p className="text-lg text-[#52525b]">
              Comprehensive solutions tailored for your business with Melbourne-based delivery, transparent pricing, and
              fully managed operations after launch.
            </p>
          </div>

          <div className="mt-12 grid grid-cols-1 gap-6 sm:grid-cols-3">
            {serviceStats.map((stat) => (
              <div
                key={stat.label}
                className="rounded-2xl border border-white/80 bg-white shadow-[0_15px_35px_rgba(15,23,42,0.08)] p-6 text-center"
              >
                <p className="text-3xl font-bold text-[#0f172a]">{stat.value}</p>
                <p className="mt-2 text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          {isLoading ? (
            <div className="flex justify-center py-16">
              <div className="h-16 w-16 animate-spin rounded-full border-b-2 border-[#f9cb07]" />
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
              {servicesToDisplay.map((service) => {
                const IconComponent = serviceIconMap[service.icon] || Bot;
                const accent = accentStyles[service.badge?.toLowerCase()] || accentStyles.automation;
                return (
                  <Card
                    key={service.id}
                    className="flex h-full flex-col rounded-2xl border border-white/80 bg-white/95 backdrop-blur shadow-[0_20px_50px_rgba(15,23,42,0.08)]"
                  >
                    <CardHeader className="p-6 pb-4">
                      <div className="flex items-center justify-between">
                        <div className={`h-12 w-12 rounded-xl ring-8 ring-white ${accent.bg} flex items-center justify-center`}>
                          <IconComponent className={`h-5 w-5 ${accent.text}`} />
                        </div>
                        {service.badge && (
                          <span className="rounded-full bg-[#f5f5f4] px-3 py-1 text-xs font-semibold text-[#18181b]">
                            {service.badge}
                          </span>
                        )}
                      </div>
                      <CardTitle className="mt-6 text-2xl font-bold text-[#09090b]">{service.title}</CardTitle>
                      <CardDescription className="mt-2 text-sm text-[#6b7280] leading-relaxed">
                        {service.description}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="flex flex-1 flex-col gap-4 p-6 pt-0">
                      {service.outcomes?.length > 0 && (
                        <ul className="text-sm text-[#52525b] space-y-2">
                          {service.outcomes.slice(0, 4).map((feature, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                              <span className="text-[#f9cb07] mt-1">•</span>
                              <span>{feature}</span>
                            </li>
                          ))}
                        </ul>
                      )}

                      <div className="mt-auto space-y-3">
                        <Link href={`/services/${service.slug || service.id}`}>
                          <Button className="w-full bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] text-black font-bold py-3">
                            Learn More
                            <ArrowRight className="ml-2 h-4 w-4" />
                          </Button>
                        </Link>
                        <Button
                          variant="outline"
                          className="w-full border-2 border-[#f9cb07]/50 text-[#f9cb07] hover:bg-[#f9cb07] hover:text-black"
                        >
                          Get Custom Quote
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </div>
      </section>

      <section className="py-20 bg-white relative overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-10 left-10 h-48 w-48 rounded-full bg-[#dbeafe]/40 blur-[150px]" />
        </div>
        <div className="container mx-auto px-4 relative z-10">
          <div className="text-center mb-16">
            <span className="codeteki-pill mb-6">How we ship</span>
            <h2 className="text-4xl font-bold text-black mb-4">Our delivery framework</h2>
          </div>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {processSteps.map((step, idx) => {
              const IconComponent = processIconMap[(step.icon || "").toLowerCase()] || Sparkles;
              return (
                <div key={step.title} className="rounded-2xl border border-[#eef1f7] bg-white/90 p-6 shadow-sm">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[#f9cb07]/15 text-[#f9cb07] font-bold">
                      {idx + 1}
                    </span>
                    <IconComponent className="h-5 w-5 text-[#0f172a]" />
                  </div>
                  <h3 className="text-xl font-semibold text-[#0f172a] mb-2">{step.title}</h3>
                  <p className="text-sm text-gray-600">{step.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="py-20 bg-[#0f172a] text-white relative overflow-hidden">
        <div className="absolute inset-0 opacity-30 bg-[radial-gradient(circle_at_top,_rgba(249,203,7,0.2),transparent_60%)]" />
        <div className="container mx-auto px-4 relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Why Australian teams pick Codeteki</h2>
            <p className="text-lg text-white/80 max-w-3xl mx-auto">
              Local pods, unlimited capabilities, and hands-on support long after launch.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {reasons.map((reason) => (
              <div key={reason.title} className="rounded-2xl border border-white/20 bg-white/5 p-6 text-center shadow">
                <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-white/20 text-2xl">
                  {reason.emoji || <Star className="h-6 w-6" />}
                </div>
                <h3 className="text-xl font-semibold mb-2">{reason.title}</h3>
                <p className="text-sm text-white/80">{reason.copy}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 bg-[#f9cb07]/5">
        <div className="container mx-auto px-4 text-center max-w-4xl">
          <span className="codeteki-pill mb-6">{ctaSection.subtitle || "Ready to Transform?"}</span>
          <h2 className="text-4xl font-bold text-black mb-4">{ctaSection.title}</h2>
          <p className="text-lg text-gray-600 mb-8">{ctaSection.description}</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            {ctaSection.primaryButton && (
              <Link href={ctaSection.primaryButton.url || "/contact"}>
                <Button size="lg" className="bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] text-black font-semibold px-8 py-4">
                  {ctaSection.primaryButton.text || "Start Free Consultation"}
                </Button>
              </Link>
            )}
            {ctaSection.secondaryButton && (
              <Link href={ctaSection.secondaryButton.url || "/ai-tools"}>
                <Button
                  variant="outline"
                  size="lg"
                  className="border-2 border-[#f9cb07] text-[#f9cb07] hover:bg-[#f9cb07] hover:text-black font-semibold px-8 py-4"
                >
                  {ctaSection.secondaryButton.text || "View Portfolio"}
                </Button>
              </Link>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
