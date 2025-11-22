import { TrendingUp, Clock, DollarSign, Zap } from "lucide-react";

const stats = [
  {
    icon: TrendingUp,
    value: "10x",
    label: "Customer Inquiries Handled",
    color: "text-blue-600",
    bgColor: "bg-blue-100",
  },
  {
    icon: Clock,
    value: "24/7",
    label: "Operation Capability",
    color: "text-green-600",
    bgColor: "bg-green-100",
  },
  {
    icon: DollarSign,
    value: "60%",
    label: "Cost Reduction",
    color: "text-yellow-600",
    bgColor: "bg-yellow-100",
  },
  {
    icon: Zap,
    value: "<2s",
    label: "Response Time",
    color: "text-purple-600",
    bgColor: "bg-purple-100",
  },
];

export default function BusinessImpact() {
  return (
    <section className="py-16 bg-white">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-black mb-4">REAL BUSINESS IMPACT</h2>
          <p className="text-lg text-[var(--codeteki-gray)] max-w-3xl mx-auto">
            Our AI-powered solutions deliver concrete business outcomes that transform how your business operates.
          </p>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, index) => {
            const IconComponent = stat.icon;
            return (
              <div
                key={index}
                className={`group text-center cursor-pointer transform hover:scale-110 transition-all duration-500 hover:-translate-y-2 ${
                  index % 2 === 0 ? "animate-scale-in" : "animate-fade-in-up"
                }`}
                style={{ animationDelay: `${index * 0.2}s` }}
              >
                <div
                  className={`relative ${stat.bgColor} w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 transform group-hover:scale-125 group-hover:rotate-12 transition-all duration-300 shadow-lg group-hover:shadow-2xl`}
                >
                  <IconComponent className={`text-2xl ${stat.color} group-hover:animate-bounce`} size={24} />
                  <div className="absolute inset-0 bg-gradient-to-r from-[#f9cb07]/20 to-transparent rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

                  {/* Floating particles */}
                  <div className="absolute -top-2 -right-2 w-3 h-3 bg-[#f9cb07]/30 rounded-full opacity-0 group-hover:opacity-100 animate-ping" />
                  <div className="absolute -bottom-1 -left-1 w-2 h-2 bg-blue-500/30 rounded-full opacity-0 group-hover:opacity-100 animate-pulse" />
                </div>

                <div className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-black to-[#f9cb07] group-hover:from-[#f9cb07] group-hover:to-[#ff6b35] mb-2 transition-all duration-300 group-hover:animate-pulse">
                  {stat.value}
                </div>
                <div className="text-gray-600 group-hover:text-gray-800 transition-colors duration-300 font-medium">
                  {stat.label}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
