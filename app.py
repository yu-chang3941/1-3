import streamlit as st
from google import genai
from google.genai import types

# 페이지 설정
st.set_page_config(
    page_title="연애상담 챗봇",
    page_icon="💌",
)

st.title("💌 연애상담 챗봇")
st.caption("Gemini 2.5 Flash Lite 기반 상담 챗봇")

# API 키 불러오기
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Secrets에 GEMINI_API_KEY를 등록해주세요.")
    st.stop()

# Gemini 클라이언트 생성
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Gemini 클라이언트 생성 실패: {e}")
    st.stop()

# 시스템 프롬프트
SYSTEM_PROMPT = """
너는 따뜻하고 공감 능력이 뛰어난 연애상담 챗봇이다.

규칙:
- 사용자의 감정을 존중한다.
- 비난하거나 공격적으로 말하지 않는다.
- 현실적이고 도움이 되는 조언을 제공한다.
- 짧고 읽기 쉽게 답변한다.
- 필요하면 위로와 공감을 먼저 한다.
"""

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
user_input = st.chat_input("연애 고민을 이야기해보세요...")

if user_input:
    # 사용자 메시지 저장
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # 사용자 메시지 출력
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI 응답 생성
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        try:
            # 대화 기록 문자열 생성
            history_text = ""

            for msg in st.session_state.messages:
                role = "사용자" if msg["role"] == "user" else "상담사"
                history_text += f"{role}: {msg['content']}\n"

            prompt = f"""
{SYSTEM_PROMPT}

다음은 지금까지의 대화 내용이다.

{history_text}

상담사 답변:
"""

            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.8,
                    max_output_tokens=500,
                )
            )

            ai_response = response.text

            # 응답 출력
            message_placeholder.markdown(ai_response)

            # 대화 저장
            st.session_state.messages.append({
                "role": "assistant",
                "content": ai_response
            })

        except Exception as e:
            error_message = f"오류가 발생했어요 😢\n\n{str(e)}"

            message_placeholder.error(error_message)

            st.session_state.messages.append({
                "role": "assistant",
                "content": error_message
            })

# 사이드바
with st.sidebar:
    st.header("⚙️ 설정")

    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("""
### 📌 사용 모델
- gemini-2.5-flash-lite

### 💡 예시 질문
- 썸남이 연락이 줄었어요
- 헤어진 전애인이 생각나요
- 고백해도 될까요?
- 장거리 연애가 힘들어요
""")
