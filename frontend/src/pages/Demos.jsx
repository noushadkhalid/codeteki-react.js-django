import { useEffect, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import {
  Sparkles,
  Bot,
  Building2,
  Utensils,
  Car,
  Heart,
  GraduationCap,
  ShoppingBag,
  Wrench,
  ExternalLink,
} from "lucide-react";
import { Card } from "../components/ui/card";
import { useLocation } from "wouter";
import SEOHead from "../components/SEOHead";

const iconMap = {
  Sparkles,
  Bot,
  Building2,
  Utensils,
  Car,
  Heart,
  GraduationCap,
  ShoppingBag,
  Wrench,
};

const statusTokens = {
  "Live Demo": { badge: "bg-green-100 text-green-800", button: "Try Live Demo" },
  "Coming Soon": { badge: "bg-blue-50 text-blue-700", button: "Coming Soon" },
  "In Development": { badge: "bg-orange-50 text-orange-700", button: "In Development" },
  Planning: { badge: "bg-gray-100 text-gray-600", button: "Planning" },
};

const fallbackDemos = [];

export default function Demos() {
  const [, setLocation] = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  const { data, isLoading } = useQuery({
    queryKey: ["/api/demos/"],
  });

  const demoSites = useMemo(() => {
    const payload = data?.data?.demos || data?.demos;
    return payload && payload.length ? payload : fallbackDemos;
  }, [data]);

  const liveCount = demoSites.filter((demo) => demo.status === "Live Demo").length;
  const comingSoonCount = demoSites.length - liveCount;

  const renderFeatures = (features = []) => {
    if (!Array.isArray(features) || !features.length) return null;
    const preview = features.slice(0, 3);
    return (
      <ul className="space-y-2 mt-4 text-sm text-gray-600">
        {preview.map((feature, idx) => (
          <li key={idx} className="flex items-start gap-2">
            <span className="mt-1 block h-1.5 w-1.5 rounded-full bg-[#f9cb07]" />
            <span>{feature}</span>
          </li>
        ))}
        {features.length > 3 && (
          <li className="text-xs text-gray-500 italic">+{features.length - 3} more features</li>
        )}
      </ul>
    );
  };

  const renderCard = (demo) => {
    const IconComponent = iconMap[demo.icon] || Building2;
    const status = statusTokens[demo.status] || statusTokens.Planning;
    const features = Array.isArray(demo.features) ? demo.features : [];

    return (
      <div
        key={demo.slug || demo.id || demo.title}
        className="flex h-full flex-col rounded-2xl border border-[#eef0f3] bg-white p-6 shadow-[0_10px_35px_rgba(15,23,42,0.06)]"
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-2xl bg-[#f9cb07]/15 text-[#f9cb07] flex items-center justify-center">
              <IconComponent className="h-6 w-6" />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-gray-500">{demo.industry}</p>
              <h3 className="text-xl font-bold text-[#0f172a]">{demo.title}</h3>
            </div>
          </div>
          <Badge className={`${status.badge} px-3 py-1 text-[11px] font-semibold`}>{demo.status}</Badge>
        </div>

        <p className="mt-4 text-sm text-gray-600 leading-relaxed flex-1">{demo.description}</p>

        {renderFeatures(features)}

        <div className="mt-6">
          {demo.status === "Live Demo" && demo.demoUrl ? (
            <Button
              className="w-full justify-between bg-[#f9cb07] text-black font-semibold hover:bg-[#ffcd3c]"
              onClick={() => window.open(demo.demoUrl, "_blank")}
            >
              Try the demo
              <ExternalLink className="h-4 w-4" />
            </Button>
          ) : (
            <Button variant="outline" className="w-full border-dashed text-gray-500" disabled>
              {status.button}
            </Button>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-[#f8fafc]">
      <SEOHead
        title="AI Demo Sites | Codeteki - Live Industry Examples"
        description="Explore live AI chatbot and voice assistant demos across cleaning, hospitality, automotive, health, and beyond."
        keywords="AI demos, chatbot demo, voice assistant demo, Codeteki demos, industry AI showcase"
      />

      <section className="bg-white py-20">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center space-y-6">
            <span className="codeteki-pill text-base">🚀 Industry Demo Sites</span>
            <h1 className="text-4xl sm:text-5xl font-bold text-[#0f172a] leading-tight">See AI in Action Across Industries</h1>
            <p className="text-lg sm:text-xl text-gray-600">
              Every showcase below is powered by the same back-office we provide to clients. Explore how Codeteki copilots
              adapt to different workflows, compliance requirements, and user experiences.
            </p>
            <div className="flex flex-wrap justify-center gap-3 text-sm font-semibold text-gray-600">
              <span className="inline-flex items-center gap-2 rounded-full bg-gray-100 px-4 py-2">
                {demoSites.length} total demos
              </span>
              <span className="inline-flex items-center gap-2 rounded-full bg-green-100 text-green-700 px-4 py-2">
                {liveCount} live now
              </span>
              <span className="inline-flex items-center gap-2 rounded-full bg-yellow-100 text-yellow-800 px-4 py-2">
                {comingSoonCount} coming soon
              </span>
            </div>
          </div>
        </div>
      </section>

      <section className="py-16">
        <div className="container mx-auto px-4">
          {isLoading ? (
            <div className="text-center py-16">
              <div className="mx-auto h-16 w-16 animate-spin rounded-full border-b-2 border-[#f9cb07]" />
              <p className="mt-4 text-gray-600">Loading demo sites...</p>
            </div>
          ) : demoSites.length === 0 ? (
            <div className="text-center py-16">
              <h3 className="text-2xl font-bold text-gray-700 mb-3">No Demo Sites Published Yet</h3>
              <p className="text-gray-500">Once demos are configured in the admin, they will appear here.</p>
              <Button className="mt-6 bg-[#f9cb07] text-black" onClick={() => setLocation("/contact")}>
                Book a custom demo
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">{demoSites.map(renderCard)}</div>
          )}
        </div>
      </section>

      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <Card className="max-w-4xl mx-auto border border-[#f1f5f9] shadow-none p-10 text-center space-y-4">
            <Badge className="mx-auto bg-blue-50 text-blue-700 font-semibold px-4 py-1.5">
              Custom builds available
            </Badge>
            <h3 className="text-3xl font-bold text-[#0f172a]">Need a demo in your industry?</h3>
            <p className="text-gray-600">
              We design white-label demos tailored to your workflows so stakeholders can see Codeteki in action before launch.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                size="lg"
                className="bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] text-black font-semibold px-8 py-4"
                onClick={() => setLocation("/contact")}
              >
                Request a custom demo
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="border-2 border-[#f9cb07] text-[#f9cb07] hover:bg-[#f9cb07]/10 font-semibold px-8 py-4"
                onClick={() => setLocation("/ai-tools")}
              >
                Explore AI tools
              </Button>
            </div>
          </Card>
        </div>
      </section>
    </div>
  );
}
