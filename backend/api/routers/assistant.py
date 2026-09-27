"""/api/v1/assistant — Trợ lý tra cứu Human Design (widget chat).

Agent ReAct chạy trên chuỗi LLM đã cấu hình (Cài đặt → AI / LLM): user được
chọn model, mỗi lượt chat log đầy đủ token/chi phí vào ``chat_messages`` và
``llm_usage`` (purpose="chat").
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.reporting.assistant import agent_turn_events, run_agent_turn
from backend.reporting.llm_client import LLMError, estimate_cost

from ..assistant_tools import make_executor
from ..deps import current_user, get_db, require_admin
from ..models import ChatMessage, ChatSession, User
from ..schemas import (
    AssistantModelOut, ChatAdminSessionOut, ChatAdminStatsOut, ChatMessageOut, ChatRateIn, ChatSendIn, ChatSendOut,
    ChatSessionDetailOut, ChatSessionOut, ChatUserStat,
)
from ..services import collect_attempts, org_llm_configs, save_llm_usages

router = APIRouter(prefix="/assistant", tags=["assistant"])

CHAT_HOURLY_LIMIT = 60
HISTORY_TURNS = 12


def _session_out(session: ChatSession) -> ChatSessionOut:
    return ChatSessionOut(
        id=session.id, title=session.title, provider=session.provider, model=session.model,
        message_count=session.message_count, total_cost_usd=session.total_cost_usd,
        created_at=session.created_at, updated_at=session.updated_at,
    )


def _message_out(message: ChatMessage) -> ChatMessageOut:
    return ChatMessageOut(
        id=message.id, role=message.role, content=message.content,
        tools_used=list(message.tools_used or []), sources=list(message.sources or []),
        prompt_tokens=message.prompt_tokens, completion_tokens=message.completion_tokens,
        cost_usd=message.cost_usd, latency_ms=message.latency_ms, rating=message.rating,
        created_at=message.created_at,
    )


def _effective_message(payload: ChatSendIn) -> str:
    """Câu hỏi gửi cho LLM, kèm ghi chú ngữ cảnh (trang đang xem) nếu có."""
    notes = []
    if payload.context_client_id:
        notes.append(f"đang xem hồ sơ khách hàng #{payload.context_client_id} "
                     "(ưu tiên dùng client_chart với client_id này khi câu hỏi liên quan tới khách hàng)")
    if payload.context_report_id:
        notes.append(f"đang xem báo cáo {payload.context_report_id} "
                     "(ưu tiên dùng report_info với report_id này khi câu hỏi liên quan tới báo cáo)")
    if not notes:
        return payload.message
    return "[Ngữ cảnh: " + "; ".join(notes) + "]\n" + payload.message


def _price_turn(attempts: list) -> tuple[float, bool]:
    turn_cost, priced = 0.0, False
    for entry in attempts:
        usage = entry["usage"]
        if usage is None:
            continue
        cost = estimate_cost(usage, entry["config"].input_price, entry["config"].output_price)
        if cost is not None:
            priced = True
            turn_cost += cost
    return turn_cost, priced


def _prepare_turn(db: Session, user: User, secret: str, payload: ChatSendIn):
    """Kiểm tra chain/rate-limit/session chung cho /chat và /chat/stream."""
    chain = _chain_or_503(db, user, secret)
    if payload.model_index >= len(chain):
        raise HTTPException(status_code=422, detail="Mô hình đã chọn không còn khả dụng, hãy chọn lại.")
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=1)
    recent = db.scalar(select(func.count()).select_from(ChatMessage).join(ChatSession)
                       .where(ChatSession.user_id == user.id, ChatMessage.role == "user",
                              ChatMessage.created_at >= cutoff)) or 0
    if recent >= CHAT_HOURLY_LIMIT:
        raise HTTPException(status_code=429, detail="Bạn đã hỏi quá 60 câu trong 1 giờ, hãy nghỉ một lát rồi hỏi tiếp.")

    if payload.session_id:
        session = db.get(ChatSession, payload.session_id)
        if session is None or session.user_id != user.id:
            raise HTTPException(status_code=404, detail="Không tìm thấy cuộc trò chuyện.")
    else:
        title = " ".join(payload.message.split())[:60] or "Cuộc trò chuyện mới"
        session = ChatSession(id=str(uuid4()), org_id=user.org_id, user_id=user.id, title=title)
        db.add(session)
        db.flush()

    ordered = chain[payload.model_index:] + chain[:payload.model_index]
    rows = db.scalars(select(ChatMessage).where(ChatMessage.session_id == session.id)
                      .order_by(ChatMessage.id.desc()).limit(HISTORY_TURNS)).all()
    history = [{"role": m.role, "content": m.content[:1500]} for m in reversed(rows)]
    return ordered, session, history


def _chain_or_503(db: Session, user: User, secret: str):
    chain = org_llm_configs(db, user.org_id, secret)
    if not chain:
        raise HTTPException(status_code=503, detail="AI chưa được cấu hình (Cài đặt → AI / LLM hoặc HD_LLM_API_KEY).")
    return chain


@router.get("/models", response_model=list[AssistantModelOut])
def list_models(request: Request, user: User = Depends(current_user),
                db: Session = Depends(get_db)) -> list[AssistantModelOut]:
    chain = org_llm_configs(db, user.org_id, request.app.state.secret_key)
    return [AssistantModelOut(index=i, name=c.name or f"Nhà cung cấp {i + 1}", model=c.model)
            for i, c in enumerate(chain)]


@router.post("/chat", response_model=ChatSendOut)
def chat(payload: ChatSendIn, request: Request, user: User = Depends(current_user),
         db: Session = Depends(get_db)) -> ChatSendOut:
    ordered, session, history = _prepare_turn(db, user, request.app.state.secret_key, payload)
    selected = ordered[0]

    attempts: list = []
    started = time.perf_counter()
    try:
        result = run_agent_turn(_effective_message(payload), history, ordered, make_executor(db, user),
                                transport=request.app.state.llm_transport,
                                on_llm_attempt=collect_attempts(attempts),
                                temperature=0.2)  # chat tra cứu: ổn định, ít bịa
    except LLMError as exc:
        raise HTTPException(status_code=503, detail=f"AI đang bận, thử lại sau: {exc}") from exc
    latency_ms = int((time.perf_counter() - started) * 1000)

    turn_cost, priced = _price_turn(attempts)
    db.add(ChatMessage(session_id=session.id, role="user", content=payload.message))
    assistant_message = ChatMessage(
        session_id=session.id, role="assistant", content=result.answer,
        tools_used=result.tools_used, sources=result.sources,
        prompt_tokens=result.prompt_tokens, completion_tokens=result.completion_tokens,
        cost_usd=turn_cost if priced else None, latency_ms=latency_ms,
    )
    db.add(assistant_message)
    save_llm_usages(db, user.org_id, None, "chat", attempts)
    session.message_count = (session.message_count or 0) + 2
    session.total_cost_usd = (session.total_cost_usd or 0.0) + (turn_cost if priced else 0.0)
    session.provider = selected.name or f"Nhà cung cấp {payload.model_index + 1}"
    session.model = selected.model
    db.commit()
    db.refresh(assistant_message)
    return ChatSendOut(session=_session_out(session), message=_message_out(assistant_message),
                       provider=session.provider, model=session.model)


def _sse(name: str, data: object) -> str:
    return f"event: {name}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/chat/stream")
def chat_stream(payload: ChatSendIn, request: Request, user: User = Depends(current_user),
                db: Session = Depends(get_db)) -> StreamingResponse:
    """Chat có stream SSE: ``meta`` → ``token``*/``tool``* → ``done`` (hoặc ``error``)."""
    ordered, session, history = _prepare_turn(db, user, request.app.state.secret_key, payload)
    selected = ordered[0]
    session_id, user_id, org_id = session.id, user.id, user.org_id
    provider_label = selected.name or f"Nhà cung cấp {payload.model_index + 1}"
    model_name, effective = selected.model, _effective_message(payload)
    # Lưu tin nhắn user ngay để không mất khi client ngắt giữa chừng.
    db.add(ChatMessage(session_id=session_id, role="user", content=payload.message))
    session.message_count = (session.message_count or 0) + 1
    db.commit()

    transport = request.app.state.llm_transport
    factory = request.app.state.db.session_factory

    def _generate():  # chạy trong threadpool → dùng session DB riêng, không chạm object của request
        gdb = factory()
        try:
            yield _sse("meta", {"session_id": session_id, "provider": provider_label, "model": model_name})
            attempts: list = []
            agent_user = gdb.get(User, user_id)
            started = time.perf_counter()
            try:
                events = agent_turn_events(effective, history, ordered, make_executor(gdb, agent_user),
                                           transport=transport, on_llm_attempt=collect_attempts(attempts),
                                           temperature=0.2)  # chat tra cứu: ổn định, ít bịa
                final = None
                for kind, data in events:
                    if kind == "token":
                        yield _sse("token", {"text": data})
                    elif kind == "tool_start":
                        yield _sse("tool", {"phase": "start", "tool": data})
                    elif kind == "tool_done":
                        yield _sse("tool", {"phase": "done", **data})
                    elif kind == "result":
                        final = data
            except LLMError as exc:
                save_llm_usages(gdb, org_id, None, "chat", attempts)
                gdb.commit()
                yield _sse("error", {"message": f"AI đang bận, thử lại sau: {exc}"})
                return
            assert final is not None
            latency_ms = int((time.perf_counter() - started) * 1000)
            turn_cost, priced = _price_turn(attempts)
            assistant_message = ChatMessage(
                session_id=session_id, role="assistant", content=final.answer,
                tools_used=final.tools_used, sources=final.sources,
                prompt_tokens=final.prompt_tokens, completion_tokens=final.completion_tokens,
                cost_usd=turn_cost if priced else None, latency_ms=latency_ms,
            )
            gdb.add(assistant_message)
            save_llm_usages(gdb, org_id, None, "chat", attempts)
            live = gdb.get(ChatSession, session_id)
            live.message_count = (live.message_count or 0) + 1
            live.total_cost_usd = (live.total_cost_usd or 0.0) + (turn_cost if priced else 0.0)
            live.provider, live.model = provider_label, model_name
            gdb.commit()
            gdb.refresh(assistant_message)
            yield _sse("done", {"message": _message_out(assistant_message).model_dump(mode="json")})
        finally:
            gdb.close()

    return StreamingResponse(_generate(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.post("/messages/{message_id}/rate", response_model=ChatMessageOut)
def rate_message(message_id: int, body: ChatRateIn, user: User = Depends(current_user),
                 db: Session = Depends(get_db)) -> ChatMessageOut:
    """Đánh giá 👍/👎 (hoặc 0 để gỡ) cho một câu trả lời của trợ lý."""
    message = db.get(ChatMessage, message_id)
    if message is None or message.role != "assistant":
        raise HTTPException(status_code=404, detail="Không tìm thấy câu trả lời.")
    session = db.get(ChatSession, message.session_id)
    if session is None or (session.user_id != user.id
                            and (user.role != "admin" or session.org_id != user.org_id)):
        raise HTTPException(status_code=404, detail="Không tìm thấy câu trả lời.")
    message.rating = body.rating if body.rating != 0 else None
    db.commit()
    db.refresh(message)
    return _message_out(message)


@router.get("/sessions", response_model=list[ChatSessionOut])
def list_sessions(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[ChatSessionOut]:
    rows = db.scalars(select(ChatSession).where(ChatSession.user_id == user.id)
                      .order_by(ChatSession.updated_at.desc()).limit(50)).all()
    return [_session_out(s) for s in rows]


def _readable_session(db: Session, user: User, session_id: str) -> ChatSession:
    session = db.get(ChatSession, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy cuộc trò chuyện.")
    if session.user_id != user.id and (user.role != "admin" or session.org_id != user.org_id):
        raise HTTPException(status_code=404, detail="Không tìm thấy cuộc trò chuyện.")
    return session


@router.get("/sessions/{session_id}", response_model=ChatSessionDetailOut)
def get_session(session_id: str, user: User = Depends(current_user),
                db: Session = Depends(get_db)) -> ChatSessionDetailOut:
    session = _readable_session(db, user, session_id)
    rows = db.scalars(select(ChatMessage).where(ChatMessage.session_id == session.id)
                      .order_by(ChatMessage.id).limit(200)).all()
    return ChatSessionDetailOut(session=_session_out(session), messages=[_message_out(m) for m in rows])


@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(session_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)) -> None:
    session = _readable_session(db, user, session_id)
    for message in db.scalars(select(ChatMessage).where(ChatMessage.session_id == session.id)).all():
        db.delete(message)
    db.delete(session)
    db.commit()


@router.get("/admin/stats", response_model=ChatAdminStatsOut)
def admin_stats(days: int = Query(30, ge=1, le=365), user: User = Depends(require_admin),
                db: Session = Depends(get_db)) -> ChatAdminStatsOut:
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)
    sessions = db.scalar(select(func.count()).select_from(ChatSession)
                         .where(ChatSession.org_id == user.org_id, ChatSession.created_at >= cutoff)) or 0
    totals = db.execute(
        select(func.count(), func.coalesce(func.sum(ChatMessage.prompt_tokens), 0),
               func.coalesce(func.sum(ChatMessage.completion_tokens), 0),
               func.coalesce(func.sum(ChatMessage.cost_usd), 0.0))
        .select_from(ChatMessage).join(ChatSession)
        .where(ChatSession.org_id == user.org_id, ChatMessage.role == "assistant",
               ChatMessage.created_at >= cutoff)).one()
    user_rows = db.execute(
        select(User.id, User.email, User.full_name, func.count(func.distinct(ChatSession.id)),
               func.count(ChatMessage.id), func.coalesce(func.sum(ChatMessage.cost_usd), 0.0))
        .select_from(User).join(ChatSession, ChatSession.user_id == User.id)
        .outerjoin(ChatMessage, (ChatMessage.session_id == ChatSession.id) & (ChatMessage.role == "assistant"))
        .where(User.org_id == user.org_id, ChatSession.created_at >= cutoff)
        .group_by(User.id, User.email, User.full_name)
        .order_by(func.count(ChatMessage.id).desc())).all()
    likes = db.scalar(select(func.count()).select_from(ChatMessage).join(ChatSession)
                      .where(ChatSession.org_id == user.org_id, ChatMessage.role == "assistant",
                             ChatMessage.rating == 1, ChatMessage.created_at >= cutoff)) or 0
    dislikes = db.scalar(select(func.count()).select_from(ChatMessage).join(ChatSession)
                         .where(ChatSession.org_id == user.org_id, ChatMessage.role == "assistant",
                                ChatMessage.rating == -1, ChatMessage.created_at >= cutoff)) or 0
    return ChatAdminStatsOut(
        days=days, sessions=sessions, messages=totals[0], prompt_tokens=totals[1],
        completion_tokens=totals[2], cost_usd=totals[3], likes=likes, dislikes=dislikes,
        by_user=[ChatUserStat(user_id=r[0], email=r[1], full_name=r[2] or "", sessions=r[3],
                              messages=r[4], cost_usd=r[5]) for r in user_rows],
    )


@router.get("/admin/sessions", response_model=list[ChatAdminSessionOut])
def admin_sessions(limit: int = Query(50, ge=1, le=200), user: User = Depends(require_admin),
                   db: Session = Depends(get_db)) -> list[ChatAdminSessionOut]:
    from ..schemas import ChatAdminSessionOut as Out

    rows = db.execute(select(ChatSession, User.email, User.full_name).join(User)
                      .where(ChatSession.org_id == user.org_id)
                      .order_by(ChatSession.updated_at.desc()).limit(limit)).all()
    return [Out(**_session_out(s).model_dump(), user_email=email, user_name=full_name or "")
            for s, email, full_name in rows]
