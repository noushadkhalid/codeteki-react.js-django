import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "../components/ui/accordion";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Phone, Mail, MessageCircle } from "lucide-react";
import SEOHead from "../components/SEOHead";
import BookingModal from "../components/BookingModal";

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

const supportCards = [
  {
    title: "Call our team",
    description: "Speak directly with an AI strategist",
    meta: "Business hours: 9 AM - 6 PM AEST",
    icon: Phone,
    cta: "Call Now",
    action: () => window.open("tel:+61469807872", "_self"),
  },
  {
    title: "Live Chat",
    description: "Get instant answers online",
    meta: "Available during business hours",
    icon: MessageCircle,
    cta: "Start Chat",
    action: () => {
      const message = encodeURIComponent("Hi! I have a question about your AI services.");
      window.open(`https://wa.me/61469807872?text=${message}`, "_blank");
    },
  },
  {
    title: "Email Support",
    description: "Detailed responses within 24h",
    meta: "We reply within one business day",
    icon: Mail,
    cta: "Send Email",
    action: () =>
      window.open(
        "mailto:info@codeteki.au?subject=Support%20Request&body=Hi%20Codeteki%20Team,%0A%0A",
        "_blank"
      ),
  },
];

export default function FAQ() {
  const [bookingOpen, setBookingOpen] = useState(false);
  const [activeCategory, setActiveCategory] = useState("All");
  const [search, setSearch] = useState("");

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  const { data, isLoading } = useQuery({
    queryKey: ["/api/faq/"],
  });

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

      <section className="bg-white py-20">
        <div className="container mx-auto px-4 text-center max-w-3xl">
          <span className="codeteki-pill mb-4">Your questions, answered</span>
          <h1 className="text-4xl font-bold text-[#0f172a] mb-4">Answers for every stage of your AI journey</h1>
          <p className="text-lg text-gray-600">
            Learn how we design, build, and support Codeteki deployments across industries. Can’t find what you need?
            Message the team anytime.
          </p>
          <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-center">
            <input
              type="text"
              placeholder="Search FAQs..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              className="w-full rounded-full border border-gray-200 px-5 py-3 text-sm focus:border-[#f9cb07] focus:ring-2 focus:ring-[#f9cb07]/30"
            />
            <div className="flex flex-wrap gap-2 justify-center">
              {categoryFilters.map((cat) => (
                <Button
                  key={cat}
                  variant={activeCategory === cat ? "default" : "outline"}
                  size="sm"
                  className={`rounded-full ${
                    activeCategory === cat
                      ? "bg-[#0f172a] text-white"
                      : "border-gray-200 text-gray-600 hover:border-[#0f172a]/40"
                  }`}
                  onClick={() => setActiveCategory(cat)}
                >
                  {cat}
                </Button>
              ))}
            </div>
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
            {supportCards.map((option) => (
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
                onClick={() => supportCards[2].action()}
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
