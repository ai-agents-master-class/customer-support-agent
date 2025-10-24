import streamlit as st
from agents import function_tool, AgentHooks, Agent, Tool, RunContextWrapper
from models import UserAccountContext
import random
from datetime import datetime, timedelta


# =============================================================================
# TECHNICAL SUPPORT TOOLS
# =============================================================================


@function_tool
def run_diagnostic_check(
    context: UserAccountContext, product_name: str, issue_description: str
) -> str:
    """
    고객 제품에 대한 진단 점검을 수행해 잠재 이슈를 식별함.

    Args:
        product_name: 문제가 발생한 제품 이름
        issue_description: 문제에 대한 설명
    """
    # 진단 결과 예시 데이터 구성
    diagnostics = [
        "Server connectivity: 정상",
        "API endpoints: 응답 양호",
        "Cache memory: 85% 사용 (정리 권장)",
        "Database connections: 안정적",
        "Last update: 7일 전 (업데이트 가능)",
    ]

    return f"다음은 {product_name}에 대한 진단 결과:\n" + "\n".join(diagnostics)


@function_tool
def provide_troubleshooting_steps(context: UserAccountContext, issue_type: str) -> str:
    """
    일반적인 이슈 유형에 대한 단계별 트러블슈팅 지침을 제공함.

    Args:
        issue_type: 이슈 유형 (connection, login, performance, crash 등)
    """
    # 이슈 유형별 단계 매핑
    steps_map = {
        "connection": [
            "1. 인터넷 연결 상태 확인",
            "2. 브라우저 캐시 및 쿠키 삭제",
            "3. 브라우저 확장 프로그램 일시 비활성화",
            "4. 시크릿/프라이빗 모드로 재시도",
            "5. 라우터/모뎀 재부팅",
        ],
        "login": [
            "1. 사용자명과 비밀번호 확인",
            "2. Caps Lock 해제 여부 확인",
            "3. 브라우저 캐시 삭제",
            "4. 필요 시 비밀번호 재설정",
            "5. VPN 일시 비활성화",
        ],
        "performance": [
            "1. 불필요한 브라우저 탭 닫기",
            "2. 브라우저 캐시 삭제",
            "3. 사용 가능한 RAM 및 저장 공간 확인",
            "4. 브라우저 업데이트",
            "5. 애플리케이션 재시작",
        ],
        "crash": [
            "1. 최신 버전으로 업데이트",
            "2. 애플리케이션 재시작",
            "3. 시스템 요구사항 확인",
            "4. 충돌 가능성이 있는 소프트웨어 비활성화",
            "5. 안전 모드로 실행",
        ],
    }

    # 미정의 유형에 대한 기본 단계
    steps = steps_map.get(
        issue_type.lower(),
        [
            "1. 애플리케이션 재시작",
            "2. 업데이트 여부 확인",
            "3. 오류 상세와 함께 지원 팀에 문의",
        ],
    )

    # 사용자 컨텍스트에 제공한 단계 기록 남김
    context.add_troubleshooting_step(f"{issue_type} 유형 트러블슈팅 단계 제공함")
    return f"{issue_type} 이슈에 대한 트러블슈팅 단계:\n" + "\n".join(steps)


@function_tool
def escalate_to_engineering(
    context: UserAccountContext, issue_summary: str, priority: str = "medium"
) -> str:
    """
    기술 이슈를 엔지니어링 팀에 에스컬레이션함.

    Args:
        issue_summary: 기술 이슈 요약
        priority: 우선순위 (low, medium, high, critical)
    """
    # 티켓 아이디 생성
    ticket_id = f"ENG-{random.randint(10000, 99999)}"

    return (
        "엔지니어링 팀으로 이슈를 에스컬레이션함\n"
        f"티켓 ID: {ticket_id}\n"
        f"우선순위: {priority.upper()}\n"
        f"요약: {issue_summary}\n"
        f"예상 응답 시간: {2 if context.is_premium_customer() else 4}시간"
    )


# =============================================================================
# BILLING SUPPORT TOOLS
# =============================================================================


@function_tool
def lookup_billing_history(context: UserAccountContext, months_back: int = 6) -> str:
    """
    고객의 청구 및 결제 내역을 조회함.

    Args:
        months_back: 조회 개월(기본 6개월)
    """
    # 더미 결제 내역 생성
    payments = []
    for i in range(months_back):
        date = datetime.now() - timedelta(days=30 * i)
        amount = random.choice([29.99, 49.99, 99.99])
        status = random.choice(["Paid", "Paid", "Paid", "Failed"])
        payments.append(f"• {date.strftime('%b %Y')}: ${amount} - {status}")

    return f"청구 내역 (최근 {months_back}개월):\n" + "\n".join(payments)


@function_tool
def process_refund_request(
    context: UserAccountContext, refund_amount: float, reason: str
) -> str:
    """
    고객 환불 요청을 처리함.

    Args:
        refund_amount: 환불 금액
        reason: 환불 사유
    """
    # 프리미엄 고객일 경우 처리 기간 단축
    processing_days = 3 if context.is_premium_customer() else 5
    refund_id = f"REF-{random.randint(100000, 999999)}"

    return (
        "환불 요청을 처리함\n"
        f"환불 ID: {refund_id}\n"
        f"금액: ${refund_amount}\n"
        f"사유: {reason}\n"
        f"처리 기간: 영업일 기준 {processing_days}일\n"
        "환불은 원 결제수단으로 반환됨"
    )


@function_tool
def update_payment_method(context: UserAccountContext, payment_type: str) -> str:
    """
    고객 결제 수단 업데이트를 지원함.

    Args:
        payment_type: 결제 수단 유형 (credit_card, paypal, bank_transfer)
    """
    # 보안 링크 발송 안내 문구 생성
    return (
        "결제 수단 업데이트를 시작함\n"
        f"유형: {payment_type.replace('_', ' ').title()}\n"
        f"보안 링크가 다음 주소로 전송됨: {context.email}\n"
        "링크 유효기간: 24시간\n"
        "현재 서비스는 중단 없이 유지됨"
    )


@function_tool
def apply_billing_credit(
    context: UserAccountContext, credit_amount: float, reason: str
) -> str:
    """
    보상/정산 목적의 청구 크레딧을 계정에 적용함.

    Args:
        credit_amount: 적용할 크레딧 금액
        reason: 크레딧 사유
    """
    # 크레딧 적용 결과 문구 생성
    return (
        "계정 크레딧을 적용함\n"
        f"금액: ${credit_amount}\n"
        f"사유: {reason}\n"
        f"적용 계정: {context.customer_id}\n"
        f"확인 메일이 전송됨: {context.email}"
    )


# =============================================================================
# ORDER MANAGEMENT TOOLS
# =============================================================================


@function_tool
def lookup_order_status(context: UserAccountContext, order_number: str) -> str:
    """
    주문 상태와 상세 정보를 조회함.

    Args:
        order_number: 고객 주문 번호
    """
    # 상태 무작위 선택 및 배송 ETA 구성
    statuses = ["processing", "shipped", "in_transit", "delivered"]
    current_status = random.choice(statuses)
    tracking_number = f"1Z{random.randint(100000, 999999)}"
    estimated_delivery = datetime.now() + timedelta(days=random.randint(1, 5))

    return (
        f"주문 상태: {order_number}\n"
        f"상태: {current_status.title()}\n"
        f"운송장: {tracking_number}\n"
        f"예상 배송일: {estimated_delivery.strftime('%B %d, %Y')}\n"
        f"배송지 확인: {context.email}"
    )


@function_tool
def initiate_return_process(
    context: UserAccountContext, order_number: str, return_reason: str, items: str
) -> str:
    """
    주문 반품 프로세스를 시작함.

    Args:
        order_number: 반품 대상 주문 번호
        return_reason: 반품 사유
        items: 반품 품목
    """
    # 반품 ID와 라벨 비용 계산
    return_id = f"RET-{random.randint(100000, 999999)}"
    return_label_fee = 0 if context.is_premium_customer() else 5.99

    return (
        "반품을 시작함\n"
        f"반품 ID: {return_id}\n"
        f"주문: {order_number}\n"
        f"반품 품목: {items}\n"
        f"반품 라벨 비용: ${return_label_fee}\n"
        f"반품 라벨이 전송됨: {context.email}\n"
        "반품 가능 기간: 30일"
    )


@function_tool
def schedule_redelivery(
    context: UserAccountContext, tracking_number: str, preferred_date: str
) -> str:
    """
    배송 실패 건에 대해 재배송 일정을 예약함.

    Args:
        tracking_number: 운송장 번호
        preferred_date: 고객이 선호하는 배송 날짜
    """
    # 재배송 예약 결과 문구 생성
    return (
        "재배송을 예약함\n"
        f"운송장: {tracking_number}\n"
        f"새 배송일: {preferred_date}\n"
        f"주소 확인: {context.email}\n"
        "배송 30분 전에 기사 연락 예정"
    )


@function_tool
def expedite_shipping(context: UserAccountContext, order_number: str) -> str:
    """
    주문의 배송 속도를 업그레이드함 (프리미엄 고객 전용).

    Args:
        order_number: 대상 주문 번호
    """
    # 프리미엄 고객 여부 확인
    if not context.is_premium_customer():
        return "배송 속도 업그레이드는 프리미엄 멤버십이 필요함"

    return (
        "배송 속도를 업그레이드함\n"
        f"주문: {order_number}\n"
        "업그레이드: 익일 배송\n"
        "추가 요금 없음 (프리미엄 혜택)\n"
        f"업데이트된 운송장 정보가 전송됨: {context.email}"
    )


# =============================================================================
# ACCOUNT MANAGEMENT TOOLS
# =============================================================================


@function_tool
def reset_user_password(context: UserAccountContext, email: str) -> str:
    """
    고객 이메일로 비밀번호 재설정 안내를 발송함.

    Args:
        email: 재설정 안내를 보낼 이메일 주소
    """
    # 단일 사용 토큰 생성
    reset_token = f"RST-{random.randint(100000, 999999)}"

    return (
        "비밀번호 재설정을 시작함\n"
        f"재설정 링크가 전송됨: {email}\n"
        f"재설정 토큰: {reset_token}\n"
        "링크 만료: 1시간\n"
        "보안을 위해 링크는 1회용임"
    )


@function_tool
def enable_two_factor_auth(context: UserAccountContext, method: str = "app") -> str:
    """
    2단계 인증을 설정함.

    Args:
        method: 인증 방식 (app, sms, email)
    """
    # 설정 코드 생성
    setup_code = f"2FA-{random.randint(100000, 999999)}"

    return (
        "2단계 인증 설정\n"
        f"방식: {method.upper()}\n"
        f"설정 코드: {setup_code}\n"
        f"설정 안내가 전송됨: {context.email}\n"
        "보안 강화 기능이 활성화됨"
    )


@function_tool
def update_account_email(
    context: UserAccountContext, old_email: str, new_email: str
) -> str:
    """
    계정 이메일 주소 변경을 처리함.

    Args:
        old_email: 기존 이메일 주소
        new_email: 새 이메일 주소
    """
    # 이메일 변경 검증 코드 생성
    verification_code = f"VER-{random.randint(100000, 999999)}"

    return (
        "이메일 변경 요청 접수\n"
        f"변경 전: {old_email}\n"
        f"변경 후: {new_email}\n"
        f"검증 코드: {verification_code}\n"
        "코드 만료: 30분\n"
        "검증 완료 후 변경이 적용됨"
    )


@function_tool
def deactivate_account(
    context: UserAccountContext, reason: str, feedback: str = ""
) -> str:
    """
    계정 비활성화 요청을 처리함.

    Args:
        reason: 계정 비활성화 사유
        feedback: 선택 입력 피드백
    """
    # 비활성화 처리 안내 문구 생성
    return (
        "계정 비활성화를 시작함\n"
        f"계정: {context.customer_id}\n"
        f"사유: {reason}\n"
        f"피드백: {feedback if feedback else '입력 없음'}\n"
        "계정은 24시간 후 비활성화됨\n"
        "30일 이내 재활성화 가능\n"
        f"확인 메일이 전송됨: {context.email}"
    )


@function_tool
def export_account_data(context: UserAccountContext, data_types: str) -> str:
    """
    고객 계정 데이터 내보내기를 생성함.

    Args:
        data_types: 내보낼 데이터 유형 (profile, orders, billing 등)
    """
    # 내보내기 ID 생성 및 처리 시간 안내
    export_id = f"EXP-{random.randint(100000, 999999)}"

    return (
        "데이터 내보내기 요청 접수\n"
        f"내보내기 ID: {export_id}\n"
        f"데이터 유형: {data_types}\n"
        "처리 시간: 2~4시간\n"
        f"다운로드 링크가 전송될 주소: {context.email}\n"
        "링크 만료: 7일"
    )


class AgentToolUsageLoggingHooks(AgentHooks):
    # 각 훅에서 Streamlit 사이드바에 로그를 남김

    async def on_tool_start(
        self,
        context: RunContextWrapper[UserAccountContext],
        agent: Agent[UserAccountContext],
        tool: Tool,
    ):
        # 도구 실행 시작 로그
        with st.sidebar:
            st.write(f"{agent.name} 시작한 도구: `{tool.name}`")

    async def on_tool_end(
        self,
        context: RunContextWrapper[UserAccountContext],
        agent: Agent[UserAccountContext],
        tool: Tool,
        result: str,
    ):
        # 도구 실행 종료 로그와 반환값 출력
        with st.sidebar:
            st.write(f"{agent.name} 사용한 도구: `{tool.name}`")
            st.code(result)

    async def on_handoff(
        self,
        context: RunContextWrapper[UserAccountContext],
        agent: Agent[UserAccountContext],
        source: Agent[UserAccountContext],
    ):
        # 에이전트 간 핸드오프 로그
        with st.sidebar:
            st.write(f"핸드오프: {source.name} → {agent.name}")

    async def on_start(
        self,
        context: RunContextWrapper[UserAccountContext],
        agent: Agent[UserAccountContext],
    ):
        # 에이전트 시작 로그
        with st.sidebar:
            st.write(f"{agent.name} 활성화됨")

    async def on_end(
        self,
        context: RunContextWrapper[UserAccountContext],
        agent: Agent[UserAccountContext],
        output,
    ):
        # 에이전트 종료 로그
        with st.sidebar:
            st.write(f"{agent.name} 완료됨")
