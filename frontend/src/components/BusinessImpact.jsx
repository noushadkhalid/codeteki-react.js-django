import { TrendingUp, Clock, DollarSign, Zap } from "lucide-react";
import { useHomePage } from "../hooks/useHomePage";

// Icon mapping for backend icon names
const iconMap = {
  TrendingUp,
  Clock,
  DollarSign,
  Zap,
};

export default function BusinessImpact() {
  const { data, isLoading } = useHomePage();
  const section = data?.data?.impact || data?.impact;

  // Don't render if no data from backend
  if (!section || !section.metrics?.length) {
    return null;
  }

  return (
    <section className="py-16 bg-white">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-black mb-4">{section.title}</h2>
          <p className="text-lg text-[var(--codeteki-gray)] max-w-3xl mx-auto">
            {section.description}
          </p>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
          {section.metrics.map((metric, index) => {
            const IconComponent = iconMap[metric.icon] || TrendingUp;
            const bgColor = metric.theme?.bg || "bg-blue-100";
            const textColor = metric.theme?.text || "text-blue-600";

            return (
              <div
                key={metric.label}
                className={`group text-center cursor-pointer transform hover:scale-110 transition-all duration-500 hover:-translate-y-2 ${
                  index % 2 === 0 ? 'animate-scale-in' : 'animate-fade-in-up'
                }`}
                style={{ animationDelay: `${index * 0.2}s` }}
              >
                <div className={`relative ${bgColor} w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 transform group-hover:scale-125 group-hover:rotate-12 transition-all duration-300 shadow-lg group-hover:shadow-2xl`}>
                  <IconComponent className={`text-2xl ${textColor} group-hover:animate-bounce`} size={24} />
                  <div className="absolute inset-0 bg-gradient-to-r from-[#f9cb07]/20 to-transparent rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <div className="absolute -top-2 -right-2 w-3 h-3 bg-[#f9cb07]/30 rounded-full opacity-0 group-hover:opacity-100 animate-ping"></div>
                  <div className="absolute -bottom-1 -left-1 w-2 h-2 bg-blue-500/30 rounded-full opacity-0 group-hover:opacity-100 animate-pulse"></div>
                </div>

                <div className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-black to-[#f9cb07] group-hover:from-[#f9cb07] group-hover:to-[#ff6b35] mb-2 transition-all duration-300 group-hover:animate-pulse">
                  {metric.value}
                </div>
                <div className="text-gray-600 group-hover:text-gray-800 transition-colors duration-300 font-medium">
                  {metric.label}
                </div>
              </div>
            );
          })}
        </div>

        {section.cta?.label && (
          <div className="text-center mt-12">
            <a
              href={section.cta.href}
              className="inline-block px-8 py-3 bg-[#f9cb07] text-black font-semibold rounded-lg hover:bg-[#ff6b35] hover:text-white transition-all duration-300"
            >
              {section.cta.label}
            </a>
          </div>
        )}
      </div>
    </section>
  );
}
