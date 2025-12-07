import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "../components/ui/form";
import { Mail, HelpCircle, Calendar, Phone, MapPin, Clock } from "lucide-react";
import { apiRequest } from "../lib/queryClient";
import { useToast } from "../hooks/use-toast";
import { useLocation } from "wouter";
import BookingModal from "../components/BookingModal";
import { useSiteSettings } from "../hooks/useSiteSettings";
import { getSupportMeta } from "../lib/supportMeta";

const contactFormSchema = z.object({
  fullName: z.string().min(2, "Full name must be at least 2 characters"),
  email: z.string().email("Please enter a valid email address"),
  phone: z.string().optional(),
  message: z.string().min(10, "Message must be at least 10 characters"),
});

export default function Contact() {
  const { toast } = useToast();
  const [bookingOpen, setBookingOpen] = useState(false);
  const [, setLocation] = useLocation();
  const { settings } = useSiteSettings();
  const supportMeta = getSupportMeta(settings);

  const form = useForm({
    resolver: zodResolver(contactFormSchema),
    defaultValues: {
      fullName: "",
      email: "",
      phone: "",
      message: "",
    },
  });

  const contactMutation = useMutation({
    mutationFn: async (data) => {
      const response = await apiRequest("POST", "/api/contact/", data);
      return await response.json();
    },
    onSuccess: () => {
      toast({
        title: "Message Sent!",
        description: supportMeta.responseMessage,
      });
      form.reset();
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to send message. Please try again.",
        variant: "destructive",
      });
    },
  });

  const onSubmit = (data) => {
    contactMutation.mutate(data);
  };

const iconMap = {
  mail: Mail,
  phone: Phone,
  mappin: MapPin,
  map: MapPin,
  helpcircle: HelpCircle,
  calendar: Calendar,
  clock: Clock,
};

  const { data: contactData, isLoading: contactLoading } = useQuery({
    queryKey: ["/api/contact/"],
  });

  // Extract contact info from API
  const contactInfo = useMemo(() => {
    const info = contactData?.data?.info || contactData?.info || {};
    return {
      email: info.primaryEmail || settings?.contact?.email || "info@codeteki.au",
      phone: info.primaryPhone || settings?.contact?.phone || "+61 469 754 386",
      address: info.address || settings?.contact?.address || "Melbourne, Victoria",
    };
  }, [contactData, settings]);

  const quickActions = useMemo(
    () => [
      {
        icon: Calendar,
        title: "Schedule a Call",
        description: "Book a free consultation with our experts",
        action: () => {
          setBookingOpen(true);
        },
        accent: "from-[#f9cb07] to-[#ffcd3c]",
      },
      {
        icon: Mail,
        title: "Email Us",
        description: supportMeta.responseMessage,
        action: () => {
          window.location.href = `mailto:${contactInfo.email}`;
        },
        accent: "from-[#38bdf8] to-[#6366f1]",
      },
      {
        icon: HelpCircle,
        title: "FAQs & Support",
        description: "Find quick answers to common questions",
        action: () => {
          setLocation("/faq");
        },
        accent: "from-[#f472b6] to-[#c084fc]",
      },
    ],
    [setBookingOpen, setLocation, supportMeta.responseMessage, contactInfo.email]
  );

  const contactMethods = useMemo(() => {
    const methods = contactData?.data?.methods || contactData?.methods;
    if (!methods || !methods.length) {
      // Use dynamic contact info from API with fallbacks
      return [
        {
          icon: Phone,
          title: "Call Us",
          value: contactInfo.phone,
          description: "Melbourne-based support team",
          href: `tel:${contactInfo.phone.replace(/\s+/g, "")}`,
        },
        {
          icon: MapPin,
          title: "Visit Us",
          value: contactInfo.address,
          description: "Local team available across Australia",
        },
        {
          icon: Mail,
          title: "Email",
          value: contactInfo.email,
          description: supportMeta.responseMessage,
          href: `mailto:${contactInfo.email}`,
        },
      ];
    }

    return methods.map((method) => {
      const iconKey = (method.icon || "").toLowerCase();
      const IconComponent = iconMap[iconKey] || Mail;
      let href = method.value || "";
      if (href?.includes("@")) {
        href = `mailto:${href}`;
      } else if (href?.startsWith("+")) {
        href = `tel:${href.replace(/\s+/g, "")}`;
      } else {
        href = method.ctaHref || method.href || null;
      }

      return {
        icon: IconComponent,
        title: method.title,
        description: method.description,
        value: method.value,
        href,
        cta: method.cta,
      };
    });
  }, [contactData, supportMeta.responseMessage, contactInfo]);

  const businessHours = useMemo(() => {
    // Try contact API first, then settings API, then fallback
    const hours = contactData?.data?.businessHours || contactData?.businessHours || settings?.business?.hours;
    if (!hours || (Array.isArray(hours) && hours.length === 0)) {
      return [
        { day: "Monday - Friday", hours: "9:00 AM - 6:00 PM AEDT" },
        { day: "Saturday", hours: "10:00 AM - 4:00 PM AEDT" },
        { day: "Sunday", hours: "By appointment" },
      ];
    }
    if (Array.isArray(hours)) {
      return hours;
    }
    try {
      const parsed = JSON.parse(hours);
      if (Array.isArray(parsed)) return parsed;
      return [
        { day: "Monday - Friday", hours: parsed["monday-friday"] || parsed.weekdays || "9:00 AM - 6:00 PM AEDT" },
        { day: "Saturday", hours: parsed.saturday || "10:00 AM - 4:00 PM AEDT" },
        { day: "Sunday", hours: parsed.sunday || "By appointment" },
      ];
    } catch {
      return hours.split("\n").map((line) => {
        const [day, value] = line.split(":").map((part) => part.trim());
        return { day, hours: value };
      });
    }
  }, [settings, contactData]);

  return (
    <section id="contact" className="relative py-24 overflow-hidden bg-[#111827]">
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[1200px] bg-[#1f2937] rounded-full blur-[220px] opacity-60" />
        <div className="absolute bottom-0 right-10 w-[500px] h-[500px] bg-[#f9cb07]/15 rounded-full blur-[150px]" />
      </div>

      <div className="relative container mx-auto px-4">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <span className="codeteki-pill mb-6">{supportMeta.badge}</span>
          <h2 className="text-4xl lg:text-5xl font-bold text-white mb-4">Let's Connect</h2>
          <p className="text-lg text-white/70">
            Multiple ways to reach our Melbourne-based team. We're here to help transform your business with AI.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-[1.4fr_0.6fr] gap-6 max-w-6xl mx-auto">
          <Card id="contact-form" className="relative overflow-hidden rounded-2xl border border-white/10 bg-white">
            <div className="absolute inset-0 bg-gradient-to-br from-white via-transparent to-[#f9cb07]/15 opacity-80 pointer-events-none" />
            <CardHeader className="relative p-5 pb-0">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-[#f9cb07] shadow-lg flex items-center justify-center">
                  <Mail className="h-5 w-5 text-black" />
                </div>
                <div>
                  <CardTitle className="text-xl font-bold text-black">Send us a Message</CardTitle>
                  <CardDescription className="text-gray-600 text-xs">
                    {supportMeta.responseMessage}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="relative p-5">
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-3">
                  <div className="grid md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="fullName"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Full Name *</FormLabel>
                          <FormControl>
                            <Input placeholder="Full Name" className="h-10 rounded-xl border border-gray-200 focus:border-[#f9cb07]" {...field} />
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
                          <FormLabel>Email *</FormLabel>
                          <FormControl>
                            <Input type="email" placeholder="you@company.com" className="h-10 rounded-xl border border-gray-200 focus:border-[#f9cb07]" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  <div className="grid md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="phone"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Phone</FormLabel>
                          <FormControl>
                            <Input placeholder="+61 400 000 000" className="h-10 rounded-xl border border-gray-200 focus:border-[#f9cb07]" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <div className="bg-[#f9cb07]/10 border border-[#f9cb07]/30 rounded-xl px-3 py-2 text-xs text-[#7a5d00] font-medium flex flex-col justify-center">
                      <p>Typical response time:</p>
                      <p className="text-sm font-semibold text-black">{supportMeta.responseValue}</p>
                    </div>
                  </div>
                  <FormField
                    control={form.control}
                    name="message"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Briefly Describe Your Needs *</FormLabel>
                        <FormControl>
                          <Textarea
                            placeholder="Tell us about your project, goals, and any specific requirements..."
                            rows={4}
                            className="rounded-xl border border-gray-200 focus:border-[#f9cb07] resize-none"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <Button
                    type="submit"
                    className="w-full bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] hover:from-[#e6b800] hover:to-[#f9cb07] text-black font-bold py-3 text-base rounded-xl shadow-lg hover:shadow-xl transform hover:scale-[1.01] transition-all duration-300"
                    disabled={contactMutation.isPending}
                  >
                    {contactMutation.isPending ? (
                      <div className="flex items-center">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-black mr-2" />
                        Sending...
                      </div>
                    ) : (
                      "Submit Your Query"
                    )}
                  </Button>

                  <div className="pt-5 mt-2 border-t border-gray-100 grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm text-gray-600">
                    <div className="flex items-center gap-3 rounded-xl bg-gray-50 px-3 py-2">
                      <div className="h-8 w-8 rounded-full bg-[#f9cb07]/40 flex items-center justify-center text-[#7a5d00] font-semibold">
                        1:1
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900">Personal Demo</p>
                        <p>Every inquiry gets a live walkthrough with our team.</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 rounded-xl bg-gray-50 px-3 py-2">
                      <div className="h-8 w-8 rounded-full bg-[#f9cb07]/40 flex items-center justify-center text-[#7a5d00] font-semibold">
                        {supportMeta.responseValue}
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900">Response SLA</p>
                        <p>{supportMeta.responseHelper}</p>
                      </div>
                    </div>
                  </div>
                </form>
              </Form>
            </CardContent>
          </Card>

          <div className="space-y-4">
            <Card className="rounded-2xl border-0 bg-white/90 backdrop-blur p-5 shadow-lg">
              <CardHeader className="p-0 pb-3">
                <CardTitle className="text-xl font-bold text-black">Quick Contact</CardTitle>
                <CardDescription className="text-sm text-gray-600">
                  Melbourne-based support team ready to help
                </CardDescription>
              </CardHeader>
              <div className="flex flex-wrap gap-2 mt-2">
                {["Free Consultation", supportMeta.responseValue].map((badge) => (
                  <span key={badge} className="px-3 py-1 rounded-full bg-[#f9cb07]/15 text-xs font-semibold text-[#7a5d00]">
                    {badge}
                  </span>
                ))}
              </div>
            </Card>

            <div className="grid gap-3">
              {quickActions.map((action) => {
                const IconComponent = action.icon;
                return (
                  <button
                    key={action.title}
                    type="button"
                    onClick={action.action}
                    className={`group flex items-center rounded-xl border border-white/40 bg-white/80 p-3 text-left shadow-md transition-all duration-300 hover:-translate-y-1 hover:shadow-lg`}
                  >
                    <div className={`mr-3 flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-r ${action.accent} text-black shadow-md`}>
                      <IconComponent className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-black">{action.title}</p>
                      <p className="text-xs text-gray-600">{action.description}</p>
                    </div>
                  </button>
                );
              })}
            </div>

            <Card className="rounded-2xl border-0 bg-white/80 backdrop-blur shadow-lg">
              <CardContent className="p-4 space-y-3">
                {contactMethods.map((method) => {
                  const IconComponent = method.icon;
                  return (
                    <div key={method.title} className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-xl bg-[#f9cb07]/20 flex items-center justify-center text-[#f9cb07]">
                        <IconComponent className="h-4 w-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs uppercase tracking-wide text-gray-500">{method.title}</p>
                        {method.href ? (
                          <a href={method.href} className="text-sm font-semibold text-black hover:text-[#f9cb07] block truncate">
                            {method.value}
                          </a>
                        ) : (
                          <p className="text-sm font-semibold text-black truncate">{method.value}</p>
                        )}
                      </div>
                    </div>
                  );
                })}

                <div className="rounded-xl border border-gray-100 p-3 mt-3">
                  <div className="flex items-center text-black font-semibold text-xs mb-2">
                    <Clock className="h-4 w-4 mr-1.5 text-[#f9cb07]" />
                    Business Hours (AEDT)
                  </div>
                  <div className="space-y-1 text-xs text-gray-600">
                    {businessHours.map((slot) => (
                      <div key={slot.day} className="flex justify-between">
                        <span>{slot.day}</span>
                        <span className="font-medium">{slot.hours}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
      
      <BookingModal open={bookingOpen} onOpenChange={setBookingOpen} />
    </section>
  );
}
