import { useMemo, useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle 
} from "../components/ui/dialog";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Switch } from "../components/ui/switch";
import { 
  Plus, 
  Pencil, 
  Trash2, 
  ExternalLink, 
  Users, 
  MessageSquare, 
  Settings,
  DollarSign,
  TrendingUp,
  Star,
  Search,
  CheckCircle,
  XCircle,
  AlertCircle,
  LogOut,
  Mail,
  Edit,
  Briefcase,
  Cpu,
  Globe
} from "lucide-react";
import { useToast } from "../hooks/use-toast";
import SEODashboard from "../pages/SEODashboard";
import AdminLogin from "../components/AdminLogin";

function AdminDashboard() {
  const [editingType, setEditingType] = useState(null);
  const [editingItem, setEditingItem] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Submit handlers
  const handleSubmitSetting = async (data) => {
    try {
      const method = editingItem ? 'PATCH' : 'POST';
      const url = editingItem ? `/api/admin/site-settings/${editingItem.id}` : '/api/admin/site-settings';
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      if (response.ok) {
        setIsDialogOpen(false);
        setEditingItem(null);
        setEditingType(null);
        toast({ title: "Success", description: "Setting saved successfully" });
        queryClient.invalidateQueries({ queryKey: ['/api/settings/'] });
      }
    } catch (error) {
      toast({ title: "Error", description: "Failed to save setting", variant: "destructive" });
    }
  };

  const handleSubmitPricing = async (data) => {
    try {
      const method = editingItem ? 'PATCH' : 'POST';
      const url = editingItem ? `/api/admin/pricing-plans/${editingItem.id}` : '/api/admin/pricing-plans';
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      if (response.ok) {
        setIsDialogOpen(false);
        setEditingItem(null);
        setEditingType(null);
        toast({ title: "Success", description: "Pricing plan saved successfully" });
        queryClient.invalidateQueries({ queryKey: ['/api/pricing-plans'] });
      }
    } catch (error) {
      toast({ title: "Error", description: "Failed to save pricing plan", variant: "destructive" });
    }
  };

  const handleSubmitService = async (data) => {
    try {
      const method = editingItem ? 'PATCH' : 'POST';
      const url = editingItem ? `/api/admin/services/${editingItem.id}` : '/api/admin/services';
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      if (response.ok) {
        setIsDialogOpen(false);
        setEditingItem(null);
        setEditingType(null);
        toast({ title: "Success", description: "Service saved successfully" });
        queryClient.invalidateQueries({ queryKey: ['/api/services'] });
      }
    } catch (error) {
      toast({ title: "Error", description: "Failed to save service", variant: "destructive" });
    }
  };

  const handleSubmitAITool = async (data) => {
    try {
      const method = editingItem ? 'PATCH' : 'POST';
      const url = editingItem ? `/api/admin/ai-tools/${editingItem.id}` : '/api/admin/ai-tools';
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      if (response.ok) {
        setIsDialogOpen(false);
        setEditingItem(null);
        setEditingType(null);
        toast({ title: "Success", description: "AI Tool saved successfully" });
        queryClient.invalidateQueries({ queryKey: ['/api/ai-tools'] });
      }
    } catch (error) {
      toast({ title: "Error", description: "Failed to save AI tool", variant: "destructive" });
    }
  };

  const handleSubmitDemoSite = async (data) => {
    try {
      const method = editingItem ? 'PATCH' : 'POST';
      const url = editingItem ? `/api/admin/demo-sites/${editingItem.id}` : '/api/admin/demo-sites';
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      if (response.ok) {
        setIsDialogOpen(false);
        setEditingItem(null);
        setEditingType(null);
        toast({ title: "Success", description: "Demo site saved successfully" });
        queryClient.invalidateQueries({ queryKey: ['/api/demo-sites'] });
      }
    } catch (error) {
      toast({ title: "Error", description: "Failed to save demo site", variant: "destructive" });
    }
  };

  // Data queries - Always call these hooks regardless of auth state
  const { data: services, isLoading: servicesLoading } = useQuery({
    queryKey: ["/api/services"],
    retry: false,
    enabled: isAuthenticated,
  });

  const { data: aiTools, isLoading: aiToolsLoading } = useQuery({
    queryKey: ["/api/ai-tools"],
    retry: false,
    enabled: isAuthenticated,
  });

  const { data: pricingPlans, isLoading: pricingLoading } = useQuery({
    queryKey: ["/api/pricing-plans"],
    retry: false,
    enabled: isAuthenticated,
  });

  const { data: testimonials, isLoading: testimonialsLoading } = useQuery({
    queryKey: ["/api/testimonials"],
    retry: false,
    enabled: isAuthenticated,
  });

  const { data: contactInquiries, isLoading: contactLoading } = useQuery({
    queryKey: ["/api/contact-inquiries"],
    retry: false,
    enabled: isAuthenticated,
  });

  const { data: demoSites, isLoading: demoSitesLoading } = useQuery({
    queryKey: ["/api/demo-sites"],
    retry: false,
    enabled: isAuthenticated,
  });

  const { data: siteSettingsData, isLoading: settingsLoading } = useQuery({
    queryKey: ["/api/settings/"],
    retry: false,
    enabled: isAuthenticated,
  });
  const siteSettings = useMemo(() => {
    const settingsObj = siteSettingsData?.data?.settings || siteSettingsData?.settings;
    if (!settingsObj) return [];
    return Object.entries(settingsObj).map(([key, value]) => ({
      key,
      value,
    }));
  }, [siteSettingsData]);

  const { data: chatConversations, isLoading: chatLoading } = useQuery({
    queryKey: ["/api/admin/chat-conversations"],
    retry: false,
    enabled: isAuthenticated,
  });

  // Delete handler for all content types
  const handleDelete = async (type, id) => {
    if (!window.confirm('Are you sure you want to delete this item?')) return;
    
    try {
      const endpoints = {
        'inquiry': '/api/admin/contact-inquiries',
        'service': '/api/admin/services',
        'tool': '/api/admin/ai-tools',
        'demo': '/api/admin/demo-sites',
        'pricing': '/api/admin/pricing-plans',
        'setting': '/api/admin/site-settings'
      };
      
      const response = await fetch(`${endpoints[type]}/${id}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        toast({
          title: "Deleted",
          description: `${type} deleted successfully`,
        });
        // Refresh the data
        window.location.reload();
      } else {
        throw new Error('Delete failed');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to delete ${type}`,
        variant: "destructive",
      });
    }
  };

  // Check admin authentication status
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const response = await fetch('/api/admin/status');
        const data = await response.json();
        setIsAuthenticated(data.isAdmin || false);
      } catch (error) {
        setIsAuthenticated(false);
      } finally {
        setIsCheckingAuth(false);
      }
    };

    checkAuthStatus();
  }, []);

  // Handle admin logout
  const handleLogout = async () => {
    try {
      const response = await fetch('/api/admin/logout', {
        method: 'POST',
      });
      
      if (response.ok) {
        // Invalidate admin status queries to refresh header navigation
        queryClient.invalidateQueries({ queryKey: ["/api/admin/status"] });
        queryClient.invalidateQueries({ queryKey: ["/api/auth/role"] });
        
        setIsAuthenticated(false);
        toast({
          title: "Logged Out",
          description: "You have been logged out successfully",
        });
      }
    } catch (error) {
      toast({
        title: "Logout Error",
        description: "Failed to logout properly",
        variant: "destructive",
      });
    }
  };

  // Show login form if not authenticated
  if (isCheckingAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-[#f9cb07]"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AdminLogin onLoginSuccess={() => setIsAuthenticated(true)} />;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-black">Admin Dashboard</h1>
          <p className="text-gray-600 mt-2">Manage your business content and settings</p>
        </div>
        <Button 
          onClick={handleLogout}
          variant="outline"
          className="text-red-600 border-red-600 hover:bg-red-50"
        >
          <LogOut className="h-4 w-4 mr-2" />
          Logout
        </Button>
      </div>

      <Tabs defaultValue="inquiries" className="space-y-6">
        <TabsList className="grid w-full grid-cols-8">
          <TabsTrigger value="inquiries">Contact Inquiries</TabsTrigger>
          <TabsTrigger value="leads">Chat Leads</TabsTrigger>
          <TabsTrigger value="services">Services</TabsTrigger>
          <TabsTrigger value="ai-tools">AI Tools</TabsTrigger>
          <TabsTrigger value="pricing">Pricing</TabsTrigger>
          <TabsTrigger value="demo-sites">Demo Sites</TabsTrigger>
          <TabsTrigger value="seo">SEO</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        {/* Contact Inquiries Tab */}
        <TabsContent value="inquiries" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Mail className="h-5 w-5" />
                  Contact Inquiries
                </div>
                <Button
                  onClick={() => {
                    setEditingType('inquiry');
                    setEditingItem(null);
                    setIsDialogOpen(true);
                  }}
                  size="sm"
                  className="flex items-center gap-2"
                >
                  <Plus className="h-4 w-4" />
                  Add Inquiry
                </Button>
              </CardTitle>
              <CardDescription>
                Manage customer inquiries and contact requests
              </CardDescription>
            </CardHeader>
            <CardContent>
              {contactLoading ? (
                <div className="flex justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : contactInquiries && contactInquiries.length > 0 ? (
                <div className="space-y-4">
                  {contactInquiries.map((inquiry) => (
                    <div key={inquiry.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-medium">{inquiry.name}</h3>
                            <Badge variant={inquiry.status === 'new' ? 'destructive' : 'default'}>
                              {inquiry.status}
                            </Badge>
                          </div>
                          <p className="text-sm text-gray-600">{inquiry.email}</p>
                          {inquiry.phone && (
                            <p className="text-sm text-gray-600">{inquiry.phone}</p>
                          )}
                          {inquiry.company && (
                            <p className="text-sm font-medium text-gray-700">{inquiry.company}</p>
                          )}
                        </div>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setEditingType('inquiry');
                              setEditingItem(inquiry);
                              setIsDialogOpen(true);
                            }}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDelete('inquiry', inquiry.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      <p className="text-sm text-gray-700 mb-3">{inquiry.message}</p>
                      <div className="flex justify-between items-center text-xs text-gray-500">
                        <span>{new Date(inquiry.createdAt).toLocaleDateString()}</span>
                        <span>Updated: {new Date(inquiry.updatedAt).toLocaleDateString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Mail className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-500">No contact inquiries yet</p>
                  <p className="text-sm text-gray-400 mt-1">
                    Customer inquiries will appear here
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Services Tab */}
        <TabsContent value="services" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Briefcase className="h-5 w-5" />
                  Services Management
                </div>
                <Button
                  onClick={() => {
                    setEditingType('service');
                    setEditingItem(null);
                    setIsDialogOpen(true);
                  }}
                  size="sm"
                  className="flex items-center gap-2"
                >
                  <Plus className="h-4 w-4" />
                  Add Service
                </Button>
              </CardTitle>
              <CardDescription>
                Manage your business services and offerings
              </CardDescription>
            </CardHeader>
            <CardContent>
              {servicesLoading ? (
                <div className="flex justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : services && services.length > 0 ? (
                <div className="space-y-4">
                  {services.map((service) => (
                    <div key={service.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h3 className="font-medium text-lg">{service.title}</h3>
                          <p className="text-sm text-gray-600 mt-1">{service.description}</p>
                          <div className="flex flex-wrap gap-2 mt-2">
                            {service.features && service.features.map((feature, index) => (
                              <Badge key={index} variant="outline" className="text-xs">
                                {feature}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setEditingType('service');
                              setEditingItem(service);
                              setIsDialogOpen(true);
                            }}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDelete('service', service.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Briefcase className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-500">No services configured</p>
                  <p className="text-sm text-gray-400 mt-1">
                    Business services will appear here
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Services Tab */}
        <TabsContent value="services" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Services Management</CardTitle>
              <CardDescription>
                Manage your business services
              </CardDescription>
            </CardHeader>
            <CardContent>
              {servicesLoading ? (
                <div className="flex justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : services && services.length > 0 ? (
                <div className="space-y-4">
                  {services.map((service) => (
                    <div key={service.id} className="border rounded-lg p-4">
                      <h3 className="font-semibold mb-2">{service.name}</h3>
                      <p className="text-sm text-gray-600">{service.description}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No services found.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Tools Tab */}
        <TabsContent value="ai-tools" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Cpu className="h-5 w-5" />
                  AI Tools Management
                </div>
                <Button
                  onClick={() => {
                    setEditingType('ai-tool');
                    setEditingItem(null);
                    setIsDialogOpen(true);
                  }}
                  className="bg-yellow-500 hover:bg-yellow-600 text-black"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add AI Tool
                </Button>
              </CardTitle>
              <CardDescription>
                Manage AI tools catalog
              </CardDescription>
            </CardHeader>
            <CardContent>
              {aiToolsLoading ? (
                <div className="flex justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : aiTools && aiTools.length > 0 ? (
                <div className="space-y-4">
                  {aiTools.map((tool) => (
                    <div key={tool.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-semibold">{tool.name}</h3>
                        <div className="flex items-center gap-2">
                          <div className="flex gap-2">
                            {tool.isFree && <Badge className="bg-green-100 text-green-800">Free</Badge>}
                            {tool.requiresCredits && <Badge className="bg-blue-100 text-blue-800">Credits</Badge>}
                            {tool.premium && <Badge className="bg-purple-100 text-purple-800">Premium</Badge>}
                            {tool.comingSoon && <Badge className="bg-gray-100 text-gray-800">Coming Soon</Badge>}
                          </div>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setEditingType('ai-tool');
                              setEditingItem(tool);
                              setIsDialogOpen(true);
                            }}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDelete('ai-tool', tool.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      <p className="text-sm text-gray-600">{tool.description}</p>
                      {tool.url && (
                        <a
                          href={tool.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-blue-600 hover:underline"
                        >
                          Visit Tool →
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Cpu className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-500">No AI tools found</p>
                  <p className="text-sm text-gray-400 mt-1">
                    AI tools and utilities will appear here
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Pricing Tab */}
        <TabsContent value="pricing" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <DollarSign className="h-5 w-5" />
                  Pricing Plans
                </div>
                <Button
                  onClick={() => {
                    setEditingType('pricing');
                    setEditingItem(null);
                    setIsDialogOpen(true);
                  }}
                  className="bg-yellow-500 hover:bg-yellow-600 text-black"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Pricing Plan
                </Button>
              </CardTitle>
              <CardDescription>
                Manage your service pricing and plans
              </CardDescription>
            </CardHeader>
            <CardContent>
              {pricingLoading ? (
                <div className="flex justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : pricingPlans && pricingPlans.length > 0 ? (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {pricingPlans.map((plan) => (
                    <div key={plan.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-semibold">{plan.name}</h3>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setEditingType('pricing');
                              setEditingItem(plan);
                              setIsDialogOpen(true);
                            }}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDelete('pricing', plan.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      <div className="mb-2">
                        <div className="text-2xl font-bold text-yellow-600">
                          {plan.currency} ${plan.price}
                        </div>
                        {plan.originalPrice && plan.originalPrice !== plan.price && (
                          <div className="text-sm text-gray-500 line-through">
                            Original: {plan.currency} ${plan.originalPrice}
                          </div>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{plan.description}</p>
                      <Badge className={plan.isActive ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"}>
                        {plan.isActive ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <DollarSign className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-500">No pricing plans found</p>
                  <p className="text-sm text-gray-400 mt-1">
                    Service pricing and plans will appear here
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Demo Sites Tab */}
        <TabsContent value="demo-sites" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Globe className="h-5 w-5" />
                  Demo Sites Management
                </div>
                <Button
                  onClick={() => {
                    setEditingType('demo-site');
                    setEditingItem(null);
                    setIsDialogOpen(true);
                  }}
                  className="bg-yellow-500 hover:bg-yellow-600 text-black"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Demo Site
                </Button>
              </CardTitle>
              <CardDescription>
                Manage your industry demo showcases
              </CardDescription>
            </CardHeader>
            <CardContent>
              {demoSitesLoading ? (
                <div className="flex justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : demoSites && demoSites.length > 0 ? (
                <div className="grid gap-4 md:grid-cols-2">
                  {demoSites.map((demo) => (
                    <div key={demo.id} className="border rounded-lg p-4 relative">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h3 className="font-semibold text-lg">{demo.title}</h3>
                            <Badge variant="outline" className="text-xs">
                              {demo.industry}
                            </Badge>
                          </div>
                          <p className="text-sm text-gray-600 mb-3">{demo.description}</p>
                          
                          <div className="flex items-center gap-2 mb-2">
                            <Badge className={demo.status === 'Live Demo' ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"}>
                              {demo.status}
                            </Badge>
                            {demo.featured && (
                              <Badge className="bg-yellow-100 text-yellow-800">
                                Featured
                              </Badge>
                            )}
                          </div>
                          
                          {demo.url && demo.url !== '#' && (
                            <a
                              href={demo.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sm text-blue-600 hover:underline inline-flex items-center gap-1"
                            >
                              View Demo <ExternalLink className="h-3 w-3" />
                            </a>
                          )}
                        </div>
                        
                        <div className="flex items-center gap-1 ml-4">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setEditingType('demo-site');
                              setEditingItem(demo);
                              setIsDialogOpen(true);
                            }}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDelete('demo-site', demo.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      
                      <div className="text-xs text-gray-500">
                        Order: {demo.sortOrder}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Globe className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-500">No demo sites found</p>
                  <p className="text-sm text-gray-400 mt-1">
                    Industry demo showcases will appear here
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* SEO Tab */}
        <TabsContent value="seo" className="space-y-6">
          <SEODashboard />
        </TabsContent>

        {/* Chat Leads Tab */}
        <TabsContent value="leads" className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <MessageSquare className="h-8 w-8 text-blue-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Total Conversations</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {chatConversations?.length || 0}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <Users className="h-8 w-8 text-green-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Qualified Leads</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {chatConversations?.filter((c) => c.leadQuality === 'high' || c.leadQuality === 'medium').length || 0}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <TrendingUp className="h-8 w-8 text-purple-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Conversion Rate</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {chatConversations?.length > 0 
                        ? Math.round((chatConversations.filter((c) => c.leadQuality === 'high').length / chatConversations.length) * 100)
                        : 0}%
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Chat Leads Overview */}
          <Card>
            <CardHeader>
              <CardTitle>Chat Leads Overview</CardTitle>
              <CardDescription>
                Summarized view of chat conversations with lead potential
              </CardDescription>
            </CardHeader>
            <CardContent>
              {chatLoading ? (
                <div className="flex justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : chatConversations && chatConversations.length > 0 ? (
                <div className="space-y-4">
                  {chatConversations.map((conversation, index) => (
                    <div key={conversation.sessionId} className="border rounded-lg p-4 hover:bg-gray-50">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <MessageSquare className="h-5 w-5 text-blue-500" />
                          <div>
                            <h3 className="font-medium text-gray-900">
                              Session {conversation.sessionId?.slice(-6) || index + 1}
                            </h3>
                            <p className="text-sm text-gray-500">
                              {new Date(conversation.createdAt || Date.now()).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-4">
                          <div className="text-right">
                            <p className="text-sm text-gray-600">
                              <span className="font-medium">Contact:</span>{' '}
                              {(() => {
                                try {
                                  const leadData = typeof conversation.leadData === 'string' 
                                    ? JSON.parse(conversation.leadData) 
                                    : conversation.leadData;
                                  return leadData?.email || leadData?.phone || 'Not provided';
                                } catch {
                                  return 'Not provided';
                                }
                              })()}
                            </p>
                            <p className="text-sm text-gray-600">
                              <span className="font-medium">Interest:</span>{' '}
                              {(() => {
                                try {
                                  const leadData = typeof conversation.leadData === 'string' 
                                    ? JSON.parse(conversation.leadData) 
                                    : conversation.leadData;
                                  return leadData?.interest || 'General inquiry';
                                } catch {
                                  return 'General inquiry';
                                }
                              })()}
                            </p>
                          </div>
                          
                          <Badge 
                            variant={
                              conversation.leadQuality === 'high' ? 'destructive' : 
                              conversation.leadQuality === 'medium' ? 'default' : 'secondary'
                            }
                          >
                            {conversation.leadQuality === 'high' ? 'High Quality' :
                             conversation.leadQuality === 'medium' ? 'Medium Quality' : 'Low Quality'}
                          </Badge>
                          
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              // Set selected conversation for modal
                              setEditingType('chat');
                              setEditingItem(conversation);
                              setIsDialogOpen(true);
                            }}
                            className="flex items-center gap-2"
                          >
                            <ExternalLink className="h-4 w-4" />
                            View Chat
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-500">No chat leads yet</p>
                  <p className="text-sm text-gray-400 mt-1">
                    Chat conversations with potential customers will appear here
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Chat Conversation Modal */}
          <Dialog open={isDialogOpen && editingType === 'chat'} onOpenChange={setIsDialogOpen}>
            <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Chat Conversation Details</DialogTitle>
                <DialogDescription>
                  Full conversation history and lead information
                </DialogDescription>
              </DialogHeader>
              
              {editingItem && (
                <div className="space-y-4">
                  {/* Lead Information */}
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="font-medium mb-3">Lead Information</h3>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="font-medium">Session ID:</span>
                        <p>{editingItem.sessionId}</p>
                      </div>
                      <div>
                        <span className="font-medium">Quality:</span>
                        <Badge className="ml-2" variant={
                          editingItem.leadQuality === 'high' ? 'destructive' : 
                          editingItem.leadQuality === 'medium' ? 'default' : 'secondary'
                        }>
                          {editingItem.leadQuality || 'Unknown'}
                        </Badge>
                      </div>
                      {(() => {
                        try {
                          const leadData = typeof editingItem.leadData === 'string' 
                            ? JSON.parse(editingItem.leadData) 
                            : editingItem.leadData || {};
                          
                          return (
                            <>
                              {leadData.email && (
                                <div>
                                  <span className="font-medium">Email:</span>
                                  <p>{leadData.email}</p>
                                </div>
                              )}
                              {leadData.phone && (
                                <div>
                                  <span className="font-medium">Phone:</span>
                                  <p>{leadData.phone}</p>
                                </div>
                              )}
                              {leadData.interest && (
                                <div>
                                  <span className="font-medium">Interest:</span>
                                  <p>{leadData.interest}</p>
                                </div>
                              )}
                              {leadData.budget && (
                                <div>
                                  <span className="font-medium">Budget:</span>
                                  <p>{leadData.budget}</p>
                                </div>
                              )}
                              {leadData.company && (
                                <div>
                                  <span className="font-medium">Company:</span>
                                  <p>{leadData.company}</p>
                                </div>
                              )}
                              {leadData.business && (
                                <div>
                                  <span className="font-medium">Business:</span>
                                  <p>{leadData.business}</p>
                                </div>
                              )}
                            </>
                          );
                        } catch {
                          return null;
                        }
                      })()}
                    </div>
                  </div>

                  {/* Conversation History */}
                  <div>
                    <h3 className="font-medium mb-3">Conversation History</h3>
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                      {(() => {
                        try {
                          const messages = typeof editingItem.messages === 'string' 
                            ? JSON.parse(editingItem.messages) 
                            : editingItem.messages || [];
                          
                          return messages.length > 0 ? (
                            messages.map((message, index) => (
                              <div
                                key={index}
                                className={`p-3 rounded-lg ${
                                  message.role === 'user' 
                                    ? 'bg-blue-50 border-l-4 border-blue-500' 
                                    : 'bg-gray-50 border-l-4 border-gray-500'
                                }`}
                              >
                                <div className="flex items-center gap-2 mb-1">
                                  <Badge variant={message.role === 'user' ? 'default' : 'outline'}>
                                    {message.role === 'user' ? 'Customer' : 'AI Assistant'}
                                  </Badge>
                                  <span className="text-xs text-gray-500">
                                    {new Date(message.timestamp || Date.now()).toLocaleTimeString()}
                                  </span>
                                </div>
                                <p className="text-sm">{message.content}</p>
                              </div>
                            ))
                          ) : (
                            <p className="text-gray-500 text-center py-4">
                              {editingItem.summary || "No conversation history available"}
                            </p>
                          );
                        } catch {
                          return (
                            <p className="text-gray-500 text-center py-4">
                              {editingItem.summary || "No conversation history available"}
                            </p>
                          );
                        }
                      })()}
                    </div>
                  </div>
                </div>
              )}
            </DialogContent>
          </Dialog>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  Site Settings
                </div>
                <Button
                  onClick={() => {
                    setEditingType('setting');
                    setEditingItem(null);
                    setIsDialogOpen(true);
                  }}
                  size="sm"
                  className="flex items-center gap-2"
                >
                  <Plus className="h-4 w-4" />
                  Add Setting
                </Button>
              </CardTitle>
              <CardDescription>
                Manage your website configuration and business information - these connect directly to the frontend
              </CardDescription>
            </CardHeader>
            <CardContent>
              {settingsLoading ? (
                <div className="flex justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : siteSettings && siteSettings.length > 0 ? (
                <div className="space-y-4">
                  {siteSettings.map((setting) => (
                    <div key={setting.id || setting.key} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-medium text-sm">{setting.key}</h3>
                          </div>
                          <div className="mt-2 p-3 bg-gray-50 rounded text-sm font-mono max-h-32 overflow-y-auto">
                            {typeof setting.value === 'object' 
                              ? JSON.stringify(setting.value, null, 2)
                              : setting.value
                            }
                          </div>
                        </div>
                        <div className="flex items-center gap-2 ml-4">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setEditingType('setting');
                              setEditingItem(setting);
                              setIsDialogOpen(true);
                            }}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDelete('setting', setting.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Settings className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-500">No site settings configured</p>
                  <p className="text-sm text-gray-400 mt-1">
                    Business information and site configuration will appear here
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

      </Tabs>

      {/* Edit Dialog - Only for non-chat items */}
      <Dialog open={isDialogOpen && editingType !== 'chat'} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {editingItem ? `Edit ${editingType}` : `Add New ${editingType}`}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {editingType === 'chat' && editingItem && (
              <div className="space-y-4">
                {/* This is handled by the chat modal above, not the generic edit dialog */}
              </div>
            )}

            {editingType === 'setting' && (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="key">Setting Key</Label>
                  <Input
                    id="key"
                    defaultValue={editingItem?.key || ''}
                    placeholder="e.g., contact_email"
                  />
                </div>
                <div>
                  <Label htmlFor="value">Setting Value</Label>
                  <Textarea
                    id="value"
                    defaultValue={editingItem?.value || ''}
                    placeholder="Enter the setting value"
                    rows={4}
                  />
                </div>
                <Button onClick={() => {
                  const key = document.getElementById('key').value;
                  const value = document.getElementById('value').value;
                  handleSubmitSetting({ key, value });
                }}>
                  {editingItem ? 'Update' : 'Create'} Setting
                </Button>
              </div>
            )}
            
            {editingType === 'pricing' && (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="name">Plan Name</Label>
                  <Input
                    id="name"
                    defaultValue={editingItem?.name || ''}
                    placeholder="e.g., Voice AI Assistants"
                  />
                </div>
                <div>
                  <Label htmlFor="price">Current Price</Label>
                  <Input
                    id="price"
                    defaultValue={editingItem?.price || ''}
                    placeholder="e.g., 899"
                  />
                </div>
                <div>
                  <Label htmlFor="originalPrice">Original Price (crossed out)</Label>
                  <Input
                    id="originalPrice"
                    defaultValue={editingItem?.originalPrice || ''}
                    placeholder="e.g., 1299"
                  />
                </div>
                <div>
                  <Label htmlFor="currency">Currency</Label>
                  <Input
                    id="currency"
                    defaultValue={editingItem?.currency || 'AUD'}
                    placeholder="AUD"
                  />
                </div>
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    defaultValue={editingItem?.description || ''}
                    placeholder="Plan description"
                    rows={3}
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <Switch id="isActive" defaultChecked={editingItem?.isActive !== false} />
                  <Label htmlFor="isActive">Active</Label>
                </div>
                <Button onClick={() => {
                  const name = document.getElementById('name').value;
                  const price = document.getElementById('price').value;
                  const originalPrice = document.getElementById('originalPrice').value;
                  const currency = document.getElementById('currency').value;
                  const description = document.getElementById('description').value;
                  const isActive = document.getElementById('isActive').checked;
                  handleSubmitPricing({ name, price, originalPrice, currency, description, isActive });
                }}>
                  {editingItem ? 'Update' : 'Create'} Pricing Plan
                </Button>
              </div>
            )}

            {editingType === 'service' && (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="title">Service Title</Label>
                  <Input
                    id="title"
                    defaultValue={editingItem?.title || ''}
                    placeholder="e.g., AI Chatbots"
                  />
                </div>
                <div>
                  <Label htmlFor="service-description">Description</Label>
                  <Textarea
                    id="service-description"
                    defaultValue={editingItem?.description || ''}
                    placeholder="Service description"
                    rows={3}
                  />
                </div>
                <Button onClick={() => {
                  const title = document.getElementById('title').value;
                  const description = document.getElementById('service-description').value;
                  handleSubmitService({ title, description, features: [] });
                }}>
                  {editingItem ? 'Update' : 'Create'} Service
                </Button>
              </div>
            )}

            {editingType === 'ai-tool' && (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="ai-tool-name">Tool Name</Label>
                  <Input
                    id="ai-tool-name"
                    defaultValue={editingItem?.name || ''}
                    placeholder="e.g., Advanced Age Calculator"
                  />
                </div>
                <div>
                  <Label htmlFor="ai-tool-description">Description</Label>
                  <Textarea
                    id="ai-tool-description"
                    defaultValue={editingItem?.description || ''}
                    placeholder="Tool description"
                    rows={3}
                  />
                </div>
                <div>
                  <Label htmlFor="ai-tool-url">Tool URL</Label>
                  <Input
                    id="ai-tool-url"
                    defaultValue={editingItem?.url || ''}
                    placeholder="https://example.com"
                  />
                </div>
                <Button onClick={() => {
                  const name = document.getElementById('ai-tool-name').value;
                  const description = document.getElementById('ai-tool-description').value;
                  const url = document.getElementById('ai-tool-url').value;
                  handleSubmitAITool({ name, description, url, category: 'Utility' });
                }}>
                  {editingItem ? 'Update' : 'Create'} AI Tool
                </Button>
              </div>
            )}

            {editingType === 'demo-site' && (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="demo-title">Demo Title</Label>
                  <Input
                    id="demo-title"
                    defaultValue={editingItem?.title || ''}
                    placeholder="e.g., CleanPro AI Assistant"
                  />
                </div>
                <div>
                  <Label htmlFor="demo-industry">Industry</Label>
                  <Input
                    id="demo-industry"
                    defaultValue={editingItem?.industry || ''}
                    placeholder="e.g., Cleaning Services"
                  />
                </div>
                <div>
                  <Label htmlFor="demo-description">Description</Label>
                  <Textarea
                    id="demo-description"
                    defaultValue={editingItem?.description || ''}
                    placeholder="Demo description"
                    rows={3}
                  />
                </div>
                <div>
                  <Label htmlFor="demo-url">Demo URL</Label>
                  <Input
                    id="demo-url"
                    defaultValue={editingItem?.url || ''}
                    placeholder="https://demo.example.com"
                  />
                </div>
                <Button onClick={() => {
                  const title = document.getElementById('demo-title').value;
                  const industry = document.getElementById('demo-industry').value;
                  const description = document.getElementById('demo-description').value;
                  const url = document.getElementById('demo-url').value;
                  handleSubmitDemoSite({ title, industry, description, url, status: 'Live Demo' });
                }}>
                  {editingItem ? 'Update' : 'Create'} Demo Site
                </Button>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default AdminDashboard;
