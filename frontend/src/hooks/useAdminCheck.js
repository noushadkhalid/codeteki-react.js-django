import { useQuery } from "@tanstack/react-query";

export function useAdminCheck() {
  // Check both auth systems for admin status with refetch intervals
  const { data: replitAuth, isLoading: replitLoading } = useQuery({
    queryKey: ["/api/auth/role"],
    retry: false,
    refetchInterval: 30000, // Refetch every 30 seconds
    refetchOnWindowFocus: true, // Refetch when window regains focus
  });

  const { data: envAuth, isLoading: envLoading } = useQuery({
    queryKey: ["/api/admin/status"],
    retry: false,
    refetchInterval: 30000, // Refetch every 30 seconds
    refetchOnWindowFocus: true, // Refetch when window regains focus
  });

  return {
    isAdmin: replitAuth?.isAdmin || envAuth?.isAdmin || false,
    user: replitAuth?.user || envAuth?.user || null,
    isLoading: replitLoading || envLoading,
  };
}