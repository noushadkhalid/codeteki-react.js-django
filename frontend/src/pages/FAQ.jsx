import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "../components/ui/accordion";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Phone, Mail, MessageCircle, Search } from "lucide-react";
import SEOHead from "../components/SEOHead";
import BookingModal from "../components/BookingModal";
import { useSiteSettings } from "../hooks/useSiteSettings";
import { getSupportMeta } from "../lib/supportMeta";
import heroIllustration from "../assets/codeteki-hero.png";

const fallbackFaqs = [
  {
    title: "Our Capabilities & Approach",
    items: [
      {
        question: "What types of solutions can you build?",
        answer:
          "From AI workforce solutions and custom automation tools to business integrations and web development — every project is tailored to your needs.",
      },
      {
        question: "How do you determine what solution is right for me?",
        answer:
          "We start with a free consultation to understand your business goals and systems, then design a custom solution for your requirements.",
      },
    ],
  },
];

const fallbackHeroHighlights = [
  { value: "80+", label: "Documented answers" },
  { value: "14", label: "Industries supported" },
];

const supportCards = [
  {
    key: "call",
    title: "Call our team",
    description: "Speak directly with an AI strategist",
    meta: "Business hours: 9 AM - 6 PM AEST",
    icon: Phone,
    cta: "Call Now",
  },
  {
    key: "chat",
    title: "Live Chat",
    description: "Get instant answers online",
    meta: "Available during business hours",
    icon: MessageCircle,
    cta: "Start Chat",
  },
  {
    key: "email",
    title: "Email Support",
    description: "Detailed responses from our Melbourne team",
    meta: "We reply quickly",
    icon: Mail,
    cta: "Send Email",
  },
];

export default function FAQ() {
  const [bookingOpen, setBookingOpen] = useState(false);
  const [activeCategory, setActiveCategory] = useState("All");
  const [search, setSearch] = useState("");
  const { settings } = useSiteSettings();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  const { data, isLoading } = useQuery({
    queryKey: ["/api/faq/"],
  });

  const supportMeta = useMemo(() => getSupportMeta(settings), [settings]);
  const heroHighlights = useMemo(
    () => [
      {
        value: supportMeta.responseValue,
        label: supportMeta.responseLabel,
        detail: supportMeta.responseHelper,
      },
      ...fallbackHeroHighlights,
    ],
    [supportMeta.responseValue, supportMeta.responseLabel, supportMeta.responseHelper]
  );
  const contactPhone = settings?.contact?.primaryPhone || "+61 469 754 386";
  const contactEmail = settings?.contact?.primaryEmail || "info@codeteki.au";
  const normalizedPhone = contactPhone ? contactPhone.replace(/\s+/g, "") : "+61469754386";
  const whatsappNumber = normalizedPhone.replace(/^\+/, "") || "61469754386";
  const phoneHref = `tel:${normalizedPhone}`;
  const emailHref = `mailto:${contactEmail}?subject=${encodeURIComponent("Support Request")}&body=${encodeURIComponent(
    "Hi Codeteki Team,\n\n"
  )}`;
  const openCall = () => window.open(phoneHref, "_self");
  const openEmail = () => window.open(emailHref, "_blank");
  const openChat = () => {
    const message = encodeURIComponent("Hi! I have a question about your AI services.");
    window.open(`https://wa.me/${whatsappNumber}?text=${message}`, "_blank");
  };
  const supportOptions = supportCards.map((card) => {
    if (card.key === "call") {
      return { ...card, action: openCall, value: contactPhone };
    }
    if (card.key === "chat") {
      return { ...card, action: openChat };
    }
    if (card.key === "email") {
      return {
        ...card,
        action: openEmail,
        description: supportMeta.responseMessage,
        meta: supportMeta.responseHelper || card.meta,
        value: contactEmail,
      };
    }
    return card;
  });
  const chatOption = supportOptions.find((option) => option.key === "chat");
  const emailOption = supportOptions.find((option) => option.key === "email");

  const categories = useMemo(() => {
    const payload = data?.data?.categories || data?.categories;
    return payload && payload.length ? payload : fallbackFaqs;
  }, [data]);

  const filteredFAQs = useMemo(() => {
    const lowerSearch = search.toLowerCase();
    const list = activeCategory === "All" ? categories : categories.filter((cat) => cat.title === activeCategory);
    if (!lowerSearch) return list;
    return list
      .map((cat) => ({
        ...cat,
        items: cat.items.filter(
          (item) =>
            item.question?.toLowerCase().includes(lowerSearch) || item.answer?.toLowerCase().includes(lowerSearch)
        ),
      }))
      .filter((cat) => cat.items.length);
  }, [categories, activeCategory, search]);

  const categoryFilters = useMemo(() => ["All", ...categories.map((cat) => cat.title)], [categories]);

  return (
    <div className="min-h-screen bg-[#f8fafc]">
      <SEOHead
        title="FAQ | Codeteki - AI Solutions"
        description="Get answers to the most common questions about Codeteki automation, AI copilots, delivery timelines, and pricing."
        keywords="Codeteki FAQ, AI automation FAQ, chatbot FAQ, Melbourne AI services"
      />

      <section className="relative overflow-hidden bg-gradient-to-br from-[#050c1b] via-[#0f172a] to-[#11182d] py-24 text-white">
        <div className="absolute inset-0 opacity-60">
          <div className="absolute -top-32 left-1/3 h-72 w-72 rounded-full bg-[#f9cb07]/25 blur-[200px]" />
          <div className="absolute bottom-0 right-0 h-80 w-80 rounded-full bg-[#6366f1]/20 blur-[180px]" />
        </div>
        <div className="container mx-auto px-4 relative">
          <div className="grid gap-12 items-center lg:grid-cols-[1.2fr,0.8fr]">
            <div className="space-y-8">
              <span className="inline-flex items-center gap-2 rounded-full border border-white/30 bg-white/10 px-4 py-1 text-xs font-semibold uppercase tracking-[0.4em]">
                FAQ Hub
              </span>
              <div>
                <h1 className="text-4xl lg:text-5xl font-bold leading-tight">
                  Answers for every stage of your AI journey
                </h1>
                <p className="mt-4 text-lg text-white/80 max-w-3xl">
                  Learn how we design, build, and support Codeteki deployments across industries. Can’t find what you
                  need? Message our Melbourne-based pod anytime.
                </p>
              </div>
              <div className="grid gap-4 sm:grid-cols-3">
                {heroHighlights.map((item) => (
                  <div
                    key={item.label}
                    className="rounded-2xl border border-white/15 bg-white/5 p-4 backdrop-blur-sm"
                  >
                    <p className="text-3xl font-bold text-white">{item.value}</p>
                    <p className="text-sm text-white/70">{item.label}</p>
                    {item.detail && <p className="text-xs text-white/60 mt-1">{item.detail}</p>}
                  </div>
                ))}
              </div>
              <div className="rounded-3xl border border-white/15 bg-white/5 p-6 backdrop-blur">
                <p className="text-sm font-semibold tracking-[0.2em] text-white/70 uppercase">Search Knowledge Base</p>
                <div className="mt-4 flex flex-col gap-4 lg:flex-row lg:items-center">
                  <div className="flex min-w-0 flex-1 items-center gap-3 rounded-2xl bg-white/95 px-5 py-3 shadow-xl">
                    <Search className="h-5 w-5 text-gray-500" />
                    <input
                      type="text"
                      placeholder="Search FAQs..."
                      value={search}
                      onChange={(event) => setSearch(event.target.value)}
                      className="w-full bg-transparent text-base text-[#0f172a] placeholder:text-gray-500 focus:outline-none"
                    />
                  </div>
                  <Button
                    type="button"
                    className="h-12 rounded-2xl bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] px-6 text-base font-semibold text-black shadow-lg hover:from-[#ffcd3c] hover:to-[#f9cb07]"
                    onClick={() => setBookingOpen(true)}
                  >
                    Book strategy call
                  </Button>
                </div>
                <p className="mt-3 text-sm text-white/70">
                  Still stuck?{" "}
                  <button
                    type="button"
                    className="font-semibold text-[#fbd65c] underline-offset-4 hover:underline"
                    onClick={() => chatOption?.action?.()}
                  >
                    Message the team
                  </button>
                </p>
              </div>
            </div>

            <div className="relative">
              <div className="absolute -inset-6 rounded-[36px] bg-gradient-to-br from-[#f9cb07]/20 via-[#7c3aed]/10 to-transparent blur-3xl opacity-70" />
              <div className="relative rounded-[32px] border border-white/15 bg-white/5 p-4 shadow-[0_30px_90px_rgba(15,23,42,0.6)] backdrop-blur">
                <div className="relative overflow-hidden rounded-[28px] bg-[#020617]">
                  <img
                    src={heroIllustration}
                    alt="Codeteki AI support pod"
                    className="h-[420px] w-full object-cover"
                    loading="lazy"
                  />
                  <div className="absolute inset-x-5 bottom-5 rounded-2xl bg-white/95 p-5 text-[#0f172a] shadow-2xl">
                    <p className="text-xs font-semibold uppercase tracking-[0.3em] text-gray-500">On-demand pod</p>
                    <p className="mt-2 text-3xl font-bold">{supportMeta.responseValue}</p>
                    <p className="text-sm text-gray-600">{supportMeta.responseLabel}</p>
                    <p className="text-xs text-gray-500">{supportMeta.responseHelper}</p>
                    <div className="mt-4 grid gap-3">
                      <div className="flex items-center justify-between rounded-2xl border border-[#e4e4e7] bg-white px-4 py-3">
                        <div>
                          <p className="text-xs uppercase tracking-[0.3em] text-gray-500">Call direct</p>
                          <p className="text-lg font-semibold text-[#0f172a]">{contactPhone}</p>
                        </div>
                        <Button
                          type="button"
                          variant="ghost"
                          className="rounded-xl border border-[#f9cb07]/40 bg-[#f9cb07]/10 px-4 text-[#7a5d00] hover:bg-[#f9cb07]"
                          onClick={openCall}
                        >
                          Call
                        </Button>
                      </div>
                      <div className="flex items-center justify-between rounded-2xl border border-[#e4e4e7] bg-white px-4 py-3">
                        <div>
                          <p className="text-xs uppercase tracking-[0.3em] text-gray-500">Email studio</p>
                          <p className="text-sm font-semibold text-[#0f172a]">{contactEmail}</p>
                        </div>
                        <Button
                          type="button"
                          variant="outline"
                          className="rounded-xl border border-[#0f172a]/10 text-[#0f172a] hover:bg-[#f9cb07]/10"
                          onClick={openEmail}
                        >
                          Email
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-white border-b border-[#e2e8f0]">
        <div className="container mx-auto px-4 py-8 space-y-4">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.3em] text-[#0f172a]/70">Browse by topic</p>
              <p className="text-sm text-gray-600">Jump to curated categories or view everything in All.</p>
            </div>
          </div>
          <div className="-mx-1 flex gap-2 overflow-x-auto pb-1">
            {categoryFilters.map((cat) => (
              <Button
                key={cat}
                type="button"
                variant="outline"
                size="sm"
                className={`rounded-full border px-4 py-2 text-sm font-semibold transition ${
                  activeCategory === cat
                    ? "border-transparent bg-[#f9cb07] text-black shadow-lg"
                    : "border-[#e6e8ee] bg-white text-gray-600 hover:border-[#f9cb07]/40"
                }`}
                onClick={() => setActiveCategory(cat)}
              >
                {cat}
              </Button>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16">
        <div className="container mx-auto px-4">
          {isLoading ? (
            <div className="text-center py-16">
              <div className="h-16 w-16 animate-spin rounded-full border-b-2 border-[#f9cb07] mx-auto" />
              <p className="mt-4 text-gray-600">Loading FAQs...</p>
            </div>
          ) : (
            filteredFAQs.map((category) => (
              <div key={category.title} className="mx-auto max-w-4xl mb-8">
                <h2 className="text-2xl font-bold text-[#0f172a] mb-4">{category.title}</h2>
                <Accordion type="single" collapsible className="space-y-4">
                  {category.items.map((item, idx) => (
                    <AccordionItem
                      key={`${category.title}-${idx}`}
                      value={`${category.title}-${idx}`}
                      className="overflow-hidden rounded-2xl border border-[#eef1f7] bg-white shadow-sm"
                    >
                      <AccordionTrigger className="px-6 py-4 text-left hover:bg-[#f9fbfd]">
                        <div className="flex items-center gap-3">
                          <Badge className="bg-[#f9cb07]/15 text-[#f9cb07]">{idx + 1}</Badge>
                          <span className="text-lg font-semibold text-[#0f172a]">{item.question}</span>
                        </div>
                      </AccordionTrigger>
                      <AccordionContent className="px-6 pb-6 text-gray-600 leading-relaxed">
                        {item.answer}
                      </AccordionContent>
                    </AccordionItem>
                  ))}
                </Accordion>
              </div>
            ))
          )}
        </div>
      </section>

      <section className="py-16 bg-[#fefce8]">
        <div className="container mx-auto px-4">
          <div className="grid gap-6 md:grid-cols-3">
            {supportOptions.map((option) => (
              <Card
                key={option.title}
                className="relative h-full overflow-hidden border border-[#e4e7ec] bg-white/90 shadow-lg"
              >
                <CardContent className="flex h-full flex-col items-center text-center gap-4 px-6 py-8">
                  <span className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[#f9cb07]/15 text-[#f9cb07]">
                    <option.icon className="h-8 w-8" />
                  </span>
                  <div>
                    <CardTitle className="text-2xl font-semibold text-[#0f172a]">{option.title}</CardTitle>
                    <CardDescription className="mt-2 text-gray-600">{option.description}</CardDescription>
                  </div>
                  <p className="text-sm text-gray-500">{option.meta}</p>
                  <Button className="mt-auto w-full bg-[#f9cb07] text-black font-semibold" onClick={option.action}>
                    {option.cta}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <Card className="max-w-4xl mx-auto border border-[#f1f5f9] shadow-none p-10 text-center space-y-4">
            <Badge className="mx-auto bg-blue-50 text-blue-700 font-semibold px-4 py-1.5">
              Custom builds available
            </Badge>
            <h3 className="text-3xl font-bold text-[#0f172a]">Still have questions?</h3>
            <p className="text-gray-600">
              Book a free consultation to discuss your specific needs and see our solutions in action.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                size="lg"
                className="bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] text-black font-semibold px-8 py-4"
                onClick={() => setBookingOpen(true)}
              >
                Book Free Consultation
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="border-2 border-[#f9cb07] text-[#f9cb07] hover:bg-[#f9cb07]/10 font-semibold px-8 py-4"
                onClick={() => emailOption?.action?.()}
              >
                Prefer Email? Reach Out
              </Button>
            </div>
          </Card>
        </div>
      </section>

      <BookingModal open={bookingOpen} onOpenChange={setBookingOpen} />
    </div>
  );
}
