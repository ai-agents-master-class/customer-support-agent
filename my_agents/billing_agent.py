from agents import Agent, RunContextWrapper
from models import UserAccountContext
from tools import (
    lookup_billing_history,
    process_refund_request,
    update_payment_method,
    apply_billing_credit,
    AgentToolUsageLoggingHooks,
)

# 결제 및 청구 관련 문제를 처리하는 Billing Support 에이전트의 프롬프트를 동적으로 생성하는 함수
# wrapper: 실행 컨텍스트 객체 (UserAccountContext 포함)
#          → 사용자 이름(name), 등급(tier) 등의 정보를 포함
# agent: 현재 실행 중인 Agent 객체 (시그니처 일관성 유지용으로 전달)
def dynamic_billing_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    # f-string을 사용해 사용자별 이름(name)과 tier(등급)를 프롬프트에 삽입함
    # tier가 "basic"이 아닐 경우 "Premium Billing Support" 문구를 추가로 포함시킴
    return f"""
    당신은 {wrapper.context.name} 님을 지원하는 결제 지원(Billing Support) 전문 담당자입니다.
    고객 등급: {wrapper.context.tier} {"(Premium Billing Support)" if wrapper.context.tier != "basic" else ""}

    역할: 고객의 결제, 환불, 구독 관련 문제를 해결하는 것입니다.

    결제 지원 절차:
    1. 계정 정보와 결제 정보를 확인합니다.
    2. 구체적인 결제 문제를 식별합니다.
    3. 결제 내역과 구독 상태를 점검합니다.
    4. 명확한 해결책과 다음 단계를 안내합니다.
    5. 필요한 경우 환불 또는 금액 조정을 처리합니다.

    자주 발생하는 결제 문제:
    - 결제 실패 또는 카드 승인 거부
    - 예상치 못한 요금 또는 청구 이의 제기
    - 구독 변경 또는 해지 요청
    - 환불 요청
    - 청구서 및 인보이스 관련 문의

    결제 정책:
    - 대부분의 서비스는 30일 이내 환불 가능
    - 프리미엄 고객은 우선 처리 대상
    - 모든 청구 내역은 명확히 설명해야 함
    - 필요 시 할부 또는 결제 계획 옵션을 제시

    {"프리미엄 혜택: 환불 우선 처리 및 유연한 결제 옵션 제공." if wrapper.context.tier != "basic" else ""}
    """


# 실제 Billing Support 에이전트 정의
# instructions로 위에서 정의한 dynamic_billing_agent_instructions 함수를 전달함
# 실행 시 wrapper.context의 사용자 정보(name, tier 등)를 기반으로 프롬프트를 동적으로 구성함
billing_agent = Agent(
    name="Billing Support Agent",
    instructions=dynamic_billing_agent_instructions,
    tools=[
        lookup_billing_history,
        process_refund_request,
        update_payment_method,
        apply_billing_credit,
    ],
    hooks=AgentToolUsageLoggingHooks(),
)
