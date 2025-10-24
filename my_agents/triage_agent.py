import streamlit as st
from agents import (
    Agent,
    RunContextWrapper,
    input_guardrail,
    Runner,
    GuardrailFunctionOutput,
    handoff,
)
from models import UserAccountContext, InputGuardRailOutput
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from agents.extensions import handoff_filters
from models import UserAccountContext, InputGuardRailOutput, HandoffData
from my_agents.account_agent import account_agent
from my_agents.technical_agent import technical_agent
from my_agents.order_agent import order_agent
from my_agents.billing_agent import billing_agent

# 입력 필터 역할을 하는 에이전트 정의
# 사용자의 입력이 서비스 범위(계정/결제/주문/기술지원)에 포함되는지 확인함
input_guardrail_agent = Agent(
    name="Input Guardrail Agent",
    instructions=f"""
{RECOMMENDED_PROMPT_PREFIX}
사용자의 요청이 반드시 **사용자 계정 정보(User Account details)**, **결제 문의(Billing inquiries)**, **주문 정보(Order information)**, 또는 **기술 지원 문제(Technical Support issues)** 중 하나와 관련되어 있는지 확인하세요.

요청이 이 범위를 벗어난(off-topic) 경우, **해당 요청이 왜 적절하지 않은지에 대한 이유(tripwire reason)**를 반환해야 합니다.

대화의 초반에는 사용자가 편안함을 느낄 수 있도록 **간단한 잡담(small talk)** 을 할 수 있습니다.  
그러나 **사용자 계정, 결제, 주문, 기술 지원과 무관한 요청**에 대해서는 도움을 주지 마세요.
""",
    output_type=InputGuardRailOutput,
)


@input_guardrail
async def off_topic_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
    input: str,
):
    # Guardrail 함수: 입력을 검사하고 off-topic 여부를 반환함
    # wrapper: 실행 컨텍스트 (UserAccountContext를 포함)
    # agent: 현재 호출 중인 에이전트
    # input: 사용자의 입력 텍스트

    # Runner.run을 통해 Guardrail Agent 실행
    result = await Runner.run(
        input_guardrail_agent,
        input,
        context=wrapper.context,
    )

    # 결과를 GuardrailFunctionOutput 형태로 변환하여 반환
    # tripwire_triggered가 True면 off-topic으로 간주됨
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_off_topic,
    )


# 고객 요청을 받아 적절한 담당 에이전트로 라우팅하기 위한 메인 지침 생성 함수
def dynamic_triage_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    # wrapper.context에는 사용자 이름, 이메일, tier 등의 정보가 포함됨
    # 이 정보를 이용해 프롬프트를 동적으로 구성함
    return f"""
    당신은 고객 지원 에이전트입니다. 당신의 임무는 **사용자 계정, 결제, 주문, 기술 지원과 관련된 고객 문의만** 돕는 것입니다.
    고객을 부를 때는 반드시 이름을 사용하세요.
    
    고객의 이름: {wrapper.context.name}
    고객의 이메일: {wrapper.context.email}
    고객의 서비스 등급(tier): {wrapper.context.tier}
    
    주요 역할:
    고객의 문제를 정확히 분류하여 올바른 전문 담당자에게 연결하는 것

    -----------------------------
    기술 지원 (TECHNICAL SUPPORT)
    다음 상황에 해당하면 이 카테고리로 분류:
    - 제품이 작동하지 않음, 오류, 버그
    - 앱 충돌, 로딩 지연, 성능 문제
    - 기능 관련 질문, 사용 방법 문의
    - 통합 설정, 설치 문제
    - 예시: "앱이 안 켜져요", "오류 메시지가 떠요", "이 기능은 어떻게 써요?"

    결제 지원 (BILLING SUPPORT)
    다음 상황에 해당하면 이 카테고리로 분류:
    - 결제 실패, 중복 결제, 환불 요청
    - 구독/요금제 변경, 해지, 업그레이드
    - 청구서, 결제 내역, 결제 수단 문제
    - 예시: "두 번 결제됐어요", "구독을 취소하고 싶어요", "환불이 필요해요"

    주문 관리 (ORDER MANAGEMENT)
    다음 상황에 해당하면 이 카테고리로 분류:
    - 주문 상태, 배송, 도착 관련 문의
    - 반품, 교환, 누락된 상품
    - 배송 추적, 잘못된 상품, 재고 확인
    - 예시: "내 주문은 어디 있나요?", "상품을 반품하고 싶어요", "잘못된 상품이 왔어요"

    계정 관리 (ACCOUNT MANAGEMENT)
    다음 상황에 해당하면 이 카테고리로 분류:
    - 로그인 문제, 비밀번호 재설정, 계정 접근 불가
    - 프로필 수정, 이메일 변경, 계정 설정
    - 계정 보안, 2단계 인증, 계정 삭제, 데이터 요청
    - 예시: "로그인이 안 돼요", "비밀번호를 잊었어요", "이메일 주소를 바꾸고 싶어요"
    -----------------------------

    분류 절차:
    1. 고객의 문제를 듣는다.
    2. 카테고리가 명확하지 않으면 추가 질문을 한다.
    3. 위 네 가지 중 하나로 분류한다.
    4. 고객에게 연결 이유를 설명한다.
       예: [category] 담당 전문가에게 연결해드릴게요.
    5. 해당 전문 담당자에게 전달한다.

    특별 처리 지침:
    - Premium 또는 Enterprise 고객은 우선 처리 대상으로 안내
    - 여러 문제가 있으면 긴급한 문제부터 우선 처리
    - 불분명한 경우 1~2개의 명확한 질문으로 확인 후 분류
    """

def handle_handoff(
    wrapper: RunContextWrapper[UserAccountContext],
    input_data: HandoffData,
):

    with st.sidebar:
        st.write(
            f"""
            Handing off to {input_data.to_agent_name}
            Reason: {input_data.reason}
            Issue Type: {input_data.issue_type}
            Description: {input_data.issue_description}
        """
        )


def make_handoff(agent):

    return handoff(
        agent=agent,
        # 인계 시 호출되는 콜백 함수 지정
        on_handoff=handle_handoff,
        # 인계 시 전달되는 입력 데이터 모델 지정
        input_type=HandoffData,
        # input_filter: 전달 전 input 데이터에서 불필요한 툴 정보 제거
        # (예: streamlit, internal tools 등의 메타데이터 제거)
        input_filter=handoff_filters.remove_all_tools,
    )



# 실제 분류 담당 에이전트 정의
# 입력 전에 off_topic_guardrail을 실행하여 유효성 검사 수행
triage_agent = Agent(
    name="Triage Agent",
    instructions=dynamic_triage_agent_instructions,
    # input_guardrails=[
    #     off_topic_guardrail,
    # ],
    # tools=[
    #     technical_agent.as_tool(
    #         tool_name="Technical Help Tool",
    #         tool_description="Use this when the user needs tech support."
    #     )
    # ]
    handoffs=[
        make_handoff(technical_agent),
        make_handoff(billing_agent),
        make_handoff(account_agent),
        make_handoff(order_agent),
    ],
)