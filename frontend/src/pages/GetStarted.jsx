import { useState, useEffect, useMemo } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useSearch } from "wouter";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "../components/ui/form";
import { Badge } from "../components/ui/badge";
import SEOHead from "../components/SEOHead";
import BookingModal from "../components/BookingModal";
import { apiRequest } from "../lib/queryClient";
import { useToast } from "../hooks/use-toast";
import {
  UtensilsCrossed, Wrench, Scissors, ShoppingBag, Dumbbell, Briefcase,
  Home, Stethoscope, Car, Hotel, MoreHorizontal,
  ArrowLeft, ArrowRight, Check, MessageCircle, CalendarCheck,
  ShoppingCart, FileText, Image, Search, Star, Gift, Package,
  Users, Smartphone, Globe, Bot, Shield, Sparkles, Loader2,
} from "lucide-react";

// ─── Static data ────────────────────────────────────────────

const INDUSTRIES = [
  { key: "restaurant", label: "Restaurant / Cafe", icon: UtensilsCrossed },
  { key: "trades", label: "Trades", icon: Wrench },
  { key: "health-beauty", label: "Health & Beauty", icon: Scissors },
  { key: "retail", label: "Retail", icon: ShoppingBag },
  { key: "fitness", label: "Fitness", icon: Dumbbell },
  { key: "professional-services", label: "Professional Services", icon: Briefcase },
  { key: "real-estate", label: "Real Estate", icon: Home },
  { key: "medical", label: "Medical", icon: Stethoscope },
  { key: "automotive", label: "Automotive", icon: Car },
  { key: "accommodation", label: "Accommodation", icon: Hotel },
  { key: "other", label: "Other", icon: MoreHorizontal },
];

const PAIN_POINTS = {
  restaurant: [
    "I don't have a website at all",
    "Taking orders is chaotic during rush hours",
    "Managing bookings manually (phone, notepad)",
    "Not showing up on Google when people search",
  ],
  trades: [
    "I don't have a website at all",
    "Spending evenings writing quotes",
    "No way to show my work to new customers",
    "Customers can't find me on Google",
  ],
  "health-beauty": [
    "I don't have a website at all",
    "Clients no-show without reminders",
    "Can't take bookings outside hours",
    "Hard to showcase my work online",
  ],
  retail: [
    "I don't have a website at all",
    "Missing out on online sales",
    "Stock management is a headache",
    "Hard to compete with big retailers online",
  ],
  fitness: [
    "I don't have a website at all",
    "Class bookings are chaotic",
    "Members cancel or no-show too often",
    "Hard to attract new members online",
  ],
  "professional-services": [
    "I don't have a website at all",
    "Website doesn't reflect my expertise",
    "Chasing invoices and late payments",
    "Not enough leads coming in",
  ],
  "real-estate": [
    "I don't have a website at all",
    "Leads fall through the cracks",
    "Listings site looks outdated",
    "Can't compete with big agencies online",
  ],
  medical: [
    "I don't have a website at all",
    "Patients no-show without reminders",
    "Reception overwhelmed with phone bookings",
    "Not ranking on Google for local searches",
  ],
  automotive: [
    "I don't have a website at all",
    "Phone keeps ringing for simple bookings",
    "Hard to build trust with new customers",
    "No online presence beyond Yellow Pages",
  ],
  accommodation: [
    "I don't have a website at all",
    "Paying too much in OTA commissions",
    "Website doesn't convert visitors",
    "Not showing up on Google for local stays",
  ],
  other: [
    "I don't have a website at all",
    "Customers can't find me online",
    "Too much manual admin work",
    "Not sure what technology I need",
  ],
};

const FEATURE_ICONS = {
  ShoppingCart, FileText, Image, Search, Star, Gift, Package,
  Users, Smartphone, Globe, Bot, Shield, CalendarCheck,
  Home,
};

const contactSchema = z.object({
  name: z.string().min(2, "Name is required"),
  email: z.string().email("Please enter a valid email"),
  phone: z.string().optional(),
});

// ─── Component ──────────────────────────────────────────────

export default function GetStarted() {
  const searchString = useSearch();
  const ref = useMemo(() => new URLSearchParams(searchString).get("ref") || "", [searchString]);

  const [step, setStep] = useState(1);
  const [industry, setIndustry] = useState("");
  const [customIndustry, setCustomIndustry] = useState("");
  const [showOtherInput, setShowOtherInput] = useState(false);
  const [challenges, setChallenges] = useState([]);
  const [customChallenges, setCustomChallenges] = useState("");
  const [results, setResults] = useState(null);
  const [bookingOpen, setBookingOpen] = useState(false);
  const { toast } = useToast();

  // Ref lookup for pre-fill
  const { data: refData } = useQuery({
    queryKey: [`/api/get-started/?ref=${ref}`],
    enabled: !!ref,
  });

  const prefill = refData?.data || refData || {};

  const form = useForm({
    resolver: zodResolver(contactSchema),
    defaultValues: { name: "", email: "", phone: "" },
  });

  // Pre-fill name when ref lookup returns
  useEffect(() => {
    if (prefill.found && prefill.name) {
      form.setValue("name", prefill.name);
    }
  }, [prefill.found, prefill.name, form]);

  const submitMutation = useMutation({
    mutationFn: async (formData) => {
      // Merge preset challenges + custom typed ones
      const customList = customChallenges
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      const allChallenges = [...challenges, ...customList];

      const res = await apiRequest("POST", "/api/get-started/", {
        ref,
        industry: customIndustry || industry,
        challenges: allChallenges,
        name: formData.name,
        email: formData.email,
        phone: formData.phone || "",
      });
      return await res.json();
    },
    onSuccess: (data) => {
      const d = data?.data || data;
      setResults(d);
      setStep(4);
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Something went wrong. Please try again.",
        variant: "destructive",
      });
    },
  });

  const onContactSubmit = (data) => submitMutation.mutate(data);

  // Fetch AI pain points for custom business types
  const { data: suggestData, isFetching: suggestLoading } = useQuery({
    queryKey: [`/api/get-started/?suggest_for=${encodeURIComponent(customIndustry)}`],
    enabled: !!customIndustry && industry === "other",
  });

  const selectIndustry = (key) => {
    if (key === "other") {
      setIndustry("other");
      setShowOtherInput(true);
      return;
    }
    setIndustry(key);
    setShowOtherInput(false);
    setCustomIndustry("");
    setStep(2);
  };

  const confirmCustomIndustry = () => {
    if (!customIndustry.trim()) return;
    setStep(2);
  };

  const toggleChallenge = (c) => {
    setChallenges((prev) =>
      prev.includes(c) ? prev.filter((x) => x !== c) : [...prev, c]
    );
  };

  const industryLabel = customIndustry || INDUSTRIES.find((i) => i.key === industry)?.label || industry;
  const aiPainPoints = suggestData?.data?.pain_points || suggestData?.pain_points;
  const painPoints = (industry === "other" && aiPainPoints?.length) ? aiPainPoints : (PAIN_POINTS[industry] || PAIN_POINTS.other);
  const progress = step <= 3 ? (step / 3) * 100 : 100;

  return (
    <div className="min-h-screen bg-[#111827]">
      <SEOHead
        title="Get Started | Codeteki — See What We'd Build for You"
        description="Answer 3 quick questions and get personalized recommendations for your business — websites, apps, AI, SEO, and more."
      />

      {/* Progress bar */}
      {step <= 3 && (
        <div className="fixed top-0 left-0 right-0 z-50 h-1 bg-white/10">
          <div
            className="h-full bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}

      <div className="min-h-screen flex flex-col items-center justify-center px-3 sm:px-4 py-16 sm:py-20">

        {/* ─── STEP 1: Industry Selection ─── */}
        {step === 1 && (
          <div className="w-full max-w-2xl animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="text-center mb-8">
              <span className="inline-block px-3 py-1 rounded-full bg-[#f9cb07]/15 text-[#f9cb07] text-xs font-semibold mb-4">
                Step 1 of 3
              </span>
              <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-white mb-2">
                What type of business do you run?
              </h1>
              <p className="text-white/60 text-xs sm:text-sm">Tap your industry — we'll tailor everything from here.</p>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 sm:gap-3">
              {INDUSTRIES.map(({ key, label, icon: Icon }) => (
                <button
                  key={key}
                  onClick={() => selectIndustry(key)}
                  className={`group flex flex-col items-center gap-1.5 sm:gap-2 rounded-2xl border p-3 sm:p-5 text-center transition-all duration-200 active:scale-95 ${
                    showOtherInput && key === "other"
                      ? "border-[#f9cb07] bg-[#f9cb07]/15"
                      : "border-white/10 bg-white/5 hover:border-[#f9cb07]/50 hover:bg-[#f9cb07]/10"
                  }`}
                >
                  <div className={`flex h-10 w-10 sm:h-12 sm:w-12 items-center justify-center rounded-xl transition-colors ${
                    showOtherInput && key === "other"
                      ? "bg-[#f9cb07]/20 text-[#f9cb07]"
                      : "bg-white/10 text-white group-hover:bg-[#f9cb07]/20 group-hover:text-[#f9cb07]"
                  }`}>
                    <Icon className="h-5 w-5 sm:h-6 sm:w-6" />
                  </div>
                  <span className={`text-xs sm:text-sm font-medium ${
                    showOtherInput && key === "other" ? "text-white" : "text-white/80 group-hover:text-white"
                  }`}>
                    {label}
                  </span>
                </button>
              ))}
            </div>

            {/* Custom business type input (shown when "Other" is tapped) */}
            {showOtherInput && (
              <div className="mt-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
                <label className="block text-white/70 text-sm mb-2">
                  Tell us what you do
                </label>
                <div className="flex gap-3">
                  <Input
                    value={customIndustry}
                    onChange={(e) => setCustomIndustry(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && confirmCustomIndustry()}
                    placeholder="e.g. Nursery, Pet Grooming, Music School..."
                    className="flex-1 h-12 rounded-xl bg-white/10 border-white/20 text-white placeholder:text-white/30 focus:border-[#f9cb07]"
                    autoFocus
                  />
                  <Button
                    onClick={confirmCustomIndustry}
                    disabled={!customIndustry.trim() || suggestLoading}
                    className="h-12 px-6 bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] text-black font-semibold hover:from-[#e6b800] hover:to-[#f9cb07] rounded-xl"
                  >
                    {suggestLoading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <>Next <ArrowRight className="h-4 w-4 ml-1" /></>
                    )}
                  </Button>
                </div>
                <p className="text-white/40 text-xs mt-2">
                  We'll tailor the next step to your specific business
                </p>
              </div>
            )}
          </div>
        )}

        {/* ─── STEP 2: Pain Points ─── */}
        {step === 2 && (
          <div className="w-full max-w-xl animate-in fade-in slide-in-from-right-4 duration-500">
            <div className="text-center mb-8">
              <span className="inline-block px-3 py-1 rounded-full bg-[#f9cb07]/15 text-[#f9cb07] text-xs font-semibold mb-4">
                Step 2 of 3
              </span>
              <h2 className="text-xl sm:text-2xl md:text-3xl font-bold text-white mb-2">
                {customIndustry
                  ? `What challenges does your ${customIndustry} face?`
                  : "What's your biggest challenge?"}
              </h2>
              <p className="text-white/60 text-xs sm:text-sm">Select all that apply — helps us prioritise.</p>
            </div>

            {suggestLoading ? (
              <div className="flex flex-col items-center gap-3 py-12">
                <Loader2 className="h-8 w-8 text-[#f9cb07] animate-spin" />
                <p className="text-white/50 text-sm">Tailoring questions for your {customIndustry} business...</p>
              </div>
            ) : (
            <>
            <div className="space-y-3">
              {painPoints.map((point) => {
                const selected = challenges.includes(point);
                return (
                  <button
                    key={point}
                    onClick={() => toggleChallenge(point)}
                    className={`w-full flex items-center gap-3 rounded-xl border p-3 sm:p-4 text-left transition-all duration-200 active:scale-[0.98] ${
                      selected
                        ? "border-[#f9cb07] bg-[#f9cb07]/15 text-white"
                        : "border-white/10 bg-white/5 text-white/70 hover:border-white/30"
                    }`}
                  >
                    <div
                      className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-md border transition-colors ${
                        selected
                          ? "border-[#f9cb07] bg-[#f9cb07] text-black"
                          : "border-white/30"
                      }`}
                    >
                      {selected && <Check className="h-4 w-4" />}
                    </div>
                    <span className="text-sm font-medium">{point}</span>
                  </button>
                );
              })}
            </div>

            {/* Custom challenges input */}
            <div className="mt-4">
              <label className="block text-white/60 text-xs mb-2">
                Anything else? Type your own challenges, separated by commas
              </label>
              <textarea
                value={customChallenges}
                onChange={(e) => setCustomChallenges(e.target.value)}
                placeholder="e.g. Need a booking system, want to accept online payments, social media is too time-consuming"
                rows={2}
                className="w-full rounded-xl bg-white/10 border border-white/20 text-white text-sm placeholder:text-white/30 p-3 focus:border-[#f9cb07] focus:outline-none focus:ring-1 focus:ring-[#f9cb07]/50 resize-none"
              />
            </div>

            <div className="mt-6 flex gap-3">
              <Button
                variant="ghost"
                className="border border-white/20 text-white/70 hover:text-white hover:bg-white/10"
                onClick={() => { setStep(1); setChallenges([]); setCustomChallenges(""); }}
              >
                <ArrowLeft className="h-4 w-4 mr-1" /> Back
              </Button>
              <Button
                className="flex-1 bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] text-black font-semibold hover:from-[#e6b800] hover:to-[#f9cb07]"
                onClick={() => setStep(3)}
                disabled={challenges.length === 0 && !customChallenges.trim()}
              >
                Next <ArrowRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
            </>
            )}
          </div>
        )}

        {/* ─── STEP 3: Contact Capture ─── */}
        {step === 3 && (
          <div className="w-full max-w-md animate-in fade-in slide-in-from-right-4 duration-500">
            <div className="text-center mb-8">
              <span className="inline-block px-3 py-1 rounded-full bg-[#f9cb07]/15 text-[#f9cb07] text-xs font-semibold mb-4">
                Step 3 of 3
              </span>
              <h2 className="text-xl sm:text-2xl md:text-3xl font-bold text-white mb-2">
                Almost there!
              </h2>
              <p className="text-white/60 text-sm">
                We'll put together your personalized plan.
              </p>
            </div>

            <Card className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur">
              <CardContent className="p-6">
                <Form {...form}>
                  <form onSubmit={form.handleSubmit(onContactSubmit)} className="space-y-4">
                    <FormField
                      control={form.control}
                      name="name"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-white/80">Your Name *</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="Your name"
                              className="h-11 rounded-xl bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-[#f9cb07]"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="email"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-white/80">Email *</FormLabel>
                          <FormControl>
                            <Input
                              type="email"
                              placeholder="you@business.com"
                              className="h-11 rounded-xl bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-[#f9cb07]"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    {!prefill.found && (
                      <FormField
                        control={form.control}
                        name="phone"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel className="text-white/80">Phone</FormLabel>
                            <FormControl>
                              <Input
                                placeholder="+61 400 000 000"
                                className="h-11 rounded-xl bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-[#f9cb07]"
                                {...field}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    )}

                    {prefill.found && prefill.phone_last4 && (
                      <p className="text-white/50 text-xs">
                        We have your phone ending in ***{prefill.phone_last4}
                      </p>
                    )}

                    <div className="flex gap-3 pt-2">
                      <Button
                        type="button"
                        variant="ghost"
                        className="border border-white/20 text-white/70 hover:text-white hover:bg-white/10"
                        onClick={() => setStep(2)}
                      >
                        <ArrowLeft className="h-4 w-4 mr-1" /> Back
                      </Button>
                      <Button
                        type="submit"
                        className="flex-1 bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] text-black font-bold hover:from-[#e6b800] hover:to-[#f9cb07]"
                        disabled={submitMutation.isPending}
                      >
                        {submitMutation.isPending ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Building your plan...
                          </>
                        ) : (
                          <>
                            See My Recommendations <Sparkles className="h-4 w-4 ml-1" />
                          </>
                        )}
                      </Button>
                    </div>
                  </form>
                </Form>
              </CardContent>
            </Card>
          </div>
        )}

        {/* ─── STEP 4: Results ─── */}
        {step === 4 && results && (
          <div className="w-full max-w-3xl animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="text-center mb-10">
              <div className="inline-flex h-12 w-12 sm:h-16 sm:w-16 items-center justify-center rounded-full bg-[#f9cb07]/20 mb-4">
                <Sparkles className="h-6 w-6 sm:h-8 sm:w-8 text-[#f9cb07]" />
              </div>
              <h2 className="text-xl sm:text-2xl md:text-3xl font-bold text-white mb-2">
                Here's what we'd build for your {industryLabel},{" "}
                {(results.contact_name || "").split(" ")[0] || "there"}
              </h2>
              {results.summary && (
                <p className="text-white/70 text-sm max-w-xl mx-auto mt-3 leading-relaxed">
                  {results.summary}
                </p>
              )}
            </div>

            {/* Feature cards */}
            <div className="grid gap-3 sm:gap-4 sm:grid-cols-2">
              {(results.recommendations || []).map((feat) => {
                const IconComp = FEATURE_ICONS[feat.icon] || Globe;
                return (
                  <Card
                    key={feat.key}
                    className="rounded-xl sm:rounded-2xl border border-white/10 bg-white/5 overflow-hidden hover:border-[#f9cb07]/30 transition-colors"
                  >
                    <CardContent className="p-4 sm:p-5">
                      <div className="flex items-start gap-4">
                        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[#f9cb07]/15 text-[#f9cb07]">
                          <IconComp className="h-5 w-5" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="text-sm font-bold text-white truncate">{feat.title}</h3>
                            {feat.impact && (
                              <Badge variant="outline" className="text-[10px] border-[#f9cb07]/40 text-[#f9cb07] shrink-0">
                                {feat.impact}
                              </Badge>
                            )}
                          </div>
                          <p className="text-xs text-white/60 leading-relaxed">
                            {feat.description}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            {/* CTAs */}
            <div className="mt-8 sm:mt-10 flex flex-col sm:flex-row gap-3 justify-center">
              <Button
                size="lg"
                className="w-full sm:w-auto bg-[#25D366] hover:bg-[#20bd5a] text-white font-semibold px-6 sm:px-8 py-4 sm:py-5 text-sm sm:text-base rounded-xl shadow-lg"
                asChild
              >
                <a
                  href="https://wa.me/61469754386?text=Hey%2C%20I%20just%20filled%20out%20the%20questionnaire%20on%20your%20site%20%E2%80%94%20keen%20to%20chat!"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <MessageCircle className="h-5 w-5 mr-2" />
                  Let's chat about this
                </a>
              </Button>
              <Button
                size="lg"
                variant="ghost"
                className="w-full sm:w-auto border border-white/30 text-white/80 hover:bg-[#f9cb07] hover:text-black hover:border-[#f9cb07] px-6 sm:px-8 py-4 sm:py-5 text-sm sm:text-base rounded-xl transition-all"
                onClick={() => setBookingOpen(true)}
              >
                <CalendarCheck className="h-5 w-5 mr-2" />
                Book a free call
              </Button>
            </div>

            {results.whatsapp_sent && (
              <p className="text-center text-white/40 text-xs mt-6">
                We've also sent you a message — check your WhatsApp or SMS.
              </p>
            )}
          </div>
        )}
      </div>

      <BookingModal
        open={bookingOpen}
        onOpenChange={setBookingOpen}
        context={results ? {
          name: results.contact_name || form.getValues("name"),
          email: form.getValues("email"),
          phone: form.getValues("phone"),
          industry: industryLabel,
          challenges,
          summary: results.summary,
          service: "Web Dev",
          message: `Coming from Get Started questionnaire:\n\nBusiness: ${industryLabel}\nChallenges: ${challenges.join(", ")}${results.summary ? `\n\nAI Recommendations: ${results.summary}` : ""}${(results.recommendations || []).length ? `\n\nRecommended: ${results.recommendations.map(r => r.title).join(", ")}` : ""}`,
        } : undefined}
      />
    </div>
  );
}
