import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Shield, User } from "lucide-react";

export default function AdminTestLogin() {
  const handleTestLogin = () => {
    // Simulate admin login for testing
    localStorage.setItem('test-admin', 'true');
    window.location.href = '/admin';
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mb-4">
            <Shield className="h-6 w-6 text-red-600" />
          </div>
          <CardTitle>Admin Access Required</CardTitle>
          <CardDescription>
            You need admin privileges to access the admin dashboard
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-semibold text-blue-900 mb-2">For Testing:</h4>
            <p className="text-sm text-blue-800 mb-3">
              Click below to access admin features including the SEO optimization dashboard
            </p>
            <Button 
              onClick={handleTestLogin}
              className="w-full bg-blue-600 hover:bg-blue-700"
            >
              <User className="h-4 w-4 mr-2" />
              Access Admin Dashboard
            </Button>
          </div>
          
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h4 className="font-semibold text-yellow-900 mb-2">For Production:</h4>
            <ol className="text-sm text-yellow-800 space-y-1">
              <li>1. Log in with Replit Auth</li>
              <li>2. Have someone run: npm run admin:make your-email</li>
              <li>3. Refresh the page</li>
            </ol>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}