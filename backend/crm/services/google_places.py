"""
Google Places API (New) service for discovering local business leads.

Uses Places API (New) — cheaper pricing, 10K free calls/month.
Geocoding API still uses the legacy endpoint (no "new" version exists).
Details fetched at search time now — free tier is generous enough.
"""

import logging
import re
import time
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class GooglePlacesService:
    """Search Google Places API (New) to discover local business leads."""

    PLACES_URL = 'https://places.googleapis.com/v1'
    GEOCODE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

    # Maps industry choices to Google Place types (New API format)
    INDUSTRY_TO_PLACE_TYPES = {
        'restaurant': ['restaurant', 'cafe', 'bakery', 'bar', 'meal_delivery'],
        'trades': ['plumber', 'electrician', 'locksmith', 'roofing_contractor', 'painter'],
        'health_beauty': ['beauty_salon', 'hair_salon', 'spa'],
        'retail': ['store', 'clothing_store', 'furniture_store', 'jewelry_store'],
        'fitness': ['gym', 'yoga_studio'],
        'automotive': ['car_repair', 'car_dealer', 'car_wash'],
        'medical': ['doctor', 'dentist', 'physiotherapist', 'pharmacy'],
        'real_estate': ['real_estate_agency'],
        'legal': ['lawyer'],
        'accounting': ['accounting'],
        'accommodation': ['lodging', 'hotel'],
        'education': ['school', 'university'],
        'professional': ['insurance_agency', 'travel_agency'],
    }

    def __init__(self):
        self.api_key = getattr(settings, 'GOOGLE_API_KEY', '')
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not configured")

    def _geocode(self, address: str) -> tuple[float, float] | None:
        """Convert address string to lat/lng. Uses legacy Geocoding API."""
        params = {
            'address': address,
            'key': self.api_key,
            'region': 'au',
        }
        try:
            resp = requests.get(self.GEOCODE_URL, params=params, timeout=10)
            data = resp.json()
            if data.get('status') == 'OK' and data.get('results'):
                loc = data['results'][0]['geometry']['location']
                return loc['lat'], loc['lng']
            logger.warning(f"Geocode failed for '{address}': {data.get('status')}")
        except Exception as e:
            logger.error(f"Geocode error for '{address}': {e}")
        return None

    def search_nearby(self, location: str, industry: str = '', radius_km: int = 5,
                       keywords: str = '') -> dict:
        """
        Search for businesses near a location with full details (phone, website).
        New API caps at 20 per call, so we make multiple calls for more types.
        Free tier = 10K calls/month — plenty of room.

        When keywords are provided, uses text search with the keywords + industry + location
        combined into a natural query (skips geocoding entirely).

        Returns:
            {
                'success': bool,
                'businesses': [{'name', 'address', 'phone', 'website', 'has_website',
                                'rating', 'place_id', 'industry', ...}],
                'total': int,
                'without_website': int,
                'error': str (if failed)
            }
        """
        if not self.api_key:
            return {'success': False, 'error': 'GOOGLE_API_KEY not configured', 'businesses': [], 'total': 0}

        from crm.models import Contact
        place_types = self.INDUSTRY_TO_PLACE_TYPES.get(industry, [])

        if keywords:
            # Use text search for keyword-based queries (e.g. "Indian restaurant in Parramatta NSW")
            industry_label = dict(Contact.INDUSTRY_CHOICES).get(industry, industry)
            parts = [p for p in [keywords, industry_label, f"in {location}"] if p]
            query = ' '.join(parts)
            places = self._text_search(query)
        elif place_types:
            coords = self._geocode(location)
            if not coords:
                return {'success': False, 'error': f'Could not geocode "{location}". Make sure Geocoding API is enabled in Google Cloud Console.', 'businesses': [], 'total': 0}
            lat, lng = coords
            # New API supports multiple includedTypes in one call
            places = self._nearby_search(lat, lng, radius_km * 1000, place_types)
        else:
            coords = self._geocode(location)
            if not coords:
                return {'success': False, 'error': f'Could not geocode "{location}". Make sure Geocoding API is enabled in Google Cloud Console.', 'businesses': [], 'total': 0}
            # Fallback to text search for industries without mapped types
            query = f"{industry} in {location}" if industry else location
            places = self._text_search(query)

        # Now fetch details (phone, website, email) for each result
        businesses = []
        for p in places:
            details = self._get_place_details(p['place_id'])
            website = details.get('website', '') if details else ''
            email = self._scrape_email(website) if website else ''
            biz = {
                'name': p.get('name', ''),
                'address': details.get('formatted_address', p.get('address', '')) if details else p.get('address', ''),
                'phone': details.get('formatted_phone_number', '') if details else '',
                'email': email,
                'website': website,
                'has_website': bool(website),
                'rating': p.get('rating'),
                'user_ratings_total': p.get('user_ratings_total', 0),
                'place_id': p['place_id'],
                'industry': industry,
                'types': p.get('types', []),
            }
            businesses.append(biz)
            time.sleep(0.05)  # Light rate limiting

        without_website = sum(1 for b in businesses if not b['has_website'])

        return {
            'success': True,
            'businesses': businesses,
            'total': len(businesses),
            'without_website': without_website,
        }

    def _get_place_details(self, place_id: str) -> dict | None:
        """
        Get phone, website, full address for a single place.
        Returns normalized dict matching admin import expectations.
        """
        url = f"{self.PLACES_URL}/places/{place_id}"
        headers = {
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': 'nationalPhoneNumber,websiteUri,formattedAddress',
        }
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    'formatted_phone_number': data.get('nationalPhoneNumber', ''),
                    'website': data.get('websiteUri', ''),
                    'formatted_address': data.get('formattedAddress', ''),
                }
            logger.warning(f"Place details failed for {place_id}: {resp.status_code} - {resp.text[:200]}")
        except Exception as e:
            logger.error(f"Place details error for {place_id}: {e}")
        return None

    # Prefixes that indicate auto-generated / platform emails
    _JUNK_PREFIXES = (
        'noreply', 'no-reply', 'donotreply', 'do-not-reply', 'mailer-daemon',
        'postmaster', 'webmaster', 'root', 'sysadmin', 'hostmaster',
        'abuse', 'privacy',
    )

    # Platform / SaaS domains — never real business emails
    _JUNK_DOMAINS = {
        'sentry.io', 'wix.com', 'squarespace.com', 'shopify.com',
        'wordpress.com', 'wordpress.org', 'w3.org', 'schema.org',
        'googleapis.com', 'google.com', 'googletagmanager.com',
        'facebook.com', 'fb.com', 'twitter.com', 'instagram.com',
        'example.com', 'test.com', 'localhost', 'email.com',
        'yourdomain.com', 'domain.com', 'yoursite.com', 'site.com',
        'sentry-next.wixpress.com', 'wixpress.com',
        'cloudflare.com', 'jsdelivr.net', 'unpkg.com',
        'gravatar.com', 'amazonaws.com', 'herokuapp.com',
        'ghost.io', 'mailchimp.com', 'hubspot.com',
        'intercom.io', 'zendesk.com', 'freshdesk.com',
        'stripe.com', 'paypal.com', 'gstatic.com',
    }

    # Placeholder / dummy local parts
    _JUNK_LOCALS = {
        'user', 'email', 'test', 'example', 'your', 'name',
        'someemail', 'someone', 'youremail', 'yourname',
        'john', 'jane', 'johndoe', 'janedoe', 'placeholder',
    }

    def _is_junk_email(self, email: str) -> bool:
        """Return True if this email looks like a platform, placeholder, or fake address."""
        lower = email.lower()
        local, _, domain = lower.partition('@')
        if not domain:
            return True
        # File extensions embedded in HTML/CSS
        if lower.endswith(('.png', '.jpg', '.gif', '.svg', '.webp', '.css', '.js')):
            return True
        # Platform domains
        if domain in self._JUNK_DOMAINS or any(domain.endswith('.' + d) for d in self._JUNK_DOMAINS):
            return True
        # Junk prefixes
        if any(local.startswith(p) for p in self._JUNK_PREFIXES):
            return True
        # Placeholder local parts (exact match)
        local_clean = local.split('.')[0].split('+')[0]  # strip dots/plus tags
        if local_clean in self._JUNK_LOCALS:
            return True
        # Suspiciously generic: xyz.com, abc.com
        if domain in ('xyz.com', 'abc.com', 'aaa.com', 'mail.com'):
            return True
        return False

    def _scrape_email(self, url: str) -> str:
        """Try to find a contact email from the business website homepage."""
        try:
            resp = requests.get(url, timeout=5, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1)',
            })
            if resp.status_code != 200:
                return ''
            text = resp.text[:200_000]  # Cap to avoid huge pages

            # Find all email addresses via regex
            emails = re.findall(
                r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',
                text,
            )
            for email in emails:
                if not self._is_junk_email(email):
                    return email
        except Exception:
            pass
        return ''

    def get_details_batch(self, place_ids: list[str]) -> dict[str, dict]:
        """
        Fetch details for multiple places.
        Returns {place_id: details_dict}.
        """
        results = {}
        for pid in place_ids:
            details = self._get_place_details(pid)
            if details:
                results[pid] = details
            time.sleep(0.05)
        return results

    def _nearby_search(self, lat: float, lng: float, radius_m: int,
                       place_types: list[str]) -> list[dict]:
        """
        Nearby Search using Places API (New). Max 20 results per call.
        """
        url = f"{self.PLACES_URL}/places:searchNearby"
        headers = {
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': 'places.id,places.displayName,places.shortFormattedAddress,places.rating,places.userRatingCount,places.types',
            'Content-Type': 'application/json',
        }
        body = {
            'includedTypes': place_types,
            'maxResultCount': 20,
            'locationRestriction': {
                'circle': {
                    'center': {'latitude': lat, 'longitude': lng},
                    'radius': min(float(radius_m), 50000.0),
                }
            },
        }
        results = []
        try:
            resp = requests.post(url, headers=headers, json=body, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                for place in data.get('places', []):
                    results.append({
                        'place_id': place.get('id', ''),
                        'name': place.get('displayName', {}).get('text', ''),
                        'address': place.get('shortFormattedAddress', ''),
                        'rating': place.get('rating'),
                        'user_ratings_total': place.get('userRatingCount', 0),
                        'types': place.get('types', []),
                    })
            else:
                logger.warning(f"Nearby search failed: {resp.status_code} - {resp.text[:300]}")
        except Exception as e:
            logger.error(f"Nearby search error: {e}")
        return results

    def _text_search(self, query: str) -> list[dict]:
        """Text Search using Places API (New)."""
        url = f"{self.PLACES_URL}/places:searchText"
        headers = {
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': 'places.id,places.displayName,places.shortFormattedAddress,places.rating,places.userRatingCount,places.types',
            'Content-Type': 'application/json',
        }
        body = {
            'textQuery': query,
            'maxResultCount': 20,
        }
        results = []
        try:
            resp = requests.post(url, headers=headers, json=body, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                for place in data.get('places', []):
                    results.append({
                        'place_id': place.get('id', ''),
                        'name': place.get('displayName', {}).get('text', ''),
                        'address': place.get('shortFormattedAddress', ''),
                        'rating': place.get('rating'),
                        'user_ratings_total': place.get('userRatingCount', 0),
                        'types': place.get('types', []),
                    })
            else:
                logger.warning(f"Text search failed: {resp.status_code} - {resp.text[:300]}")
        except Exception as e:
            logger.error(f"Text search error: {e}")
        return results
