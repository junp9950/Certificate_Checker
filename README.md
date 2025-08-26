# SSL 인증서 체인 검증 도구

SSL 인증서가 완전한 체인을 가지고 있는지, 중간 인증서가 누락되지 않았는지 검증하는 도구입니다.

## 사용법

```bash
./cert_chain_checker.sh <인증서파일>
```

## 예시

```bash
./cert_chain_checker.sh certificate.pem
```

## 기능

- 📋 인증서 개수 확인
- 📜 각 인증서 정보 표시 (Subject, Issuer, Serial, 만료일)
- 🔍 체인 검증 (OpenSSL verify)
- 📋 체인 순서 검사 (리프 → 중간CA → 루트CA)
- 🔐 서명 검증
- 📊 최종 결과 및 문제 해결 방법 제시

## 결과

- ✅ 완전한 인증서 체인: 모든 인증서가 올바르게 연결됨
- ❌ 체인 문제: 중간 인증서 누락 또는 순서 오류

## 요구사항

- OpenSSL 설치 필요
- bash 쉘 환경