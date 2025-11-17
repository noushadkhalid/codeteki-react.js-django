import { useQuery } from "@tanstack/react-query";

const SETTINGS_QUERY_KEY = "/api/settings/";

async function fetchSiteSettings() {
  const response = await fetch("/api/settings/");
  if (!response.ok) {
    throw new Error("Failed to fetch site settings");
  }
  return response.json();
}

export function useSiteSettings(options = {}) {
  const query = useQuery({
    queryKey: [SETTINGS_QUERY_KEY],
    queryFn: fetchSiteSettings,
    staleTime: 1000 * 60 * 5,
    ...options,
  });

  const settings = query.data?.data?.settings || query.data?.settings || null;
  return { ...query, settings };
}
