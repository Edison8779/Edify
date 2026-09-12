"""
Audit Service
"""
import uuid
from typing import Any, Optional
from app.models.audit_log import AuditLog
from app.repositories.audit import AuditRepository
from app.core.logging import request_id_ctx

class AuditService:
    def __init__(self, audit_repo: AuditRepository):
        self.audit_repo = audit_repo

    async def log_action(
        self,
        action: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        actor_user_id: Optional[uuid.UUID] = None,
        old_values: Optional[dict[str, Any]] = None,
        new_values: Optional[dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        *,
        actor_id: Optional[uuid.UUID] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> AuditLog:
        actual_actor_id = actor_user_id or actor_id
        actual_entity_type = entity_type or target_type or "unknown"
        actual_entity_id = entity_id or target_id or "unknown"
        actual_new_values = new_values or details

        audit_log = AuditLog(
            actor_user_id=actual_actor_id,
            action=action,
            entity_type=actual_entity_type,
            entity_id=actual_entity_id,
            old_values=old_values,
            new_values=actual_new_values,
            request_id=request_id_ctx.get(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        return await self.audit_repo.create_audit_log(audit_log)

