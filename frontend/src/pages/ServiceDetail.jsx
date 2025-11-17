import { useRoute } from "wouter";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { 
  CheckCircle, ArrowLeft, Phone, Mail, MapPin, Clock, 
  Users, Award, DollarSign, Headphones, Bot, Mic, Cog,
  Globe, Building, Zap
} from "lucide-react";
import { Link } from "wouter";

const serviceData = {
  "ai-workforce": {
    title: "AI Workforce Solutions",
    subtitle: "Complete AI workforce with voice agents, chatbots, and custom automation solutions",
    price: "$699",
    billing: "one-time setup",
    description: "Deploy our complete AI workforce including AI-powered voice agents and intelligent chatbots that work 24/7 to engage customers, qualify leads, and handle routine inquiries with human-like conversations.",
    heroImage: "https://images.unsplash.com/photo-1531746790731-6c087fecd65a?auto=format&fit=crop&w=1200&q=80",
    features: [
      "24/7 automated customer engagement",
      "Intelligent lead qualification",
      "Multi-language support (English + South Asian languages)",
      "Custom training on your business data",
      "Seamless integration with existing systems",
      "Real-time analytics and reporting"
    ],
    capabilities: [
      {
        icon: Bot,
        title: "Smart Chatbots",
        description: "AI chatbots that understand context and provide meaningful responses to customer inquiries"
      },
      {
        icon: Mic,
        title: "AI Voice Agents",
        description: "Natural-sounding AI voice agents for phone-based customer service and appointment booking"
      },
      {
        icon: Users,
        title: "Lead Qualification",
        description: "Automatically qualify and score leads based on your criteria before human handoff"
      },
      {
        icon: Globe,
        title: "Multi-language Support",
        description: "Communicate with customers in English and major South Asian languages"
      }
    ],
    benefits: [
      "Reduce customer response time from hours to seconds",
      "Handle unlimited simultaneous conversations",
      "Capture leads outside business hours",
      "Free up your team for high-value activities"
    ],
    support: {
      setup: "Complete setup and training within 3-5 business days",
      training: "Comprehensive training session for your team",
      maintenance: "Ongoing optimization and performance monitoring",
      local: "Melbourne-based support team available during AEDT business hours"
    }
  },
  "web-development": {
    title: "Professional Web Development",
    subtitle: "Modern, responsive websites that convert visitors into customers",
    price: "$499",
    billing: "up to 3 pages",
    description: "Get a professional website built with the latest technologies, optimized for mobile devices and search engines, designed to showcase your business and drive conversions.",
    heroImage: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&q=80",
    features: [
      "Mobile-responsive design",
      "Search engine optimization (SEO)",
      "Content management system",
      "Contact forms and lead capture",
      "Social media integration",
      "Fast loading speed optimization"
    ],
    capabilities: [
      {
        icon: Building,
        title: "Modern Design",
        description: "Contemporary designs that reflect your brand and appeal to your target audience"
      },
      {
        icon: Zap,
        title: "Performance Optimized",
        description: "Fast-loading websites optimized for search engines and user experience"
      },
      {
        icon: Users,
        title: "User-Centered",
        description: "Intuitive navigation and clear calls-to-action designed to convert visitors"
      },
      {
        icon: Cog,
        title: "Easy Management",
        description: "Simple content management system for easy updates without technical knowledge"
      }
    ],
    benefits: [
      "Professional online presence that builds trust",
      "Mobile-friendly design reaches all customers",
      "SEO optimization improves search visibility",
      "Lead capture forms grow your customer base"
    ],
    support: {
      setup: "Website delivered within 7-10 business days",
      training: "Training on content management and basic maintenance",
      maintenance: "3 months of free minor updates and bug fixes",
      local: "Melbourne-based developers with local market understanding"
    }
  },
  "automation": {
    title: "Custom Automation Solutions",
    subtitle: "Streamline repetitive tasks and boost productivity",
    price: "$899",
    billing: "per automation project",
    description: "Eliminate repetitive manual tasks with custom automation solutions tailored to your business processes, saving time and reducing errors while improving efficiency.",
    heroImage: "https://images.unsplash.com/photo-1518186285589-2f7649de83e0?auto=format&fit=crop&w=1200&q=80",
    features: [
      "Custom workflow automation",
      "Data entry and processing automation",
      "Report generation automation",
      "Email and communication automation",
      "Inventory and order management",
      "Social media automation"
    ],
    capabilities: [
      {
        icon: Cog,
        title: "Process Automation",
        description: "Automate complex business processes from start to finish with intelligent workflows"
      },
      {
        icon: Zap,
        title: "Data Processing",
        description: "Automatically process, validate, and organize data from multiple sources"
      },
      {
        icon: Mail,
        title: "Communication Automation",
        description: "Automated email sequences, reminders, and customer communications"
      },
      {
        icon: Award,
        title: "Quality Assurance",
        description: "Built-in error checking and validation to ensure reliable automation"
      }
    ],
    benefits: [
      "Save 10-20 hours per week on manual tasks",
      "Eliminate human errors in repetitive processes",
      "Scale operations without hiring additional staff",
      "Focus your team on strategic, revenue-generating activities"
    ],
    support: {
      setup: "Custom automation delivered within 2-3 weeks",
      training: "Comprehensive training on managing and monitoring automation",
      maintenance: "6 months of optimization and performance tuning",
      local: "Ongoing support from experienced automation specialists in Melbourne"
    }
  }
};

export default function ServiceDetail() {
  const [match, params] = useRoute("/services/:serviceId");
  const serviceId = params?.serviceId;
  const service = serviceId ? serviceData[serviceId] : null;

  if (!service) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Service Not Found</h1>
          <p className="text-gray-600 mb-8">The requested service could not be found.</p>
          <Link href="/">
            <Button className="bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] text-black">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Home
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  const scrollToContact = () => {
    const element = document.getElementById('contact-section');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <Link href="/">
            <Button variant="ghost" className="text-gray-600 hover:text-[#f9cb07]">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Home
            </Button>
          </Link>
        </div>
      </div>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-gray-50 to-white py-20">
        <div className="container mx-auto px-4">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="animate-fade-in-left">
              <Badge className="bg-[#f9cb07] text-black mb-4">
                {service.billing}
              </Badge>
              <h1 className="text-5xl font-bold text-black mb-6 leading-tight">
                {service.title}
              </h1>
              <p className="text-xl text-gray-600 mb-8 leading-relaxed">
                {service.subtitle}
              </p>
              <div className="flex items-center gap-6 mb-8">
                <div className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-[#f9cb07] to-[#ff6b35]">
                  {service.price}
                </div>
                <div className="text-gray-600">{service.billing}</div>
              </div>
              <div className="flex flex-col sm:flex-row gap-4">
                <Button 
                  size="lg"
                  className="bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] hover:from-[#e6b800] hover:to-[#f9cb07] text-black font-semibold px-8 py-4"
                  onClick={scrollToContact}
                >
                  <Phone className="mr-2 h-5 w-5" />
                  Get Started Today
                </Button>
                <Button 
                  variant="outline"
                  size="lg"
                  className="border-2 border-[#f9cb07] text-[#f9cb07] hover:bg-[#f9cb07] hover:text-black font-semibold px-8 py-4"
                  onClick={scrollToContact}
                >
                  Request Quote
                </Button>
              </div>
            </div>
            <div className="relative animate-float">
              <img
                src={service.heroImage}
                alt={service.title}
                className="w-full h-auto rounded-2xl shadow-2xl"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Description Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl font-bold text-black mb-6">What You Get</h2>
            <p className="text-lg text-gray-600 leading-relaxed">
              {service.description}
            </p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-black text-center mb-12">Key Features</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
            {service.features.map((feature, index) => (
              <div 
                key={index}
                className="flex items-center p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-300"
              >
                <CheckCircle className="h-6 w-6 text-[#f9cb07] mr-4 flex-shrink-0" />
                <span className="text-gray-700">{feature}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Capabilities Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-black text-center mb-12">Our Capabilities</h2>
          <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
            {service.capabilities.map((capability, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow duration-300">
                <CardHeader>
                  <div className="flex items-center mb-4">
                    <div className="bg-[#f9cb07]/10 p-3 rounded-lg mr-4">
                      <capability.icon className="h-6 w-6 text-[#f9cb07]" />
                    </div>
                    <CardTitle className="text-xl font-bold text-black">
                      {capability.title}
                    </CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-600">
                    {capability.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-black text-center mb-12">Why Choose Our Service</h2>
          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {service.benefits.map((benefit, index) => (
              <div 
                key={index}
                className="flex items-start p-6 bg-white rounded-lg shadow-sm"
              >
                <div className="bg-green-100 p-2 rounded-full mr-4 mt-1">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                </div>
                <span className="text-gray-700 leading-relaxed">{benefit}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Local Support Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-black mb-4">Affordable Local Support</h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Based in Melbourne, we provide personalized support and understand the unique needs of Australian businesses
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            <Card className="text-center hover:shadow-lg transition-shadow duration-300">
              <CardHeader>
                <Clock className="h-8 w-8 text-[#f9cb07] mx-auto mb-2" />
                <CardTitle className="text-lg">Quick Setup</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 text-sm">{service.support.setup}</p>
              </CardContent>
            </Card>
            
            <Card className="text-center hover:shadow-lg transition-shadow duration-300">
              <CardHeader>
                <Users className="h-8 w-8 text-[#f9cb07] mx-auto mb-2" />
                <CardTitle className="text-lg">Training</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 text-sm">{service.support.training}</p>
              </CardContent>
            </Card>
            
            <Card className="text-center hover:shadow-lg transition-shadow duration-300">
              <CardHeader>
                <Cog className="h-8 w-8 text-[#f9cb07] mx-auto mb-2" />
                <CardTitle className="text-lg">Maintenance</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 text-sm">{service.support.maintenance}</p>
              </CardContent>
            </Card>
            
            <Card className="text-center hover:shadow-lg transition-shadow duration-300">
              <CardHeader>
                <MapPin className="h-8 w-8 text-[#f9cb07] mx-auto mb-2" />
                <CardTitle className="text-lg">Local Team</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 text-sm">{service.support.local}</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact-section" className="py-16 bg-[#f9cb07]/5">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl font-bold text-black mb-6">Ready to Get Started?</h2>
            <p className="text-lg text-gray-600 mb-8">
              Contact us today for a free consultation and personalized quote for your {service.title.toLowerCase()}
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                size="lg"
                className="bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] hover:from-[#e6b800] hover:to-[#f9cb07] text-black font-semibold px-8 py-4"
              >
                <Phone className="mr-2 h-5 w-5" />
                Call Us Now
              </Button>
              <Button 
                variant="outline"
                size="lg"
                className="border-2 border-[#f9cb07] text-[#f9cb07] hover:bg-[#f9cb07] hover:text-black font-semibold px-8 py-4"
              >
                <Mail className="mr-2 h-5 w-5" />
                Send Message
              </Button>
            </div>
            <div className="mt-8 grid md:grid-cols-3 gap-6 text-center">
              <div>
                <Phone className="h-6 w-6 text-[#f9cb07] mx-auto mb-2" />
                <p className="text-gray-600">+61 (03) 1234 5678</p>
              </div>
              <div>
                <Mail className="h-6 w-6 text-[#f9cb07] mx-auto mb-2" />
                <p className="text-gray-600">hello@codeteki.com.au</p>
              </div>
              <div>
                <MapPin className="h-6 w-6 text-[#f9cb07] mx-auto mb-2" />
                <p className="text-gray-600">Melbourne, Victoria</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}