const measurementId = process.env.REACT_APP_GA_MEASUREMENT_ID;

// Initialize Google Analytics with performance optimization
export const initGA = () => {
  if (typeof document === 'undefined' || !measurementId) return;

  // Defer GA loading to improve initial page load
  const loadGA = () => {
    // Add Google Analytics script to the head
    const script1 = document.createElement('script');
    script1.async = true;
    script1.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
    document.head.appendChild(script1);

    // Initialize gtag
    const script2 = document.createElement('script');
    script2.innerHTML = `
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', '${measurementId}');
    `;
    document.head.appendChild(script2);
  };

  // Load GA after page is interactive with minimal impact
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      // Wait for 2 seconds after DOM is ready to ensure critical path is complete
      setTimeout(loadGA, 2000);
    });
  } else {
    // Delay GA loading by 3 seconds to prioritize critical resources
    setTimeout(loadGA, 3000);
  }
};

// Track page views - useful for single-page applications
export const trackPageView = (url) => {
  if (typeof window === 'undefined' || !window.gtag) return;
  
  if (!measurementId) return;
  
  window.gtag('config', measurementId, {
    page_path: url
  });
};

// Track events
export const trackEvent = (
  action, 
  category, 
  label, 
  value
) => {
  if (typeof window === 'undefined' || !window.gtag) return;
  
  window.gtag('event', action, {
    event_category: category,
    event_label: label,
    value: value,
  });
};

// Track business-specific events
export const trackBusinessEvent = {
  contactForm: (formType) => trackEvent('contact_form_submit', 'engagement', formType),
  serviceInquiry: (service) => trackEvent('service_inquiry', 'business', service),
  pricingView: (plan) => trackEvent('pricing_view', 'engagement', plan),
  bookingStart: () => trackEvent('booking_start', 'conversion', 'booking_modal'),
  bookingComplete: (service) => trackEvent('booking_complete', 'conversion', service),
  chatbotInteraction: () => trackEvent('chatbot_interaction', 'engagement', 'ai_assistant'),
  roiCalculatorUse: () => trackEvent('roi_calculator_use', 'tools', 'roi_calculator'),
  demoSiteVisit: (industry) => trackEvent('demo_site_visit', 'engagement', industry),
};
