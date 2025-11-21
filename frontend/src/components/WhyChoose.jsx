import { useMemo } from "react";
import { useHomePage } from "../hooks/useHomePage";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import {
  DollarSign,
  Plug,
  Handshake,
  MapPin,
  Shield,
  Sparkles,
} from "lucide-react";

const iconMap = {
  dollarsign: DollarSign,
  plug: Plug,
  handshake: Handshake,
  mappin: MapPin,
  shield: Shield,
  sparkles: Sparkles,
};

const accentStyles = {
  blue: {
    iconBg: "bg-blue-50",
    iconRing: "ring-blue-200/80",
    iconText: "text-blue-600",
    shadow: "shadow-[0_25px_60px_rgba(59,130,246,0.15)]",
  },
  green: {
    iconBg: "bg-emerald-50",
    iconRing: "ring-emerald-200/80",
    iconText: "text-emerald-600",
    shadow: "shadow-[0_25px_60px_rgba(16,185,129,0.15)]",
  },
  yellow: {
    iconBg: "bg-amber-50",
    iconRing: "ring-amber-200/80",
    iconText: "text-amber-500",
    shadow: "shadow-[0_25px_60px_rgba(249,203,7,0.2)]",
  },
  purple: {
    iconBg: "bg-violet-50",
    iconRing: "ring-violet-200/80",
    iconText: "text-violet-600",
    shadow: "shadow-[0_25px_60px_rgba(139,92,246,0.18)]",
  },
};

const fallbackSection = {
  badge: "Trusted AI Delivery",
  title: "Why Choose Codeteki",
  description: "Experience enterprise-level AI solutions tailored for businesses of all sizes.",
  reasons: [
    {
      title: "Enterprise AI at SMB Prices",
      description: "Access cutting-edge automation without the enterprise-level investment.",
      icon: "DollarSign",
      color: "blue",
    },
    {
      title: "Seamless Integration",
      description: "Solutions that plug into your systems without disruption.",
      icon: "Plug",
      color: "green",
    },
    {
      title: "Human-AI Collaboration",
      description: "Balance intelligent automation with expert oversight.",
      icon: "Handshake",
      color: "yellow",
    },
    {
      title: "Melbourne-based Support",
      description: "Local specialists ready to guide delivery and adoption.",
      icon: "MapPin",
      color: "purple",
    },
  ],
};

export default function WhyChoose() {
  const { data, isLoading } = useHomePage();

  const section = useMemo(() => {
    return (
      data?.data?.whyChoose ||
      data?.whyChoose ||
      fallbackSection
    );
  }, [data]);

  const reasons = section.reasons?.length ? section.reasons : fallbackSection.reasons;

  // Don't render if no data from backend
  if (!section || !reasons?.length) {
    return null;
  }


  return (
    <section className="relative py-24">
      <div className="absolute inset-0 bg-[#f4f6fb]" aria-hidden="true" />
      <div className="relative container mx-auto px-4">
        <div className="max-w-4xl mx-auto text-center mb-16">
          <Badge className="codeteki-pill mb-6 block w-fit mx-auto text-sm">
            {section.badge || fallbackSection.badge}
          </Badge>
          <h2 className="text-4xl md:text-5xl font-bold text-black mb-4">{section.title || fallbackSection.title}</h2>
          <p className="text-lg text-[var(--codeteki-gray)]">
            {section.description || fallbackSection.description}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-10 max-w-5xl mx-auto">
          {reasons.map((reason, index) => {
            const IconComponent = iconMap[(reason.icon || "").toLowerCase()] || Sparkles;
            const accent = accentStyles[reason.color] || accentStyles.blue;

            return (
              <Card
                key={`${reason.title}-${index}`}
                className={`relative overflow-hidden rounded-3xl border border-black/5 bg-white shadow-[0_20px_45px_rgba(15,23,42,0.08)] transition-all duration-500 hover:-translate-y-1.5 hover:shadow-[0_35px_70px_rgba(15,23,42,0.12)] ${accent.shadow}`}
              >
                <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-white/60 via-white to-transparent pointer-events-none" />
                <CardHeader className="relative p-8 pb-0">
                  <span
                    className={`mb-6 inline-flex h-16 w-16 items-center justify-center rounded-full ring-8 ring-white ${accent.iconBg} ${accent.iconRing} shadow-lg`}
                  >
                    <IconComponent className={`h-6 w-6 ${accent.iconText}`} />
                  </span>
                  <CardTitle className="text-2xl font-bold text-black">
                    {reason.title}
                  </CardTitle>
                </CardHeader>
                <CardContent className="relative p-8 pt-4">
                  <CardDescription className="text-base text-[var(--codeteki-gray)] leading-relaxed">
                    {reason.description}
                  </CardDescription>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
}
