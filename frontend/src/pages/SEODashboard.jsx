import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Progress } from "../components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { Search, TrendingUp, Target, Brain, RefreshCw, CheckCircle, AlertCircle, Loader2, Settings } from "lucide-react";
import { useToast } from "../hooks/use-toast";
import { apiRequest } from "../lib/queryClient";

export default function SEODashboard() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState("overview");
  const [seoData, setSeoData] = useState(null);
  const [isImplementing, setIsImplementing] = useState(false);

  const { data: seoAnalysis, isLoading } = useQuery({
    queryKey: ["/api/admin/seo-analysis"],
    retry: false,
    enabled: false, // Don't auto-load, require manual trigger
  });

  const runAnalysisMutation = useMutation({
    mutationFn: async () => {

      
      // Make POST request to SEO analysis endpoint
      const response = await fetch('/api/seo/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`SEO analysis failed: ${response.status}`);
      }
      
      return response.json();
    },
    onSuccess: (data) => {
      setSeoData(data);
      queryClient.setQueryData(["/api/admin/seo-analysis"], data);
      setActiveTab('overview');
      toast({ 
        title: "SEO Analysis Complete", 
        description: `Found ${data.suggestions?.length || 0} optimization opportunities with current pricing` 
      });
    },
    onError: (error: Error) => {
      toast({ 
        title: "Error", 
        description: error.message,
        variant: "destructive" 
      });
    },
  });

  const implementSeoMutation = useMutation({
    mutationFn: async () => {
      const currentAnalysis = seoData || seoAnalysis;
      if (!currentAnalysis) {
        throw new Error('No SEO analysis available to implement');
      }

      const response = await fetch('/api/seo/implement', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          suggestions: currentAnalysis.suggestions || [],
          recommendations: currentAnalysis.recommendations || []
        })
      });

      if (!response.ok) {
        throw new Error(`SEO implementation failed: ${response.status}`);
      }

      return response.json();
    },
    onSuccess: (data) => {
      const implementedCount = data?.implemented?.length || 0;
      const failedCount = data?.failed?.length || 0;
      
      toast({
        title: "SEO Implementation Complete",
        description: `Implemented ${implementedCount} SEO improvements${failedCount > 0 ? `, ${failedCount} failed` : ''}`,
      });
      // Refresh analysis to show new status
      setTimeout(() => runAnalysisMutation.mutate(), 2000);
    },
    onError: (error: Error) => {
      toast({
        title: "Implementation Error",
        description: error?.message || "Failed to implement SEO changes",
        variant: "destructive"
      });
    },
  });

  const applySuggestionsMutation = useMutation({
    mutationFn: async (suggestions: SEOSuggestion[]) => {
      const response = await fetch('/api/seo/apply', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ suggestions })
      });
      
      if (!response.ok) {
        throw new Error(`Apply SEO failed: ${response.status}`);
      }
      
      return response.json();
    },
    onSuccess: (data) => {
      const count = data?.applied || data?.length || 0;
      toast({ 
        title: "SEO Applied Successfully", 
        description: `Applied SEO optimizations to ${count} pages`
      });
      
      // Refresh the analysis data to show applied status
      queryClient.invalidateQueries({ queryKey: ["/api/admin/seo-analysis"] });
    },
    onError: (error: Error) => {
      toast({ 
        title: "Error Applying SEO", 
        description: error?.message || "Failed to apply SEO suggestions",
        variant: "destructive" 
      });
    },
  });

  const applySingleMutation = useMutation({
    mutationFn: async (suggestion: SEOSuggestion) => {
      const response = await fetch('/api/seo/apply', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ suggestions: [suggestion] })
      });
      
      if (!response.ok) {
        throw new Error(`Apply SEO failed: ${response.status}`);
      }
      
      return response.json();
    },
    onSuccess: () => {
      toast({ 
        title: "SEO Applied Successfully", 
        description: "SEO suggestion applied successfully!"
      });
    },
    onError: (error: Error) => {
      toast({ 
        title: "Error Applying SEO", 
        description: error?.message || "Failed to apply SEO suggestion",
        variant: "destructive" 
      });
    },
  });

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'destructive';
      case 'medium': return 'secondary';
      case 'low': return 'outline';
      default: return 'secondary';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const currentAnalysis = seoData || seoAnalysis;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">SEO Optimization Dashboard</h2>
          <p className="text-gray-600">AI-powered SEO analysis and implementation for better search rankings</p>
        </div>
        <div className="flex gap-3">
          <Button 
            onClick={() => {
              runAnalysisMutation.mutate();
            }}
            disabled={runAnalysisMutation.isPending}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            {runAnalysisMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Search className="h-4 w-4 mr-2" />
                Run Analysis
              </>
            )}
          </Button>
          
          <Button 
            onClick={() => {
              implementSeoMutation.mutate();
            }}
            disabled={!seoData && !seoAnalysis || implementSeoMutation.isPending}
            className="bg-green-600 hover:bg-green-700 text-white"
          >
            {implementSeoMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Implementing...
              </>
            ) : (
              <>
                <CheckCircle className="h-4 w-4 mr-2" />
                Implement SEO Improvements
              </>
            )}
          </Button>
        </div>
      </div>

      {currentAnalysis && currentAnalysis.suggestions && currentAnalysis.suggestions.length > 0 ? (
        <>
          {/* Overview Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <TrendingUp className="h-8 w-8 text-blue-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">SEO Score</p>
                    <p className={`text-2xl font-bold ${getScoreColor(currentAnalysis?.overallScore || 0)}`}>
                      {currentAnalysis?.overallScore || 0}%
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <Search className="h-8 w-8 text-green-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Pages Analyzed</p>
                    <p className="text-2xl font-bold text-gray-900">{currentAnalysis?.suggestions?.length || 0}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <AlertCircle className="h-8 w-8 text-red-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">High Priority</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {currentAnalysis?.suggestions?.filter(s => s.priority === 'high').length || 0}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <Brain className="h-8 w-8 text-purple-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">AI Suggestions</p>
                    <p className="text-2xl font-bold text-gray-900">{seoAnalysis.recommendations.length}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="pages">Page Analysis</TabsTrigger>
              <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>SEO Performance Overview</CardTitle>
                  <CardDescription>
                    Overall SEO health and performance metrics
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span>Overall SEO Score</span>
                        <span className={getScoreColor(currentAnalysis?.overallScore || 0)}>
                          {currentAnalysis?.overallScore || 0}%
                        </span>
                      </div>
                      <Progress value={currentAnalysis?.overallScore || 0} className="h-2" />
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                      {['high', 'medium', 'low'].map(priority => {
                        const count = currentAnalysis?.suggestions?.filter(s => s.priority === priority).length || 0;
                        return (
                          <div key={priority} className="text-center p-4 border rounded-lg">
                            <div className="text-2xl font-bold text-gray-900">{count}</div>
                            <div className="text-sm text-gray-600 capitalize">{priority} Priority</div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="pages" className="space-y-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <div>
                    <CardTitle>Page-by-Page Analysis</CardTitle>
                    <CardDescription>
                      Detailed SEO suggestions for each page
                    </CardDescription>
                  </div>
                  <Button 
                    onClick={() => applySuggestionsMutation.mutate(currentAnalysis?.suggestions || [])}
                    disabled={applySuggestionsMutation.isPending}
                    className="bg-purple-600 hover:bg-purple-700 text-white"
                  >
                    {applySuggestionsMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Applying...
                      </>
                    ) : (
                      <>
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Apply All SEO Changes
                      </>
                    )}
                  </Button>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {(currentAnalysis?.suggestions || []).map((suggestion, index) => (
                      <div key={index} className="border rounded-lg p-6 hover:bg-gray-50 transition-colors">
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center space-x-3">
                            <h3 className="text-lg font-semibold text-gray-900">{suggestion.page}</h3>
                            <Badge variant={getPriorityColor(suggestion.priority)}>
                              {suggestion.priority} priority
                            </Badge>
                          </div>
                          <Button 
                            size="sm"
                            onClick={() => applySingleMutation.mutate(suggestion)}
                            disabled={applySingleMutation.isPending}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white"
                          >
                            {applySingleMutation.isPending ? 'Applying...' : 'Apply SEO'}
                          </Button>
                        </div>
                        
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                          <div>
                            <h4 className="font-medium text-gray-900 mb-2">Suggested Title</h4>
                            <div className="p-3 bg-green-50 border border-green-200 rounded text-sm">
                              {suggestion.suggestedTitle}
                            </div>
                          </div>
                          
                          <div>
                            <h4 className="font-medium text-gray-900 mb-2">Suggested Description</h4>
                            <div className="p-3 bg-green-50 border border-green-200 rounded text-sm">
                              {suggestion.suggestedDescription}
                            </div>
                          </div>
                        </div>
                        
                        <div className="mt-4">
                          <h4 className="font-medium text-gray-900 mb-2">Suggested Keywords</h4>
                          <div className="p-3 bg-blue-50 border border-blue-200 rounded text-sm">
                            {suggestion.suggestedKeywords}
                          </div>
                        </div>
                        
                        <div className="mt-4">
                          <h4 className="font-medium text-gray-900 mb-2">AI Reasoning</h4>
                          <p className="text-sm text-gray-600">{suggestion.reasoning}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="recommendations" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>AI-Powered Recommendations</CardTitle>
                  <CardDescription>
                    Strategic SEO improvements to boost your search rankings
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                      <p className="text-blue-800 text-sm mb-3 font-medium">Priority focus: Update SEO for Homepage, Services, Pricing, AI Tools, Demos, Contact pages</p>
                      <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                        <p className="text-green-700 text-sm font-medium">✅ Actionable Implementation Available</p>
                        <p className="text-gray-600 text-xs mt-1">Click "Implement SEO Improvements" to automatically apply meta tags, structured data, sitemap generation, and internal linking optimization.</p>
                      </div>
                    </div>
                    {(currentAnalysis?.recommendations || []).map((recommendation, index) => (
                      <div key={index} className="flex items-start space-x-3 p-4 border rounded-lg">
                        <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                        <p className="text-sm text-gray-700">{recommendation}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </>
      ) : (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Search className="h-16 w-16 text-gray-400 mb-4" />
            <h3 className="text-xl font-semibold text-gray-600 mb-2">Ready for SEO Analysis</h3>
            <p className="text-gray-500 text-center mb-6 max-w-md">
              Click "Run Analysis" to start AI-powered SEO optimization for your Australian business. 
              We'll analyze your pages and provide location-specific keywords and recommendations.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
              <div className="p-4 border rounded-lg">
                <div className="text-2xl font-bold text-blue-600">🇦🇺</div>
                <div className="text-sm font-medium">Australian Market</div>
                <div className="text-xs text-gray-500">Location targeting</div>
              </div>
              <div className="p-4 border rounded-lg">
                <div className="text-2xl font-bold text-green-600">💰</div>
                <div className="text-sm font-medium">Pricing Keywords</div>
                <div className="text-xs text-gray-500">Commercial intent</div>
              </div>
              <div className="p-4 border rounded-lg">
                <div className="text-2xl font-bold text-purple-600">🤖</div>
                <div className="text-sm font-medium">AI Suggestions</div>
                <div className="text-xs text-gray-500">Smart recommendations</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}