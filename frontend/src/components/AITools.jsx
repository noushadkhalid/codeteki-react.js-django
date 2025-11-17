import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { ExternalLink } from "lucide-react";

const remoteUrl = "https://www.desifirms.com.au/ai-tools";

const fallbackTools = [
  {
    title: "Australian Trip Planner",
    description: "Discover curated itineraries, verified attractions, and travel tips for every Australian city.",
    emoji: "🧭",
    status: "free",
    category: "lifestyle",
    link: `${remoteUrl}/australian-trip-planner`,
  },
  {
    title: "Baby Growth Tracker",
    description: "Track milestones, immunisation schedules, and growth charts aligned with Australian health data.",
    emoji: "👶",
    status: "free",
    category: "health",
    link: `${remoteUrl}/baby-growth-tracker`,
  },
  {
    title: "Pregnancy Due Date Calculator",
    description: "Plan trimester visits and due dates using conception or cycle data.",
    emoji: "🍼",
    status: "free",
    category: "health",
    link: `${remoteUrl}/pregnancy-due-date`,
  },
  {
    title: "Water Intake Calculator",
    description: "Daily hydration goals tuned for local climate and lifestyle.",
    emoji: "💧",
    status: "free",
    category: "health",
    link: `${remoteUrl}/water-intake-calculator`,
  },
  {
    title: "Body Fat Percentage Calculator",
    description: "Estimate body fat using multiple measurement formulas and guidance.",
    emoji: "📊",
    status: "free",
    category: "health",
    link: `${remoteUrl}/body-fat-percentage`,
  },
  {
    title: "Calorie Calculator",
    description: "Get personalised calorie targets for weight gain, maintenance, or loss.",
    emoji: "🍎",
    status: "free",
    category: "health",
    link: `${remoteUrl}/calorie-calculator`,
  },
  {
    title: "BMI Calculator",
    description: "BMI with imperial/metric inputs and health categories.",
    emoji: "⚖️",
    status: "free",
    category: "health",
    link: `${remoteUrl}/bmi-calculator`,
  },
  {
    title: "Mid-Market Exchange Rate Tool",
    description: "Live rates and fee guidance for sending money overseas.",
    emoji: "💱",
    status: "free",
    category: "finance",
    link: `${remoteUrl}/exchange-rate-tool`,
  },
  {
    title: "Gift Ideas Generator",
    description: "Culture-aware gift suggestions for every occasion and relationship.",
    emoji: "🎁",
    status: "credits",
    minCredits: 15,
    category: "lifestyle",
    link: `${remoteUrl}/gift-ideas-generator`,
  },
  {
    title: "Smart Invoice Builder",
    description: "AI-powered invoices with summaries, PDF export, and compliance checks.",
    emoji: "🧾",
    status: "credits",
    minCredits: 20,
    category: "business",
    link: `${remoteUrl}/invoice-builder`,
  },
  {
    title: "Product Description Generator",
    description: "Create bilingual descriptions for marketplaces and catalogues.",
    emoji: "🛍️",
    status: "credits",
    minCredits: 18,
    category: "business",
    link: `${remoteUrl}/product-description-generator`,
  },
  {
    title: "Desi Party Food Planner",
    description: "Plan perfect South Asian food quantities for weddings and parties.",
    emoji: "🍽️",
    status: "premium",
    creditCost: 75,
    category: "lifestyle",
    previewLink: `${remoteUrl}/desi-food-planner`,
    launchLink: `${remoteUrl}/desi-food-planner`,
  },
  {
    title: "Desi Diet & Weight Management",
    description: "Diet plans with Desi ingredient swaps and weekly shopping lists.",
    emoji: "🥗",
    status: "premium",
    creditCost: 65,
    category: "health",
    previewLink: `${remoteUrl}/diet-planner`,
    launchLink: `${remoteUrl}/diet-planner`,
  },
  {
    title: "Visa Immigration Assistant",
    description: "Analyse visa options and pathways with personalised scoring.",
    emoji: "🛂",
    status: "premium",
    creditCost: 40,
    category: "immigration",
    previewLink: `${remoteUrl}/visa-guidance`,
    launchLink: `${remoteUrl}/visa-guidance`,
  },
  {
    title: "Property Development Planner",
    description: "See what you can build based on zoning law, setbacks, and council data.",
    emoji: "🏗️",
    status: "premium",
    creditCost: 90,
    category: "property",
    previewLink: `${remoteUrl}/property-development-planner`,
    launchLink: `${remoteUrl}/property-development-planner`,
  },
  {
    title: "Investment Property Analyzer",
    description: "Detailed feasibility reports that combine council data with AI recommendations.",
    emoji: "📈",
    status: "premium",
    creditCost: 70,
    category: "property",
    previewLink: `${remoteUrl}/investment-property-analyzer`,
    launchLink: `${remoteUrl}/investment-property-analyzer`,
    comingSoon: true,
  },
  {
    title: "Jet Lag Recovery Planner",
    description: "Personalised routines that adapt to your itinerary, hydration, and sleep data.",
    emoji: "🛫",
    status: "premium",
    creditCost: 50,
    category: "lifestyle",
    previewLink: `${remoteUrl}/jet-lag-recovery-planner`,
    launchLink: `${remoteUrl}/jet-lag-recovery-planner`,
    comingSoon: true,
  },
  {
    title: "Business Ideas Generator",
    description: "Category-aware ideas for service businesses, retail concepts, and franchises.",
    emoji: "💡",
    status: "credits",
    minCredits: 25,
    category: "business",
    link: `${remoteUrl}/business-ideas-generator`,
    comingSoon: true,
  },
  {
    title: "Unified PDF Editor",
    description: "Merge, annotate, translate, and sign documents with Desi-focused templates.",
    emoji: "📄",
    status: "credits",
    minCredits: 22,
    category: "business",
    link: `${remoteUrl}/unified-pdf-editor`,
    comingSoon: true,
  },
];

const fallbackSection = {
  badge: "Built by Codeteki • Hosted on DesiFirms",
  title: "Explore the production-ready AI tools we already operate",
  description:
    "All Codeteki utilities are deployed on DesiFirms.com.au for the Australian market. This page connects you directly to the live tools—no mock-ups, no future promises.",
};

export const aiToolsDataset = fallbackTools;

const categoryStyles = {
  health: { bg: "bg-[#fefce8]", icon: "text-[#92400e]" },
  finance: { bg: "bg-[#e0f2fe]", icon: "text-[#075985]" },
  lifestyle: { bg: "bg-[#fef3c7]", icon: "text-[#92400e]" },
  business: { bg: "bg-[#ede9fe]", icon: "text-[#5b21b6]" },
  immigration: { bg: "bg-[#fee2e2]", icon: "text-[#b91c1c]" },
  property: { bg: "bg-[#ecfccb]", icon: "text-[#3f6212]" },
  general: { bg: "bg-[#f4f4f5]", icon: "text-[#27272a]" },
};

const statusConfig = {
  free: { label: "Free Tool", className: "bg-green-100 text-green-800" },
  credits: { label: "Credits", className: "bg-blue-100 text-blue-800" },
  premium: { label: "Premium", className: "bg-purple-100 text-purple-800" },
};

const Pill = ({ children, className = "" }) => (
  <span className={`text-[11px] font-semibold px-3 py-1 rounded-full ${className}`}>{children}</span>
);

const getCounts = (items) =>
  items.reduce(
    (acc, tool) => {
      acc.total += 1;
      if (tool.comingSoon) {
        acc.comingSoon += 1;
      } else {
        if (tool.status === "free") acc.free += 1;
        if (tool.status === "credits") acc.credits += 1;
        if (tool.status === "premium") acc.premium += 1;
      }
      return acc;
    },
    { total: 0, free: 0, credits: 0, premium: 0, comingSoon: 0 }
  );

const filterTools = (tools, tab) => {
  switch (tab) {
    case "free":
      return tools.filter((tool) => tool.status === "free" && !tool.comingSoon);
    case "credits":
      return tools.filter((tool) => tool.status === "credits" && !tool.comingSoon);
    case "premium":
      return tools.filter((tool) => tool.status === "premium" && !tool.comingSoon);
    case "coming-soon":
      return tools.filter((tool) => tool.comingSoon);
    default:
      return tools;
  }
};

const normalizeBackendTools = (tools = []) =>
  tools.map((tool) => ({
    title: tool.title,
    description: tool.description,
    emoji: tool.emoji || tool.icon || "⚡️",
    status: tool.status || "free",
    category: tool.category || "general",
    link: tool.externalUrl || tool.cta?.url || tool.secondaryCta?.url || remoteUrl,
    previewLink: tool.previewUrl || tool.secondaryCta?.url || tool.externalUrl,
    launchLink: tool.cta?.url || tool.externalUrl || tool.previewUrl,
    minCredits: tool.minCredits || 0,
    creditCost: tool.creditCost || 0,
    comingSoon: Boolean(tool.comingSoon),
    badge: tool.badge,
  }));

export default function AITools({ showEmbed = false }) {
  const [activeFilter, setActiveFilter] = useState("all");
  const { data, isLoading } = useQuery({
    queryKey: ["/api/ai-tools/"],
  });

  const apiSection = data?.data?.aiTools || data?.aiTools;
  const normalizedTools = useMemo(() => normalizeBackendTools(apiSection?.tools), [apiSection]);
  const dataset = normalizedTools.length ? normalizedTools : fallbackTools;

  const sectionCopy = apiSection || fallbackSection;

  const toolCounts = useMemo(() => getCounts(dataset), [dataset]);
  const filterOptions = useMemo(
    () => [
      { key: "all", label: `All Tools (${toolCounts.total})` },
      { key: "free", label: `Free Tools (${toolCounts.free})` },
      { key: "credits", label: `Credit Tools (${toolCounts.credits})` },
      { key: "premium", label: `Premium (${toolCounts.premium})` },
      { key: "coming-soon", label: `Coming Soon (${toolCounts.comingSoon})` },
    ],
    [toolCounts]
  );

  const filteredTools = useMemo(
    () => filterTools(dataset, activeFilter),
    [dataset, activeFilter]
  );

  return (
    <section className="relative py-20 bg-gradient-to-b from-white via-[#f7f8fb] to-white overflow-hidden">
      <div className="absolute inset-y-0 right-0 w-1/2 bg-[#f9cb07]/10 blur-[150px]" aria-hidden="true" />
      <div className="absolute inset-y-0 left-0 w-1/3 bg-[#c4b5fd]/15 blur-[150px]" aria-hidden="true" />

      <div className="relative container mx-auto px-4">
        <div className="text-center max-w-4xl mx-auto mb-12">
          <span className="codeteki-pill mb-6">
            {sectionCopy.badge || fallbackSection.badge}
          </span>
          <h2 className="text-4xl lg:text-5xl font-bold text-black mb-4">
            {sectionCopy.title || fallbackSection.title}
          </h2>
          {sectionCopy.description ? (
            <p
              className="text-lg text-[var(--codeteki-gray)]"
              dangerouslySetInnerHTML={{ __html: sectionCopy.description }}
            />
          ) : (
            <p className="text-lg text-[var(--codeteki-gray)]">{fallbackSection.description}</p>
          )}
        </div>

        <div className="bg-white/80 border border-white/70 rounded-2xl shadow-[0_15px_60px_rgba(15,23,42,0.07)] p-3 flex flex-wrap items-center gap-3 justify-center">
          {filterOptions.map((option) => (
            <button
              key={option.key}
              onClick={() => setActiveFilter(option.key)}
              className={`text-sm font-semibold px-4 py-2 rounded-full border transition-all duration-200 ${
                activeFilter === option.key
                  ? "bg-[#0f172a] text-white border-[#0f172a]"
                  : "bg-white text-[#0f172a] border-[#e4e4e7] hover:border-[#0f172a]/40"
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>

        {isLoading && !normalizedTools.length ? (
          <div className="mt-10 flex justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#f9cb07]" />
          </div>
        ) : (
          <div className="mt-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredTools.map((tool) => {
              const status = statusConfig[tool.status];
              const accents = categoryStyles[tool.category] || categoryStyles.general;

              return (
                <div
                  key={tool.title}
                  className={`relative flex h-full flex-col rounded-2xl border border-[#e5e7eb] bg-white p-5 text-left shadow-sm transition-all duration-200 hover:-translate-y-1 hover:shadow-lg ${
                    tool.comingSoon ? "opacity-80" : ""
                  }`}
                >
                  {tool.comingSoon && (
                    <div className="absolute inset-0 rounded-2xl bg-white/70 backdrop-blur-sm flex items-center justify-center text-[#0f172a] font-semibold">
                      Coming Soon
                    </div>
                  )}
                  <div className="flex items-start justify-between">
                    <div className={`h-12 w-12 rounded-2xl ring-8 ring-white ${accents.bg} flex items-center justify-center text-2xl`}>
                      {tool.emoji || "⚡️"}
                    </div>
                    {!tool.comingSoon && status && (
                      <Badge className={`${status.className} text-xs font-semibold`}>
                        {status.label}
                      </Badge>
                    )}
                  </div>
                  <div className="mt-4 space-y-2">
                    <h3 className="text-lg font-semibold text-slate-900">{tool.title}</h3>
                    <p className="text-sm text-slate-600 leading-relaxed">{tool.description}</p>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-4">
                    {!tool.comingSoon && status && (
                      <Pill className={`${status.className} uppercase`}>
                        {status.label}
                      </Pill>
                    )}
                    {tool.minCredits > 0 && !tool.comingSoon && (
                      <Pill className="bg-[#e0f2fe] text-[#075985]">
                        Min {tool.minCredits} credits
                      </Pill>
                    )}
                    {tool.creditCost > 0 && !tool.comingSoon && (
                      <Pill className="bg-[#ede9fe] text-[#5b21b6]">
                        {tool.creditCost} credits
                      </Pill>
                    )}
                    {tool.badge && (
                      <Pill className="bg-[#fef9c3] text-[#854d0e]">{tool.badge}</Pill>
                    )}
                  </div>
                  <div className="mt-auto pt-5">
                    {tool.comingSoon ? (
                      <Button variant="outline" className="w-full" disabled>
                        Launching soon
                      </Button>
                    ) : tool.status === "premium" ? (
                      <div className="flex gap-2">
                        {tool.previewLink && (
                          <Button
                            variant="outline"
                            className="flex-1 text-xs font-semibold border-[#e5e7eb] text-slate-700 hover:bg-[#0093E9]/10 hover:text-[#0093E9]"
                            asChild
                          >
                            <a href={tool.previewLink} target="_blank" rel="noopener noreferrer">
                              Preview Results
                            </a>
                          </Button>
                        )}
                        <Button className="flex-1 text-xs font-semibold bg-gradient-to-r from-[#7c3aed] to-[#9f67ff]" asChild>
                          <a href={tool.launchLink || tool.link} target="_blank" rel="noopener noreferrer">
                            Try Now
                          </a>
                        </Button>
                      </div>
                    ) : (
                      <Button
                        variant="ghost"
                        className="px-0 text-sm font-semibold text-[#0093E9] hover:bg-[#0093E9]/10 hover:text-[#0093E9]"
                        asChild
                      >
                        <a href={tool.link} target="_blank" rel="noopener noreferrer">
                          Open Tool <ExternalLink className="h-4 w-4 ml-2" />
                        </a>
                      </Button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        <div className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Button asChild size="lg" className="px-8 py-6 text-lg bg-[#020617] text-white font-semibold hover:bg-[#020617]/90">
            <a href={remoteUrl} target="_blank" rel="noopener noreferrer">
              Explore all tools on DesiFirms
              <ExternalLink className="h-5 w-5 ml-2" />
            </a>
          </Button>
          <Button variant="outline" size="lg" className="px-8 py-6 text-lg border-black text-black hover:bg-black hover:text-white">
            <a href="mailto:info@codeteki.au">Request a white-label build</a>
          </Button>
        </div>

        {showEmbed && null}
      </div>
    </section>
  );
}
