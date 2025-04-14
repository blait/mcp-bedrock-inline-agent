# AWS Chat Assistant with Thought Process

AWS CLI 명령을 실행하고 결과를 해석하는 대화형 어시스턴트입니다. Amazon Bedrock과 AWS CLI를 활용하여 AWS 리소스를 관리하고 정보를 조회할 수 있습니다.


<img width="753" alt="image" src="https://github.com/user-attachments/assets/5496f5cf-f8e8-4133-9085-4f9f4719acf5" />

## 사전 요구사항

1. **Python 3.9 이상** 설치
2. **Docker** 설치 (최신 버전 권장)
3. **AWS 계정** 및 적절한 권한을 가진 IAM 사용자
4. **Amazon Bedrock** 접근 권한 (Claude 모델 사용)
5. **Amazon Bedrock Inline Agent SDK** 설치 (아래 설치 방법 참조)

## 설치 방법

1. 저장소 클론 또는 다운로드:
   ```bash
   git clone <repository-url>
   cd aws_chat_app
   ```

2. 가상 환경 생성 및 활성화:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # 또는
   .venv\Scripts\activate  # Windows
   ```

3. 필요한 패키지 설치:
   ```bash
   pip install -r requirements.txt
   ```
   > 참고: requirements.txt 파일에는 streamlit, boto3, mcp 패키지가 포함되어 있습니다.

4. Amazon Bedrock Inline Agent SDK 설치:
   ```bash
   # Amazon Bedrock Agent 샘플 저장소 클론
   git clone https://github.com/awslabs/amazon-bedrock-agent-samples.git
   
   # InlineAgent 디렉토리로 이동
   cd amazon-bedrock-agent-samples/src/InlineAgent
   
   # 개발 모드로 패키지 설치
   pip install -e .
   
   # 원래 디렉토리로 돌아가기
   cd ../../../
   ```
   > 중요: InlineAgent SDK는 Amazon Bedrock의 Inline Agent 기능을 사용하기 위한 Python 래퍼입니다. 이 SDK는 AWS CLI 명령을 실행하고 결과를 처리하는 데 필요합니다.

5. Docker 이미지 다운로드:
   ```bash
   docker pull ghcr.io/alexei-led/aws-mcp-server:latest
   ```

5. AWS 자격 증명 설정:
   - `~/.aws/credentials` 파일에 AWS 자격 증명이 설정되어 있어야 합니다.
   - 필요한 AWS 권한이 설정되어 있어야 합니다.
   ```
   [default]
   aws_access_key_id = YOUR_ACCESS_KEY
   aws_secret_access_key = YOUR_SECRET_KEY
   region = YOUR_PREFERRED_REGION
   ```

   > 중요: 애플리케이션은 자동으로 사용자의 홈 디렉토리에서 AWS 자격 증명을 찾습니다. 코드에서 `USER_HOME` 변수가 자동으로 사용자의 홈 디렉토리를 감지합니다.

## 실행 방법

1. 가상 환경이 활성화되어 있는지 확인:
   ```bash
   source .venv/bin/activate  # Linux/macOS
   # 또는
   .venv\Scripts\activate  # Windows
   ```

2. 애플리케이션 실행:
   ```bash
   streamlit run aws_chat_with_thoughts.py
   ```

3. 웹 브라우저가 자동으로 열리고 애플리케이션에 접속됩니다.
   - 기본 URL: http://localhost:8501

## 문제 해결

1. **Docker 관련 오류**:
   - Docker 데몬이 실행 중인지 확인: `docker ps`
   - 이미지가 제대로 다운로드되었는지 확인: `docker images`

2. **AWS 자격 증명 오류**:
   - AWS CLI가 제대로 구성되었는지 확인: `aws sts get-caller-identity`
   - 필요한 권한이 있는지 확인

3. **라이브러리 관련 오류**:
   - 가상 환경이 활성화되어 있는지 확인
   - 필요한 모든 패키지가 설치되어 있는지 확인: `pip list`

4. **InlineAgent SDK 관련 오류**:
   - InlineAgent SDK가 올바르게 설치되었는지 확인: `pip list | grep InlineAgent`
   - 설치 과정에서 오류가 발생한 경우 다음 명령으로 다시 시도:
     ```bash
     cd amazon-bedrock-agent-samples/src/InlineAgent
     pip install -e .
     ```
   - 저장소 클론에 문제가 있는 경우 저장소를 삭제하고 다시 클론:
     ```bash
     rm -rf amazon-bedrock-agent-samples
     git clone https://github.com/awslabs/amazon-bedrock-agent-samples.git
     ```

## 아키텍처 및 작동 방식

이 애플리케이션은 다음과 같은 구성 요소로 이루어져 있습니다:

1. **Streamlit 웹 인터페이스**
   - 사용자 입력을 받고 결과를 표시하는 대화형 웹 인터페이스
   - 실시간으로 AI의 사고 과정을 보여주는 확장 패널

2. **Amazon Bedrock Inline Agent**
   - 사용자 질문을 해석하고 적절한 AWS CLI 명령을 결정
   - InlineAgent SDK를 통해 통합

3. **MCP (Model Context Protocol) 서버**
   - Docker 컨테이너에서 실행되는 AWS CLI 명령 처리기
   - AWS 자격 증명을 안전하게 사용하여 명령 실행

4. **작동 흐름**
   - 사용자가 질문 입력
   - Bedrock Inline Agent가 질문을 해석하고 필요한 AWS CLI 명령 결정
   - MCP 서버가 AWS CLI 명령을 실행하고 결과 반환
   - 결과를 해석하여 사용자에게 표시

![아키텍처 다이어그램](https://github.com/user-attachments/assets/5496f5cf-f8e8-4133-9085-4f9f4719acf5)

## 주요 기능

- AWS CLI 명령 실행 및 결과 해석
- 대화형 인터페이스로 AWS 리소스 관리
- AI의 사고 과정 확인 가능 (Thought Process 확장 패널)
- 채팅 히스토리 저장 및 초기화 (사이드바의 Reset Chat 버튼)
- AWS 리소스 생성, 조회, 수정 및 삭제 기능

## 예시 질문

- "cost explorer 를 조회해서 2025년 3월 aws 비용을 조회 해"
- "S3 버킷 목록을 보여줘"
- "ec2 를 새로 만들어줘"
- "Lambda 함수를 생성하는 CLI 명령은 무엇인가요?"
- "현재 계정의 모든 리전에서 실행 중인 EC2 인스턴스를 찾아줘"
- "지난 달 가장 비용이 많이 발생한 서비스는 무엇인가요?"






