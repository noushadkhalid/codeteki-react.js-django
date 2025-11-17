import Hero from "../components/Hero";
import BusinessImpact from "../components/BusinessImpact";
import Services from "../components/Services";
import SEOHead from "../components/SEOHead";
import AITools from "../components/AITools";
import ROICalculator from "../components/ROICalculator";
import WhyChoose from "../components/WhyChoose";
import Contact from "../components/Contact";

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
      <Services />
      <AITools />
      <ROICalculator />
      <WhyChoose />
      <Contact />
    </div>
  );
}
