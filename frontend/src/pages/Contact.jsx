import { useEffect } from "react";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Sparkles, ShieldCheck, Globe } from "lucide-react";
import SEOHead from "../components/SEOHead";
import ContactSection from "../components/Contact";
import { useSiteSettings } from "../hooks/useSiteSettings";

export default function ContactPage() {
  const { settings } = useSiteSettings();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  const heroHeading = settings?.cta?.heading || settings?.siteTagline || "Let's Connect";
  const heroDescription =
    settings?.cta?.description ||
    settings?.siteDescription ||
    "Multiple ways to reach our Melbourne-based team. We're here to help transform your business with AI.";

  const highlightStats = [
    {
      label: "Average response time",
      value: "< 24 hrs",
      helper: "Based on care plan",
      icon: Sparkles,
    },
    {
      label: "Projects delivered",
      value: "70+",
      helper: "Web, AI, automation",
      icon: ShieldCheck,
    },
    {
      label: "Live AI copilots",
      value: "20+",
      helper: "Hosted for AU businesses",
      icon: Globe,
    },
  ];

  return (
    <div className="min-h-screen bg-white">
      <SEOHead
        title="Contact Codeteki | AI Automation Studio"
        description="Contact Codeteki to discuss AI automation, custom copilots, and white-label projects. Melbourne team responds within 24 hours."
        keywords="Contact Codeteki, AI automation contact, Melbourne AI studio"
      />

      <section className="bg-[#111827] py-24 relative overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[1200px] bg-[#1f2937] rounded-full blur-[220px] opacity-60" />
          <div className="absolute bottom-0.right-10 w-[500px] h-[500px] bg-[#f9cb07]/15 rounded-full blur-[150px]" />
        </div>
        <div className="relative container mx-auto px-4 text-center max-w-3xl">
          <span className="codeteki-pill mb-6">We respond within 24 hours</span>
          <h1 className="text-4xl lg:text-5xl font-bold text-white mb-4">{heroHeading}</h1>
          <p className="text-lg text-white/80">{heroDescription}</p>
          <div className="mt-10 grid gap-4 md:grid-cols-3">
            {highlightStats.map((stat) => (
              <div key={stat.label} className="rounded-2xl border border-white/10 bg-white/5 p-6 text-left flex items-start gap-4">
                <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#f9cb07]/15 text-[#f9cb07]">
                  <stat.icon className="h-5 w-5" />
                </span>
                <div>
                  <p className="text-2xl font-bold text-white">{stat.value}</p>
                  <p className="text-sm text-white/80">{stat.label}</p>
                  <p className="text-xs text-white/60">{stat.helper}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-6 flex flex-col sm:flex-row justify-center gap-3">
            <Button
              size="lg"
              className="bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] text-black font-semibold px-8 py-4"
              asChild
            >
              <a href="mailto:info@codeteki.au">Email the studio</a>
            </Button>
            <Button variant="outline" size="lg" className="border-white/40 text-white hover:bg-white/10" asChild>
              <a href="tel:+61469807872">Call Melbourne pod</a>
            </Button>
          </div>
        </div>
      </section>

      <ContactSection />
    </div>
  );
}
