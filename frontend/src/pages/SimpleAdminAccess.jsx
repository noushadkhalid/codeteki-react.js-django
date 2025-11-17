import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Settings } from "lucide-react";

export default function SimpleAdminAccess() {
  const [password, setPassword] = useState("");
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Simple password protection for internal use
  const handleLogin = () => {
    // Use a simple password check - you can change this password
    if (password === "codeteki2025") {
      setIsAuthenticated(true);
      localStorage.setItem("admin_access", "true");
    } else {
      alert("Incorrect password");
    }
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem("admin_access");
  };

  // Check if already authenticated
  useState(() => {
    if (localStorage.getItem("admin_access") === "true") {
      setIsAuthenticated(true);
    }
  });

  if (isAuthenticated) {
    // Import and render the full admin dashboard
    import("./AdminDashboard").then((module) => {
      const AdminDashboard = module.default;
      return <AdminDashboard />;
    });
    
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-white border-b">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                  <Settings className="h-6 w-6" />
                  Codeteki Admin Dashboard
                </h1>
                <p className="text-gray-600">Internal management portal</p>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-600">Admin User</span>
                <Button variant="outline" onClick={handleLogout}>
                  Logout
                </Button>
              </div>
            </div>
          </div>
        </div>
        
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading admin dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <Card className="w-full max-w-md mx-4">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Admin Access
          </CardTitle>
          <CardDescription>
            Enter password to access the internal admin dashboard
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleLogin()}
              placeholder="Enter admin password"
            />
          </div>
          <Button onClick={handleLogin} className="w-full">
            Access Dashboard
          </Button>
          <p className="text-xs text-gray-500 text-center">
            Internal use only - Contact IT for password
          </p>
        </CardContent>
      </Card>
    </div>
  );
}