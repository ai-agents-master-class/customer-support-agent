from agents.voice import VoiceWorkflowBase, VoiceWorkflowHelper
from agents import Runner
import streamlit as st


# 음성 입력 기반 사용자 요청을 처리하는 커스텀 워크플로우 정의
class CustomWorkflow(VoiceWorkflowBase):

    def __init__(self, context):
        # 대화나 사용자 관련 정보를 담는 컨텍스트 저장
        self.context = context

    async def run(self, transcription):
        # 음성 입력을 텍스트로 변환한 transcription을 받아
        # Agent에 전달하여 스트리밍 형태로 응답을 생성함

        # Agent를 스트리밍 모드로 실행
        result = Runner.run_streamed(
            st.session_state["agent"],              # 현재 활성화된 Agent 인스턴스
            transcription,                          # 음성 인식 결과 텍스트
            session=st.session_state["session"],    # 대화 세션 상태 관리
            context=self.context,                   # 사용자 컨텍스트 전달
        )

        # 모델 응답을 한 덩어리(chunk)씩 비동기로 받아 처리
        async for chunk in VoiceWorkflowHelper.stream_text_from(result):
            # 각 텍스트 조각을 실시간으로 반환하여 Streamlit에 표시
            yield chunk

        # 대화 후 마지막 Agent 상태를 세션에 저장하여 다음 요청 시 이어서 사용
        st.session_state["agent"] = result.last_agent
