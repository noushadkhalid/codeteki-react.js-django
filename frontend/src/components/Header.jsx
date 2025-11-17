import { useMemo, useState } from "react";
import { useAdminCheck } from "../hooks/useAdminCheck";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Sheet, SheetContent, SheetTrigger } from "../components/ui/sheet";
import { Menu, X, ArrowRight, Calendar, Settings } from "lucide-react";
import { Link, useLocation } from "wouter";
import BookingModal from "../components/BookingModal";

export default function Header() {
  const [isOpen, setIsOpen] = useState(false);
  const [bookingOpen, setBookingOpen] = useState(false);
  const { isAdmin } = useAdminCheck();
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
    ...(isAdmin ? [{ name: 'Admin', href: '/admin' }] : []),
  ];

  return (
    <header className="bg-white/95 backdrop-blur-md shadow-sm sticky top-0 z-50 border-b border-gray-100/50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between py-4">
          <Link href="/" aria-label="Codeteki Home">
            <img
              src={logoSrc}
              alt="Codeteki - AI Business Solutions"
              className="h-12 cursor-pointer transition-transform duration-300 hover:scale-110"
              loading="eager"
              decoding="async"
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
            {isAdmin && (
              <Link href="/admin">
                <Button
                  variant="outline"
                  className="hidden md:inline-flex items-center space-x-1 bg-red-50 border-red-200 hover:bg-red-100"
                  title="Access Admin Dashboard - Manage content, SEO, users, and site settings"
                >
                  <Settings className="h-4 w-4 text-red-600" />
                  <span className="text-red-700">Admin Dashboard</span>
                  <Badge variant="destructive" className="text-xs">Settings</Badge>
                </Button>
              </Link>
            )}
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
                <Button variant="ghost" size="icon" className="md:hidden">
                  <Menu className="h-6 w-6" />
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
                  {isAdmin && (
                    <Link href="/admin">
                      <Button
                        variant="outline"
                        className="w-full justify-start bg-red-50 border-red-200 hover:bg-red-100 text-red-700"
                        onClick={() => setIsOpen(false)}
                      >
                        <Settings className="h-4 w-4 mr-2" />
                        Admin Dashboard
                      </Button>
                    </Link>
                  )}
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
