# 🔐 SSL Certificate Checker v2.0 - Final

## 📋 **최종 완성 버전**
OpenSSL 설치 없이 Pure Python으로 SSL 인증서를 검증하는 데스크톱 애플리케이션

## 📁 **최종 파일 구성**

### **필수 파일 (3개)**
- 🚀 **Start_SSL_Checker.bat** - 원클릭 실행기 (자동 설치 + 실행)
- 🖥️ **ssl_checker_pure.py** - Pure Python GUI 앱 (메인)  
- 📋 **requirements.txt** - 의존성 목록 (cryptography만 필요)

### **테스트용 인증서들**
- **IIS/**: STAR.nhlogis.co.kr.pfx (비밀번호: nhlogis2152)
- **Nginx/**: STAR.nhlogis.co.kr.crt, STAR.nhlogis.co.kr.key, ca-bundle.crt
- **PEM/**: STAR.nhlogis.co.kr_cert.pem, STAR.nhlogis.co.kr_key.pem, ca-bundle.pem
- **Tomcat/**: STAR.nhlogis.co.kr.keystore

### **문서**
- 📖 **README.md** - 기존 bash 스크립트 가이드
- 📝 **CLAUDE.md** - 작업 기록
- 📄 **README_FINAL.md** - 이 파일

## 🚀 **사용 방법**

### **Windows에서 실행 (GUI 추천)**
```bash
더블클릭: Start_SSL_Checker.bat
```

### **Linux/macOS에서 실행 (CLI)**
```bash
# bash 스크립트 버전 (OpenSSL 필요)
chmod +x cert_chain_checker.sh
./cert_chain_checker.sh certificate.pem

# 또는 GUI 버전
pip install cryptography
python ssl_checker_pure.py
```

### **수동 실행**
```bash
pip install cryptography
python ssl_checker_pure.py
```

## ✨ **주요 기능**
- 🔍 **다양한 형식 지원**: PEM, CRT, PFX, P12, DER
- 🔐 **PFX 비밀번호 지원**: 안전한 비밀번호 입력
- 📊 **3단계 분석**: 요약 / 상세 정보 / 확장 필드
- 🌐 **SAN 도메인 표시**: Subject Alternative Name 파싱
- ⏰ **만료일 체크**: 정확한 만료 날짜까지 일수 계산
- 🔧 **강력한 오류 처리**: 어떤 인증서든 안전하게 분석

## 🛠️ **기술 특징**
- ✅ **Pure Python**: OpenSSL 설치 불필요
- ✅ **cryptography 라이브러리**: 업계 표준 암호화 라이브러리
- ✅ **크로스 플랫폼**: Windows, macOS, Linux 지원
- ✅ **GUI 인터페이스**: Tkinter 기반 직관적 UI
- ✅ **안전한 처리**: 모든 파싱 오류 예외 처리

## 🔒 **보안**
- 🏠 **로컬 실행**: 네트워크 전송 없음
- 🗑️ **임시 파일 자동 삭제**: PFX 추출 후 즉시 정리
- ✅ **입력 검증**: 파일 크기/확장자 검증
- 🛡️ **안전한 명령어**: 인젝션 공격 방지

## 🧪 **테스트된 인증서들**
- ✅ **nhlogis.co.kr 와일드카드 인증서**
- ✅ **GoGetSSL RSA DV CA 발급**
- ✅ **2025-08-20 ~ 2026-09-19 유효**
- ✅ **모든 형식에서 동일한 Serial Number 확인**

---

## 🎯 **사용법 요약**
1. `Start_SSL_Checker.bat` 더블클릭
2. 인증서 파일 선택 (PEM, CRT, PFX 등)
3. PFX인 경우 비밀번호 입력
4. 검증 버튼 클릭
5. 결과 확인 (요약/상세/확장 탭)

**완성! 🎉**