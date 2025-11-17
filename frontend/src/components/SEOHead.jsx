import { Helmet } from "react-helmet-async";
import { useQuery } from "@tanstack/react-query";
import { useLocation } from "wouter";
import { useSiteSettings } from "../hooks/useSiteSettings";

export default function SEOHead({ title, description, keywords, page }) {
  const [location] = useLocation();
  const canonicalUrl = `https://codeteki.au${location === "/" ? "" : location.replace(/\/$/, "")}`;

  const { settings } = useSiteSettings();

  const { data: pageSeoData } = useQuery({
    queryKey: ["/api/seo/", page || "home"],
    queryFn: async () => {
      const params = page ? `?page=${encodeURIComponent(page)}` : "";
      const response = await fetch(`/api/seo/${params}`);
      if (!response.ok) throw new Error("Failed to fetch page SEO");
      return response.json();
    },
    staleTime: 1000 * 60 * 5,
  });

  const pageSEO = pageSeoData?.data?.seo || pageSeoData?.seo || null;

  let structuredData = settings?.structuredData || settings?.structured_data || null;
  if (structuredData && typeof structuredData === "string") {
    try {
      structuredData = JSON.parse(structuredData);
    } catch {
      structuredData = null;
    }
  }
  if (!structuredData) {
    structuredData = {
      "@context": "https://schema.org",
      "@type": "LocalBusiness",
      "name": settings?.siteName || "Codeteki",
      "description":
        settings?.siteDescription ||
        "AI-powered business solutions including chatbots, voice assistants, and custom automation. Melbourne-based AI development team.",
      "url": "https://codeteki.au",
      "telephone": settings?.contact?.primaryPhone || "+61 469 807 872",
      "email": settings?.contact?.primaryEmail || "info@codeteki.au",
      "address": {
        "@type": "PostalAddress",
        "addressLocality": settings?.contact?.address || "Melbourne",
        "addressRegion": "Victoria",
        "addressCountry": "AU",
      },
      "geo": {
        "@type": "GeoCoordinates",
        "latitude": "-37.8136",
        "longitude": "144.9631",
      },
      "openingHours": ["Mo-Fr 09:00-17:00"],
      "priceRange": "$499-$999",
      "areaServed": {
        "@type": "Country",
        "name": "Australia",
      },
      "hasOfferCatalog": {
        "@type": "OfferCatalog",
        "name": "AI Business Solutions",
        "itemListElement": [
          {
            "@type": "Offer",
            "name": "AI Chatbots",
            "price": "999",
            "priceCurrency": "AUD",
            "description": "Custom AI chatbot development and integration"
          },
          {
            "@type": "Offer", 
            "name": "Voice AI Assistants",
            "price": "899",
            "priceCurrency": "AUD",
            "description": "Intelligent voice assistant systems"
          },
          {
            "@type": "Offer",
            "name": "Website Development",
            "price": "499", 
            "priceCurrency": "AUD",
            "description": "Professional website development services"
          }
        ],
      },
    };
  }

  const cleanTitle =
    (typeof pageSEO?.metaTitle === "string" && pageSEO.metaTitle) ||
    title ||
    settings?.siteName ||
    "Codeteki - AI Business Solutions";

  const cleanDescription =
    (typeof pageSEO?.metaDescription === "string" && pageSEO.metaDescription) ||
    description ||
    settings?.siteTagline ||
    "AI-Powered Business Solutions for Modern Entrepreneurs";

  const cleanKeywords =
    (typeof pageSEO?.metaKeywords === "string" && pageSEO.metaKeywords) ||
    keywords ||
    "AI chatbot development Australia, voice assistant Melbourne, business automation, website development Melbourne";

  const ogImage = pageSEO?.ogImage || settings?.logos?.main || "https://codeteki.au/favicon.png";

  const truncatedTitle = cleanTitle.length > 60 ? cleanTitle.substring(0, 57) + "..." : cleanTitle;

  const finalTitle = truncatedTitle;
  const finalDescription = cleanDescription;
  const finalKeywords = cleanKeywords;

  return (
    <Helmet>
      <title>{finalTitle}</title>
      <meta name="description" content={finalDescription} />
      <meta name="keywords" content={finalKeywords} />
      
      {/* Open Graph tags */}
      <meta property="og:title" content={finalTitle} />
      <meta property="og:description" content={finalDescription} />
      <meta property="og:type" content="website" />
      <meta property="og:url" content={canonicalUrl} />
      <meta property="og:image" content={ogImage} />
      <meta property="og:site_name" content={settings?.siteName || "Codeteki"} />
      <meta property="og:locale" content="en_AU" />
      
      {/* Twitter Card tags */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={finalTitle} />
      <meta name="twitter:description" content={finalDescription} />
      <meta name="twitter:image" content={ogImage} />
      
      {/* Additional SEO tags */}
      <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1" />
      <meta name="author" content={settings?.siteName || "Codeteki"} />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <meta name="theme-color" content="#f9cb07" />
      <meta name="msapplication-TileColor" content="#f9cb07" />
      <meta name="apple-mobile-web-app-capable" content="yes" />
      <meta name="apple-mobile-web-app-status-bar-style" content="default" />
      
      {/* Canonical URL - ensure clean URLs without trailing slashes */}
      <link rel="canonical" href={canonicalUrl} />
      
      {/* Prevent duplicate content issues */}
      <meta name="google" content="notranslate" />
      <meta httpEquiv="Content-Language" content="en-AU" />
      
      {/* Enhanced indexing directives */}
      <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1" />
      <meta name="googlebot" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1" />
      <meta name="bingbot" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1" />
      
      {/* SEO optimizations for better crawling */}
      <meta name="googlebot" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1" />
      <meta name="bingbot" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1" />
      <meta name="language" content="en-AU" />
      <meta name="distribution" content="global" />
      <meta name="rating" content="general" />
      <meta name="revisit-after" content="3 days" />
      
      {/* Structured Data */}
      {structuredData && (
        <script type="application/ld+json">
          {JSON.stringify(structuredData)}
        </script>
      )}
      
      {/* Performance Optimization Resource Hints */}
      <link rel="preconnect" href="https://fonts.googleapis.com" />
      <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
      <link rel="preconnect" href="https://www.googletagmanager.com" />
      <link rel="dns-prefetch" href="https://www.google-analytics.com" />
      <link rel="dns-prefetch" href="https://api.openai.com" />
      
      {/* Additional meta tags for Australian businesses */}
      <meta name="geo.region" content="AU-VIC" />
      <meta name="geo.placename" content="Melbourne" />
      <meta name="geo.position" content="-37.8136;144.9631" />
      <meta name="ICBM" content="-37.8136, 144.9631" />
    </Helmet>
  );
}
