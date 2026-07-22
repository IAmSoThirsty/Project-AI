"""Versioned human-authentication HTTP routes."""

import ipaddress
from typing import Annotated, Literal, cast
from urllib.parse import urlsplit

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, Security, status
from fastapi.security import APIKeyCookie

from accounts import (
    Account,
    AccountConflict,
    AccountLocked,
    AccountRole,
    AccountService,
    AccountServiceError,
    BootstrapUnavailable,
    InvalidBootstrapSecret,
    InvalidCredentials,
    InvalidCsrf,
    InvalidMfa,
    InvalidRecovery,
    InvalidSession,
    MachineCredential,
    MfaRequired,
    MfaUnavailable,
    PasswordRejected,
    PermissionDenied,
    RateLimited,
    SessionBundle,
    StoredSession,
)
from project_ai_api.models import (
    AccountCreateRequest,
    AccountCreateResponse,
    AccountRoleRequest,
    AccountsResponse,
    AccountStatusRequest,
    AuthAccount,
    BootstrapRequest,
    BootstrapResponse,
    BootstrapStatusResponse,
    LoginRequest,
    MachineCredentialCreateRequest,
    MachineCredentialCreateResponse,
    MachineCredentialsResponse,
    ManagedAccount,
    MessageResponse,
    MfaCodeRequest,
    MfaDisableRequest,
    MfaEnrollmentRequest,
    MfaEnrollmentResponse,
    MfaStatusResponse,
    PasswordChangeRequest,
    RecoveryCompleteRequest,
    RecoveryStartRequest,
    SecurityEventResponse,
    SecurityEventsResponse,
    SessionInfo,
    SessionResponse,
    SessionsResponse,
)
from project_ai_api.models import (
    MachineCredential as MachineCredentialResponse,
)

SESSION_COOKIE = "project_ai_session"
CSRF_COOKIE = "project_ai_csrf"
COOKIE_MAX_AGE = 12 * 60 * 60

# Declared once so every session-authenticated route advertises the same OpenAPI
# security scheme; auto_error=False keeps each route's own 401/503 semantics.
SESSION_COOKIE_SCHEME = APIKeyCookie(
    name=SESSION_COOKIE,
    scheme_name="sessionCookie",
    description="Opaque server-side human session cookie; grants no machine capability.",
    auto_error=False,
)


def _source(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def request_source(request: Request) -> str:
    """Return the bounded source identity used by durable interface rate limits."""
    return _source(request)


def _user_agent(request: Request) -> str:
    return request.headers.get("user-agent", "unknown")


def _loopback_source(request: Request, trust_private_proxy: bool = False) -> bool:
    host = _source(request)
    if host == "testclient":
        return True
    try:
        immediate = ipaddress.ip_address(host)
    except ValueError:
        return False
    if immediate.is_loopback:
        return True
    if not trust_private_proxy or not immediate.is_private:
        return False
    forwarded = request.headers.get("x-forwarded-for", "").split(",", maxsplit=1)[0].strip()
    try:
        forwarded_ip = ipaddress.ip_address(forwarded)
        return forwarded_ip.is_loopback or forwarded_ip.is_private
    except ValueError:
        return False


def _require_same_origin(request: Request) -> None:
    """Reject browser state changes submitted by a different web origin."""
    origin = request.headers.get("origin")
    if origin is None:
        return
    parsed = urlsplit(origin)
    request_port = request.url.port or (443 if request.url.scheme == "https" else 80)
    origin_port = parsed.port or (443 if parsed.scheme == "https" else 80)
    if (
        parsed.scheme != request.url.scheme
        or parsed.hostname != request.url.hostname
        or origin_port != request_port
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cross-origin authentication request rejected",
        )


def require_same_origin(request: Request) -> None:
    """Apply the human-interface same-origin policy outside the auth router."""
    _require_same_origin(request)


def _safe_account(account: Account) -> AuthAccount:
    return AuthAccount(
        id=account.id,
        username=account.username,
        display_name=account.display_name,
        role=account.role.value,
        actor_id=account.actor_id,
        mfa_enabled=account.mfa_enabled,
        status=cast(Literal["active", "disabled"], account.status),
        must_change_password=account.must_change_password,
    )


def _managed_account(account: Account) -> ManagedAccount:
    return ManagedAccount(
        **_safe_account(account).model_dump(), created_at=account.created_at.isoformat()
    )


def _machine_credential(item: object) -> MachineCredentialResponse:
    credential = cast("MachineCredential", item)
    return MachineCredentialResponse(
        id=credential.id,
        label=credential.label,
        scopes=cast(
            tuple[Literal["evidence.read", "evidence.write", "analysis.generate"], ...],
            credential.scopes,
        ),
        created_at=credential.created_at.isoformat(),
        created_by=credential.created_by,
        last_used_at=credential.last_used_at.isoformat() if credential.last_used_at else None,
        revoked_at=credential.revoked_at.isoformat() if credential.revoked_at else None,
    )


def _session_response(bundle: SessionBundle) -> SessionResponse:
    return SessionResponse(
        account=_safe_account(bundle.account),
        session_id=bundle.session.id,
        csrf_token=bundle.csrf_token,
        idle_expires_at=bundle.session.idle_expires_at.isoformat(),
        absolute_expires_at=bundle.session.absolute_expires_at.isoformat(),
        mfa_verified_at=(
            bundle.session.mfa_verified_at.isoformat() if bundle.session.mfa_verified_at else None
        ),
    )


def _set_session_cookies(response: Response, bundle: SessionBundle, secure: bool) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        bundle.token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        CSRF_COOKIE,
        bundle.csrf_token,
        max_age=COOKIE_MAX_AGE,
        httponly=False,
        secure=secure,
        samesite="strict",
        path="/",
    )


def _delete_session_cookies(response: Response, secure: bool) -> None:
    response.delete_cookie(SESSION_COOKIE, path="/", secure=secure, httponly=True)
    response.delete_cookie(CSRF_COOKIE, path="/", secure=secure, httponly=False)


def _raise_account_error(error: AccountServiceError) -> None:
    if isinstance(error, (AccountLocked, RateLimited)):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(error))
    if isinstance(error, (InvalidCredentials, InvalidBootstrapSecret, InvalidRecovery)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))
    if isinstance(error, InvalidCsrf):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
    if isinstance(error, InvalidSession):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))
    if isinstance(error, MfaRequired):
        raise HTTPException(status_code=status.HTTP_428_PRECONDITION_REQUIRED, detail=str(error))
    if isinstance(error, InvalidMfa):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))
    if isinstance(error, MfaUnavailable):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error))
    if isinstance(error, PermissionDenied):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
    if isinstance(error, BootstrapUnavailable):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
    if isinstance(error, AccountConflict):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
    if isinstance(error, PasswordRejected):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error))
    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error))


def install_auth_routes(
    application: FastAPI,
    account_service: AccountService | None,
    *,
    secure_cookie: bool,
    trust_private_bootstrap_proxy: bool = False,
) -> None:
    def service() -> AccountService:
        if account_service is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Human account storage is not configured",
            )
        return account_service

    def current(
        session_token: Annotated[str | None, Security(SESSION_COOKIE_SCHEME)] = None,
    ) -> tuple[Account, StoredSession, str]:
        if not session_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in required")
        try:
            account, session = service().authenticate(session_token)
        except AccountServiceError as error:
            _raise_account_error(error)
        return account, session, session_token

    @application.get("/api/v1/auth/bootstrap-status", response_model=BootstrapStatusResponse)
    def bootstrap_status() -> BootstrapStatusResponse:
        if account_service is None:
            return BootstrapStatusResponse(status="unconfigured", setup_secret_required=True)
        return BootstrapStatusResponse(
            status="required" if account_service.bootstrap_required() else "closed",
            setup_secret_required=account_service.bootstrap_required(),
        )

    @application.post("/api/v1/auth/bootstrap", response_model=BootstrapResponse)
    def bootstrap(
        request: Request, payload: BootstrapRequest, response: Response
    ) -> BootstrapResponse:
        _require_same_origin(request)
        if not _loopback_source(request, trust_private_bootstrap_proxy):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bootstrap is restricted to the loopback interface",
            )
        try:
            result = service().bootstrap(
                setup_secret=payload.setup_secret,
                username=payload.username,
                display_name=payload.display_name,
                password=payload.password,
                actor_id=payload.actor_id,
                source=_source(request),
                user_agent=_user_agent(request),
            )
        except AccountServiceError as error:
            _raise_account_error(error)
        _set_session_cookies(response, result.bundle, secure_cookie)
        base = _session_response(result.bundle)
        return BootstrapResponse(**base.model_dump(), recovery_codes=result.recovery_codes)

    @application.post("/api/v1/auth/login", response_model=SessionResponse)
    def login(request: Request, payload: LoginRequest, response: Response) -> SessionResponse:
        _require_same_origin(request)
        try:
            bundle = service().login(
                payload.username,
                payload.password,
                _source(request),
                _user_agent(request),
                payload.totp_code,
            )
        except AccountServiceError as error:
            _raise_account_error(error)
        _set_session_cookies(response, bundle, secure_cookie)
        return _session_response(bundle)

    @application.get("/api/v1/auth/session", response_model=SessionResponse)
    def session_state(
        session_context: Annotated[tuple[Account, StoredSession, str], Depends(current)],
    ) -> SessionResponse:
        account, session, _ = session_context
        return SessionResponse(
            account=_safe_account(account),
            session_id=session.id,
            csrf_token="",
            idle_expires_at=session.idle_expires_at.isoformat(),
            absolute_expires_at=session.absolute_expires_at.isoformat(),
            mfa_verified_at=(
                session.mfa_verified_at.isoformat() if session.mfa_verified_at else None
            ),
        )

    @application.post("/api/v1/auth/session/refresh", response_model=SessionResponse)
    def refresh_session(
        request: Request,
        response: Response,
        session_context: Annotated[tuple[Account, StoredSession, str], Depends(current)],
        csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    ) -> SessionResponse:
        _require_same_origin(request)
        _, _, token = session_context
        try:
            bundle = service().rotate_session(
                token, csrf_token, _source(request), _user_agent(request)
            )
        except AccountServiceError as error:
            _raise_account_error(error)
        _set_session_cookies(response, bundle, secure_cookie)
        return _session_response(bundle)

    @application.post("/api/v1/auth/logout", response_model=MessageResponse)
    def logout(
        request: Request,
        response: Response,
        session_context: Annotated[tuple[Account, StoredSession, str], Depends(current)],
        csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    ) -> MessageResponse:
        _require_same_origin(request)
        _, _, token = session_context
        try:
            service().logout(token, csrf_token, _source(request))
        except AccountServiceError as error:
            _raise_account_error(error)
        _delete_session_cookies(response, secure_cookie)
        return MessageResponse(message="Signed out")

    @application.get("/api/v1/auth/sessions", response_model=SessionsResponse)
    def list_sessions(
        session_context: Annotated[tuple[Account, StoredSession, str], Depends(current)],
    ) -> SessionsResponse:
        account, current_session, _ = session_context
        return SessionsResponse(
            sessions=tuple(
                SessionInfo(
                    id=item.id,
                    current=item.id == current_session.id,
                    created_at=item.created_at.isoformat(),
                    last_seen_at=item.last_seen_at.isoformat(),
                    idle_expires_at=item.idle_expires_at.isoformat(),
                    absolute_expires_at=item.absolute_expires_at.isoformat(),
                    user_agent=item.user_agent,
                    client_host=item.client_host,
                    revoked=item.revoked_at is not None,
                    mfa_verified_at=(
                        item.mfa_verified_at.isoformat() if item.mfa_verified_at else None
                    ),
                )
                for item in service().repository.sessions_for_account(account.id)
            )
        )

    @application.delete("/api/v1/auth/sessions/{session_id}", response_model=MessageResponse)
    def revoke_session(
        session_id: str,
        request: Request,
        session_context: Annotated[tuple[Account, StoredSession, str], Depends(current)],
        csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    ) -> MessageResponse:
        _require_same_origin(request)
        _, _, token = session_context
        try:
            service().revoke_session(token, csrf_token, session_id, _source(request))
        except AccountServiceError as error:
            _raise_account_error(error)
        return MessageResponse(message="Session revoked")

    @application.post("/api/v1/auth/password/change", response_model=MessageResponse)
    def change_password(
        payload: PasswordChangeRequest,
        request: Request,
        response: Response,
        session_context: Annotated[tuple[Account, StoredSession, str], Depends(current)],
        csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    ) -> MessageResponse:
        _require_same_origin(request)
        _, _, token = session_context
        try:
            service().change_password(
                token,
                csrf_token,
                payload.current_password,
                payload.new_password,
                _source(request),
            )
        except AccountServiceError as error:
            _raise_account_error(error)
        _delete_session_cookies(response, secure_cookie)
        return MessageResponse(message="Password changed; sign in again")

    @application.get("/api/v1/auth/mfa", response_model=MfaStatusResponse)
    def mfa_status(
        session_context: Annotated[tuple[Account, StoredSession, str], Depends(current)],
    ) -> MfaStatusResponse:
        account, _, _ = session_context
        return MfaStatusResponse(
            enabled=account.mfa_enabled,
            enrollment_pending=bool(account.mfa_secret_ciphertext and not account.mfa_enabled),
        )

    @application.post("/api/v1/auth/mfa/enroll", response_model=MfaEnrollmentResponse)
    def mfa_enroll(
        payload: MfaEnrollmentRequest,
        request: Request,
        session_context: Annotated[tuple[Account, StoredSession, str], Depends(current)],
        csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    ) -> MfaEnrollmentResponse:
        _require_same_origin(request)
        _, _, token = session_context
        try:
            enrollment = service().begin_mfa_enrollment(
                token, csrf_token, payload.current_password, _source(request)
            )
        except AccountServiceError as error:
            _raise_account_error(error)
        return MfaEnrollmentResponse(
            secret=enrollment.secret, provisioning_uri=enrollment.provisioning_uri
        )

    @application.post("/api/v1/auth/mfa/confirm", response_model=MessageResponse)
    def mfa_confirm(
        payload: MfaCodeRequest,
        request: Request,
        session_context: Annotated[tuple[Account, StoredSession, str], Depends(current)],
        csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    ) -> MessageResponse:
        _require_same_origin(request)
        _, _, token = session_context
        try:
            service().confirm_mfa_enrollment(token, csrf_token, payload.code, _source(request))
        except AccountServiceError as error:
            _raise_account_error(error)
        return MessageResponse(message="Authenticator enabled")

    @application.post("/api/v1/auth/mfa/step-up", response_model=MessageResponse)
    def mfa_step_up(
        payload: MfaCodeRequest,
        request: Request,
        session_context: Annotated[tuple[Account, StoredSession, str], Depends(current)],
        csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    ) -> MessageResponse:
        _require_same_origin(request)
        _, _, token = session_context
        try:
            service().step_up_mfa(token, csrf_token, payload.code, _source(request))
        except AccountServiceError as error:
            _raise_account_error(error)
        return MessageResponse(message="Step-up authentication completed")

    @application.delete("/api/v1/auth/mfa", response_model=MessageResponse)
    def mfa_disable(
        payload: MfaDisableRequest,
        request: Request,
        response: Response,
        session_context: Annotated[tuple[Account, StoredSession, str], Depends(current)],
        csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    ) -> MessageResponse:
        _require_same_origin(request)
        _, _, token = session_context
        try:
            service().disable_mfa(
                token,
                csrf_token,
                payload.current_password,
                payload.code,
                _source(request),
            )
        except AccountServiceError as error:
            _raise_account_error(error)
        _delete_session_cookies(response, secure_cookie)
        return MessageResponse(message="Authenticator disabled; sign in again")

    @application.post("/api/v1/auth/recovery/start", response_model=MessageResponse)
    def recovery_start(payload: RecoveryStartRequest) -> MessageResponse:
        _ = payload
        return MessageResponse(
            message="If local recovery is available, continue with a saved recovery code."
        )

    @application.post("/api/v1/auth/recovery/complete", response_model=MessageResponse)
    def recovery_complete(
        payload: RecoveryCompleteRequest, request: Request, response: Response
    ) -> MessageResponse:
        _require_same_origin(request)
        try:
            service().recover(
                payload.username, payload.recovery_code, payload.new_password, _source(request)
            )
        except AccountServiceError as error:
            _raise_account_error(error)
        _delete_session_cookies(response, secure_cookie)
        return MessageResponse(message="Recovery completed; sign in with the new password")

    @application.get("/api/v1/me", response_model=AuthAccount)
    def me(
        session_context: Annotated[tuple[Account, StoredSession, str], Depends(current)],
    ) -> AuthAccount:
        account, _, _ = session_context
        return _safe_account(account)

    @application.get("/api/v1/admin/accounts", response_model=AccountsResponse)
    def admin_accounts(
        session_context: Annotated[tuple[Account, StoredSession, str], Depends(current)],
    ) -> AccountsResponse:
        _, _, token = session_context
        try:
            accounts = service().list_accounts(token)
        except AccountServiceError as error:
            _raise_account_error(error)
        return AccountsResponse(accounts=tuple(_managed_account(item) for item in accounts))

    @application.post("/api/v1/admin/accounts", response_model=AccountCreateResponse)
    def admin_create_account(
        payload: AccountCreateRequest,
        request: Request,
        session_context: Annotated[tuple[Account, StoredSession, str], Depends(current)],
        csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    ) -> AccountCreateResponse:
        _require_same_origin(request)
        _, _, token = session_context
        try:
            result = service().create_managed_account(
                token,
                csrf_token,
                username=payload.username,
                display_name=payload.display_name,
                password=payload.password,
                role=AccountRole(payload.role),
                actor_id=payload.actor_id,
                source=_source(request),
            )
        except AccountServiceError as error:
            _raise_account_error(error)
        return AccountCreateResponse(
            account=_managed_account(result.account), recovery_codes=result.recovery_codes
        )

    @application.post("/api/v1/admin/accounts/{account_id}/role", response_model=MessageResponse)
    def admin_change_role(
        account_id: str,
        payload: AccountRoleRequest,
        request: Request,
        session_context: Annotated[tuple[Account, StoredSession, str], Depends(current)],
        csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    ) -> MessageResponse:
        _require_same_origin(request)
        _, _, token = session_context
        try:
            service().set_managed_account_role(
                token, csrf_token, account_id, AccountRole(payload.role), _source(request)
            )
        except AccountServiceError as error:
            _raise_account_error(error)
        return MessageResponse(message="Account role changed; active sessions revoked")

    @application.post("/api/v1/admin/accounts/{account_id}/status", response_model=MessageResponse)
    def admin_change_status(
        account_id: str,
        payload: AccountStatusRequest,
        request: Request,
        session_context: Annotated[tuple[Account, StoredSession, str], Depends(current)],
        csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    ) -> MessageResponse:
        _require_same_origin(request)
        _, _, token = session_context
        try:
            service().set_managed_account_status(
                token, csrf_token, account_id, payload.enabled, _source(request)
            )
        except AccountServiceError as error:
            _raise_account_error(error)
        return MessageResponse(message="Account status changed")

    @application.get("/api/v1/admin/machine-credentials", response_model=MachineCredentialsResponse)
    def admin_machine_credentials(
        session_context: Annotated[tuple[Account, StoredSession, str], Depends(current)],
    ) -> MachineCredentialsResponse:
        _, _, token = session_context
        try:
            credentials = service().list_machine_credentials(token)
        except AccountServiceError as error:
            _raise_account_error(error)
        return MachineCredentialsResponse(
            credentials=tuple(_machine_credential(item) for item in credentials)
        )

    @application.post(
        "/api/v1/admin/machine-credentials",
        response_model=MachineCredentialCreateResponse,
    )
    def admin_create_machine_credential(
        payload: MachineCredentialCreateRequest,
        request: Request,
        session_context: Annotated[tuple[Account, StoredSession, str], Depends(current)],
        csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    ) -> MachineCredentialCreateResponse:
        _require_same_origin(request)
        _, _, token = session_context
        try:
            result = service().create_machine_credential(
                token,
                csrf_token,
                label=payload.label,
                scopes=tuple(payload.scopes),
                source=_source(request),
            )
        except AccountServiceError as error:
            _raise_account_error(error)
        return MachineCredentialCreateResponse(
            credential=_machine_credential(result.credential), token=result.token
        )

    @application.post(
        "/api/v1/admin/machine-credentials/{credential_id}/revoke",
        response_model=MessageResponse,
    )
    def admin_revoke_machine_credential(
        credential_id: str,
        request: Request,
        session_context: Annotated[tuple[Account, StoredSession, str], Depends(current)],
        csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    ) -> MessageResponse:
        _require_same_origin(request)
        _, _, token = session_context
        try:
            service().revoke_machine_credential(token, csrf_token, credential_id, _source(request))
        except AccountServiceError as error:
            _raise_account_error(error)
        return MessageResponse(message="Machine credential revoked")

    @application.get("/api/v1/admin/security-events", response_model=SecurityEventsResponse)
    def admin_security_events(
        session_context: Annotated[tuple[Account, StoredSession, str], Depends(current)],
    ) -> SecurityEventsResponse:
        _, _, token = session_context
        try:
            events = service().list_security_events(token)
        except AccountServiceError as error:
            _raise_account_error(error)
        return SecurityEventsResponse(
            events=tuple(
                SecurityEventResponse(
                    id=item.id,
                    event_type=item.event_type,
                    account_id=item.account_id,
                    occurred_at=item.occurred_at.isoformat(),
                    source=item.source,
                    detail=item.detail,
                )
                for item in events
            )
        )
