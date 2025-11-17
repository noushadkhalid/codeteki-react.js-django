import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useToast } from "./hooks/use-toast";

export function useAdminAuth() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  // Check admin status - works for both Replit and environment auth
  const { data: adminStatus, isLoading } = useQuery({
    queryKey: ['/api/admin/status'],
    retry: false,
  });

  // Also check Replit auth status as fallback
  const { data: replitStatus } = useQuery({
    queryKey: ['/api/auth/role'],
    retry: false,
  });

  // Determine if user is admin from either auth system
  const isAdmin = adminStatus?.isAdmin || replitStatus?.isAdmin || false;
  const user = adminStatus?.user || replitStatus?.user || null;

  // Login mutation for environment-based auth
  const loginMutation = useMutation({
    mutationFn: async (credentials: { email: string; password: string }) => {
      const response = await fetch('/api/admin/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Login failed');
      }
      
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/admin/status'] });
      toast({
        title: "Login Successful",
        description: "Welcome to the admin dashboard",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Login Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  // Logout mutation
  const logoutMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch('/api/admin/logout', {
        method: 'POST',
      });
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/admin/status'] });
      queryClient.invalidateQueries({ queryKey: ['/api/auth/role'] });
      toast({
        title: "Logged Out",
        description: "You have been logged out successfully",
      });
    },
  });

  return {
    isAdmin,
    user,
    isLoading,
    login: loginMutation.mutate,
    logout: logoutMutation.mutate,
    isLoggingIn: loginMutation.isPending,
    isLoggingOut: logoutMutation.isPending,
  };
}