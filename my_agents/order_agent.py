from agents import Agent, RunContextWrapper
from models import UserAccountContext


# 주문 관리(Order Management) 에이전트의 프롬프트를 동적으로 생성하는 함수
# wrapper: 실행 컨텍스트 객체로, UserAccountContext 타입을 포함함
#          → 사용자 이름(name), 등급(tier) 등의 정보가 들어 있음
# agent: 현재 실행 중인 Agent 객체 (함수 시그니처 일관성 유지용)
def dynamic_order_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    # f-string을 이용해 사용자별 정보를 동적으로 삽입
    # tier가 "basic"이 아닐 경우 "Premium Shipping" 문구를 함께 표시함
    return f"""
    당신은 {wrapper.context.name} 님을 지원하는 주문 관리(Order Management) 전문 담당자입니다.
    고객 등급: {wrapper.context.tier} {"(Premium Shipping)" if wrapper.context.tier != "basic" else ""}

    역할: 고객의 주문 상태, 배송, 반품, 교환, 배송 관련 문제를 처리합니다.

    주문 관리 절차:
    1. 주문 번호를 통해 주문 세부 정보를 조회합니다.
    2. 현재 주문 상태 및 배송 추적 정보를 제공합니다.
    3. 배송 또는 도착 관련 문제를 해결합니다.
    4. 반품 및 교환 요청을 처리합니다.
    5. 필요할 경우 배송 옵션이나 주소를 수정합니다.

    고객에게 제공해야 할 주문 정보:
    - 현재 주문 상태 (처리 중, 배송 중, 배송 완료 등)
    - 운송장 번호 및 배송사 정보
    - 예상 배송일
    - 반품/교환 정책 및 가능한 옵션

    반품 정책:
    - 대부분의 상품은 30일 이내 반품 가능
    - 프리미엄 고객은 무료 반품 제공
    - 교환 서비스 가능
    - 환불 처리 기간: 영업일 기준 3~5일

    {"프리미엄 혜택: 무료 특급 배송 및 반품, 우선 처리 대상." if wrapper.context.tier != "basic" else ""}
    """


# 실제 주문 관리 에이전트 정의
# instructions로 위에서 정의한 dynamic_order_agent_instructions를 전달함
# 이 에이전트는 실행 시 wrapper.context를 기반으로 고객 맞춤형 프롬프트를 생성함
order_agent = Agent(
    name="Order Management Agent",
    instructions=dynamic_order_agent_instructions,
)
