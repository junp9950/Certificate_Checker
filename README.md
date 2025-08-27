# 🔐 SSL Certificate Checker v5.1

OpenSSL 설치 없이 SSL 인증서의 체인 완전성을 검증하는 크로스플랫폼 데스크톱 도구입니다.

## ✨ 주요 기능

- 🔍 **인증서 체인 완전성 검증** - 5단계 검증 로직으로 정확한 체인 상태 판별
- 🎯 **실제 드래그 앤 드롭** - Windows 파일탐색기에서 바로 끌어다 놓기 지원
- 🎨 **VS Code 스타일 다크테마** - 전문적인 UI/UX와 라이트/다크 모드 전환
- 🌳 **트리 시각화** - 인증서 체인을 직관적인 트리 구조로 표시
- 📦 **다양한 형식 지원** - PEM, CRT, PFX, P12, DER 파일 분석
- 🔐 **자동 PFX 비밀번호** - 팝업으로 안전한 비밀번호 입력
- 🖥️ **Pure Python GUI** - OpenSSL 설치 불필요
- 🌐 **크로스플랫폼** - Windows GUI + Linux/macOS CLI 모두 지원

## 🚀 빠른 시작

### Windows (GUI)
```bash
# 1. 다운로드 후 폴더로 이동
# 2. 더블클릭으로 자동 설치 및 실행
Start_SSL_Checker.bat

# 또는 직접 실행
python ssl_checker_v3.py
```

### Linux/macOS (CLI)
```bash
# bash 스크립트 버전 (OpenSSL 필요)
chmod +x cert_chain_checker.sh
./cert_chain_checker.sh certificate.pem

# GUI 버전 (드래그앤드롭 지원)
pip install cryptography tkinterdnd2
python ssl_checker_v3.py
```

## 🔍 분석 결과 예시

### ✅ 완전한 체인 - 트리 시각화
```
📦 PFX/PKCS#12 파일 분석 (3개 인증서)
🔑 개인키: 포함됨
🔗 체인 상태: ✅ 완전한 체인

🌳 인증서 체인 구조:
├─ 🏆 Root CA (DigiCert)
│   └─ 🔗 Intermediate CA (DigiCert TLS RSA)
│       └─ 🎯 End Entity (*.example.com)

🏷️ Subject: CN=*.example.com
📅 유효 기간: 2025-08-20 ~ 2026-09-19 (389일 남음)
🌐 도메인 (SAN): *.example.com, example.com
```

### ⚠️ 불완전한 체인 - 5단계 검증 결과
```
📄 단일 인증서 (체인 없음)
❌ 체인 상태: 중간 CA 필요

🔍 5단계 검증 결과:
✅ 1단계: 인증서 개수 확인
❌ 2단계: 루트 CA 확인 (없음)
❌ 3단계: 서명 체인 검증 (불가)
✅ 4단계: 유효 기간 확인
❌ 5단계: DN 정규화 검증 (체인 없음)

🏷️ Subject: CN=*.example.com
📅 유효 기간: 2025-08-20 ~ 2026-09-19 (389일 남음)
```

## 📋 지원 파일 형식

| 형식 | 확장자 | 설명 |
|------|--------|------|
| **PEM** | .pem | Base64 인코딩 인증서 |
| **CRT** | .crt, .cer | 인증서 파일 |
| **PFX** | .pfx, .p12 | 비밀번호로 보호된 인증서+개인키 |
| **DER** | .der | 바이너리 인코딩 |

## 🛡️ 보안 특징

- 🏠 **로컬 실행**: 네트워크 전송 없음, 인증서가 외부로 전송되지 않음
- 🗑️ **자동 정리**: PFX 추출 시 임시 파일 즉시 삭제
- ✅ **입력 검증**: 파일 크기/확장자 검증으로 악성 파일 차단
- 🔒 **안전한 파싱**: 모든 오류 상황에 대한 예외 처리
- 🔐 **보안 드래그앤드롭**: 다중 파싱 방법으로 안전한 파일 처리

## 📖 사용 예시

1. **드래그앤드롭으로 PFX 인증서 검증**
   - `Start_SSL_Checker.bat` 더블클릭
   - Windows 파일탐색기에서 PFX 파일을 GUI로 끌어다 놓기
   - 자동 비밀번호 팝업에서 입력
   - 트리 구조로 체인 시각화 확인
   - 다크/라이트 테마 전환 가능

2. **Linux 서버에서 PEM 체인 검증**
   ```bash
   ./cert_chain_checker.sh fullchain.pem
   # 결과: "✅ 완전한 인증서 체인입니다"
   ```

## 🔧 설치 및 요구사항

### 자동 설치 (Windows)
- `Start_SSL_Checker.bat` 실행 시 자동으로 `tkinterdnd2` 포함 필요 라이브러리 설치
- 4단계 자동 설치: Python 확인 → pip 업그레이드 → 의존성 설치 → GUI 실행

### 수동 설치
```bash
pip install -r requirements.txt
# 또는 개별 설치
pip install cryptography tkinterdnd2
```

### 시스템 요구사항
- **Windows**: Windows 10/11 + Python 3.7+
- **Linux**: Ubuntu 18.04+ + Python 3.7+ + OpenSSL (bash 스크립트용)
- **macOS**: macOS 10.14+ + Python 3.7+ + OpenSSL (bash 스크립트용)

## 📁 파일 구성

```
certificate_check/
├── 🚀 Start_SSL_Checker.bat     # Windows 원클릭 실행기 (v3.0)
├── 🖥️ ssl_checker_v3.py         # 고급 GUI 앱 (드래그앤드롭, 다크테마)
├── 🔧 cert_chain_checker.sh     # Linux/macOS CLI 스크립트
├── 📋 requirements.txt          # Python 의존성 (tkinterdnd2 포함)
├── 📁 docs/                     # 개발 문서
│   ├── CLAUDE.md               # 개발 히스토리
│   └── CLAUDE_FULL_HISTORY.md  # 상세 개발 로그
└── 📖 README.md                 # 이 파일
```

## 🎯 사용 케이스

- **웹 관리자**: 드래그앤드롭으로 빠른 SSL 인증서 체인 완전성 확인
- **보안 담당자**: 5단계 검증으로 정확한 중간 CA 누락 여부 판별  
- **개발자**: 트리 시각화로 직관적인 SSL 설정 검증
- **IT 운영팀**: 다크테마 UI로 편안한 대량 인증서 검증
- **시스템 관리자**: 자동화된 PFX 비밀번호 처리로 효율적인 운영

## 🤝 기여

이슈나 개선 제안은 GitHub Issues에서 언제든 환영합니다!

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

**🤖 Generated with [Claude Code](https://claude.ai/code)**

*드래그앤드롭 한 번으로 SSL 인증서 체인을 완벽하게 검증하세요! 🎯*