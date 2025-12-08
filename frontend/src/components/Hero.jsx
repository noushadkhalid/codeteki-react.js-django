import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "../components/ui/button";
import { Skeleton } from "../components/ui/skeleton";
import { Phone, Play, ArrowRight, Calculator } from "lucide-react";

// Optimized WebP images served via Django static with proper cache headers
const heroImageDesktop = "/static/images/hero-desktop.webp";
const heroImageMobile = "/static/images/hero-mobile.webp";

const fallbackHero = {
  badge: "AI-Powered Business Solutions",
  badgeEmoji: "🚀",
  title: "Transform Your Business with",
  highlighted: "AI-Powered",
  highlightGradientFrom: "#f9cb07",
  highlightGradientTo: "#ff6b35",
  description:
    "At Codeteki, we revolutionize business operations through advanced AI technology and human expertise. Based in Melbourne, Australia, we combine innovative design, powerful automation, and intelligent solutions.",
  primaryCta: { label: "Talk to Us Today", href: "#contact" },
  secondaryCta: { label: "View Our Services", href: "#services" },
  image: heroImageDesktop,
};

export default function Hero() {
  const { data, isLoading } = useQuery({ queryKey: ["/api/hero/"] });
  const hero = useMemo(() => {
    const payload = data?.data?.hero;
    if (!payload) return fallbackHero;
    return {
      badge: payload.badge || fallbackHero.badge,
      badgeEmoji: payload.badgeEmoji || payload.badge_emoji || "🚀",
      title: payload.title || fallbackHero.title,
      highlighted: payload.highlighted || payload.highlighted_text || fallbackHero.highlighted,
      highlightGradientFrom:
        payload.highlightGradientFrom || payload.highlight_gradient_from || fallbackHero.highlightGradientFrom,
      highlightGradientTo:
        payload.highlightGradientTo || payload.highlight_gradient_to || fallbackHero.highlightGradientTo,
      description: payload.description || fallbackHero.description,
      primaryCta: payload.primaryCta || fallbackHero.primaryCta,
      secondaryCta: payload.secondaryCta || fallbackHero.secondaryCta,
      image: payload.media || payload.image || payload.image_url || heroImageDesktop,
      imageMobile: heroImageMobile,
    };
  }, [data]);

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  const ImageBlock = () => (
    <div className="lg:w-1/2 relative animate-float">
      <div className="absolute -inset-4 bg-gradient-to-r from-[#f9cb07]/30 via-blue-500/20 to-purple-500/20 rounded-2xl blur-xl animate-pulse-slow" />
      <div className="absolute inset-0 bg-gradient-to-br from-[#f9cb07]/10 via-transparent to-blue-500/10 rounded-2xl animate-gradient-shift" />
      <div className="relative group cursor-pointer">
        {isLoading ? (
          <Skeleton className="h-[360px] w-full rounded-2xl bg-white/20" />
        ) : (
          <picture>
            {/* Mobile-optimized image for screens < 768px */}
            <source
              media="(max-width: 767px)"
              srcSet={hero.imageMobile || heroImageMobile}
              type="image/webp"
            />
            {/* Desktop image for larger screens */}
            <source
              media="(min-width: 768px)"
              srcSet={hero.image || heroImageDesktop}
              type="image/webp"
            />
            <img
              src={hero.image || heroImageDesktop}
              alt="AI-Powered Business Workspace"
              className="rounded-2xl shadow-2xl w-full h-auto transition-all duration-700 group-hover:scale-105 group-hover:shadow-3xl transform group-hover:rotate-1"
              loading="eager"
              decoding="async"
              fetchpriority="high"
              width="600"
              height="339"
            />
          </picture>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        <div className="absolute top-4 left-4 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-sm font-medium text-gray-800 opacity-0 group-hover:opacity-100 transition-all duration-500 transform translate-y-2 group-hover:translate-y-0">
          AI-Powered Future 🤖
        </div>
      </div>
      <div className="absolute top-10 -right-4 w-20 h-20 bg-gradient-to-r from-[#f9cb07]/20 to-blue-500/20 rounded-full animate-float-delayed blur-sm" />
      <div className="absolute bottom-10 -left-4 w-16 h-16 bg-gradient-to-r from-purple-500/20 to-[#f9cb07]/20 rounded-full animate-float-slow blur-sm" />
      <div className="absolute top-1/2 -right-8 w-12 h-12 bg-gradient-to-r from-blue-500/30 to-purple-500/30 rounded-full animate-bounce-slow blur-sm" />
    </div>
  );

  return (
    <section id="home" className="bg-gradient-to-br from-white via-gray-50 to-blue-50 py-20 overflow-hidden">
      <div className="container mx-auto px-4">
        <div className="flex flex-col lg:flex-row items-center gap-12">
          <div className="lg:w-1/2 animate-fade-in-left">
            <div className="inline-block mb-4">
              {isLoading ? (
                <Skeleton className="h-10 w-64 rounded-full bg-white/40" />
              ) : (
                <span className="px-4 py-2 bg-[#f9cb07] text-black rounded-full text-sm font-semibold animate-pulse">
                  {hero.badgeEmoji} {hero.badge}
                </span>
              )}
            </div>
            {isLoading ? (
              <div className="space-y-4 mb-6">
                <Skeleton className="h-10 w-full bg-white/40" />
                <Skeleton className="h-10 w-3/4 bg-white/40" />
              </div>
            ) : (
              <h1 className="text-5xl lg:text-6xl font-bold text-black leading-tight mb-6 animate-gradient-text">
                {hero.title}{" "}
                <span
                  className="text-transparent bg-clip-text animate-shimmer"
                  style={{
                    backgroundImage: `linear-gradient(90deg, ${hero.highlightGradientFrom}, ${hero.highlightGradientTo})`,
                  }}
                >
                  {hero.highlighted}
                </span>{" "}
                Solutions
              </h1>
            )}
            <p className="text-xl text-gray-600 mb-8 leading-relaxed animate-fade-in-delayed">
              {isLoading ? <Skeleton className="h-20 w-full bg-white/40" /> : hero.description}
            </p>
            <div className="flex flex-col sm:flex-row flex-wrap gap-4 animate-fade-in-delayed-2">
              <Button
                className="group bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] hover:from-[#e6b800] hover:to-[#f9cb07] text-black px-8 py-4 rounded-lg font-semibold text-lg shadow-lg hover:shadow-2xl transition-all duration-500 transform hover:scale-105 hover:rotate-1 btn-animated"
                onClick={() => scrollToSection(hero.primaryCta?.href?.replace("#", "") || "contact")}
              >
                <Phone className="mr-2 h-5 w-5 transition-transform duration-300 group-hover:scale-110" />
                {hero.primaryCta?.label || "Talk to Us Today"}
                <ArrowRight className="ml-2 h-5 w-5 transition-transform duration-300 group-hover:translate-x-1" />
              </Button>
              <Button
                className="group bg-[#f9cb07] text-black hover:bg-[#e6b800] px-8 py-4 rounded-lg font-semibold text-lg shadow-lg hover:shadow-xl transition-all duration-500 transform hover:scale-105"
                onClick={() => scrollToSection("roi-calculator")}
              >
                <Calculator className="mr-2 h-5 w-5 transition-transform duration-300 group-hover:scale-110" />
                Calculate ROI
              </Button>
              <Button
                variant="outline"
                className="group border-2 border-[#f9cb07] text-[#f9cb07] hover:bg-gradient-to-r hover:from-[#f9cb07] hover:to-[#ffcd3c] hover:text-black px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-500 transform hover:scale-105 hover:-rotate-1 backdrop-blur-sm"
                onClick={() => scrollToSection(hero.secondaryCta?.href?.replace("#", "") || "services")}
              >
                <Play className="mr-2 h-5 w-5 transition-transform duration-300 group-hover:scale-110" />
                {hero.secondaryCta?.label || "View Our Services"}
              </Button>
            </div>
          </div>
          <ImageBlock />
        </div>
      </div>
    </section>
  );
}
