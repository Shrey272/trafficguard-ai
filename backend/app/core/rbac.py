from typing import List, Dict

# Define all available permissions in the system
class Permissions:
    CAMERA_READ = "camera.read"
    CAMERA_WRITE = "camera.write"
    CAMERA_CREDENTIALS_MANAGE = "camera.credentials.manage"
    INCIDENT_READ = "incident.read"
    INCIDENT_ACKNOWLEDGE = "incident.acknowledge"
    INCIDENT_RESOLVE = "incident.resolve"
    ANPR_SEARCH = "anpr.search"
    WATCHLIST_MANAGE = "watchlist.manage"
    USERS_MANAGE = "users.manage"
    AUDIT_READ = "audit.read"
    SYSTEM_CONFIG = "system.config"

# Map roles to permissions
ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "ADMIN": [
        Permissions.CAMERA_READ,
        Permissions.CAMERA_WRITE,
        Permissions.CAMERA_CREDENTIALS_MANAGE,
        Permissions.INCIDENT_READ,
        Permissions.INCIDENT_ACKNOWLEDGE,
        Permissions.INCIDENT_RESOLVE,
        Permissions.ANPR_SEARCH,
        Permissions.WATCHLIST_MANAGE,
        Permissions.USERS_MANAGE,
        Permissions.AUDIT_READ,
        Permissions.SYSTEM_CONFIG
    ],
    "OPERATOR": [
        Permissions.CAMERA_READ,
        Permissions.INCIDENT_READ,
        Permissions.INCIDENT_ACKNOWLEDGE,
        Permissions.INCIDENT_RESOLVE,
        Permissions.ANPR_SEARCH,
        Permissions.WATCHLIST_MANAGE
    ],
    "VIEWER": [
        Permissions.CAMERA_READ,
        Permissions.INCIDENT_READ,
        Permissions.ANPR_SEARCH
    ]
}

def has_permission(role: str, permission: str) -> bool:
    """Check if a specific role contains a given permission."""
    permissions = ROLE_PERMISSIONS.get(role, [])
    return permission in permissions
