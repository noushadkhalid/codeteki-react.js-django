import { useMemo } from "react";
import { Link } from "wouter";
import { useQuery } from "@tanstack/react-query";
import { useSiteSettings } from "../hooks/useSiteSettings";
import { MapPin, Mail, Phone, Facebook, Twitter, Linkedin, Instagram, Youtube, Github } from "lucide-react";

// Map platform names to Lucide icons
const socialIcons = {
  facebook: Facebook,
  twitter: Twitter,
  linkedin: Linkedin,
  instagram: Instagram,
  youtube: Youtube,
  github: Github,
};

export default function Footer() {
  const currentYear = new Date().getFullYear();
  const { settings } = useSiteSettings();

  const { data: footerData } = useQuery({
    queryKey: ["/api/footer/"],
    staleTime: 1000 * 60 * 5,
  });

  const { data: servicesData } = useQuery({
    queryKey: ["/api/services/"],
    staleTime: 1000 * 60 * 5,
  });

  const footer = footerData?.data?.footer || footerData?.footer || {};
  const services = servicesData?.data?.services || servicesData?.services || [];

  const contactEmail = settings?.contact?.primaryEmail || "info@codeteki.au";
  const primaryPhone = settings?.contact?.primaryPhone || "+61 469 754 386";
  const secondaryPhone = settings?.contact?.secondaryPhone || "+61 424 538 777";
  const officeAddress = settings?.contact?.address || "Melbourne, Victoria";

  // Split services into two columns
  const serviceLinks = useMemo(() => {
    if (services.length > 0) {
      return services.map((svc) => ({
        name: svc.title,
        href: `/services#${svc.id || svc.slug}`,
      }));
    }
    return [
      { name: "AI Workforce", href: "/services" },
      { name: "Web Development", href: "/services" },
      { name: "Custom Automation", href: "/services" },
      { name: "AI Tools", href: "/ai-tools" },
      { name: "MCP Integration", href: "/services" },
      { name: "SEO Engine", href: "/services" },
    ];
  }, [services]);

  const midPoint = Math.ceil(serviceLinks.length / 2);
  const servicesCol1 = serviceLinks.slice(0, midPoint);
  const servicesCol2 = serviceLinks.slice(midPoint);

  return (
    <footer className="bg-black text-white py-12">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
          {/* Logo & Description */}
          <div className="lg:col-span-1">
            {footer.logo ? (
              <img
                src={footer.logo}
                alt={`${footer.company || "Codeteki"} Logo`}
                className="h-12 w-auto mb-4"
                loading="lazy"
                decoding="async"
                width="185"
                height="48"
              />
            ) : (
              <img
                src="/footer-logo.png"
                alt="Codeteki Logo"
                className="h-12 w-auto mb-4"
                loading="lazy"
                decoding="async"
                width="185"
                height="48"
              />
            )}
            <p className="text-gray-400 leading-relaxed text-sm mb-4">
              {footer.description || "Revolutionizing business operations through advanced AI technology and human expertise."}
            </p>
            {/* Social Links */}
            {footer.socialLinks?.length > 0 && (
              <div className="flex gap-3">
                {footer.socialLinks.map((social, idx) => {
                  const IconComponent = socialIcons[social.platform];
                  return (
                    <a
                      key={idx}
                      href={social.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-9 h-9 rounded-full bg-gray-800 hover:bg-[#f9cb07] flex items-center justify-center transition-colors"
                      title={social.label}
                    >
                      {IconComponent ? (
                        <IconComponent className="h-4 w-4 text-gray-400 hover:text-black" />
                      ) : (
                        <span className="text-xs text-gray-400">{social.platform.charAt(0).toUpperCase()}</span>
                      )}
                    </a>
                  );
                })}
              </div>
            )}
          </div>

          {/* Services Column 1 */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Services</h3>
            <ul className="space-y-2">
              {servicesCol1.map((link, idx) => (
                <li key={idx}>
                  <Link href={link.href}>
                    <span className="text-gray-400 hover:text-[#f9cb07] transition-colors cursor-pointer text-sm">
                      {link.name}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Services Column 2 */}
          <div>
            <h3 className="text-lg font-semibold mb-4 invisible" aria-hidden="true">Services</h3>
            <ul className="space-y-2">
              {servicesCol2.map((link, idx) => (
                <li key={idx}>
                  <Link href={link.href}>
                    <span className="text-gray-400 hover:text-[#f9cb07] transition-colors cursor-pointer text-sm">
                      {link.name}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/ai-tools">
                  <span className="text-gray-400 hover:text-[#f9cb07] transition-colors cursor-pointer text-sm">
                    AI Tools
                  </span>
                </Link>
              </li>
              <li>
                <Link href="/faq">
                  <span className="text-gray-400 hover:text-[#f9cb07] transition-colors cursor-pointer text-sm">
                    FAQ
                  </span>
                </Link>
              </li>
              <li>
                <Link href="/contact">
                  <span className="text-gray-400 hover:text-[#f9cb07] transition-colors cursor-pointer text-sm">
                    Contact Us
                  </span>
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact Info */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Contact Info</h3>
            <div className="space-y-3">
              <div className="flex items-start gap-2">
                <MapPin className="h-4 w-4 text-[#f9cb07] mt-0.5 flex-shrink-0" />
                <span className="text-gray-400 text-sm">{officeAddress}</span>
              </div>
              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4 text-[#f9cb07] flex-shrink-0" />
                <a
                  href={`mailto:${contactEmail}`}
                  className="text-gray-400 hover:text-[#f9cb07] transition-colors text-sm"
                >
                  {contactEmail}
                </a>
              </div>
              <div className="flex items-center gap-2">
                <Phone className="h-4 w-4 text-[#f9cb07] flex-shrink-0" />
                <a
                  href={`tel:${primaryPhone.replace(/\s/g, "")}`}
                  className="text-gray-400 hover:text-[#f9cb07] transition-colors text-sm"
                >
                  {primaryPhone}
                </a>
              </div>
              {secondaryPhone && (
                <div className="flex items-center gap-2">
                  <Phone className="h-4 w-4 text-[#f9cb07] flex-shrink-0" />
                  <a
                    href={`tel:${secondaryPhone.replace(/\s/g, "")}`}
                    className="text-gray-400 hover:text-[#f9cb07] transition-colors text-sm"
                  >
                    {secondaryPhone}
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-12 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-400 text-sm">
              © {currentYear} {footer.company || "Codeteki Digital Services"} {(footer.abn || settings?.business?.abn) ? `| ABN: ${footer.abn || settings?.business?.abn}` : ""}
            </p>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <Link href="/privacy-policy">
                <span className="text-gray-400 hover:text-[#f9cb07] transition-colors cursor-pointer text-sm">
                  Privacy Policy
                </span>
              </Link>
              <Link href="/terms-of-service">
                <span className="text-gray-400 hover:text-[#f9cb07] transition-colors cursor-pointer text-sm">
                  Terms of Service
                </span>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
