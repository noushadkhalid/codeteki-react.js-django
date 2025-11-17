import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { AlertCircle, Home, ArrowLeft, Phone, Mail } from "lucide-react";
import { useLocation } from "wouter";
import SEOHead from "../components/SEOHead";

export default function NotFound() {
  const [, setLocation] = useLocation();

  const handleGoHome = () => {
    setLocation('/');
  };

  const handleGoBack = () => {
    window.history.back();
  };

  const handleContactUs = () => {
    setLocation('/contact');
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-gray-50">
      <SEOHead 
        title="404 - Page Not Found | Codeteki"
        description="The page you're looking for doesn't exist. Browse our AI business solutions or contact us for help."
        keywords="404 error, page not found, AI business solutions"
      />
      
      <Card className="w-full max-w-lg mx-4">
        <CardContent className="pt-8 pb-8">
          <div className="text-center">
            <div className="flex justify-center mb-6">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                <AlertCircle className="h-8 w-8 text-red-500" />
              </div>
            </div>
            
            <h1 className="text-3xl font-bold text-gray-900 mb-4">404 - Page Not Found</h1>
            
            <p className="text-lg text-gray-600 mb-8">
              The page you're looking for doesn't exist or has been moved.
            </p>
            
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Button 
                  onClick={handleGoHome}
                  className="bg-[#f9cb07] hover:bg-[#e6b800] text-black font-semibold"
                >
                  <Home className="mr-2 h-4 w-4" />
                  Go to Homepage
                </Button>
                
                <Button 
                  variant="outline"
                  onClick={handleGoBack}
                  className="border-gray-300 text-gray-700 hover:bg-gray-50"
                >
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Go Back
                </Button>
              </div>
              
              <Button 
                variant="outline"
                onClick={handleContactUs}
                className="w-full border-[#f9cb07] text-[#f9cb07] hover:bg-[#f9cb07] hover:text-black"
              >
                <Mail className="mr-2 h-4 w-4" />
                Contact Support
              </Button>
            </div>
            
            <div className="mt-8 pt-6 border-t border-gray-200">
              <p className="text-sm text-gray-500 mb-4">
                Looking for our AI business solutions?
              </p>
              <div className="flex flex-wrap justify-center gap-2">
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => setLocation('/services')}
                  className="text-[#f9cb07] hover:text-[#e6b800]"
                >
                  Services
                </Button>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => setLocation('/pricing')}
                  className="text-[#f9cb07] hover:text-[#e6b800]"
                >
                  Pricing
                </Button>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => setLocation('/demos')}
                  className="text-[#f9cb07] hover:text-[#e6b800]"
                >
                  Demos
                </Button>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => setLocation('/faq')}
                  className="text-[#f9cb07] hover:text-[#e6b800]"
                >
                  FAQ
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
