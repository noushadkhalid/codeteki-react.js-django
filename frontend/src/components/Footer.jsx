import { Link } from "wouter";
import { useQuery } from "@tanstack/react-query";
import { useSiteSettings } from "../hooks/useSiteSettings";

export default function Footer() {
  const currentYear = new Date().getFullYear();
  const { settings } = useSiteSettings();

  const { data: footerData } = useQuery({
    queryKey: ["/api/footer/"],
    queryFn: async () => {
      const response = await fetch("/api/footer/");
      if (!response.ok) {
        throw new Error("Failed to fetch footer content");
      }
      return response.json();
    },
    staleTime: 1000 * 60 * 5,
  });

  const footer = footerData?.data?.footer || footerData?.footer || {};

  const contactEmail = settings?.contact?.primaryEmail || "info@codeteki.au";
  const primaryPhone = settings?.contact?.primaryPhone || "+61 469 754 386";
  const secondaryPhone = settings?.contact?.secondaryPhone || "+61 424 538 777";
  const officeAddress = settings?.contact?.address || "Melbourne, Victoria";

  const mapLinks = (items = []) =>
    items.map((link) => ({
      name: link.title || link.name,
      href: link.url || link.link || link.href || "#",
    }));

  const footerSections = [
    {
      title: "Services",
      links: footer.links?.services ? mapLinks(footer.links.services) : [
        { name: "AI Workforce", href: "/services" },
        { name: "Web Development", href: "/services" },
        { name: "Custom Automation", href: "/services" },
        { name: "AI Tools", href: "/ai-tools" },
      ],
    },
    {
      title: "Company",
      links: footer.links?.company ? mapLinks(footer.links.company) : [
        { name: "About Us", href: "/" },
        { name: "Portfolio", href: "/ai-tools" },
        { name: "Contact", href: "/contact" },
      ],
    },
    {
      title: "Contact Info",
      links: footer.links?.contact ? mapLinks(footer.links.contact) : [
        { name: officeAddress, href: "#" },
        { name: contactEmail, href: `mailto:${contactEmail}` },
        { name: primaryPhone, href: `tel:${primaryPhone.replace(/\s/g, "")}` },
        { name: secondaryPhone, href: `tel:${secondaryPhone.replace(/\s/g, "")}` },
      ],
    },
  ];

  const scrollToSection = (sectionId) => {
    if (sectionId.startsWith('#')) {
      const element = document.getElementById(sectionId.substring(1));
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
    }
  };

  return (
    <footer className="bg-black text-white py-12">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            {footer.logo ? (
              <img
                src={footer.logo}
                alt={`${footer.company || "Codeteki"} Logo`}
                className="h-12 w-auto mb-4"
                loading="lazy"
                decoding="async"
              />
            ) : (
              <img
                src="/footer-logo.png"
                alt="Codeteki Logo"
                className="h-12 w-auto mb-4"
                loading="lazy"
                decoding="async"
              />
            )}
            <p className="text-gray-400 leading-relaxed">
              {footer.description || "Revolutionizing business operations through advanced AI technology and human expertise."}
            </p>
          </div>
          
          {footerSections.map((section, index) => (
            <div key={index}>
              <h4 className="text-lg font-semibold mb-4">{section.title}</h4>
              {section.links ? (
                <ul className="space-y-2">
                  {section.links.map((link, linkIndex) => {
                    const href = link.url || link.href || "#";
                    const isExternalProtocol = href.startsWith('mailto:') || href.startsWith('tel:') || href.startsWith('http');
                    return (
                      <li key={linkIndex}>
                        {isExternalProtocol ? (
                          <a 
                            href={href}
                            className="text-gray-400 hover:text-[#f9cb07] transition-colors"
                            target={href.startsWith('http') ? '_blank' : undefined}
                            rel={href.startsWith('http') ? 'noopener noreferrer' : undefined}
                          >
                            {link.name}
                          </a>
                        ) : (
                          <Link href={href}>
                            <span className="text-gray-400 hover:text-[#f9cb07] transition-colors cursor-pointer">
                              {link.name}
                            </span>
                          </Link>
                        )}
                      </li>
                    );
                  })}
                </ul>
              ) : (
                <div className="space-y-3">
                  {section.content?.map((item, itemIndex) => {
                    const IconComponent = item.icon;
                    return (
                      <div key={itemIndex} className="flex items-center space-x-2">
                        <IconComponent className="h-4 w-4 text-[#f9cb07]" />
                        {item.href ? (
                          <a 
                            href={item.href} 
                            className="text-gray-400 hover:text-[#f9cb07] transition-colors"
                          >
                            {item.text}
                          </a>
                        ) : (
                          <span className="text-gray-400">{item.text}</span>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          ))}
        </div>
        
        <div className="border-t border-gray-800 mt-12 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-400">
              © {currentYear} {footer.company || "Codeteki Digital Services"} {footer.abn ? `| ABN: ${footer.abn}` : null}
            </p>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <Link href="/privacy-policy">
                <span className="text-gray-400 hover:text-[#f9cb07] transition-colors cursor-pointer">
                  Privacy Policy
                </span>
              </Link>
              <Link href="/terms-of-service">
                <span className="text-gray-400 hover:text-[#f9cb07] transition-colors cursor-pointer">
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
