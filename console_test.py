import boto3
import uuid
import json
import sys
import asyncio
import subprocess
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client

# AWS CLI 쿼리 실행 함수
async def run_aws_query(prompt: str):
    print(f"Starting query execution for prompt: {prompt}")
    
    try:
        print("Creating Bedrock Agent Runtime client")
        # Bedrock Agent Runtime 클라이언트 생성
        bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')
        
        # 고유한 세션 ID 생성
        session_id = f'aws-assistant-session-{str(uuid.uuid4())}'
        print(f"Generated session ID: {session_id}")
        
        # Bedrock 호출
        print("Calling invoke_inline_agent")
        response = bedrock_agent_runtime.invoke_inline_agent(
            foundationModel='anthropic.claude-3-haiku-20240307-v1:0',
            instruction="""you have proper AWS permission. You are An expert assistant who resolves user inquiries about AWS services. 
            Directly perform AWS CLI to create resources or analyze resource status and information of AWS accounts. 
            If a problem occurs during the process, find another way through AWS CLI and try again.""",
            sessionId=session_id,
            enableTrace=True,
            inputText=prompt
        )
        
        print("invoke_inline_agent call completed")
        
        # 응답 추출
        completion_stream = response.get('completion')
        print(f"Received completion stream: {type(completion_stream)}")
        
        # EventStream에서 텍스트 추출
        full_text = ""
        trace_data = {}
        
        if hasattr(completion_stream, '__iter__'):
            print("Processing EventStream")
            chunks = []
            
            for event in completion_stream:
                print(f"Processing event: {type(event)}")
                
                # 이벤트에서 chunk 추출 시도
                if isinstance(event, dict) and 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        try:
                            text = chunk['bytes'].decode('utf-8')
                            chunks.append(text)
                            print(f"Extracted chunk: {text}")
                        except Exception as e:
                            print(f"Failed to decode bytes: {str(e)}")
                
                # 트레이스 정보 추출 시도
                if isinstance(event, dict) and 'trace' in event:
                    trace_data = event['trace']
                    print("Extracted trace data")
            
            # 모든 청크 결합
            full_text = "".join(chunks)
            print(f"Combined text: {full_text}")
        
        # 트레이스 정보를 JSON 문자열로 변환
        trace_str = json.dumps(trace_data, indent=2) if trace_data else "{}"
        print("Trace information processed")
        
        return full_text, trace_str
    
    except Exception as e:
        import traceback
        print(f"Error in run_aws_query: {str(e)}")
        print(f"Error details: {traceback.format_exc()}")
        raise

# 직접 AWS CLI 명령 실행 (subprocess 사용)
def run_aws_cli_command(command: str):
    print(f"Running AWS CLI command: {command}")
    
    try:
        # subprocess를 사용하여 AWS CLI 명령 실행
        result = subprocess.run(command.split(), capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Command succeeded with output: {result.stdout}")
            return result.stdout
        else:
            print(f"Command failed with error: {result.stderr}")
            return result.stderr
    
    except Exception as e:
        import traceback
        print(f"Error executing command: {str(e)}")
        print(f"Error details: {traceback.format_exc()}")
        return f"Error: {str(e)}"

async def main():
    # 테스트 프롬프트
    prompt = "S3 버킷 목록을 보여줘"
    
    try:
        # 응답 생성
        response, thought = await run_aws_query(prompt)
        print("\n--- Final Results from Bedrock ---")
        print(f"Response: {response}")
        print(f"Thought (sample): {thought[:200]}...")
        
        # AWS CLI 명령 실행 테스트
        print("\n--- Testing AWS CLI Command ---")
        cli_response = run_aws_cli_command("aws s3 ls")
        print(f"CLI Response: {cli_response}")
    
    except Exception as e:
        print(f"Error in main: {str(e)}")

if __name__ == "__main__":
    # 이벤트 루프 생성 및 실행
    asyncio.run(main())
