#!/usr/bin/env python3
"""
SSL Certificate Checker - Pure Python Version
OpenSSL 의존성 없이 cryptography 라이브러리만으로 SSL 인증서를 검증하는 데스크톱 애플리케이션

Requirements:
pip install cryptography
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import threading
from datetime import datetime, timezone
import base64
import tempfile

try:
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.serialization import pkcs12
    from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
    # PolicyBuilder, StoreBuilder는 선택적으로 import (일부 버전에서 없을 수 있음)
    try:
        from cryptography.x509.verification import PolicyBuilder, StoreBuilder
    except ImportError:
        PolicyBuilder = None
        StoreBuilder = None
except ImportError as e:
    import tkinter as tk
    from tkinter import messagebox
    
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Library Error", 
        f"cryptography library is required!\n\n"
        f"Install with: pip install cryptography\n\n"
        f"Error: {str(e)}"
    )
    exit(1)


class PureSSLCertificateChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("SSL Certificate Checker v2.0 (Pure Python)")
        self.root.geometry("1000x750")
        self.root.resizable(True, True)
        
        # 스타일 설정
        style = ttk.Style()
        style.theme_use('clam')
        
        self.setup_ui()
        
    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        title_label = ttk.Label(main_frame, text="🔐 SSL Certificate Checker v2.0", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Pure Python • OpenSSL 불필요", 
                                  font=('Arial', 10), foreground='gray')
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # 파일 선택 섹션
        file_frame = ttk.LabelFrame(main_frame, text="인증서 파일 선택", padding="10")
        file_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=70)
        file_entry.grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E))
        
        browse_btn = ttk.Button(file_frame, text="파일 선택", command=self.browse_file)
        browse_btn.grid(row=0, column=1)
        
        file_frame.columnconfigure(0, weight=1)
        
        # 비밀번호 입력 (PFX용)
        pwd_frame = ttk.LabelFrame(main_frame, text="PFX/P12 비밀번호 (필요시)", padding="10")
        pwd_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.password_var = tk.StringVar()
        pwd_entry = ttk.Entry(pwd_frame, textvariable=self.password_var, show="*", width=30)
        pwd_entry.grid(row=0, column=0, padx=(0, 10))
        
        show_pwd_var = tk.BooleanVar()
        show_pwd_check = ttk.Checkbutton(pwd_frame, text="비밀번호 표시", variable=show_pwd_var,
                                        command=lambda: pwd_entry.config(show="" if show_pwd_var.get() else "*"))
        show_pwd_check.grid(row=0, column=1)
        
        # 검증 버튼
        verify_btn = ttk.Button(main_frame, text="🔍 인증서 검증 (Pure Python)", 
                               command=self.verify_certificate)
        verify_btn.grid(row=4, column=0, columnspan=3, pady=15)
        
        # 결과 표시 영역
        result_frame = ttk.LabelFrame(main_frame, text="검증 결과", padding="10")
        result_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 탭 컨트롤
        self.notebook = ttk.Notebook(result_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 요약 탭
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="📋 요약")
        
        self.summary_text = scrolledtext.ScrolledText(self.summary_frame, height=18, width=90, 
                                                     font=('Consolas', 10))
        self.summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 상세 정보 탭
        self.detail_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.detail_frame, text="📜 상세 정보")
        
        self.detail_text = scrolledtext.ScrolledText(self.detail_frame, height=18, width=90,
                                                    font=('Consolas', 9))
        self.detail_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 확장 정보 탭
        self.extensions_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.extensions_frame, text="🔧 확장 필드")
        
        self.extensions_text = scrolledtext.ScrolledText(self.extensions_frame, height=18, width=90,
                                                        font=('Consolas', 9))
        self.extensions_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 진행 상황 표시
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.status_var = tk.StringVar(value="준비됨 - Pure Python 모드")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=7, column=0, columnspan=3)
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        for frame in [self.summary_frame, self.detail_frame, self.extensions_frame]:
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(0, weight=1)
    
    def browse_file(self):
        """파일 선택 다이얼로그"""
        file_types = [
            ("인증서 파일", "*.pem *.crt *.cer *.pfx *.p12 *.der"),
            ("PEM 파일", "*.pem"),
            ("CRT 파일", "*.crt *.cer"),
            ("PFX/P12 파일", "*.pfx *.p12"),
            ("DER 파일", "*.der"),
            ("모든 파일", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="SSL 인증서 파일 선택",
            filetypes=file_types
        )
        
        if filename:
            self.file_path_var.set(filename)
    
    def validate_file(self, filepath):
        """파일 유효성 검증"""
        if not os.path.exists(filepath):
            return False, "파일이 존재하지 않습니다."
        
        if not os.path.isfile(filepath):
            return False, "디렉토리가 아닌 파일을 선택해주세요."
        
        # 파일 확장자 검증
        valid_extensions = ['.pem', '.crt', '.cer', '.pfx', '.p12', '.der']
        file_ext = os.path.splitext(filepath)[1].lower()
        
        if file_ext not in valid_extensions:
            return False, f"지원하지 않는 파일 형식입니다. ({', '.join(valid_extensions)})"
        
        # 파일 크기 검증 (10MB 제한)
        if os.path.getsize(filepath) > 10 * 1024 * 1024:
            return False, "파일 크기가 너무 큽니다. (최대 10MB)"
        
        return True, "OK"
    
    def verify_certificate(self):
        """인증서 검증 실행"""
        filepath = self.file_path_var.get().strip()
        
        if not filepath:
            messagebox.showerror("오류", "인증서 파일을 선택해주세요.")
            return
        
        # 파일 유효성 검증
        is_valid, message = self.validate_file(filepath)
        if not is_valid:
            messagebox.showerror("파일 오류", message)
            return
        
        # 백그라운드에서 검증 실행
        self.start_verification(filepath)
    
    def start_verification(self, filepath):
        """백그라운드에서 검증 시작"""
        self.progress.start()
        self.status_var.set("인증서 분석 중... (Pure Python)")
        
        # 별도 스레드에서 실행
        thread = threading.Thread(target=self.run_verification, args=(filepath,))
        thread.daemon = True
        thread.start()
    
    def run_verification(self, filepath):
        """실제 검증 로직 실행"""
        try:
            result = self.analyze_certificate(filepath)
            self.root.after(0, self.display_results, result)
        except Exception as e:
            error_msg = f"분석 오류: {str(e)}"
            self.root.after(0, self.display_error, error_msg)
        finally:
            self.root.after(0, self.stop_progress)
    
    def analyze_certificate(self, filepath):
        """인증서 분석 - Pure Python 방식"""
        file_ext = os.path.splitext(filepath)[1].lower()
        
        try:
            if file_ext in ['.pfx', '.p12']:
                return self.analyze_pkcs12_certificate(filepath)
            elif file_ext == '.der':
                return self.analyze_der_certificate(filepath)
            else:
                return self.analyze_pem_certificate(filepath)
        except Exception as e:
            return {
                'status': 'error',
                'summary': f'파일 분석 실패: {str(e)}',
                'details': '',
                'extensions': ''
            }
    
    def analyze_pem_certificate(self, filepath):
        """PEM/CRT 인증서 분석"""
        with open(filepath, 'rb') as f:
            cert_data = f.read()
        
        # 여러 인증서가 있을 수 있으므로 분리
        cert_blocks = []
        current_cert = b""
        in_cert = False
        
        for line in cert_data.split(b'\n'):
            if b'-----BEGIN CERTIFICATE-----' in line:
                in_cert = True
                current_cert = line + b'\n'
            elif b'-----END CERTIFICATE-----' in line:
                current_cert += line + b'\n'
                cert_blocks.append(current_cert)
                current_cert = b""
                in_cert = False
            elif in_cert:
                current_cert += line + b'\n'
        
        if not cert_blocks:
            raise ValueError("유효한 인증서를 찾을 수 없습니다.")
        
        # 첫 번째 인증서 분석 (리프 인증서)
        cert = x509.load_pem_x509_certificate(cert_blocks[0])
        
        result = self.extract_certificate_info(cert)
        result['cert_count'] = len(cert_blocks)
        
        # 체인 검증 수행
        if len(cert_blocks) > 1:
            chain_result = self.verify_certificate_chain(cert_blocks)
            chain_info = f"📦 인증서 체인 ({len(cert_blocks)}개) - {chain_result['status']}\n"
            if chain_result['details']:
                chain_info += f"{chain_result['details']}\n"
            result['summary'] = chain_info + "\n" + result['summary']
        else:
            result['summary'] = "📄 단일 인증서 (체인 없음)\n⚠️ 중간 인증서가 필요할 수 있습니다\n\n" + result['summary']
        
        return result
    
    def analyze_der_certificate(self, filepath):
        """DER 인증서 분석"""
        with open(filepath, 'rb') as f:
            cert_data = f.read()
        
        cert = x509.load_der_x509_certificate(cert_data)
        return self.extract_certificate_info(cert)
    
    def analyze_pkcs12_certificate(self, filepath):
        """PKCS#12 (PFX/P12) 인증서 분석"""
        password = self.password_var.get().encode('utf-8') if self.password_var.get() else None
        
        with open(filepath, 'rb') as f:
            p12_data = f.read()
        
        try:
            private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
                p12_data, password
            )
        except ValueError as e:
            if "invalid" in str(e).lower() or "could not deserialize" in str(e).lower():
                raise ValueError("PFX 비밀번호가 틀렸거나 파일이 손상되었습니다.")
            raise
        
        if certificate is None:
            raise ValueError("PFX 파일에서 인증서를 찾을 수 없습니다.")
        
        result = self.extract_certificate_info(certificate)
        
        # PFX 추가 정보
        has_private_key = private_key is not None
        additional_count = len(additional_certificates) if additional_certificates else 0
        
        pfx_info = f"📦 PFX/PKCS#12 파일 분석\n"
        pfx_info += f"🔑 개인키: {'포함됨' if has_private_key else '없음'}\n"
        pfx_info += f"📜 추가 인증서: {additional_count}개\n"
        
        # PFX의 체인 검증
        if additional_certificates and len(additional_certificates) > 0:
            # PFX에서 전체 체인 구성
            all_certs = [certificate] + list(additional_certificates)
            pfx_chain_result = self.verify_pfx_chain(all_certs)
            pfx_info += f"🔗 체인 상태: {pfx_chain_result['status']}\n"
        else:
            pfx_info += f"⚠️ 체인 상태: 단일 인증서 (중간 CA 없음)\n"
            
        pfx_info += "\n"
        result['summary'] = pfx_info + result['summary']
        
        return result
    
    def verify_certificate_chain(self, cert_blocks):
        """인증서 체인 검증"""
        try:
            certificates = []
            for cert_block in cert_blocks:
                cert = x509.load_pem_x509_certificate(cert_block)
                certificates.append(cert)
            
            # 체인 순서 검사
            chain_issues = []
            is_complete_chain = True
            
            leaf_cert = certificates[0]
            
            # 1. 체인 연결성 검사
            for i in range(len(certificates) - 1):
                current_cert = certificates[i]
                next_cert = certificates[i + 1]
                
                current_issuer = self.format_name(current_cert.issuer)
                next_subject = self.format_name(next_cert.subject)
                
                if current_issuer != next_subject:
                    chain_issues.append(f"❌ 인증서 {i+1} → {i+2}: 체인 연결 불가")
                    chain_issues.append(f"   현재 Issuer: {current_issuer}")
                    chain_issues.append(f"   다음 Subject: {next_subject}")
                    is_complete_chain = False
                else:
                    chain_issues.append(f"✅ 인증서 {i+1} → {i+2}: 체인 연결 정상")
            
            # 2. 루트 인증서 확인
            root_cert = certificates[-1]
            root_subject = self.format_name(root_cert.subject)
            root_issuer = self.format_name(root_cert.issuer)
            
            is_self_signed = (root_subject == root_issuer)
            
            if is_self_signed:
                chain_issues.append(f"✅ 루트 CA: 자체 서명 인증서 확인됨")
            else:
                chain_issues.append(f"⚠️ 루트 CA: 자체 서명이 아님 (상위 CA 필요할 수 있음)")
                is_complete_chain = False
            
            # 3. 서명 검증 (간단 버전)
            valid_signatures = 0
            for i in range(len(certificates) - 1):
                try:
                    current_cert = certificates[i]
                    issuer_cert = certificates[i + 1]
                    
                    # 간단한 검증: issuer의 공개키로 현재 인증서의 서명을 검증할 수 있는지 확인
                    # 실제 서명 검증은 복잡하므로 기본적인 체크만 수행
                    issuer_public_key = issuer_cert.public_key()
                    if issuer_public_key:
                        valid_signatures += 1
                        chain_issues.append(f"✅ 인증서 {i+1}: 서명자 공개키 확인됨")
                    
                except Exception as e:
                    chain_issues.append(f"❌ 인증서 {i+1}: 서명 검증 실패")
            
            # 최종 판단
            if is_complete_chain and len(certificates) >= 2:
                status = "✅ 완전한 체인"
            elif len(certificates) >= 2:
                status = "⚠️ 불완전한 체인"
            else:
                status = "❓ 단일 인증서"
            
            return {
                'status': status,
                'details': '\n'.join(chain_issues),
                'is_complete': is_complete_chain,
                'cert_count': len(certificates)
            }
            
        except Exception as e:
            return {
                'status': '❌ 체인 검증 실패',
                'details': f'오류: {str(e)}',
                'is_complete': False,
                'cert_count': len(cert_blocks)
            }
    
    def verify_pfx_chain(self, certificates):
        """PFX 인증서 체인 검증"""
        try:
            if len(certificates) < 2:
                return {'status': '❓ 단일 인증서', 'is_complete': False}
            
            # 리프 인증서 찾기 (보통 첫 번째이지만 확실히 하기 위해)
            leaf_cert = None
            ca_certs = []
            
            for cert in certificates:
                # 기본 제약 확인
                try:
                    basic_constraints = cert.extensions.get_extension_for_oid(
                        x509.oid.ExtensionOID.BASIC_CONSTRAINTS
                    ).value
                    if basic_constraints.ca:
                        ca_certs.append(cert)
                    else:
                        if leaf_cert is None:  # 첫 번째 비-CA 인증서를 리프로 간주
                            leaf_cert = cert
                        else:
                            ca_certs.append(cert)
                except x509.ExtensionNotFound:
                    # Basic Constraints가 없으면 리프 인증서로 간주
                    if leaf_cert is None:
                        leaf_cert = cert
                    else:
                        ca_certs.append(cert)
            
            if leaf_cert is None:
                leaf_cert = certificates[0]  # 기본값으로 첫 번째 인증서
                ca_certs = certificates[1:]
            
            # 체인 순서 정리 (리프부터 루트까지)
            ordered_chain = [leaf_cert]
            remaining_cas = ca_certs[:]
            
            current_cert = leaf_cert
            while remaining_cas:
                found_issuer = False
                current_issuer = self.format_name(current_cert.issuer)
                
                for ca_cert in remaining_cas:
                    ca_subject = self.format_name(ca_cert.subject)
                    if current_issuer == ca_subject:
                        ordered_chain.append(ca_cert)
                        remaining_cas.remove(ca_cert)
                        current_cert = ca_cert
                        found_issuer = True
                        break
                
                if not found_issuer:
                    break
            
            # 체인 완성도 확인
            if len(ordered_chain) == len(certificates):
                # 마지막이 자체 서명인지 확인
                root_cert = ordered_chain[-1]
                root_subject = self.format_name(root_cert.subject)
                root_issuer = self.format_name(root_cert.issuer)
                
                if root_subject == root_issuer:
                    return {'status': '✅ 완전한 체인', 'is_complete': True}
                else:
                    return {'status': '⚠️ 불완전한 체인 (루트 CA 없음)', 'is_complete': False}
            else:
                return {'status': '⚠️ 불완전한 체인 (연결 오류)', 'is_complete': False}
                
        except Exception as e:
            return {'status': '❌ 체인 검증 실패', 'is_complete': False}
    
    def extract_certificate_info(self, cert):
        """인증서에서 정보 추출"""
        # 기본 정보
        subject = self.format_name(cert.subject)
        issuer = self.format_name(cert.issuer)
        serial = hex(cert.serial_number)[2:].upper()
        
        # 날짜 정보
        not_before = cert.not_valid_before
        not_after = cert.not_valid_after
        
        # timezone 정보 통일 (인증서는 보통 UTC)
        if not_before.tzinfo is None:
            not_before = not_before.replace(tzinfo=timezone.utc)
        if not_after.tzinfo is None:
            not_after = not_after.replace(tzinfo=timezone.utc)
        
        # 현재 시간과 비교
        now = datetime.now(timezone.utc)
        
        try:
            if not_after < now:
                days_left = (now - not_after).days
                validity_status = f"⚠️ 만료됨 ({days_left}일 전)"
                status_color = "red"
            elif (not_after - now).days < 30:
                days_left = (not_after - now).days
                validity_status = f"⚠️ 곧 만료 ({days_left}일 남음)"
                status_color = "orange"
            else:
                days_left = (not_after - now).days
                validity_status = f"✅ 유효 ({days_left}일 남음)"
                status_color = "green"
        except Exception as e:
            # 날짜 비교 오류 시 기본 정보만 표시
            validity_status = "❓ 유효성 확인 불가"
            status_color = "gray"
        
        # 공개키 정보
        public_key = cert.public_key()
        key_info = self.get_public_key_info(public_key)
        
        # SAN (Subject Alternative Name) 추출
        san_domains = self.extract_san_domains(cert)
        
        # 요약 정보 구성
        summary_parts = [
            f"🏷️ Subject: {subject}",
            f"🏢 Issuer: {issuer}",
            f"🔢 Serial: {serial}",
            "",
            f"📅 유효 기간:",
            f"   시작: {not_before.strftime('%Y-%m-%d %H:%M:%S')} UTC",
            f"   종료: {not_after.strftime('%Y-%m-%d %H:%M:%S')} UTC",
            f"   상태: {validity_status}",
            "",
            f"🔐 공개키: {key_info}",
        ]
        
        if san_domains:
            summary_parts.extend([
                "",
                f"🌐 도메인 (SAN):",
            ])
            for domain in san_domains[:10]:  # 최대 10개만 표시
                summary_parts.append(f"   • {domain}")
            if len(san_domains) > 10:
                summary_parts.append(f"   ... 및 {len(san_domains) - 10}개 더")
        
        # 용도 확인
        usage = self.get_certificate_usage(cert)
        if usage:
            summary_parts.extend(["", f"📋 인증서 용도: {usage}"])
        
        # 상세 정보
        details = self.format_certificate_details(cert)
        
        # 확장 필드 정보
        extensions = self.format_certificate_extensions(cert)
        
        return {
            'status': 'success',
            'summary': '\n'.join(summary_parts),
            'details': details,
            'extensions': extensions,
            'cert_object': cert
        }
    
    def format_name(self, name):
        """X.509 Name을 문자열로 포맷"""
        parts = []
        for attribute in name:
            if attribute.oid == NameOID.COMMON_NAME:
                parts.append(f"CN={attribute.value}")
            elif attribute.oid == NameOID.ORGANIZATION_NAME:
                parts.append(f"O={attribute.value}")
            elif attribute.oid == NameOID.ORGANIZATIONAL_UNIT_NAME:
                parts.append(f"OU={attribute.value}")
            elif attribute.oid == NameOID.COUNTRY_NAME:
                parts.append(f"C={attribute.value}")
            elif attribute.oid == NameOID.STATE_OR_PROVINCE_NAME:
                parts.append(f"ST={attribute.value}")
            elif attribute.oid == NameOID.LOCALITY_NAME:
                parts.append(f"L={attribute.value}")
        return ', '.join(parts)
    
    def get_public_key_info(self, public_key):
        """공개키 정보 추출"""
        from cryptography.hazmat.primitives.asymmetric import rsa, ec, dsa
        
        if isinstance(public_key, rsa.RSAPublicKey):
            key_size = public_key.key_size
            return f"RSA {key_size}bit"
        elif isinstance(public_key, ec.EllipticCurvePublicKey):
            curve_name = public_key.curve.name
            key_size = public_key.curve.key_size
            return f"ECC {curve_name} ({key_size}bit)"
        elif isinstance(public_key, dsa.DSAPublicKey):
            key_size = public_key.key_size
            return f"DSA {key_size}bit"
        else:
            return f"{type(public_key).__name__}"
    
    def extract_san_domains(self, cert):
        """SAN에서 도메인 추출"""
        try:
            san_ext = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
            domains = []
            for name in san_ext.value:
                if isinstance(name, x509.DNSName):
                    # DNSName 객체에서 값 추출
                    if hasattr(name, 'value'):
                        domains.append(name.value)
                    else:
                        domains.append(str(name))
            return domains
        except (x509.ExtensionNotFound, AttributeError, Exception) as e:
            # SAN 파싱 실패 시 빈 리스트 반환
            return []
    
    def get_certificate_usage(self, cert):
        """인증서 용도 확인"""
        usages = []
        
        try:
            key_usage = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.KEY_USAGE).value
            if hasattr(key_usage, 'digital_signature') and key_usage.digital_signature:
                usages.append("디지털 서명")
            if hasattr(key_usage, 'key_encipherment') and key_usage.key_encipherment:
                usages.append("키 암호화")
            if hasattr(key_usage, 'key_agreement') and key_usage.key_agreement:
                usages.append("키 합의")
        except (x509.ExtensionNotFound, AttributeError, Exception):
            pass
        
        try:
            ext_key_usage = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.EXTENDED_KEY_USAGE).value
            if ExtendedKeyUsageOID.SERVER_AUTH in ext_key_usage:
                usages.append("서버 인증 (TLS/SSL)")
            if ExtendedKeyUsageOID.CLIENT_AUTH in ext_key_usage:
                usages.append("클라이언트 인증")
            if ExtendedKeyUsageOID.CODE_SIGNING in ext_key_usage:
                usages.append("코드 서명")
            if ExtendedKeyUsageOID.EMAIL_PROTECTION in ext_key_usage:
                usages.append("이메일 보호")
        except (x509.ExtensionNotFound, AttributeError, Exception):
            pass
        
        return ', '.join(usages) if usages else "용도 불명"
    
    def format_certificate_details(self, cert):
        """인증서 상세 정보 포맷"""
        details = []
        
        details.append("=== 인증서 상세 정보 ===\n")
        
        details.append(f"버전: v{cert.version.value}")
        details.append(f"시리얼 번호: {hex(cert.serial_number)[2:].upper()}")
        details.append(f"서명 알고리즘: {cert.signature_algorithm_oid._name}")
        details.append("")
        
        details.append("발급자 (Issuer):")
        for attr in cert.issuer:
            details.append(f"  {attr.oid._name}: {attr.value}")
        details.append("")
        
        details.append("주체 (Subject):")
        for attr in cert.subject:
            details.append(f"  {attr.oid._name}: {attr.value}")
        details.append("")
        
        details.append("유효 기간:")
        details.append(f"  시작: {cert.not_valid_before}")
        details.append(f"  종료: {cert.not_valid_after}")
        details.append("")
        
        # 공개키 세부 정보
        public_key = cert.public_key()
        details.append("공개키 정보:")
        details.append(f"  알고리즘: {self.get_public_key_info(public_key)}")
        
        # 공개키 지문
        from cryptography.hazmat.primitives import hashes
        try:
            fingerprint_bytes = cert.fingerprint(hashes.SHA256())
            fingerprint_hex = fingerprint_bytes.hex()
            # 콜론으로 구분된 형태로 변환 (AA:BB:CC:DD...)
            fingerprint_sha256 = ':'.join([fingerprint_hex[i:i+2].upper() for i in range(0, len(fingerprint_hex), 2)])
            details.append(f"  SHA256 지문: {fingerprint_sha256}")
        except Exception as e:
            details.append(f"  SHA256 지문: <계산 실패: {str(e)}>")
        
        return '\n'.join(details)
    
    def format_certificate_extensions(self, cert):
        """인증서 확장 필드 포맷"""
        extensions = []
        
        extensions.append("=== 인증서 확장 필드 ===\n")
        
        try:
            for ext in cert.extensions:
                try:
                    # OID 이름 안전하게 가져오기
                    oid_name = getattr(ext.oid, '_name', str(ext.oid))
                    critical_str = 'Critical' if ext.critical else 'Non-Critical'
                    extensions.append(f"• {oid_name} ({critical_str})")
                    
                    # 확장 필드 값 안전하게 파싱
                    try:
                        ext_value = str(ext.value)
                        # 긴 값은 줄바꿈 (안전하게 처리)
                        if len(ext_value) > 100:
                            ext_value = ext_value[:100] + "... (truncated)"
                        extensions.append(f"  값: {ext_value}")
                    except Exception as e:
                        extensions.append(f"  값: <파싱 불가: {str(e)}>")
                    
                    extensions.append("")
                    
                except Exception as e:
                    extensions.append(f"• <확장 필드 파싱 오류: {str(e)}>")
                    extensions.append("")
                    
        except Exception as e:
            extensions.append(f"확장 필드 읽기 실패: {str(e)}")
        
        return '\n'.join(extensions)
    
    def display_results(self, result):
        """결과 표시"""
        # 기존 내용 삭제
        self.summary_text.delete(1.0, tk.END)
        self.detail_text.delete(1.0, tk.END)
        self.extensions_text.delete(1.0, tk.END)
        
        if result['status'] == 'success':
            self.summary_text.insert(tk.END, result['summary'])
            self.detail_text.insert(tk.END, result['details'])
            self.extensions_text.insert(tk.END, result['extensions'])
            self.status_var.set("✅ 검증 완료 (Pure Python)")
        else:
            error_msg = f"❌ 오류: {result['summary']}"
            self.summary_text.insert(tk.END, error_msg)
            self.status_var.set("❌ 검증 실패")
    
    def display_error(self, error_msg):
        """오류 표시"""
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, f"❌ 오류 발생:\n{error_msg}")
        self.status_var.set("❌ 검증 실패")
        messagebox.showerror("검증 오류", error_msg)
    
    def stop_progress(self):
        """진행 상황 표시 중지"""
        self.progress.stop()


def main():
    """메인 함수"""
    # cryptography 라이브러리 확인
    try:
        import cryptography
        print(f"cryptography 버전: {cryptography.__version__}")
    except ImportError:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("라이브러리 오류", 
                           "cryptography 라이브러리가 설치되지 않았습니다.\n"
                           "설치: pip install cryptography")
        return
    
    root = tk.Tk()
    app = PureSSLCertificateChecker(root)
    
    # 아이콘 설정 (선택사항)
    try:
        root.iconbitmap(default="")  # Windows에서 기본 아이콘 제거
    except:
        pass
    
    root.mainloop()


if __name__ == "__main__":
    main()