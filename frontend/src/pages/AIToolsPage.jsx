import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import AIToolsShowcase, { aiToolsFallbackSection } from "../components/AITools";
import Contact from "../components/Contact";
import SEOHead from "../components/SEOHead";
import { ExternalLink, Layers, ShieldCheck, Sparkles } from "lucide-react";

const getToolCounts = (tools = []) =>
  tools.reduce(
    (acc, tool) => {
      acc.total += 1;
      if (tool.comingSoon || tool.is_coming_soon) {
        acc.comingSoon += 1;
        return acc;
      }
      const status = (tool.status || "free").toString().toLowerCase();
      if (status === "free") acc.free += 1;
      if (status === "credits") acc.credits += 1;
      if (status === "premium") acc.premium += 1;
      return acc;
    },
    { total: 0, free: 0, credits: 0, premium: 0, comingSoon: 0 }
  );

export default function AIToolsPage() {
  const { data } = useQuery({
    queryKey: ["/api/ai-tools/"],
  });
  const aiToolsSection = data?.data?.aiTools || data?.aiTools || aiToolsFallbackSection;
  const toolCounts = useMemo(() => getToolCounts(aiToolsSection.tools || []), [aiToolsSection.tools]);

  return (
    <div className="min-h-screen bg-white">
      <SEOHead
        title="AI Tools | Codeteki - Complete AI Tools Collection"
        description="Discover AI-powered tools Codeteki already shipped for DesiFirms. Explore business, health, immigration, and finance copilots that are live in production."
        keywords="AI tools, health calculator, business generator, Australia, desifirms"
      />

      <section className="relative bg-gradient-to-br from-gray-50 to-white py-20 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(249,203,7,0.2),transparent_60%)]" aria-hidden="true" />
        <div className="container mx-auto px-4">
          <div className="relative max-w-5xl mx-auto text-center">
            <span className="codeteki-pill mb-6">
              {aiToolsSection.badge}
            </span>
            <h1 className="text-5xl font-bold text-black mb-6 leading-tight">
              {aiToolsSection.title}
            </h1>
            <p
              className="text-xl text-gray-600 mb-8 leading-relaxed max-w-4xl mx-auto"
              dangerouslySetInnerHTML={{ __html: aiToolsSection.description || "" }}
            />
            <div className="flex flex-wrap gap-2 sm:gap-4 justify-center max-w-4xl mx-auto">
              <Badge className="bg-green-100 text-green-800 px-3 py-2 text-sm sm:text-base">
                Free Tools ({toolCounts.free}) • Ready Now
              </Badge>
              <Badge className="bg-blue-100 text-blue-800 px-3 py-2 text-sm sm:text-base">
                Credit Tools ({toolCounts.credits}) • Live
              </Badge>
              <Badge className="bg-purple-100 text-purple-800 px-3 py-2 text-sm sm:text-base">
                Premium Copilots ({toolCounts.premium})
              </Badge>
              <Badge className="bg-gray-100 text-gray-800 px-3 py-2 text-sm sm:text-base">
                New Drops Every Month
              </Badge>
            </div>
            <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button
                asChild
                size="lg"
                className="px-8 py-6 text-lg bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] text-black font-semibold"
              >
                <a href="https://www.desifirms.com.au/ai-tools" target="_blank" rel="noopener noreferrer">
                  Open DesiFirms AI Tools
                  <ExternalLink className="h-5 w-5 ml-2" />
                </a>
              </Button>
              <Button variant="outline" size="lg" className="px-8 py-6 text-lg">
                <a href="mailto:info@codeteki.au">Integrate these into my business</a>
              </Button>
            </div>
          </div>
        </div>
      </section>

      <AIToolsShowcase showEmbed />

      <section className="relative py-24 bg-[#020617] overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute -top-36 right-0 w-[520px] h-[520px] bg-[#f9cb07]/15 blur-[160px]" />
          <div className="absolute bottom-0 left-0 w-[680px] h-[680px] bg-[#312e81]/40 blur-[200px]" />
          <div className="absolute inset-0 opacity-30 bg-[radial-gradient(circle,_rgba(255,255,255,0.12)_1px,_transparent_1px)] [background-size:40px_40px]" />
        </div>
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute right-12 top-12 w-32 h-32 border border-white/10 rounded-full animate-[spin_18s_linear_infinite]" />
          <div className="absolute left-20 bottom-10 w-20 h-20 border border-white/10 rounded-full animate-[spin_22s_linear_reverse_infinite]" />
        </div>
        <div className="relative container mx-auto px-4">
          <div className="max-w-6xl mx-auto grid gap-12 lg:grid-cols-[1.15fr_0.85fr] items-center">
            <div className="text-white space-y-6">
              <span className="codeteki-pill mb-2">Need white-label delivery?</span>
              <h2 className="text-4xl lg:text-5xl font-bold leading-tight">
                White-label AI tools & web apps that launch in weeks—not quarters.
              </h2>
              <p className="text-lg text-white/75">
                Everything you saw above already powers DesiFirms.com.au. We can rebrand, extend, or embed the entire toolkit
                into your own experience while we handle hosting, analytics, credit logic, compliance, and support.
              </p>
              <div className="grid sm:grid-cols-2 gap-4">
                {[
                  { icon: Sparkles, title: "Custom skin & flows", caption: "Match your brand, routes, tone, and UX." },
                  { icon: Layers, title: "MCP & API ready", caption: "Secure Claude + LLM access to your data." },
                ].map((item) => (
                  <div
                    key={item.title}
                    className="flex items-start gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 shadow-[0_20px_45px_rgba(15,23,42,0.35)]"
                  >
                    <item.icon className="h-5 w-5 text-[#f9cb07]" />
                    <div>
                      <p className="text-base font-semibold">{item.title}</p>
                      <p className="text-sm text-white/70">{item.caption}</p>
                    </div>
                  </div>
                ))}
              </div>
              <div className="flex flex-col sm:flex-row items-center gap-4 pt-4">
                <Button
                  asChild
                  className="px-8 py-5 bg-white text-[#020617] font-semibold hover:bg-slate-100 shadow-[0_20px_40px_rgba(15,23,42,0.45)]"
                >
                  <a href="mailto:info@codeteki.au">Request a white-label build</a>
                </Button>
                <Button
                  asChild
                  variant="outline"
                  className="px-8 py-5 border-white/60 text-white hover:bg-white/10"
                >
                  <a href="/contact">Book a build workshop</a>
                </Button>
              </div>
              <p className="uppercase tracking-[0.3em] text-xs text-white/60 pt-2">
                Built by Codeteki • Hosted on DesiFirms
              </p>
            </div>
            <div className="relative">
              <div className="absolute -top-10 -right-6 w-32 h-32 bg-[#f9cb07]/20 blur-3xl rounded-full" />
              <div className="relative rounded-[32px] border border-white/10 bg-white/5 p-8 backdrop-blur-xl shadow-[0_35px_80px_rgba(15,23,42,0.45)]">
                <div className="flex items-center justify-between gap-6 pb-8 border-b border-white/10">
                  <div>
                    <p className="text-sm uppercase tracking-[0.2em] text-white/60">Delivery Program</p>
                    <p className="text-2xl font-bold text-white mt-2">Codeteki Fulfilment Pod</p>
                  </div>
                  <div className="inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-2 text-sm font-semibold">
                    <ShieldCheck className="h-4 w-4 text-[#f9cb07]" />
                    Managed
                  </div>
                </div>
                <div className="space-y-4 pt-8">
                  {[
                    "Dedicated Melbourne pod (PM + designer + engineers)",
                    "Hosting, observability, and analytics handled for you",
                    "Credit/paywall logic, billing, and access tiers included",
                    "DesiFirms-grade UX (shadcn + custom animations)"
                  ].map((item) => (
                    <div key={item} className="flex items-start gap-3">
                      <span className="mt-1 h-2 w-2 rounded-full bg-[#f9cb07]" />
                      <p className="text-sm text-white/75 leading-relaxed">{item}</p>
                    </div>
                  ))}
                </div>
                <div className="mt-10 grid grid-cols-2 gap-4">
                  <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-center">
                    <p className="text-3xl font-bold text-white">4-6w</p>
                    <p className="text-xs uppercase tracking-wide text-white/60 mt-1">Avg. launch timeline</p>
                  </div>
                  <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-center">
                    <p className="text-3xl font-bold text-white">20+</p>
                    <p className="text-xs uppercase tracking-wide text-white/60 mt-1">Live tools shipped</p>
                  </div>
                </div>
                <div className="mt-8 rounded-2xl border border-[#f9cb07]/40 bg-[#f9cb07]/10 p-5 text-sm text-[#fee794]">
                  Need the DesiFirms suite inside your product? We’ll deploy a mirrored environment with your branding, domain,
                  and compliance requirements (PCI, SOC2-ready architecture).
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <Contact />
    </div>
  );
}
