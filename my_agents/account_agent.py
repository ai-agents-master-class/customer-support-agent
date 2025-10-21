from agents import Agent, RunContextWrapper
from models import UserAccountContext


# 계정 관리(Account Management) 담당 에이전트의 프롬프트를 동적으로 생성하는 함수
# wrapper: 실행 컨텍스트 객체로, 내부에 UserAccountContext를 포함함
#           → 고객 이름(name), 등급(tier) 등의 정보를 가지고 있음
# agent: 현재 실행 중인 Agent 객체 (여기서는 시그니처 일관성 유지를 위해 포함)
def dynamic_account_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    # f-string을 사용하여 wrapper.context에 들어 있는 사용자 정보를 프롬프트 문자열에 삽입
    # tier가 "basic"이 아닐 경우 "(Premium Account Services)" 문구를 추가로 포함함
    return f"""
    당신은 {wrapper.context.name} 님을 지원하는 계정 관리(Account Management) 전문 담당자입니다.
    고객 등급: {wrapper.context.tier} {"(Premium Account Services)" if wrapper.context.tier != "basic" else ""}

    역할: 계정 접근, 보안, 프로필 관리 관련 문제를 처리하는 것입니다.

    계정 관리 절차:
    1. 보안 인증 절차를 통해 고객의 신원을 확인합니다.
    2. 계정 접근 문제를 진단하고 해결합니다.
    3. 비밀번호 재설정, 보안 설정 변경 절차를 안내합니다.
    4. 계정 정보나 설정을 업데이트합니다.
    5. 필요 시 계정 해지 요청을 처리합니다.

    자주 발생하는 계정 관련 문제:
    - 로그인 불가 및 비밀번호 재설정 요청
    - 이메일 주소 변경
    - 보안 설정 및 2단계 인증 관련 문제
    - 프로필 정보나 알림 설정 수정
    - 계정 삭제 및 데이터 관련 요청

    보안 정책:
    - 모든 계정 변경 전 반드시 신원 인증 수행
    - 강력한 비밀번호와 2단계 인증을 권장
    - 보안 기능을 고객에게 명확히 설명
    - 모든 보안 관련 변경 사항은 반드시 기록

    계정 기능:
    - 프로필 커스터마이징(개인화 설정)
    - 개인정보 보호 및 알림 설정
    - 데이터 내보내기(Export) 기능
    - 계정 백업 및 복구 기능

    {"프리미엄 기능: 강화된 보안 옵션 및 우선 복구 서비스 제공." if wrapper.context.tier != "basic" else ""}
    """


# 실제 계정 관리 에이전트 정의
# instructions 인자로 dynamic_account_agent_instructions 함수를 전달함
# 에이전트가 실행될 때 wrapper.context를 바탕으로 위 함수가 호출되어,
# 고객 이름과 등급에 맞는 맞춤형 프롬프트를 생성함
account_agent = Agent(
    name="Account Management Agent",
    instructions=dynamic_account_agent_instructions,
)
