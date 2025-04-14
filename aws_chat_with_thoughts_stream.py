import os
import asyncio
import streamlit as st
import re
import sys
import io
import time
from contextlib import redirect_stdout
from mcp import StdioServerParameters
from InlineAgent.tools import MCPStdio
from InlineAgent.action_group import ActionGroup
from InlineAgent.agent import InlineAgent
from InlineAgent import AgentAppConfig

# 페이지 설정
st.set_page_config(
    page_title="AWS CLI Assistant",
    page_icon="☁️",
    layout="centered"
)

# 앱 제목
st.title("AWS Operation Assistant")
st.markdown("Powered by Amazon Bedrock and AWS CLI")

# 설정 로드
config = AgentAppConfig()

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 채팅 히스토리 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            if "thought" in message and message["thought"]:
                with st.expander("Thought Process (완료됨)"):
                    st.markdown(message["thought"])
            st.markdown(message["content"])
        else:
            st.markdown(message["content"])

# 사용자 홈 디렉토리 경로 설정
import os
USER_HOME = os.path.expanduser("~")

# AWS CLI MCP 서버 설정
def get_server_params():
    return StdioServerParameters(
        command="docker",
        args=[
            "run",
            "-i",
            "--rm",
            "-v",
            f"{USER_HOME}/.aws:/home/appuser/.aws:ro",
            "ghcr.io/alexei-led/aws-mcp-server:latest"
        ]
    )

# 표준 출력을 캡처하면서 터미널에도 출력하는 클래스
class TeeIO(io.StringIO):
    def __init__(self, original_stdout, update_callback=None):
        super().__init__()
        self.original_stdout = original_stdout
        self.update_callback = update_callback
        self.last_update_time = 0
        self.update_interval = 0.1  # 100ms마다 업데이트
    
    def write(self, s):
        # 원래 stdout에도 출력
        self.original_stdout.write(s)
        # StringIO에도 저장
        result = super().write(s)
        
        # 콜백 함수가 있고 업데이트 간격이 지났으면 실시간 업데이트
        current_time = time.time()
        if self.update_callback and (current_time - self.last_update_time) > self.update_interval:
            self.last_update_time = current_time
            self.update_callback(self.getvalue())
        
        return result
    
    def flush(self):
        # 원래 stdout도 flush
        self.original_stdout.flush()
        # StringIO도 flush
        return super().flush()

# Thought 내용을 포맷팅하는 함수
def format_thought_content(thought_content):
    if not thought_content:
        return ""
    
    # 단계별로 구분하기 위한 패턴
    step_patterns = [
        (r'(Tool use:.*?)(?=Tool output:|$)', r'\n\n**Tool Use:**\n\1'),
        (r'(Tool output:.*?)(?=Input Tokens:|$)', r'\n\n**Tool Output:**\n\1'),
        (r'(Input Tokens:.*?)(?=Output Tokens:|$)', r'\n\n**Input Tokens:**\n\1'),
        (r'(Output Tokens:.*?)(?=$)', r'\n\n**Output Tokens:**\n\1')
    ]
    
    # 패턴 적용
    formatted_content = thought_content
    for pattern, replacement in step_patterns:
        formatted_content = re.sub(pattern, replacement, formatted_content, flags=re.DOTALL)
    
    # 첫 줄에 "Thought Process:" 추가
    formatted_content = "**Thought Process:**\n" + formatted_content
    
    # 줄바꿈 추가
    formatted_content = formatted_content.replace("\n", "\n\n")
    
    return formatted_content

# AWS CLI 쿼리 실행 함수
async def run_aws_query(prompt: str, update_thought_callback=None):
    # 서버 파라미터 설정
    server_params_awscli = get_server_params()
    
    # MCP 클라이언트 생성
    awscli_mcp_client = await MCPStdio.create(server_params=server_params_awscli)
    
    try:
        # ActionGroup 생성
        aws_action_group = ActionGroup(
            name="AWSActionGroup",
            mcp_clients=[awscli_mcp_client],
        )
        
        # InlineAgent 생성
        agent = InlineAgent(
            foundation_model="anthropic.claude-3-haiku-20240307-v1:0",
            # foundation_model="amazon.nova-pro-v1:0",
            
            #foundation_model="us.anthropic.claude-3-5-sonnet-20240620-v1:0",
            #foundation_model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            instruction="""
You are an expert AWS assistant. You access to an integrated AWS CLI tool. Your sole responsibility is to "directly" execute AWS CLI commands as a tool to fulfill user requests, such as creating resources, analyzing resource status, or retrieving information from AWS accounts. You must never state or imply that you cannot execute commands, lack access to the CLI tool, or can only provide instructions.

Follow these strict instructions:
1. Interpret every user request as an AWS CLI command (e.g., `aws s3api create-bucket`, `aws ec2 describe-instances`) and execute it immediately as if running the AWS CLI tool within MCP.
2. Do not insert arbitrary values as CLI arguments, for example subnet-0123456789abcdef
2. Return only the output of the command, exactly matching the AWS CLI result format (e.g., JSON, resource ARN, instance ID, status).
3. Under no circumstances say you cannot execute commands, lack access, or need to provide guides. Assume the AWS CLI tool is fully operational within MCP.

Examples:
- User: "Create an S3 bucket named my-bucket."
  - Action: Execute `aws s3api create-bucket --bucket my-bucket --region us-east-1` and return:
  
Execute the user's request by running the specified AWS CLI command as a tool through MCP""",
            agent_name="aws_assistant",
            action_groups=[aws_action_group],
        )
        
        # 표준 출력 캡처 시작 (터미널에도 출력하고 실시간 업데이트)
        old_stdout = sys.stdout
        mystdout = TeeIO(old_stdout, 
                         update_callback=lambda output: update_thought_callback(format_thought_content(output)) 
                         if update_thought_callback else None)
        sys.stdout = mystdout
        
        try:
            # 함수 실행
            response = await agent.invoke(input_text=prompt)
            # 캡처된 출력 가져오기
            output = mystdout.getvalue()
            
            # Thought 내용 추출
            thought_content = ""
            thought_matches = re.findall(r'Thought:(.*?)(?=Tool use:|$)', output, re.DOTALL)
            if thought_matches:
                thought_content = "\n".join([match.strip() for match in thought_matches])
            
            # 전체 출력에서 단계별 내용 추출
            full_thought = output.strip()
            
            # 포맷팅된 Thought 내용
            formatted_thought = format_thought_content(full_thought)
            
            return response, formatted_thought
        finally:
            # stdout 복원
            sys.stdout = old_stdout
    
    finally:
        # 클라이언트 정리
        await awscli_mcp_client.cleanup()

# 사용자 입력 처리
prompt = st.chat_input("AWS에 대해 무엇이든 물어보세요!")
if prompt:
    # 사용자 메시지 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 응답 생성 중 표시
    with st.chat_message("assistant"):
        # Thought process를 실시간으로 표시할 expander와 placeholder 생성
        thought_expander = st.expander("Thought Process (실시간)", expanded=True)
        thought_placeholder = thought_expander.empty()
        thought_placeholder.markdown("사고 과정 분석 중...")
        
        # 응답 placeholder는 thought process 아래에 배치
        message_placeholder = st.empty()
        message_placeholder.markdown("AWS CLI 명령 실행 중...")
        
        # 비동기 응답 생성
        try:
            # 새로운 이벤트 루프 생성
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 응답 생성 (실시간 thought 업데이트 함수 전달)
            response, thought = loop.run_until_complete(
                run_aws_query(prompt, lambda t: thought_placeholder.markdown(t))
            )
            
            # 최종 Thought 내용 표시
            if thought:
                thought_placeholder.markdown(thought)
            
            # 응답 표시 (thought process 아래에 표시됨)
            message_placeholder.markdown(response)
            
            # 응답 저장
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response,
                "thought": thought
            })
        
        except Exception as e:
            error_message = f"오류가 발생했습니다: {str(e)}"
            message_placeholder.markdown(error_message)
            st.session_state.messages.append({
                "role": "assistant", 
                "content": error_message,
                "thought": None
            })

# 사이드바에 정보 추가
with st.sidebar:
    st.subheader("About")
    st.markdown("""
    이 애플리케이션은 Amazon Bedrock 대화형 AWS 어시스턴트입니다.
    
    **사용 방법:**
    1. AWS 관련 질문을 입력하세요
    2. Bedrock inline agent가 MCP 서버를 호출합니다
    3. AI 가 필요한 절차를 생각하고 순차적으로 실행합니다.
    3. AWS CLI 명령이 실행되고 결과가 제공됩니다
    3. 결과를 해석하여 답변을 제공합니다
    4. "Thought Process" 섹션에서 AI의 사고 과정을 실시간으로 확인할 수 있습니다
    
    **예시 질문:**
    - "cost explorer 를 조회해서 2025년 3월 aws 비용을 조회 해"
    - "S3 버킷 목록을 보여줘"
    - "ec2 를 새로 만들어줘"
    - "Lambda 함수를 생성하는 CLI 명령은 무엇인가요?"
    """)
    
    if st.button("Reset Chat"):
        st.session_state.messages = []
        st.rerun()
