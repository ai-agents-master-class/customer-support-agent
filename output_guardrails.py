from agents import (
    Agent,
    output_guardrail,
    Runner,
    RunContextWrapper,
    GuardrailFunctionOutput,
)
from models import TechnicalOutputGuardRailOutput, UserAccountContext


# 기술 지원 응답 내의 부적절한 내용을 검증하는 에이전트 정의
technical_output_guardrail_agent = Agent(
    name="Technical Support Guardrail",
    instructions="""
    기술 지원 응답을 분석해서 다음과 같은 부적절한 내용이 포함되어 있는지 확인한다.
    
    - 결제 정보 (결제, 환불, 요금, 구독 등)
    - 주문 정보 (배송, 추적, 배달, 반품 등)
    - 계정 관리 정보 (비밀번호, 이메일 변경, 계정 설정 등)
    
    기술 지원 에이전트는 오직 기술적 문제 해결, 진단, 제품 지원만 제공해야 한다.
    기술 지원 응답에 부적절한 내용이 포함되어 있다면 해당 필드에 true를 반환한다.
    """,
    output_type=TechnicalOutputGuardRailOutput,
)


@output_guardrail
async def technical_output_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent,
    output: str,
):
    # 기술 지원 검증 에이전트를 실행하여 결과를 받음
    result = await Runner.run(
        technical_output_guardrail_agent,
        output,
        context=wrapper.context,
    )

    # 에이전트의 최종 결과를 가져옴
    validation = result.final_output

    # 결과 중 하나라도 부적절한 내용이 있으면 tripwire를 작동시킴
    # TechnicalOutputGuardRailOutput의 필드들을 검사
    triggered = (
        validation.contains_off_topic
        or validation.contains_billing_data
        or validation.contains_account_data
    )

    # 검증 결과와 트리거 상태를 반환
    return GuardrailFunctionOutput(
        output_info=validation,
        tripwire_triggered=triggered,
    )
