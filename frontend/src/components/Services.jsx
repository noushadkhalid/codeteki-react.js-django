import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Bot, Globe, Cog, Repeat, Cable, Code, Search } from "lucide-react";

const iconMap = {
  bot: Bot,
  globe: Globe,
  cog: Cog,
  repeat: Repeat,
  cable: Cable,
  code: Code,
  search: Search,
};

const accentStyles = {
  automation: { iconBg: "bg-blue-50", iconColor: "text-blue-600", pill: "bg-blue-100 text-blue-700" },
  workforce: { iconBg: "bg-purple-50", iconColor: "text-purple-600", pill: "bg-purple-100 text-purple-700" },
  integration: { iconBg: "bg-emerald-50", iconColor: "text-emerald-600", pill: "bg-emerald-100 text-emerald-700" },
  tooling: { iconBg: "bg-amber-50", iconColor: "text-amber-600", pill: "bg-amber-100 text-amber-700" },
  web: { iconBg: "bg-slate-50", iconColor: "text-slate-600", pill: "bg-slate-100 text-slate-700" },
  new: { iconBg: "bg-rose-50", iconColor: "text-rose-600", pill: "bg-rose-100 text-rose-700" },
  seo: { iconBg: "bg-teal-50", iconColor: "text-teal-600", pill: "bg-teal-100 text-teal-700" },
};

const defaultServices = [
  {
    id: 1,
    title: "AI Workforce Solutions",
    description: "Deploy domain-trained AI agents that collaborate with your team, manage workflows, and eliminate repetitive busy work.",
    icon: "bot",
    category: "workforce",
    badge: "Enterprise Ready",
    outcomes: ["Human-in-the-loop guardrails", "Secure knowledge base integrations", "Realtime analytics + alerts"],
  },
  {
    id: 2,
    title: "Custom Tool Development",
    description: "Design and ship bespoke internal tools, portals, and dashboards that plug straight into your existing ecosystem.",
    icon: "code",
    category: "tooling",
    badge: "Tailored Builds",
    outcomes: ["Pixel-perfect UI/UX", "First-party API integrations", "Ongoing roadmap partnership"],
  },
  {
    id: 3,
    title: "Business Automation Tools",
    description: "Automate approvals, reporting, compliance, and daily operations with orchestrated workflows across your stack.",
    icon: "cog",
    category: "automation",
    badge: "Process Automation",
    outcomes: ["Unified task orchestration", "Codeteki governance layer", "Return on investment reporting"],
  },
  {
    id: 4,
    title: "MCP Integration Services",
    description: "Connect the Model Context Protocol to your proprietary knowledge bases and tooling to unlock trustworthy automation.",
    icon: "cable",
    category: "integration",
    badge: "MCP Experts",
    outcomes: ["Source-of-truth syncing", "Guardrailed data pipelines", "Observability dashboards"],
  },
  {
    id: 5,
    title: "AI Tools for Daily Tasks",
    description: "Personalized copilots for sales, support, HR, and finance that meet your policies and tone of voice from day one.",
    icon: "repeat",
    category: "tooling",
    badge: "Personal Copilots",
    outcomes: ["Secure workspace libraries", "Role-based access + auditing", "No more context switching"],
  },
  {
    id: 6,
    title: "Professional Web Development",
    description: "Full-stack product teams that deliver marketing sites, customer portals, and high-performance web apps.",
    icon: "globe",
    category: "web",
    badge: "Full Stack",
    outcomes: ["React + Django specialists", "Accessibility-grade builds", "Training + documentation"],
  },
];

export default function Services({ featuredOnly = false }) {
  const queryUrl = featuredOnly ? "/api/services/?featured=1" : "/api/services/";
  const { data, isLoading } = useQuery({
    queryKey: [queryUrl],
  });

  const services = data?.data?.services || data?.services || [];

  const cards = useMemo(() => {
    if (services.length > 0) {
      return services.map((service, idx) => ({
        id: service.id || idx,
        title: service.title || service.name,
        description: service.description,
        icon: (service.icon || "bot").toLowerCase(),
        category: (service.category || "automation").toLowerCase().replace(/\s+/g, ""),
        badge: service.badge,
        outcomes: service.outcomes || [],
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
            AI Solutions That Drive Real Business Results
          </h2>
          <p className="text-lg text-[#52525b] mb-8">
            From intelligent automation to custom development, we deliver end-to-end AI solutions with Melbourne-based support, transparent pricing, and fully managed operations.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button asChild size="lg" className="px-8 py-6 text-lg bg-[#f9cb07] text-black font-semibold hover:bg-[#e6b800]">
              <a href="/contact">Book Consultation</a>
            </Button>
            <Button asChild variant="outline" size="lg" className="px-8 py-6 text-lg border-2 border-black text-black font-semibold hover:bg-black hover:text-white">
              <a href="mailto:info@codeteki.au?subject=Proposal Request">Request Proposal</a>
            </Button>
          </div>
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
                      {service.badge && (
                        <span className="rounded-full bg-[#f9cb07] px-3 py-1 text-xs font-semibold text-black shadow-sm">
                          {service.badge}
                        </span>
                      )}
                    </div>
                    <CardTitle className="mt-6 text-2xl font-bold text-[#09090b]">{service.title}</CardTitle>
                    <CardDescription className="mt-2 text-sm text-[#6b7280] leading-relaxed">
                      {service.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex flex-col flex-grow p-6 pt-0">
                    <div className="flex-grow">
                      {service.outcomes?.length > 0 && (
                        <ul className="text-sm text-[#52525b] space-y-2">
                          {service.outcomes.slice(0, 4).map((outcome, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                              <span className="text-[#f9cb07] mt-1">✓</span>
                              <span>{outcome}</span>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>

                    <div className="flex flex-col gap-3 pt-6">
                      <Button asChild className="w-full bg-[#f9cb07] text-black font-semibold hover:bg-[#e6b800]">
                        <a href="/contact">Book Consultation</a>
                      </Button>
                      <Button
                        asChild
                        variant="outline"
                        className="w-full text-xs uppercase tracking-wide border border-[#e4e4e7] text-[#18181b] hover:bg-[#0f172a] hover:text-white"
                      >
                        <a href={`mailto:info@codeteki.au?subject=Proposal Request - ${service.title}`}>Request Proposal</a>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}

        {/* See All Services Button */}
        <div className="mt-12 text-center">
          <Button asChild size="lg" variant="outline" className="px-8 py-6 text-lg border-2 border-black text-black font-semibold hover:bg-black hover:text-white">
            <a href="/services">See All Services</a>
          </Button>
        </div>
      </div>
    </section>
  );
}
