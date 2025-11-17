import { useEffect, useState } from 'react';

const API_BASE =
  (process.env.REACT_APP_API_BASE && process.env.REACT_APP_API_BASE.trim()) ||
  '/api';

export function useCodetekiContent(endpoint, fallback) {
  const [data, setData] = useState(fallback);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    async function fetchData() {
      try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
          headers,
        });
        if (!response.ok) {
          throw new Error('Failed to fetch data');
        }
        const json = await response.json();
        if (isMounted) {
          setData(json.data ?? json);
          setError(null);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    fetchData();

    return () => {
      isMounted = false;
    };
  }, [endpoint]);

  return { data, loading, error };
}
