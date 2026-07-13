from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..auth import agent_user, current_user
from ..db import execute, fetch_all, fetch_one

router = APIRouter()


class ChatMessageBody(BaseModel):
    userId: UUID | None = None
    message: str


@router.get("/agent/chat/threads")
def list_agent_chat_threads(user: Annotated[dict, Depends(agent_user)]):
    return fetch_all(
        """
        SELECT
          u.id AS user_id,
          u.full_name,
          u.email,
          u.avatar_url,
          u.plan,
          u.last_active_at,
          latest.message AS last_message,
          latest.created_at AS last_message_at,
          COALESCE(unread.unread_count, 0)::int AS unread_count
        FROM users u
        JOIN (
          SELECT DISTINCT user_id
          FROM agent_messages
          WHERE agent_id = %s
          UNION
          SELECT user_id
          FROM agent_user_shares
          WHERE agent_id = %s
          UNION
          SELECT a.user_id
          FROM applications a
          JOIN agent_job_assignments aja ON aja.job_id = a.job_id
          WHERE aja.agent_id = %s
        ) visible ON visible.user_id = u.id
        LEFT JOIN LATERAL (
          SELECT message, created_at
          FROM agent_messages
          WHERE agent_id = %s AND user_id = u.id
          ORDER BY created_at DESC
          LIMIT 1
        ) latest ON true
        LEFT JOIN LATERAL (
          SELECT COUNT(*) AS unread_count
          FROM agent_messages
          WHERE agent_id = %s AND user_id = u.id AND sender_role = 'user' AND read_at IS NULL
        ) unread ON true
        WHERE u.role IN ('member', 'user')
        ORDER BY latest.created_at DESC NULLS LAST, u.full_name
        """,
        (user["id"], user["id"], user["id"], user["id"], user["id"]),
    )


@router.get("/agent/chat/messages")
def list_agent_chat_messages(user_id: UUID, user: Annotated[dict, Depends(agent_user)]):
    target = fetch_one("SELECT id FROM users WHERE id = %s AND role IN ('member', 'user')", (user_id,))
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    execute(
        "UPDATE agent_messages SET read_at = NOW() WHERE agent_id = %s AND user_id = %s AND sender_role = 'user' AND read_at IS NULL",
        (user["id"], user_id),
    )
    return fetch_all(
        """
        SELECT *
        FROM agent_messages
        WHERE agent_id = %s AND user_id = %s
        ORDER BY created_at ASC
        """,
        (user["id"], user_id),
    )


@router.post("/agent/chat/messages", status_code=201)
def create_agent_chat_message(body: ChatMessageBody, user: Annotated[dict, Depends(agent_user)]):
    if not body.userId:
        raise HTTPException(status_code=400, detail="User is required")
    target = fetch_one("SELECT id FROM users WHERE id = %s AND role IN ('member', 'user')", (body.userId,))
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    return execute(
        """
        INSERT INTO agent_messages (agent_id, user_id, sender_role, message)
        VALUES (%s,%s,'agent',%s)
        RETURNING *
        """,
        (user["id"], body.userId, body.message),
    )


@router.get("/user/agent-chat/messages")
def list_user_agent_chat_messages(agent_id: UUID, user: Annotated[dict, Depends(current_user)]):
    agent = fetch_one("SELECT id FROM users WHERE id = %s AND role = 'agent'", (agent_id,))
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    execute(
        "UPDATE agent_messages SET read_at = NOW() WHERE agent_id = %s AND user_id = %s AND sender_role = 'agent' AND read_at IS NULL",
        (agent_id, user["id"]),
    )
    return fetch_all(
        """
        SELECT *
        FROM agent_messages
        WHERE agent_id = %s AND user_id = %s
        ORDER BY created_at ASC
        """,
        (agent_id, user["id"]),
    )


@router.post("/user/agent-chat/messages", status_code=201)
def create_user_agent_chat_message(body: ChatMessageBody, user: Annotated[dict, Depends(current_user)]):
    if not body.userId:
        raise HTTPException(status_code=400, detail="Agent is required")
    agent = fetch_one("SELECT id FROM users WHERE id = %s AND role = 'agent'", (body.userId,))
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return execute(
        """
        INSERT INTO agent_messages (agent_id, user_id, sender_role, message)
        VALUES (%s,%s,'user',%s)
        RETURNING *
        """,
        (body.userId, user["id"], body.message),
    )
