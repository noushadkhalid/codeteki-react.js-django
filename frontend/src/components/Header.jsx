import { useMemo, useState } from "react";
import { Button } from "../components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "../components/ui/sheet";
import { Menu, ArrowRight, Calendar } from "lucide-react";
import { Link, useLocation } from "wouter";
import BookingModal from "../components/BookingModal";

export default function Header() {
  const [isOpen, setIsOpen] = useState(false);
  const [bookingOpen, setBookingOpen] = useState(false);
  const [location] = useLocation();
  const logoSrc = useMemo(
    () => `${process.env.PUBLIC_URL || ""}/navbar-logo.png`,
    []
  );

  const navigation = [
    { name: 'Home', href: '/' },
    { name: 'Services', href: '/services' },
    { name: 'AI Tools', href: '/ai-tools' },
    { name: 'Demos', href: '/demos' },
    { name: 'FAQ', href: '/faq' },
    { name: 'Contact', href: '/contact' },
  ];

  return (
    <header className="bg-white/95 backdrop-blur-md shadow-sm sticky top-0 z-50 border-b border-gray-100/50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between py-4">
          <Link href="/" aria-label="Codeteki Home">
            <img
              src={logoSrc}
              alt="Codeteki - AI Business Solutions"
              className="h-12 w-auto cursor-pointer transition-transform duration-300 hover:scale-110"
              loading="eager"
              decoding="async"
              width="93"
              height="48"
              fetchpriority="high"
            />
          </Link>
          
          <nav id="navigation" className="hidden md:flex space-x-8">
            {navigation.map((item, index) => (
              <Link key={item.name} href={item.href}>
                <button
                  className={`relative font-medium transition-all duration-300 transform hover:scale-105 group ${
                    location === item.href ? 'text-[#f9cb07]' : 'text-gray-700 hover:text-[#f9cb07]'
                  }`}
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  {item.name}
                  <span className={`absolute bottom-0 left-0 h-0.5 bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] transition-all duration-300 ${
                    location === item.href ? 'w-full' : 'w-0 group-hover:w-full'
                  }`}></span>
                </button>
              </Link>
            ))}
          </nav>

          <div className="flex items-center space-x-4">
            <Button
              onClick={() => setBookingOpen(true)}
              className="group bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] hover:from-[#e6b800] hover:to-[#f9cb07] text-black font-semibold hidden md:inline-flex transition-all duration-300 transform hover:scale-105 hover:shadow-lg btn-animated"
            >
              <Calendar className="w-4 h-4 mr-2" />
              <span className="transform group-hover:translate-x-1 transition-transform duration-300">Book Call</span>
              <ArrowRight className="ml-2 h-4 w-4 transform group-hover:translate-x-1 transition-transform duration-300" />
            </Button>
            
            <Sheet open={isOpen} onOpenChange={setIsOpen}>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="md:hidden" aria-label="Open navigation menu">
                  <Menu className="h-6 w-6" />
                  <span className="sr-only">Menu</span>
                </Button>
              </SheetTrigger>
              <SheetContent side="right" className="w-[300px] sm:w-[400px]">
                <div className="flex flex-col space-y-4 mt-8">
                  {navigation.map((item) => (
                    <Link key={item.name} href={item.href}>
                      <button
                        onClick={() => setIsOpen(false)}
                        className="text-left text-lg font-medium text-gray-700 hover:text-[#f9cb07] transition-colors w-full"
                      >
                        {item.name}
                      </button>
                    </Link>
                  ))}
                  <Button
                    className="bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] hover:from-[#e6b800] hover:to-[#f9cb07] text-black font-semibold mt-4"
                    onClick={() => {
                      setBookingOpen(true);
                      setIsOpen(false);
                    }}
                  >
                    <Calendar className="w-4 h-4 mr-2" />
                    Book Call
                  </Button>
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </div>
      
      <BookingModal open={bookingOpen} onOpenChange={setBookingOpen} />
    </header>
  );
}
