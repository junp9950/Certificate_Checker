#!/bin/bash

# SSL 인증서 체인 검증 도구
# 사용법: ./cert_chain_checker.sh <certificate_file>

CERT_FILE="$1"

if [ -z "$CERT_FILE" ]; then
    echo "사용법: $0 <인증서_파일>"
    echo "예시: $0 certificate.pem"
    exit 1
fi

if [ ! -f "$CERT_FILE" ]; then
    echo "오류: 파일 '$CERT_FILE'이 존재하지 않습니다."
    exit 1
fi

echo "=== SSL 인증서 체인 검증 도구 ==="
echo "대상 파일: $CERT_FILE"
echo ""

# 1. 인증서 개수 확인
CERT_COUNT=$(grep -c "BEGIN CERTIFICATE" "$CERT_FILE")
echo "📋 발견된 인증서 개수: $CERT_COUNT개"

if [ "$CERT_COUNT" -eq 0 ]; then
    echo "❌ 오류: 유효한 인증서가 없습니다."
    exit 1
fi

# 2. 각 인증서 정보 표시
echo ""
echo "📜 인증서 정보:"
echo "----------------------------------------"

# 임시 디렉토리 생성
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# 인증서들을 개별 파일로 분리
split_certs() {
    local file="$1"
    local temp_dir="$2"
    local cert_num=0
    local in_cert=false
    local cert_content=""
    
    while IFS= read -r line; do
        if [[ "$line" == "-----BEGIN CERTIFICATE-----" ]]; then
            in_cert=true
            cert_content="$line"$'\n'
        elif [[ "$line" == "-----END CERTIFICATE-----" ]]; then
            cert_content+="$line"
            echo "$cert_content" > "$temp_dir/cert_$cert_num.pem"
            cert_num=$((cert_num + 1))
            in_cert=false
            cert_content=""
        elif [ "$in_cert" = true ]; then
            cert_content+="$line"$'\n'
        fi
    done < "$file"
}

split_certs "$CERT_FILE" "$TEMP_DIR"

# 각 인증서 정보 출력
for i in $(seq 0 $((CERT_COUNT - 1))); do
    echo "[$((i + 1))] 인증서 정보:"
    
    # Subject와 Issuer 정보 추출
    SUBJECT=$(openssl x509 -in "$TEMP_DIR/cert_$i.pem" -noout -subject 2>/dev/null | sed 's/subject=//')
    ISSUER=$(openssl x509 -in "$TEMP_DIR/cert_$i.pem" -noout -issuer 2>/dev/null | sed 's/issuer=//')
    SERIAL=$(openssl x509 -in "$TEMP_DIR/cert_$i.pem" -noout -serial 2>/dev/null | sed 's/serial=//')
    
    echo "   Subject: $SUBJECT"
    echo "   Issuer:  $ISSUER"
    echo "   Serial:  $SERIAL"
    
    # 만료일 확인
    EXPIRY=$(openssl x509 -in "$TEMP_DIR/cert_$i.pem" -noout -enddate 2>/dev/null | sed 's/notAfter=//')
    echo "   만료일:  $EXPIRY"
    
    # 자체 서명 인증서인지 확인
    if [ "$SUBJECT" = "$ISSUER" ]; then
        echo "   타입:    루트 CA (자체 서명)"
    elif [ $i -eq 0 ]; then
        echo "   타입:    엔드 엔티티 (리프 인증서)"
    else
        echo "   타입:    중간 CA"
    fi
    echo ""
done

# 3. 체인 검증
echo "🔍 체인 검증 결과:"
echo "----------------------------------------"

# OpenSSL로 체인 검증
VERIFY_RESULT=$(openssl verify -CAfile <(cat "$CERT_FILE") "$TEMP_DIR/cert_0.pem" 2>&1)
VERIFY_EXIT_CODE=$?

if [ $VERIFY_EXIT_CODE -eq 0 ]; then
    echo "✅ 인증서 체인이 유효합니다."
else
    echo "❌ 인증서 체인에 문제가 있습니다:"
    echo "   $VERIFY_RESULT"
fi

# 4. 추가 검사들
echo ""
echo "🔧 추가 검사:"
echo "----------------------------------------"

# 체인 순서 확인
echo "📋 체인 순서 검사:"
CHAIN_OK=true

for i in $(seq 0 $((CERT_COUNT - 2))); do
    NEXT_I=$((i + 1))
    
    # 현재 인증서의 Issuer와 다음 인증서의 Subject 비교
    CURRENT_ISSUER=$(openssl x509 -in "$TEMP_DIR/cert_$i.pem" -noout -issuer 2>/dev/null | sed 's/issuer=//')
    NEXT_SUBJECT=$(openssl x509 -in "$TEMP_DIR/cert_$NEXT_I.pem" -noout -subject 2>/dev/null | sed 's/subject=//')
    
    if [ "$CURRENT_ISSUER" = "$NEXT_SUBJECT" ]; then
        echo "   ✅ 인증서 $((i + 1)) → $((NEXT_I + 1)): 체인 연결 정상"
    else
        echo "   ❌ 인증서 $((i + 1)) → $((NEXT_I + 1)): 체인 연결 문제"
        echo "      현재 Issuer: $CURRENT_ISSUER"
        echo "      다음 Subject: $NEXT_SUBJECT"
        CHAIN_OK=false
    fi
done

# 서명 검증
echo ""
echo "🔐 서명 검증:"
for i in $(seq 0 $((CERT_COUNT - 2))); do
    NEXT_I=$((i + 1))
    
    # 다음 인증서로 현재 인증서의 서명 검증
    VERIFY_SIG=$(openssl verify -CAfile "$TEMP_DIR/cert_$NEXT_I.pem" "$TEMP_DIR/cert_$i.pem" 2>&1)
    if echo "$VERIFY_SIG" | grep -q "OK"; then
        echo "   ✅ 인증서 $((i + 1))의 서명이 인증서 $((NEXT_I + 1))로 검증됨"
    else
        echo "   ❌ 인증서 $((i + 1))의 서명 검증 실패"
        CHAIN_OK=false
    fi
done

# 최종 결과
echo ""
echo "📊 최종 결과:"
echo "----------------------------------------"
if [ "$CHAIN_OK" = true ] && [ $VERIFY_EXIT_CODE -eq 0 ]; then
    echo "✅ 완전한 인증서 체인입니다. 중간 인증서 누락 없음."
    exit 0
else
    echo "❌ 인증서 체인에 문제가 있거나 중간 인증서가 누락되었습니다."
    echo ""
    echo "💡 해결 방법:"
    echo "   1. 중간 인증서가 누락되었다면 CA에서 제공하는 전체 체인을 확인하세요"
    echo "   2. 인증서 순서가 잘못되었을 수 있습니다 (리프 → 중간CA → 루트CA 순)"
    echo "   3. 만료된 인증서가 있는지 확인하세요"
    exit 1
fi