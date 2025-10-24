import dotenv

# .env 파일의 환경 변수를 로드 (API 키 등 민감한 설정 불러오기)
dotenv.load_dotenv()
from openai import OpenAI
import asyncio
import streamlit as st
from agents import (
    Runner,
    SQLiteSession,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
)
from agents.voice import AudioInput, VoicePipeline
from models import UserAccountContext
from my_agents.triage_agent import triage_agent
import numpy as np
import wave, io
from workflow import CustomWorkflow
import sounddevice as sd

# OpenAI 클라이언트 초기화
client = OpenAI()

# 사용자 계정 컨텍스트 생성 (고객 정보 및 서비스 등급 포함)
user_account_ctx = UserAccountContext(
    customer_id=1,
    name="nana",
    tier="basic",
    email="ktra@example.com"
)

# Streamlit 세션에 대화 세션 저장소가 없을 경우 생성
if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "chat-history",                      # 세션 파일 이름
        "customer-support-memory.db",        # 로컬 SQLite DB 경로
    )
session = st.session_state["session"]

# Streamlit 세션에 활성 Agent가 없을 경우 기본 triage_agent 설정
if "agent" not in st.session_state:
    st.session_state["agent"] = triage_agent


def convert_audio(audio_input):
    """
    Streamlit 오디오 입력 데이터를 NumPy 배열로 변환하는 함수.
    음성 입력은 .wav 포맷으로 들어오며, 이 데이터를 버퍼에서 읽어 정수형 배열로 반환함.
    """
    audio_data = audio_input.getvalue()

    # WAV 파일을 메모리에서 직접 읽음
    with wave.open(io.BytesIO(audio_data), "rb") as wav_file:
        audio_frames = wav_file.readframes(-1)

    # 오디오 프레임을 NumPy 배열로 변환 (int16 형식)
    return np.frombuffer(
        audio_frames,
        dtype=np.int16,
    )


async def run_agent(audio_input):
    """
    음성 입력을 받아 VoicePipeline을 실행하는 비동기 함수.
    - 오디오 데이터를 변환
    - CustomWorkflow을 통해 처리
    - Guardrail 예외를 처리
    """
    # AI 응답 영역 생성
    with st.chat_message("ai"):
        # 처리 상태 표시 UI
        status_container = st.status("⏳ Processing voice message...")
        try:
            # 오디오 입력을 NumPy 배열로 변환
            audio_array = convert_audio(audio_input)

            # AudioInput 객체로 래핑
            audio = AudioInput(buffer=audio_array)

            # 사용자 컨텍스트를 포함한 커스텀 워크플로우 생성
            workflow = CustomWorkflow(context=user_account_ctx)

            # VoicePipeline 초기화
            pipeline = VoicePipeline(workflow=workflow)

            # 상태 업데이트: 워크플로우 실행 중
            status_container.update(label="Running workflow", state="running")

            # 파이프라인 실행 및 결과 비동기 수신
            result = await pipeline.run(audio)

            # 음성 출력 스트림 초기화 (재생용)
            player = sd.OutputStream(
                samplerate=24000,  # 샘플링 레이트
                channels=1,        # 단일 채널(모노)
                dtype=np.int16,    # 데이터 타입
            )
            player.start()

            # 상태 업데이트: 완료 표시
            status_container.update(state="complete")

            # VoicePipeline에서 반환된 이벤트 스트림을 실시간으로 재생
            async for event in result.stream():
                if event.type == "voice_stream_event_audio":
                    player.write(event.data)

        # 입력 가드레일 트리거 시 차단
        except InputGuardrailTripwireTriggered:
            st.write("I can't help you with that.")

        # 출력 가드레일 트리거 시 차단
        except OutputGuardrailTripwireTriggered:
            st.write("Cant show you that answer.")


# Streamlit 오디오 입력 컴포넌트 (마이크 녹음용)
audio_input = st.audio_input(
    "Record your message",
)

# 사용자가 오디오를 입력한 경우 실행
if audio_input:
    # 사용자의 음성 입력을 채팅 형태로 표시
    with st.chat_message("human"):
        st.audio(audio_input)
    # 비동기 파이프라인 실행
    asyncio.run(run_agent(audio_input))


# 사이드바 영역
with st.sidebar:
    # 메모리(세션) 초기화 버튼
    reset = st.button("Reset memory")
    if reset:
        asyncio.run(session.clear_session())  # 세션 데이터 삭제
    # 세션 로그 조회
    st.write(asyncio.run(session.get_items()))
