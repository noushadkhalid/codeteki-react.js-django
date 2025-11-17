import React, { useEffect } from "react";
import { Link } from "wouter";
import { Button } from "../components/ui/button";
import { Home, ArrowLeft, Search, Compass, Mail } from "lucide-react";
import SEOHead from "../components/SEOHead";

export default function NotFound() {
  useEffect(() => {
    document.title = "404 - Page Not Found | Codeteki";
  }, []);

  const suggestions = [
    { title: "AI Workforce", href: "/services#ai-workforce" },
    { title: "Custom Automation", href: "/services#automation" },
    { title: "AI Tools Gallery", href: "/ai-tools" },
    { title: "FAQ", href: "/faq" },
  ];

  return (
    <>
      <SEOHead
        title="404 - Page Not Found"
        description="Sorry, the page you are looking for could not be found. Return to Codeteki's homepage or explore our AI services."
        page="/404"
      />

      <section className="relative min-h-screen overflow-hidden bg-[#f7f8fb]">
        <div className="absolute inset-0">
          <div className="absolute -top-32 left-1/2 h-[400px] w-[400px] -translate-x-1/2 rounded-full bg-[#f9cb07]/25 blur-[140px]" />
          <div className="absolute bottom-10 right-10 h-[300px] w-[300px] rounded-full bg-[#c7d2fe]/30 blur-[160px]" />
        </div>

        <div className="relative flex min-h-screen flex-col items-center justify-center px-6 py-16">
          <div className="max-w-3xl w-full bg-white/80 backdrop-blur-lg rounded-[32px] p-10 shadow-[0_35px_120px_rgba(15,23,42,0.12)] text-center border border-white/70">
            <div className="inline-flex items-center gap-3 text-sm font-semibold text-[#f9cb07] uppercase tracking-[0.4em]">
              <Compass className="h-4 w-4" />
              Lost in the stack
            </div>
            <h1 className="mt-6 text-7xl font-black text-[#0f172a] tracking-tight">404</h1>
            <p className="mt-3 text-2xl font-semibold text-[#0f172a]">Page Not Found</p>
            <p className="mt-3 text-gray-600 px-4">
              The Codeteki page you were hunting for doesn’t live here anymore. Try one of our popular destinations or drop us a note—our team responds fast.
            </p>

            <div className="mt-8 grid gap-4 sm:grid-cols-3">
              <Link href="/">
                <Button className="w-full h-12 rounded-2xl bg-[#f9cb07] text-black font-semibold hover:bg-[#ffcd3c]">
                  <Home className="mr-2 h-4 w-4" />
                  Homepage
                </Button>
              </Link>
              <Link href="/services">
                <Button variant="outline" className="w-full h-12 rounded-2xl">
                  <Search className="mr-2 h-4 w-4" />
                  Services
                </Button>
              </Link>
              <Link href="/contact">
                <Button variant="outline" className="w-full h-12 rounded-2xl">
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Contact
                </Button>
              </Link>
            </div>

            <div className="mt-10 bg-gray-50 rounded-2xl p-6">
              <p className="text-sm font-semibold uppercase tracking-[0.25em] text-gray-500 mb-4">Popular Links</p>
              <div className="grid gap-3 sm:grid-cols-2">
                {suggestions.map((item) => (
                  <Link
                    key={item.title}
                    href={item.href}
                    className="block rounded-xl border border-[#e4e7ec] bg-white py-3 px-4 text-left text-sm font-semibold text-[#0f172a] hover:border-[#f9cb07] hover:text-[#f9cb07] transition-colors"
                  >
                    {item.title}
                  </Link>
                ))}
              </div>
            </div>

            <div className="mt-6 text-sm text-gray-500 flex items-center justify-center gap-2">
              <Mail className="h-4 w-4" />
              Stuck? Email{" "}
              <a
                className="font-semibold text-[#0f172a] hover:text-[#f9cb07]"
                href="mailto:info@codeteki.au"
              >
                info@codeteki.au
              </a>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
