import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { apiRequest } from "../lib/queryClient";
import { useToast } from "../hooks/use-toast";
import { Calculator, TrendingUp, Zap, DollarSign, Clock, Users, MessageCircle, Target } from "lucide-react";

const BASE_TOOL_OPTIONS = [
  {
    id: "voice",
    label: "Voice & Chat AI",
    description: "Great for call centres, sales pods, and inbound lead handling.",
    required: ["monthlyCalls", "missedCalls", "callDuration", "hourlyRate", "conversionRate", "orderValue"],
    fields: [
      { key: "monthlyCalls", label: "Monthly calls", placeholder: "e.g., 500", icon: Users },
      { key: "missedCalls", label: "Missed calls", placeholder: "e.g., 120", icon: MessageCircle },
      { key: "callDuration", label: "Call duration (min)", placeholder: "e.g., 6", icon: Clock },
      { key: "hourlyRate", label: "Hourly rate ($)", placeholder: "e.g., 25", icon: DollarSign },
      { key: "conversionRate", label: "Conversion rate (%)", placeholder: "e.g., 25", icon: Target },
      { key: "orderValue", label: "Average order value ($)", placeholder: "e.g., 180", icon: DollarSign },
    ],
  },
  {
    id: "support",
    label: "Support Tickets",
    description: "Deflect repetitive tickets and deliver instant omnichannel replies.",
    required: ["monthlyTickets", "ticketHandleTime", "ticketResolutionCost", "hourlyRate"],
    fields: [
      { key: "monthlyTickets", label: "Monthly tickets", placeholder: "e.g., 800", icon: MessageCircle },
      { key: "ticketHandleTime", label: "Handle time (min)", placeholder: "e.g., 12", icon: Clock },
      { key: "ticketResolutionCost", label: "Resolution cost ($)", placeholder: "e.g., 35", icon: DollarSign },
      { key: "hourlyRate", label: "Team hourly rate ($)", placeholder: "e.g., 28", icon: DollarSign },
    ],
  },
  {
    id: "automation",
    label: "Manual Tasks",
    description: "Automate repetitive back-office workflows across finance and ops.",
    required: ["manualTasksPerDay", "minutesPerTask", "systemsUsed", "hourlyRate"],
    fields: [
      { key: "manualTasksPerDay", label: "Tasks per day", placeholder: "e.g., 60", icon: Zap },
      { key: "minutesPerTask", label: "Minutes per task", placeholder: "e.g., 7", icon: Clock },
      { key: "systemsUsed", label: "Systems touched", placeholder: "e.g., 4", icon: Users },
      { key: "hourlyRate", label: "Team hourly rate ($)", placeholder: "e.g., 32", icon: DollarSign },
    ],
  },
];

const fallbackContent = {
  badge: "Smart Business Calculator",
  title: "Calculate Your Automation ROI",
  highlighted: "in minutes",
  description:
    "<p>Quantify how Codeteki copilots reduce operational costs, recover missed leads, and automate back-office workloads.</p>",
  stats: [
    { label: "Average payback", value: "3.2 months", detail: "Across 2024 deployments" },
    { label: "Manual tasks removed", value: "68%", detail: "Median reduction" },
    { label: "Lead recovery", value: "22%", detail: "From missed calls" },
  ],
};

const benefitsList = [
  { title: "Recover missed leads", metric: "+22%", description: "24/7 coverage prevents abandoned enquiries." },
  { title: "Reduce handling time", metric: "60%", description: "AI does discovery so teams focus on revenue tasks." },
  { title: "Unlock human hours", metric: "120+ hrs/mo", description: "Manual admin, scheduling, and notes eliminated." },
  { title: "Consistent CX", metric: "98%", description: "Brand-safe scripts protect tone and compliance." },
];

export default function ROICalculator() {
  const [formData, setFormData] = useState({
    monthlyCalls: 0,
    missedCalls: 0,
    callDuration: 0,
    hourlyRate: 0,
    conversionRate: 0,
    orderValue: 0,
    monthlyTickets: 0,
    ticketHandleTime: 0,
    ticketResolutionCost: 0,
    manualTasksPerDay: 0,
    minutesPerTask: 0,
    systemsUsed: 1,
  });
  const [selectedTool, setSelectedTool] = useState("voice");
  const [results, setResults] = useState(null);
  const { toast } = useToast();

  const { data: roiData } = useQuery({ queryKey: ["/api/roi-calculator/"] });
  const roiContent = roiData?.data?.calculator || fallbackContent;

  const toolOptions = useMemo(() => {
    const overrideLookup = Object.fromEntries(
      (roiContent.tools || []).map((tool) => [tool.id, tool])
    );
    return BASE_TOOL_OPTIONS.map((option) => {
      const override = overrideLookup[option.id];
      if (!override) return option;
      return {
        ...option,
        label: override.label || option.label,
        description: override.description || option.description,
      };
    });
  }, [roiContent]);

  const activeTool = toolOptions.find((tool) => tool.id === selectedTool) || toolOptions[0];

  const calculateMutation = useMutation({
    mutationFn: async (payload) => {
      const response = await apiRequest("POST", "/api/calculate-roi", payload);
      return await response.json();
    },
    onSuccess: (data) => {
      setResults(data);
      toast({ title: "ROI Calculated", description: "See your potential savings below." });
    },
    onError: () => {
      toast({ title: "Calculation Error", description: "Try again with valid inputs.", variant: "destructive" });
    },
  });

  const handleInputChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: parseFloat(value) || 0,
    }));
  };

  const handleSubmit = () => {
    const missing = activeTool.required.some((field) => (formData[field] || 0) <= 0);
    if (missing) {
      toast({
        title: "Incomplete data",
        description: "Please fill in all required fields for this scenario.",
        variant: "destructive",
      });
      return;
    }
    calculateMutation.mutate(formData);
  };

  const highlightStats = roiContent.stats?.length ? roiContent.stats : fallbackContent.stats;

  return (
    <section id="roi-calculator" className="py-20 bg-gradient-to-br from-gray-50 to-white relative overflow-hidden">
      <div className="absolute inset-0 bg-[linear-gradient(45deg,transparent_35%,rgba(249,203,7,0.05)_50%,transparent_65%)] pointer-events-none" />
      <div className="container mx-auto px-4 relative">
        <div className="text-center mb-20 animate-fade-in-up">
          <Badge className="bg-[#f9cb07]/10 text-[#f9cb07] px-6 py-3 text-lg mb-8 animate-pulse">
            <Calculator className="w-5 h-5 mr-2" />
            {roiContent.badge || fallbackContent.badge}
          </Badge>
          <h2 className="text-5xl font-bold text-black mb-6 leading-tight">
            {roiContent.title || fallbackContent.title}{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#f9cb07] to-[#ff6b35]">
              {roiContent.highlighted || fallbackContent.highlighted}
            </span>
          </h2>
          <p
            className="text-lg text-gray-600 max-w-4xl mx-auto"
            dangerouslySetInnerHTML={{ __html: roiContent.description || fallbackContent.description }}
          />
        </div>

        <div className="space-y-10">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {toolOptions.map((option) => (
              <button
                key={option.id}
                type="button"
                className={`text-left p-5 rounded-2xl border transition-all duration-300 ${
                  selectedTool === option.id
                    ? "border-[#f9cb07] bg-white shadow-xl"
                    : "border-gray-200 bg-white/70 hover:border-[#f9cb07]/60"
                }`}
                onClick={() => setSelectedTool(option.id)}
              >
                <p className="text-xs uppercase tracking-[0.2em] text-gray-500">Scenario</p>
                <h3 className="text-xl font-bold text-black mt-1">{option.label}</h3>
                <p className="text-sm text-gray-600 mt-2">{option.description}</p>
              </button>
            ))}
          </div>

          <Card className="bg-white/95 border-2 border-[#f9cb07]/10 rounded-2xl shadow-xl">
            <CardHeader>
              <CardTitle className="text-2xl font-bold text-black">
                {activeTool.label} Inputs
              </CardTitle>
              <CardDescription>Provide the metrics that match this workflow.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {activeTool.fields.map((field) => (
                  <FormField
                    key={field.key}
                    id={field.key}
                    label={field.label}
                    icon={field.icon}
                    value={formData[field.key]}
                    placeholder={field.placeholder}
                    onChange={(value) => handleInputChange(field.key, value)}
                  />
                ))}
              </div>
              <div className="text-center">
                <Button
                  className="bg-gradient-to-r from-[#f9cb07] to-[#ff6b35] hover:from-[#ff6b35] hover:to-[#f9cb07] text-black px-12 py-4 rounded-2xl font-bold text-lg shadow-2xl"
                  onClick={handleSubmit}
                  disabled={calculateMutation.isPending}
                >
                  {calculateMutation.isPending ? "Calculating…" : "Calculate ROI"}
                </Button>
              </div>
            </CardContent>
          </Card>

          {results && (
            <Card className="bg-gradient-to-br from-white to-gray-50 border-2 border-[#f9cb07]/20 rounded-2xl shadow-xl animate-fade-in-up">
              <CardHeader className="text-center">
                <CardTitle className="text-3xl font-bold text-black flex items-center justify-center gap-3">
                  <TrendingUp className="w-8 h-8 text-green-600" /> Your Potential Savings
                </CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <ResultCard title="Monthly Savings" value={`$${results.monthlySavings.toLocaleString()}`} detail="Automation + recovered revenue" />
                <ResultCard title="Annual Savings" value={`$${results.annualSavings.toLocaleString()}`} detail="12-month impact" />
                <ResultCard title="Annual ROI" value={`${results.annualROI}%`} detail="Net of implementation" />
              </CardContent>
            </Card>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {highlightStats.map((stat) => (
              <div key={stat.label} className="p-6 rounded-2xl bg-white border border-[#f9cb07]/20 text-center shadow-xl">
                <p className="text-4xl font-bold text-black">{stat.value}</p>
                <p className="text-sm text-gray-600">{stat.label}</p>
                {stat.detail && <p className="text-xs text-gray-500 mt-1">{stat.detail}</p>}
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {benefitsList.map((benefit) => (
              <Card key={benefit.title} className="border border-[#f9cb07]/20 rounded-2xl shadow-md">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-xl font-semibold text-black flex items-center gap-2">
                      <Zap className="w-4 h-4 text-[#f9cb07]" />
                      {benefit.title}
                    </CardTitle>
                    <span className="text-lg font-bold text-[#f9cb07]">{benefit.metric}</span>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600">{benefit.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

const FormField = ({ id, label, icon: Icon, value, placeholder, onChange }) => (
  <div className="space-y-2">
    <Label htmlFor={id} className="flex items-center gap-2 font-semibold text-gray-700">
      <Icon className="w-4 h-4 text-[#f9cb07]" />
      {label}
    </Label>
    <Input
      id={id}
      type="number"
      className="h-12 border-2 border-gray-200 rounded-xl focus:border-[#f9cb07] focus:ring-[#f9cb07]/20"
      value={value || ""}
      placeholder={placeholder}
      onChange={(e) => onChange(e.target.value)}
    />
  </div>
);

const ResultCard = ({ title, value, detail }) => (
  <Card className="border border-[#f9cb07]/15 rounded-2xl">
    <CardHeader className="pb-2">
      <CardTitle className="text-lg text-black">{title}</CardTitle>
    </CardHeader>
    <CardContent>
      <p className="text-4xl font-bold text-black">{value}</p>
      <p className="text-sm text-gray-600 mt-2">{detail}</p>
    </CardContent>
  </Card>
);
