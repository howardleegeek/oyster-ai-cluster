"use client";

import { useEffect, useState } from "react";

const SCRIPT_ID = "google-maps-places-script";
const GOOGLE_MAPS_URL = "https://maps.googleapis.com/maps/api/js";

export function useGooglePlacesScript() {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const apiKey = process.env.NEXT_PUBLIC_GOOGLE_PLACES_API_KEY;
    if (!apiKey || typeof window === "undefined") {
      setError("Google Places API key not configured");
      return;
    }

    if (document.getElementById(SCRIPT_ID)) {
      if (typeof window !== "undefined" && (window as unknown as { google?: unknown }).google) {
        setLoaded(true);
      }
      return;
    }

    const script = document.createElement("script");
    script.id = SCRIPT_ID;
    script.src = `${GOOGLE_MAPS_URL}?key=${apiKey}&libraries=places&callback=__googlePlacesReady`;
    script.async = true;
    script.defer = true;

    (window as unknown as { __googlePlacesReady?: () => void }).__googlePlacesReady = () => {
      setLoaded(true);
    };

    script.onerror = () => setError("Failed to load Google Places");
    document.head.appendChild(script);
  }, []);

  return { loaded: !!loaded, error };
}
