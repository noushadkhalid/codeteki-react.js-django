import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Bot, Globe, Cog, Repeat, Cable, Code } from "lucide-react";

const remoteCTA = {
  href: "mailto:info@codeteki.au",
  label: "Book consultations",
};

const iconMap = {
  bot: Bot,
  globe: Globe,
  cog: Cog,
  repeat: Repeat,
  cable: Cable,
  code: Code,
};

const accentStyles = {
  automation: { iconBg: "bg-blue-50", iconColor: "text-blue-600", pill: "bg-blue-100 text-blue-700" },
  workforce: { iconBg: "bg-purple-50", iconColor: "text-purple-600", pill: "bg-purple-100 text-purple-700" },
  integration: { iconBg: "bg-emerald-50", iconColor: "text-emerald-600", pill: "bg-emerald-100 text-emerald-700" },
  tooling: { iconBg: "bg-amber-50", iconColor: "text-amber-600", pill: "bg-amber-100 text-amber-700" },
  web: { iconBg: "bg-slate-50", iconColor: "text-slate-600", pill: "bg-slate-100 text-slate-700" },
};

const defaultServices = [
  {
    id: 1,
    title: "AI Workforce Solutions",
    description: "Unlimited chat + voice agents trained on your knowledge to pick up every call, qualify leads, and book meetings.",
    icon: "bot",
    category: "workforce",
    pricing: "from $699 setup",
    metrics: ["60% staffing savings", "24/7 availability"],
    features: ["Custom tone + persona", "Live transfer handoff", "CRM + calendar syncing", "Analytics dashboard"],
  },
  {
    id: 2,
    title: "Custom Tool Development",
    description: "Bespoke internal tools, calculators, and customer-facing AI experiences delivered end-to-end.",
    icon: "code",
    category: "tooling",
    pricing: "from $3k",
    metrics: ["4-6 week delivery", "Australian hosting"],
    features: ["React + Next.js builds", "Secure auth workflows", "Payments + billing automation", "Maintenance options"],
  },
  {
    id: 3,
    title: "Business Automation",
    description: "We eliminate repetitive tasks across operations, HR, finance, and customer success with AI-led automation.",
    icon: "cog",
    category: "automation",
    pricing: "custom per workflow",
    metrics: ["80% manual reduction", "ROI in 3 months"],
    features: ["Document + email automation", "Data entry + reconciliation", "Inventory + order syncing", "Reporting pipelines"],
  },
  {
    id: 4,
    title: "MCP Integrations",
    description: "Connect Claude and other assistants to your databases and tools using Model Context Protocol.",
    icon: "cable",
    category: "integration",
    pricing: "from $4k",
    metrics: ["Secure access", "Real-time syncing"],
    features: ["Design + implementation", "Policy + access controls", "Audit + monitoring", "LLM guardrails"],
  },
  {
    id: 5,
    title: "AI Tools for Daily Tasks",
    description: "Deploy AI tools similar to DesiFirms (diet planners, property analyzers, visa copilots) under your brand.",
    icon: "repeat",
    category: "tooling",
    pricing: "white-label or custom",
    metrics: ["Over 20 live tools", "100% managed"],
    features: ["White-label UI", "Hosting + analytics", "Credit/paywall system", "Support + updates"],
  },
  {
    id: 6,
    title: "Web Development",
    description: "High-performance, SEO-ready websites that integrate Codeteki AI agents and forms out of the box.",
    icon: "globe",
    category: "web",
    pricing: "from $499",
    metrics: ["4.5s faster than average", "100 Lighthouse score"],
    features: ["Figma-to-code delivery", "Copywriting support", "CMS + blog setup", "Ongoing care plans"],
  },
];

export default function Services() {
  const { data, isLoading } = useQuery({
    queryKey: ["/api/services/"],
  });

  const services = data?.data?.services || data?.services || [];

  const cards = useMemo(() => {
    if (services.length > 0) {
      return services.map((service, idx) => ({
        id: service.id || idx,
        title: service.title || service.name,
        description: service.description,
        icon: (service.icon || "bot").toLowerCase(),
        category: (service.badge || service.category || "automation").toLowerCase().replace(/\s+/g, ""),
        pricing: service.pricing || service.badge,
        metrics: service.outcomes || service.metrics || [],
        features: service.features || [],
        slug: service.slug,
      }));
    }
    return defaultServices;
  }, [services]);

  return (
    <section id="services" className="relative py-24 overflow-hidden bg-gradient-to-b from-white via-[#f7f8fb] to-white">
      <div className="absolute inset-x-0 top-0 h-64 bg-gradient-to-b from-[#f9cb07]/15 to-transparent pointer-events-none" />
      <div className="relative container mx-auto px-4">
        <div className="text-center max-w-4xl mx-auto mb-16">
          <span className="codeteki-pill mb-6">Our Core Services</span>
          <h2 className="text-4xl lg:text-5xl font-bold text-black mt-6 mb-4">
            From AI workforce to custom tools and MCP integration
          </h2>
          <p className="text-lg text-[#52525b]">
            Comprehensive solutions tailored for your business with Melbourne-based delivery, transparent pricing, and
            fully managed operations once we launch.
          </p>
        </div>

        {isLoading ? (
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#f9cb07]" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {cards.map((service) => {
              const IconComponent = iconMap[service.icon] || Bot;
              const accents = accentStyles[service.category] || accentStyles.automation;
              return (
                <Card
                  key={service.id}
                  className="flex h-full flex-col rounded-2xl border border-white/80 bg-white/95 backdrop-blur shadow-[0_20px_50px_rgba(15,23,42,0.08)] hover:-translate-y-1.5 transition-transform duration-300"
                >
                  <CardHeader className="p-6 pb-4">
                    <div className="flex items-center justify-between">
                      <div className={`h-12 w-12 rounded-xl ring-8 ring-white ${accents.iconBg} flex items-center justify-center`}>
                        <IconComponent className={`h-5 w-5 ${accents.iconColor}`} />
                      </div>
                      <Badge className="bg-[#f5f5f4] text-xs text-[#18181b]">{service.pricing || "Custom"}</Badge>
                    </div>
                    <CardTitle className="mt-6 text-2xl font-bold text-[#09090b]">{service.title}</CardTitle>
                    <CardDescription className="mt-2 text-sm text-[#6b7280] leading-relaxed">
                      {service.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex flex-col gap-6 p-6 pt-0">
                    {service.metrics?.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {service.metrics.map((metric, idx) => (
                          <Pill key={idx} className={accents.pill}>
                            {metric}
                          </Pill>
                        ))}
                      </div>
                    )}
                    {service.features?.length > 0 && (
                      <ul className="text-sm text-[#52525b] space-y-2">
                        {service.features.slice(0, 4).map((feature, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <span className="text-[#f9cb07] mt-1">•</span>
                            <span>{feature}</span>
                          </li>
                        ))}
                      </ul>
                    )}

                    <div className="mt-auto flex flex-col gap-3">
                      <Button asChild className="w-full bg-[#f9cb07] text-black font-semibold hover:bg-[#e6b800]">
                        <a href={remoteCTA.href}>{remoteCTA.label}</a>
                      </Button>
                      <Button
                        variant="outline"
                        className="text-xs uppercase tracking-wide border border-[#e4e4e7] text-[#18181b] hover:bg-[#0f172a] hover:text-white"
                      >
                        Request proposal
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
  );
}

const Pill = ({ children, className }) => (
  <span className={`text-xs font-semibold px-3 py-1 rounded-full ${className}`}>{children}</span>
);
