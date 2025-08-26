# 🔐 SSL Certificate Checker v2.0

OpenSSL 설치 없이 SSL 인증서의 체인 완전성을 검증하는 크로스플랫폼 데스크톱 도구입니다.

## ✨ 주요 기능

- 🔍 **인증서 체인 완전성 검증** - PFX는 "완전한 체인", 단일 PEM은 "중간 CA 필요" 정확히 판별
- 🖥️ **Pure Python GUI** - OpenSSL 설치 불필요 (cryptography 라이브러리만 사용)
- 📦 **다양한 형식 지원** - PEM, CRT, PFX, P12, DER 파일 분석
- 🔐 **PFX 비밀번호 지원** - 안전한 비밀번호 입력으로 PKCS#12 파일 분석
- 🌐 **크로스플랫폼** - Windows GUI + Linux/macOS CLI 모두 지원

## 🚀 빠른 시작

### Windows (GUI)
```bash
# 1. 다운로드 후 폴더로 이동
# 2. 더블클릭
Start_SSL_Checker.bat
```

### Linux/macOS (CLI)
```bash
# bash 스크립트 버전 (OpenSSL 필요)
chmod +x cert_chain_checker.sh
./cert_chain_checker.sh certificate.pem

# GUI 버전
pip install cryptography
python ssl_checker_pure.py
```

## 🔍 분석 결과 예시

### ✅ 완전한 체인 (PFX 파일)
```
📦 PFX/PKCS#12 파일 분석
🔑 개인키: 포함됨
📜 추가 인증서: 2개
🔗 체인 상태: ✅ 완전한 체인

🏷️ Subject: CN=*.example.com
📅 유효 기간: 2025-08-20 ~ 2026-09-19 (389일 남음)
🌐 도메인 (SAN): *.example.com, example.com
```

### ⚠️ 불완전한 체인 (단일 PEM)
```
📄 단일 인증서 (체인 없음)
⚠️ 중간 인증서가 필요할 수 있습니다

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

## 📖 사용 예시

1. **Windows에서 PFX 인증서 검증**
   - `Start_SSL_Checker.bat` 더블클릭
   - PFX 파일 선택
   - 비밀번호 입력
   - 결과 확인: "✅ 완전한 체인" 또는 "⚠️ 불완전한 체인"

2. **Linux 서버에서 PEM 체인 검증**
   ```bash
   ./cert_chain_checker.sh fullchain.pem
   # 결과: "✅ 완전한 인증서 체인입니다"
   ```

## 🔧 설치 및 요구사항

### 자동 설치 (Windows)
- `Start_SSL_Checker.bat` 실행 시 자동으로 필요한 라이브러리 설치

### 수동 설치
```bash
pip install cryptography
```

### 시스템 요구사항
- **Windows**: Windows 10/11 + Python 3.7+
- **Linux**: Ubuntu 18.04+ + Python 3.7+ + OpenSSL (bash 스크립트용)
- **macOS**: macOS 10.14+ + Python 3.7+ + OpenSSL (bash 스크립트용)

## 📁 파일 구성

```
certificate_check/
├── 🚀 Start_SSL_Checker.bat     # Windows 원클릭 실행기
├── 🖥️ ssl_checker_pure.py       # Pure Python GUI 앱
├── 🔧 cert_chain_checker.sh     # Linux/macOS CLI 스크립트
├── 📋 requirements.txt          # Python 의존성
└── 📖 README.md                 # 이 파일
```

## 🎯 사용 케이스

- **웹 관리자**: 서버 SSL 인증서 설치 전 체인 완전성 확인
- **보안 담당자**: 인증서 갱신 시 중간 CA 누락 여부 검증  
- **개발자**: 테스트 환경의 SSL 설정 검증
- **IT 운영팀**: 다양한 형식의 인증서 파일 일괄 검증

## 🤝 기여

이슈나 개선 제안은 GitHub Issues에서 언제든 환영합니다!

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

**🤖 Generated with [Claude Code](https://claude.ai/code)**

*SSL 인증서가 완전한 체인을 가지고 있는지 확실하지 않을 때, 이 도구로 한 번에 확인하세요!*