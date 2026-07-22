"""Server-side human-interface permissions; never execution authority."""

from enum import StrEnum

from accounts.models import AccountRole


class InterfacePermission(StrEnum):
    DASHBOARD_VIEW = "dashboard.view"
    EVIDENCE_VIEW = "evidence.view"
    SESSIONS_MANAGE_OWN = "sessions.manage_own"
    ACCOUNTS_MANAGE = "accounts.manage"
    ROLES_MANAGE = "roles.manage"
    SECURITY_EVENTS_VIEW = "security_events.view"
    REQUEST_SUBMIT = "requests.submit"
    REQUEST_REVIEW = "requests.review"
    MODULE_ANALYSIS_RUN = "modules.analysis.run"
    TAAR_VIEW = "taar.view"
    TAAR_RUN_READER = "taar.run_reader"
    MODULE_EXECUTION_INITIATE = "modules.execution.initiate"
    AUDIT_EXPORT = "audit.export"
    AUDIT_RAW_VIEW = "audit.raw_view"
    SYSTEM_CONFIGURE = "system.configure"


_READ = {
    InterfacePermission.DASHBOARD_VIEW,
    InterfacePermission.EVIDENCE_VIEW,
    InterfacePermission.SESSIONS_MANAGE_OWN,
}

ROLE_PERMISSIONS: dict[AccountRole, frozenset[InterfacePermission]] = {
    AccountRole.OWNER: frozenset(InterfacePermission),
    AccountRole.ADMINISTRATOR: frozenset(InterfacePermission),
    AccountRole.OPERATOR: frozenset(
        _READ
        | {
            InterfacePermission.REQUEST_SUBMIT,
            InterfacePermission.MODULE_ANALYSIS_RUN,
            InterfacePermission.MODULE_EXECUTION_INITIATE,
            InterfacePermission.TAAR_VIEW,
            InterfacePermission.TAAR_RUN_READER,
        }
    ),
    AccountRole.REVIEWER: frozenset(
        _READ
        | {
            InterfacePermission.REQUEST_REVIEW,
            InterfacePermission.MODULE_ANALYSIS_RUN,
            InterfacePermission.AUDIT_EXPORT,
            InterfacePermission.TAAR_VIEW,
        }
    ),
    AccountRole.AUDITOR: frozenset(
        _READ
        | {
            InterfacePermission.MODULE_ANALYSIS_RUN,
            InterfacePermission.AUDIT_EXPORT,
            InterfacePermission.AUDIT_RAW_VIEW,
            InterfacePermission.TAAR_VIEW,
        }
    ),
    AccountRole.VIEWER: frozenset(_READ),
}


def has_permission(role: AccountRole, permission: InterfacePermission) -> bool:
    return permission in ROLE_PERMISSIONS[role]
