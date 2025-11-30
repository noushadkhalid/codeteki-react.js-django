"""
Custom Admin Site for Codeteki CMS.
Hides the default app list and provides a clean dashboard.
"""

from django.contrib.admin import AdminSite
from unfold.sites import UnfoldAdminSite


class CodetekiAdminSite(UnfoldAdminSite):
    """
    Custom admin site that hides the default app list.
    Uses Unfold's organized sidebar navigation instead.
    """
    site_header = "Codeteki CMS"
    site_title = "Codeteki Admin"
    index_title = "Dashboard"

    def get_app_list(self, request, app_label=None):
        """
        Return empty app list to hide the default model listing.
        All navigation is done through the organized sidebar.
        """
        # Return empty list to hide "Site administration" section
        return []


# Create the custom admin site instance
codeteki_admin_site = CodetekiAdminSite(name='codeteki_admin')
