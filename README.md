# AWS Chat Assistant with Thought Process

AWS CLI 명령을 실행하고 결과를 해석하는 대화형 어시스턴트입니다. Amazon Bedrock과 AWS CLI를 활용하여 AWS 리소스를 관리하고 정보를 조회할 수 있습니다.

## 사전 요구사항

1. **Python 3.9 이상** 설치
2. **Docker** 설치 (최신 버전 권장)
3. **AWS 계정** 및 적절한 권한을 가진 IAM 사용자
4. **Amazon Bedrock** 접근 권한 (Claude 모델 사용)

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
   > 참고: requirements.txt 파일에는 streamlit, boto3, mcp 패키지가 포함되어 있습니다. boto3의 bedrock-agent-runtime 클라이언트의 invoke_inline_agent 메서드를 사용합니다.

4. Docker 이미지 다운로드:
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
