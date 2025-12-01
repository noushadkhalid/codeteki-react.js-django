import { lazy, Suspense } from "react";
import Hero from "../components/Hero";
import BusinessImpact from "../components/BusinessImpact";
import Services from "../components/Services";
import SEOHead from "../components/SEOHead";

// Lazy load below-the-fold components for better initial load
const AITools = lazy(() => import("../components/AITools"));
const ROICalculator = lazy(() => import("../components/ROICalculator"));
const WhyChoose = lazy(() => import("../components/WhyChoose"));
const Contact = lazy(() => import("../components/Contact"));

// Minimal loading placeholder for lazy components
const SectionLoader = () => (
  <div className="min-h-[200px] flex items-center justify-center">
    <div className="w-8 h-8 border-3 border-gray-200 border-t-[#f9cb07] rounded-full animate-spin"></div>
  </div>
);

export default function Home() {
  return (
    <div className="bg-codeteki-bg">
      <SEOHead
        title="Codeteki - AI Business Solutions Melbourne | Custom Tool Development & Business Automation"
        description="Transform your business with AI-powered chatbots, custom tool development, business automation, and MCP integration. Melbourne-based AI development team specializing in everyday task automation."
        keywords="AI business solutions Melbourne, chatbot development Australia, custom tool development, business automation, MCP integration, AI tools, repetitive task automation, Melbourne AI development"
        page="home"
      />
      <Hero />
      <BusinessImpact />
      <Services featuredOnly />
      <Suspense fallback={<SectionLoader />}>
        <AITools hideComingSoon />
      </Suspense>
      <Suspense fallback={<SectionLoader />}>
        <ROICalculator />
      </Suspense>
      <Suspense fallback={<SectionLoader />}>
        <WhyChoose />
      </Suspense>
      <Suspense fallback={<SectionLoader />}>
        <Contact />
      </Suspense>
    </div>
  );
}
