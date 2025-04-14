import boto3
import uuid
import json
import sys

def main():
    print("Testing invoke_inline_agent function...")
    
    # Bedrock Agent Runtime 클라이언트 생성
    bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')
    
    # 고유한 세션 ID 생성
    session_id = f'aws-assistant-session-{str(uuid.uuid4())}'
    print(f"Generated session ID: {session_id}")
    
    # 테스트 프롬프트
    prompt = "S3 버킷 목록을 보여줘"
    
    try:
        print("Calling invoke_inline_agent...")
        response = bedrock_agent_runtime.invoke_inline_agent(
            foundationModel='anthropic.claude-3-haiku-20240307-v1:0',
            instruction="""you have proper AWS permission. You are An expert assistant who resolves user inquiries about AWS services. 
            Directly perform AWS CLI to create resources or analyze resource status and information of AWS accounts. 
            If a problem occurs during the process, find another way through AWS CLI and try again.""",
            sessionId=session_id,
            enableTrace=True,
            inputText=prompt
        )
        
        print("\n--- Response Type ---")
        print(f"Response type: {type(response)}")
        print(f"Response keys: {response.keys() if isinstance(response, dict) else 'Not a dict'}")
        
        # 응답 내용 출력
        if isinstance(response, dict):
            for key, value in response.items():
                print(f"\nKey: {key}")
                print(f"Value type: {type(value)}")
                if key == 'completion':
                    print(f"Completion: {value}")
                    
                    # EventStream 처리
                    if hasattr(value, '__iter__'):
                        print("\n--- Processing EventStream ---")
                        full_text = ""
                        chunks = []
                        
                        for i, event in enumerate(value):
                            print(f"\nEvent {i+1}:")
                            print(f"Event type: {type(event)}")
                            
                            # 이벤트에서 chunk 추출 시도
                            if isinstance(event, dict) and 'chunk' in event:
                                chunk = event['chunk']
                                if 'bytes' in chunk:
                                    try:
                                        text = chunk['bytes'].decode('utf-8')
                                        chunks.append(text)
                                        print(f"Chunk text: {text}")
                                    except:
                                        print("Failed to decode bytes")
                        
                        # 모든 청크 결합
                        full_text = "".join(chunks)
                        print(f"\nFull text from chunks: {full_text}")
                
                elif key == 'trace':
                    print(f"Trace available: {bool(value)}")
                    print(f"Trace sample: {str(value)[:200]}..." if value else "No trace")
                else:
                    print(f"Value: {value}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
