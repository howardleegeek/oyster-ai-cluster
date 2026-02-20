"use client";

import { useEffect, useRef, useState } from "react";
import { useGooglePlacesScript } from "@/hooks/useGooglePlacesScript";

export interface AddressResult {
  line1: string;
  line2: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
}

type AddressComponent = { long_name: string; short_name: string; types: string[] };
type PlaceResult = {
  place_id?: string;
  address_components?: AddressComponent[];
  formatted_address?: string;
};

declare global {
  interface Window {
    google?: {
      maps: {
        places: {
          Autocomplete: new (input: HTMLInputElement, opts?: { types?: string[]; componentRestrictions?: { country: string[] }; fields?: string[] }) => {
            getPlace: () => PlaceResult;
            addListener: (event: string, fn: () => void) => { remove: () => void };
          };
          PlacesService: new (div: HTMLDivElement) => {
            getDetails: (
              req: { placeId: string; fields?: string[] },
              cb: (place: PlaceResult | null, status: string) => void
            ) => void;
          };
          PlacesServiceStatus: { OK: string };
        };
      };
    };
  }
}

function getComponent(
  components: AddressComponent[],
  type: string,
  useShort = false
): string {
  const c = components.find((x) => x.types.includes(type));
  return c ? (useShort ? c.short_name : c.long_name) : "";
}

function parseAddressComponents(components: AddressComponent[]): AddressResult {
  const streetNumber = getComponent(components, "street_number");
  const route = getComponent(components, "route");
  const line1 = [streetNumber, route].filter(Boolean).join(" ") || getComponent(components, "street_address");
  const line2 = getComponent(components, "subpremise");
  const city =
    getComponent(components, "locality") ||
    getComponent(components, "postal_town") ||
    getComponent(components, "administrative_area_level_2");
  const state = getComponent(components, "administrative_area_level_1");
  const postal_code = getComponent(components, "postal_code");
  const country = getComponent(components, "country", true) || getComponent(components, "country");

  return {
    line1: line1.trim() || "",
    line2: line2.trim() || "",
    city: city.trim() || "",
    state: state.trim() || "",
    postal_code: postal_code.trim() || "",
    country: country.trim() || "",
  };
}

interface AddressAutocompleteProps {
  value?: string;
  countryCode?: string;
  onSelect: (address: AddressResult) => void;
  placeholder?: string;
  className?: string;
  id?: string;
}

export default function AddressAutocomplete({
  value,
  countryCode,
  onSelect,
  placeholder = "Search address",
  className,
  id,
}: AddressAutocompleteProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const autocompleteRef = useRef<{ getPlace: () => PlaceResult; addListener: (e: string, fn: () => void) => { remove: () => void } } | null>(null);
  const [inputValue, setInputValue] = useState(value ?? "");
  const { loaded, error } = useGooglePlacesScript();

  useEffect(() => {
    setInputValue(value ?? "");
  }, [value]);

  useEffect(() => {
    if (!loaded || !window.google || !inputRef.current) return;

    const options: { types: string[]; componentRestrictions?: { country: string[] }; fields?: string[] } = {
      types: ["address"],
      fields: ["place_id", "address_components", "geometry"],
    };
    if (countryCode && countryCode.length === 2) {
      options.componentRestrictions = { country: [countryCode.toLowerCase()] };
    }

    if (autocompleteRef.current) return;
    const autocomplete = new window.google.maps.places.Autocomplete(inputRef.current, options);
    autocompleteRef.current = autocomplete;

    const listener = autocomplete.addListener("place_changed", () => {
      const place = autocomplete.getPlace();
      const applyParsed = (parsed: AddressResult) => {
        onSelect(parsed);
        setInputValue(
          [parsed.line1, parsed.line2, parsed.city, parsed.state, parsed.postal_code, parsed.country]
            .filter(Boolean)
            .join(", ")
        );
      };

      if (place.address_components?.length) {
        applyParsed(parseAddressComponents(place.address_components));
        return;
      }
      if (!place.place_id) return;

      const mapDiv = document.createElement("div");
      const service = new window.google!.maps.places.PlacesService(mapDiv);
      service.getDetails(
        {
          placeId: place.place_id,
          fields: ["address_components"],
        },
        (details: PlaceResult | null, status: string) => {
          if (status !== window.google!.maps.places.PlacesServiceStatus.OK || !details?.address_components) {
            return;
          }
          applyParsed(parseAddressComponents(details.address_components));
        }
      );
    });

    return () => {
      listener.remove();
      autocompleteRef.current = null;
    };
  }, [loaded, countryCode, onSelect]);

  const inputClassName = `w-full rounded-md border border-black/10 bg-white px-3 py-2 text-sm text-[#111111] focus:outline-none focus:ring-2 focus:ring-black/10 disabled:opacity-60 ${className ?? ""}`;

  if (error) {
    return (
      <input
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        placeholder={placeholder}
        className={inputClassName}
        id={id}
        autoComplete="off"
        aria-label="Address search"
      />
    );
  }

  return (
    <input
      ref={inputRef}
      value={inputValue}
      onChange={(e) => setInputValue(e.target.value)}
      placeholder={loaded ? placeholder : "Loading address search…"}
      className={inputClassName}
      id={id}
      disabled={!loaded}
      autoComplete="off"
      aria-label="Address search"
    />
  );
}
