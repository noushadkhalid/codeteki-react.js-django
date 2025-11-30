"""
Google Search Console API Service.

This service integrates with Google Search Console to get:
- Search Analytics: queries, clicks, impressions, CTR, position
- URL Inspection: indexing status, crawl info
- Sitemaps: submission status, indexed URLs
- Coverage: errors, warnings, valid pages

Uses Service Account authentication for server-to-server access.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Optional, List

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class SearchConsoleService:
    """
    Service for interacting with Google Search Console API.

    Prerequisites:
    - Service account with Search Console API access
    - Service account added as user to Search Console property
    - google-api-python-client and google-auth packages installed
    """

    SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

    def __init__(self, property_url: Optional[str] = None):
        """
        Initialize Search Console service.

        Args:
            property_url: Search Console property URL (e.g., "https://www.codeteki.au/")
        """
        self.property_url = property_url or getattr(settings, "GOOGLE_SEARCH_CONSOLE_PROPERTY", "")
        self.credentials_file = getattr(settings, "GOOGLE_SERVICE_ACCOUNT_FILE", "")
        self._service = None

    @property
    def enabled(self) -> bool:
        """Check if service is configured."""
        return bool(self.credentials_file and self.property_url)

    def _get_service(self):
        """Get or create the Search Console API service."""
        if self._service:
            return self._service

        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_file,
                scopes=self.SCOPES
            )

            self._service = build("searchconsole", "v1", credentials=credentials)
            return self._service

        except ImportError:
            logger.error("Google API client not installed. Run: pip install google-api-python-client google-auth")
            return None
        except Exception as e:
            logger.exception("Failed to initialize Search Console service")
            return None

    def get_search_analytics(
        self,
        start_date: datetime,
        end_date: datetime,
        dimensions: List[str] = None,
        row_limit: int = 25000,
        start_row: int = 0,
    ) -> dict:
        """
        Get search analytics data from Search Console.

        Args:
            start_date: Start date for data
            end_date: End date for data
            dimensions: List of dimensions (query, page, country, device, date)
            row_limit: Maximum rows to return (max 25000)
            start_row: Starting row for pagination

        Returns:
            dict with search analytics data
        """
        result = {
            "success": False,
            "property": self.property_url,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }

        if not self.enabled:
            result["error"] = "Search Console not configured. Set GOOGLE_SERVICE_ACCOUNT_FILE and GOOGLE_SEARCH_CONSOLE_PROPERTY."
            return result

        service = self._get_service()
        if not service:
            result["error"] = "Failed to initialize Search Console API service"
            return result

        try:
            # Default dimensions
            if dimensions is None:
                dimensions = ["query", "page", "date"]

            # Build request body
            request_body = {
                "startDate": start_date.strftime("%Y-%m-%d"),
                "endDate": end_date.strftime("%Y-%m-%d"),
                "dimensions": dimensions,
                "rowLimit": min(row_limit, 25000),
                "startRow": start_row,
            }

            logger.info(f"Fetching Search Console data for {self.property_url}")

            # Execute request
            response = service.searchanalytics().query(
                siteUrl=self.property_url,
                body=request_body
            ).execute()

            rows = response.get("rows", [])
            result["rows"] = []

            for row in rows:
                keys = row.get("keys", [])
                data = {
                    "clicks": row.get("clicks", 0),
                    "impressions": row.get("impressions", 0),
                    "ctr": row.get("ctr", 0),
                    "position": row.get("position", 0),
                }

                # Map dimensions to keys
                for i, dim in enumerate(dimensions):
                    if i < len(keys):
                        data[dim] = keys[i]

                result["rows"].append(data)

            result["row_count"] = len(rows)
            result["success"] = True

        except Exception as e:
            result["error"] = str(e)
            logger.exception("Error fetching Search Console data")

        return result

    def sync_data(self, sync_record) -> dict:
        """
        Sync Search Console data to database.

        Args:
            sync_record: SearchConsoleSync model instance

        Returns:
            dict with sync results
        """
        from ..models import SearchConsoleData, SearchConsoleSync

        result = {
            "success": False,
            "rows_imported": 0,
            "queries_imported": set(),
            "pages_imported": set(),
        }

        # Update status
        sync_record.status = SearchConsoleSync.STATUS_RUNNING
        sync_record.save(update_fields=["status"])

        try:
            # Fetch data from API
            analytics = self.get_search_analytics(
                start_date=sync_record.start_date,
                end_date=sync_record.end_date,
                dimensions=["query", "page", "date"],
                row_limit=25000,
            )

            if not analytics.get("success"):
                sync_record.status = SearchConsoleSync.STATUS_FAILED
                sync_record.error_message = analytics.get("error", "Unknown error")
                sync_record.save(update_fields=["status", "error_message"])
                result["error"] = analytics.get("error")
                return result

            # Process rows
            rows = analytics.get("rows", [])
            created_count = 0

            for row in rows:
                query = row.get("query", "")
                page = row.get("page", "")
                date_str = row.get("date", "")

                if not (query and page and date_str):
                    continue

                try:
                    date = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    continue

                # Create or update record
                obj, created = SearchConsoleData.objects.update_or_create(
                    date=date,
                    query=query,
                    page=page,
                    defaults={
                        "clicks": row.get("clicks", 0),
                        "impressions": row.get("impressions", 0),
                        "ctr": row.get("ctr", 0),
                        "position": row.get("position", 0),
                    }
                )

                if created:
                    created_count += 1

                result["queries_imported"].add(query)
                result["pages_imported"].add(page)

            result["rows_imported"] = created_count
            result["success"] = True

            # Update sync record
            sync_record.status = SearchConsoleSync.STATUS_COMPLETED
            sync_record.completed_at = timezone.now()
            sync_record.rows_imported = created_count
            sync_record.queries_imported = len(result["queries_imported"])
            sync_record.pages_imported = len(result["pages_imported"])
            sync_record.save()

        except Exception as e:
            sync_record.status = SearchConsoleSync.STATUS_FAILED
            sync_record.error_message = str(e)
            sync_record.save(update_fields=["status", "error_message"])
            result["error"] = str(e)
            logger.exception("Error syncing Search Console data")

        # Convert sets to counts for return
        result["queries_imported"] = len(result["queries_imported"])
        result["pages_imported"] = len(result["pages_imported"])

        return result

    def get_top_queries(
        self,
        days: int = 28,
        limit: int = 100,
        min_impressions: int = 0,
    ) -> dict:
        """
        Get top performing queries.

        Args:
            days: Number of days to look back
            limit: Maximum number of queries to return
            min_impressions: Minimum impressions filter

        Returns:
            dict with top queries
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        analytics = self.get_search_analytics(
            start_date=start_date,
            end_date=end_date,
            dimensions=["query"],
            row_limit=limit,
        )

        if not analytics.get("success"):
            return analytics

        # Filter and sort by clicks
        rows = analytics.get("rows", [])
        filtered = [r for r in rows if r.get("impressions", 0) >= min_impressions]
        sorted_rows = sorted(filtered, key=lambda x: x.get("clicks", 0), reverse=True)

        return {
            "success": True,
            "queries": sorted_rows[:limit],
            "total": len(sorted_rows),
        }

    def get_top_pages(
        self,
        days: int = 28,
        limit: int = 100,
    ) -> dict:
        """
        Get top performing pages.

        Args:
            days: Number of days to look back
            limit: Maximum number of pages to return

        Returns:
            dict with top pages
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        analytics = self.get_search_analytics(
            start_date=start_date,
            end_date=end_date,
            dimensions=["page"],
            row_limit=limit,
        )

        if not analytics.get("success"):
            return analytics

        # Sort by clicks
        rows = analytics.get("rows", [])
        sorted_rows = sorted(rows, key=lambda x: x.get("clicks", 0), reverse=True)

        return {
            "success": True,
            "pages": sorted_rows[:limit],
            "total": len(sorted_rows),
        }

    def find_content_opportunities(
        self,
        days: int = 28,
        min_impressions: int = 100,
        max_ctr: float = 0.02,
        max_position: float = 20,
    ) -> dict:
        """
        Find content optimization opportunities.

        Identifies queries with high impressions but low CTR - potential for
        improvement with better titles/descriptions.

        Args:
            days: Number of days to analyze
            min_impressions: Minimum impressions to consider
            max_ctr: Maximum CTR (lower CTR = more opportunity)
            max_position: Maximum position to consider (already ranking)

        Returns:
            dict with opportunities
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        analytics = self.get_search_analytics(
            start_date=start_date,
            end_date=end_date,
            dimensions=["query", "page"],
            row_limit=5000,
        )

        if not analytics.get("success"):
            return analytics

        opportunities = []
        for row in analytics.get("rows", []):
            impressions = row.get("impressions", 0)
            ctr = row.get("ctr", 0)
            position = row.get("position", 100)

            if (impressions >= min_impressions and
                ctr <= max_ctr and
                position <= max_position):

                # Calculate opportunity score
                # Higher impressions + lower CTR + better position = more opportunity
                potential_clicks = impressions * 0.05  # Assume 5% CTR is achievable
                current_clicks = row.get("clicks", 0)
                opportunity_score = potential_clicks - current_clicks

                opportunities.append({
                    "query": row.get("query"),
                    "page": row.get("page"),
                    "impressions": impressions,
                    "clicks": current_clicks,
                    "ctr": ctr,
                    "position": position,
                    "potential_clicks": potential_clicks,
                    "opportunity_score": opportunity_score,
                })

        # Sort by opportunity score
        opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)

        return {
            "success": True,
            "opportunities": opportunities[:50],
            "total": len(opportunities),
        }

    def find_ranking_drops(
        self,
        days_recent: int = 7,
        days_compare: int = 28,
        min_drop: float = 3.0,
    ) -> dict:
        """
        Find queries with significant ranking drops.

        Compares recent performance to previous period.

        Args:
            days_recent: Recent period (days)
            days_compare: Comparison period (days)
            min_drop: Minimum position drop to report

        Returns:
            dict with ranking drops
        """
        now = datetime.now()

        # Recent period
        recent = self.get_search_analytics(
            start_date=now - timedelta(days=days_recent),
            end_date=now,
            dimensions=["query"],
            row_limit=5000,
        )

        # Comparison period
        compare = self.get_search_analytics(
            start_date=now - timedelta(days=days_compare),
            end_date=now - timedelta(days=days_recent),
            dimensions=["query"],
            row_limit=5000,
        )

        if not recent.get("success") or not compare.get("success"):
            return {
                "success": False,
                "error": recent.get("error") or compare.get("error")
            }

        # Build lookup for comparison data
        compare_lookup = {
            row.get("query"): row for row in compare.get("rows", [])
        }

        drops = []
        for row in recent.get("rows", []):
            query = row.get("query")
            if query not in compare_lookup:
                continue

            recent_pos = row.get("position", 0)
            compare_pos = compare_lookup[query].get("position", 0)
            drop = recent_pos - compare_pos

            if drop >= min_drop:
                drops.append({
                    "query": query,
                    "recent_position": recent_pos,
                    "previous_position": compare_pos,
                    "drop": drop,
                    "recent_clicks": row.get("clicks", 0),
                    "previous_clicks": compare_lookup[query].get("clicks", 0),
                })

        # Sort by drop amount
        drops.sort(key=lambda x: x["drop"], reverse=True)

        return {
            "success": True,
            "drops": drops[:50],
            "total": len(drops),
        }

    def update_keyword_rankings(self, upload=None) -> dict:
        """
        Update keyword rankings from Search Console data.

        Links Search Console data with existing SEOKeyword records
        and creates KeywordRanking entries.

        Args:
            upload: Optional SEODataUpload to link keywords from

        Returns:
            dict with update results
        """
        from ..models import SEOKeyword, KeywordRanking, SearchConsoleData

        result = {
            "success": False,
            "keywords_updated": 0,
            "rankings_created": 0,
        }

        try:
            # Get recent Search Console data
            today = timezone.now().date()
            week_ago = today - timedelta(days=7)

            # Get keywords to update
            if upload:
                keywords = SEOKeyword.objects.filter(upload=upload)
            else:
                keywords = SEOKeyword.objects.all()

            for keyword in keywords:
                # Find matching Search Console data
                sc_data = SearchConsoleData.objects.filter(
                    query__iexact=keyword.keyword,
                    date__gte=week_ago,
                ).order_by("-date").first()

                if sc_data:
                    # Get previous ranking
                    prev_ranking = KeywordRanking.objects.filter(
                        keyword=keyword
                    ).order_by("-date").first()

                    prev_position = prev_ranking.position if prev_ranking else None

                    # Create new ranking record
                    KeywordRanking.objects.create(
                        keyword=keyword,
                        date=sc_data.date,
                        position=sc_data.position,
                        previous_position=prev_position,
                        position_change=(prev_position - sc_data.position) if prev_position else 0,
                        clicks=sc_data.clicks,
                        impressions=sc_data.impressions,
                        ctr=sc_data.ctr,
                        ranking_url=sc_data.page,
                    )

                    result["rankings_created"] += 1

                    # Update keyword with latest ranking
                    keyword.ranking_url = sc_data.page
                    keyword.save(update_fields=["ranking_url", "updated_at"])

                    result["keywords_updated"] += 1

            result["success"] = True

        except Exception as e:
            result["error"] = str(e)
            logger.exception("Error updating keyword rankings")

        return result


def sync_search_console(days: int = 28) -> dict:
    """
    Convenience function to sync recent Search Console data.

    Args:
        days: Number of days to sync

    Returns:
        dict with sync results
    """
    from ..models import SearchConsoleSync

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    # Create sync record
    sync = SearchConsoleSync.objects.create(
        property_url=getattr(settings, "GOOGLE_SEARCH_CONSOLE_PROPERTY", ""),
        start_date=start_date,
        end_date=end_date,
    )

    service = SearchConsoleService()
    return service.sync_data(sync)
