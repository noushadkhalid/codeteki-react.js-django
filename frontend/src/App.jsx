import { Switch, Route, useLocation } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { HelmetProvider } from "react-helmet-async";
import { useAnalytics } from "./hooks/use-analytics";
import { useEffect, lazy, Suspense } from "react";
import { initGA } from "./lib/analytics";
import Header from "./components/Header";
import Home from "./pages/Home";

// Lazy load UI components that use heavy dependencies (radix-ui, floating-ui)
const Toaster = lazy(() => import("./components/ui/toaster").then(m => ({ default: m.Toaster })));
const TooltipProvider = lazy(() => import("./components/ui/tooltip").then(m => ({ default: m.TooltipProvider })));

// Footer is below the fold - lazy load it
const Footer = lazy(() => import("./components/Footer"));

// Lazy load non-critical pages for code splitting
const Services = lazy(() => import("./pages/Services"));
const ServiceDetail = lazy(() => import("./pages/ServiceDetail"));
const AIToolsPage = lazy(() => import("./pages/AIToolsPage"));
const Contact = lazy(() => import("./pages/Contact"));
const Blog = lazy(() => import("./pages/Blog"));
const BlogDetail = lazy(() => import("./pages/BlogDetail"));
const FAQPage = lazy(() => import("./pages/FAQ"));
const PrivacyPolicy = lazy(() => import("./pages/PrivacyPolicy"));
const TermsOfService = lazy(() => import("./pages/TermsOfService"));
const Demos = lazy(() => import("./pages/Demos"));
const NotFound = lazy(() => import("./pages/NotFound"));

// Lazy load ChatWidget as it's not critical for initial render
const ChatWidget = lazy(() => import("./components/ChatWidget"));

// Loading fallback component
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-[50vh]">
    <div className="w-10 h-10 border-4 border-gray-200 border-t-[#f9cb07] rounded-full animate-spin"></div>
  </div>
);

function Router() {
  const [location] = useLocation();
  useAnalytics();

  // Scroll to top when route changes
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location]);

  return (
    <>
      {/* Skip Navigation Links for Accessibility */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <a href="#navigation" className="skip-link">
        Skip to navigation
      </a>
      <Header />
      <main id="main-content" tabIndex={-1}>
        <Suspense fallback={<PageLoader />}>
          <Switch>
            <Route path="/" component={Home} />
            <Route path="/services" component={Services} />
            <Route path="/services/:serviceId" component={ServiceDetail} />
            <Route path="/ai-tools" component={AIToolsPage} />
            <Route path="/demos" component={Demos} />
            <Route path="/blog" component={Blog} />
            <Route path="/blog/:slug" component={BlogDetail} />
            <Route path="/contact" component={Contact} />
            <Route path="/faq" component={FAQPage} />
            <Route path="/privacy-policy" component={PrivacyPolicy} />
            <Route path="/terms-of-service" component={TermsOfService} />
            <Route component={NotFound} />
          </Switch>
        </Suspense>
      </main>
      <Suspense fallback={<div className="bg-black h-64" />}>
        <Footer />
      </Suspense>
    </>
  );
}

function App() {
  // Initialize Google Analytics on app start
  useEffect(() => {
    initGA();
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <HelmetProvider>
        <Suspense fallback={null}>
          <TooltipProvider>
            <Suspense fallback={null}>
              <Toaster />
            </Suspense>
            <Router />
            <Suspense fallback={null}>
              <ChatWidget />
            </Suspense>
          </TooltipProvider>
        </Suspense>
      </HelmetProvider>
    </QueryClientProvider>
  );
}

export default App;
