import { useQuery } from "@tanstack/react-query";

/**
 * Unified hook for fetching all home page content from backend
 * Returns: hero, impact, services, aiTools, roiCalculator, whyChoose, testimonials, etc.
 */
export function useHomePage() {
  return useQuery({
    queryKey: ["/api/home/"],
    staleTime: 1000 * 60 * 5, // Cache for 5 minutes
  });
}
