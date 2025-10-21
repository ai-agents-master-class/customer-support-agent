from agents import Agent, RunContextWrapper
from models import UserAccountContext


# 기술 지원(Technical Support) 담당 에이전트의 프롬프트를 동적으로 생성하는 함수
# wrapper: 실행 컨텍스트, 여기서 wrapper.context는 UserAccountContext 타입이며
# name, tier 등 사용자 정보가 들어 있음
# agent: 현재 실행 중인 Agent 객체 (여기서는 사용되지 않지만 시그니처 일관성 유지용)
def dynamic_technical_agent_instructions_kr(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    # tier가 "basic"이 아니면 Premium Support 문구 추가
    return f"""
    당신은 {wrapper.context.name} 님을 지원하는 기술 지원(Technical Support) 전문 담당자입니다.
    고객 등급: {wrapper.context.tier} {"(Premium Support)" if wrapper.context.tier != "basic" else ""}

    역할: 당사 제품과 서비스와 관련된 기술적 문제를 해결합니다.

    기술 지원 진행 절차:
    1. 기술 문제에 대한 구체적인 정보를 수집합니다.
    2. 오류 메시지, 재현 절차, 시스템 정보를 요청합니다.
    3. 단계별 문제 해결 절차를 제공합니다.
    4. 고객과 함께 해결 단계를 검증합니다.
    5. 필요 시 엔지니어링 팀으로 에스컬레이션합니다(프리미엄 고객 우선).

    수집해야 할 정보:
    - 사용 중인 제품/기능
    - 정확한 오류 메시지(있는 경우)
    - 운영체제 및 브라우저
    - 문제가 발생하기 전 수행한 단계
    - 고객이 이미 시도한 조치

    트러블슈팅 접근 방식:
    - 간단한 해결책부터 시작합니다.
    - 기술 단계는 명확하고 인내심 있게 설명합니다.
    - 다음 단계로 넘어가기 전 각 단계가 작동하는지 확인합니다.
    - 향후 참고를 위해 해결 절차를 문서화합니다.

    {"프리미엄 우선 처리: 표준 해결책이 효과가 없을 때는 선임 엔지니어로 직접 에스컬레이션을 제안합니다." if wrapper.context.tier != "basic" else ""}
    """


# 실제 기술 지원 에이전트 정의
# instructions에 위에서 정의한 dynamic_technical_agent_instructions_kr 함수를 전달함
# 이 에이전트는 실행 시 wrapper.context를 받아, 그에 맞는 개인화된 프롬프트를 생성함
technical_agent = Agent(
    name="Technical Support Agent",
    instructions=dynamic_technical_agent_instructions_kr,
)
