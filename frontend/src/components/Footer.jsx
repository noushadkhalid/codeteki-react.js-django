import { useMemo } from "react";
import { Link } from "wouter";
import { useQuery } from "@tanstack/react-query";
import { useSiteSettings } from "../hooks/useSiteSettings";
import { MapPin, Mail, Phone } from "lucide-react";
import { FaFacebook, FaTwitter, FaLinkedinIn, FaInstagram, FaYoutube, FaGithub, FaTiktok, FaWhatsapp, FaPinterest, FaSnapchatGhost, FaTelegram, FaDiscord, FaReddit } from "react-icons/fa";
import { FaXTwitter } from "react-icons/fa6";

// Map platform names to brand icons with official colors
const socialIcons = {
  facebook: { icon: FaFacebook, color: "#1877F2" },
  twitter: { icon: FaTwitter, color: "#1DA1F2" },
  x: { icon: FaXTwitter, color: "#ffffff" },
  linkedin: { icon: FaLinkedinIn, color: "#0A66C2" },
  instagram: { icon: FaInstagram, color: "#E4405F" },
  youtube: { icon: FaYoutube, color: "#FF0000" },
  github: { icon: FaGithub, color: "#ffffff" },
  tiktok: { icon: FaTiktok, color: "#ffffff" },
  whatsapp: { icon: FaWhatsapp, color: "#25D366" },
  pinterest: { icon: FaPinterest, color: "#E60023" },
  snapchat: { icon: FaSnapchatGhost, color: "#FFFC00" },
  telegram: { icon: FaTelegram, color: "#0088cc" },
  discord: { icon: FaDiscord, color: "#5865F2" },
  reddit: { icon: FaReddit, color: "#FF4500" },
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
  const footerLinks = footer.links || {};

  const contactEmail = settings?.contact?.primaryEmail || "info@codeteki.au";
  const primaryPhone = settings?.contact?.primaryPhone || "+61 469 754 386";
  const secondaryPhone = settings?.contact?.secondaryPhone || "+61 424 538 777";
  const officeAddress = settings?.contact?.address || "Melbourne, Victoria";

  // Service links - use footer links if set, otherwise fall back to services API
  const serviceLinks = useMemo(() => {
    // First check if footer has custom service links
    if (footerLinks.services && footerLinks.services.length > 0) {
      return footerLinks.services.map((link) => ({
        name: link.title,
        href: link.url,
      }));
    }
    // Fall back to services from API
    if (services.length > 0) {
      return services.map((svc) => ({
        name: svc.title,
        href: `/services/${svc.id || svc.slug}`,
      }));
    }
    // Default fallback
    return [
      { name: "AI Workforce Solutions", href: "/services/ai-workforce" },
      { name: "Web Development", href: "/services/web-development" },
      { name: "Custom Automation", href: "/services/automation" },
      { name: "SEO & Digital Marketing", href: "/services/seo" },
      { name: "System Integration", href: "/services/integration" },
      { name: "AI Consulting", href: "/services/consulting" },
    ];
  }, [footerLinks.services, services]);

  // Quick links - use footer links if set, otherwise use defaults
  const quickLinks = useMemo(() => {
    if (footerLinks.company && footerLinks.company.length > 0) {
      return footerLinks.company.map((link) => ({
        name: link.title,
        href: link.url,
      }));
    }
    // Default quick links
    return [
      { name: "AI Tools", href: "/ai-tools" },
      { name: "FAQ", href: "/faq" },
      { name: "Contact Us", href: "/contact" },
    ];
  }, [footerLinks.company]);

  const midPoint = Math.ceil(serviceLinks.length / 2);
  const servicesCol1 = serviceLinks.slice(0, midPoint);
  const servicesCol2 = serviceLinks.slice(midPoint);

  return (
    <footer className="bg-black text-white py-12 min-h-[400px]">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 min-h-[280px]">
          {/* Logo & Description */}
          <div className="lg:col-span-1 min-h-[200px]">
            <div className="h-12 w-[185px] mb-4">
              {footer.logo ? (
                <img
                  src={footer.logo}
                  alt={`${footer.company || "Codeteki"} Logo`}
                  className="h-12 w-auto"
                  loading="lazy"
                  decoding="async"
                  width="185"
                  height="48"
                />
              ) : (
                <img
                  src="/static/images/navbar-logo.png"
                  alt="Codeteki Logo"
                  className="h-12 w-auto"
                  loading="lazy"
                  decoding="async"
                  width="185"
                  height="48"
                />
              )}
            </div>
            <p className="text-gray-400 leading-relaxed text-sm mb-4">
              {footer.description || "Revolutionizing business operations through advanced AI technology and human expertise."}
            </p>
            {/* Social Links with brand icons */}
            {footer.socialLinks?.length > 0 && (
              <div className="flex gap-4">
                {footer.socialLinks.map((social, idx) => {
                  const socialConfig = socialIcons[social.platform?.toLowerCase()];
                  const IconComponent = socialConfig?.icon;
                  const brandColor = socialConfig?.color || "#9ca3af";
                  return (
                    <a
                      key={idx}
                      href={social.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="transition-all duration-300 hover:scale-125 hover:opacity-80"
                      title={social.label || social.platform}
                      aria-label={`Follow us on ${social.platform}`}
                    >
                      {IconComponent ? (
                        <IconComponent size={22} style={{ color: brandColor }} />
                      ) : (
                        <span className="text-sm text-gray-400 font-bold">{social.platform?.charAt(0).toUpperCase()}</span>
                      )}
                    </a>
                  );
                })}
              </div>
            )}
          </div>

          {/* Services Column 1 */}
          <div className="min-h-[180px]">
            <h3 className="text-lg font-semibold mb-4">Services</h3>
            <ul className="space-y-2">
              {servicesCol1.map((link, idx) => (
                <li key={idx}>
                  {link.href.startsWith("http") ? (
                    <a
                      href={link.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-gray-400 hover:text-[#f9cb07] transition-colors cursor-pointer text-sm"
                    >
                      {link.name}
                    </a>
                  ) : (
                    <Link href={link.href}>
                      <span className="text-gray-400 hover:text-[#f9cb07] transition-colors cursor-pointer text-sm">
                        {link.name}
                      </span>
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          </div>

          {/* Services Column 2 */}
          <div className="min-h-[180px]">
            <h3 className="text-lg font-semibold mb-4 invisible" aria-hidden="true">Services</h3>
            <ul className="space-y-2">
              {servicesCol2.map((link, idx) => (
                <li key={idx}>
                  {link.href.startsWith("http") ? (
                    <a
                      href={link.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-gray-400 hover:text-[#f9cb07] transition-colors cursor-pointer text-sm"
                    >
                      {link.name}
                    </a>
                  ) : (
                    <Link href={link.href}>
                      <span className="text-gray-400 hover:text-[#f9cb07] transition-colors cursor-pointer text-sm">
                        {link.name}
                      </span>
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          </div>

          {/* Quick Links */}
          <div className="min-h-[180px]">
            <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2">
              {quickLinks.map((link, idx) => (
                <li key={idx}>
                  {link.href.startsWith("http") ? (
                    <a
                      href={link.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-gray-400 hover:text-[#f9cb07] transition-colors cursor-pointer text-sm"
                    >
                      {link.name}
                    </a>
                  ) : (
                    <Link href={link.href}>
                      <span className="text-gray-400 hover:text-[#f9cb07] transition-colors cursor-pointer text-sm">
                        {link.name}
                      </span>
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          </div>

          {/* Contact Info */}
          <div className="min-h-[180px]">
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
