#!/usr/bin/env python3
"""
SSL Certificate Checker v3.0 - Enhanced UI Version
직관적인 체인 상태 표시와 트리 구조 시각화를 제공하는 SSL 인증서 검증 도구

Requirements:
pip install cryptography
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from datetime import datetime, timezone
import tempfile

# tkinterdnd2 라이브러리 임포트 시도
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAS_TKINTERDND2 = True
except ImportError:
    print("tkinterdnd2를 설치하면 드래그 앤 드롭 기능을 사용할 수 있습니다: pip install tkinterdnd2")
    HAS_TKINTERDND2 = False
    DND_FILES = None

try:
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.serialization import pkcs12
    from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
    # PolicyBuilder, StoreBuilder는 선택적으로 import
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


class EnhancedSSLCertificateChecker:
    def __init__(self, root):
        self.root = root
        self.has_drag_drop = HAS_TKINTERDND2
        self.root.title("SSL Certificate Checker v3.0 - Enhanced UI")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)

        # ===== FIX 1: status_var를 가장 먼저 생성 (초기화 순서 문제 해결) =====
        self.status_var = tk.StringVar(value="준비됨 - SSL Certificate Checker v3.0")

        # 테마 모드 (기본: 라이트)
        self.dark_mode = False
        
        # 색상 테마 정의
        self.colors = self.get_color_theme()
        
        # 현재 분석 결과 저장
        self.current_result = None
        self.analysis_results = []  # 다중 파일 분석 결과
        
        # 스타일 설정
        self.setup_styles()
        self.setup_ui()
        
    def get_color_theme(self):
        """현재 테마에 따른 색상 반환 - 개선된 디자인"""
        if self.dark_mode:
            return {
                # 다크 테마 - 모던하고 세련된 디자인
                'success': '#4CAF50',      # Material Green
                'warning': '#FF9800',      # Material Orange  
                'danger': '#F44336',       # Material Red
                'info': '#2196F3',         # Material Blue
                'bg': '#1e1e1e',           # VS Code 다크 배경
                'fg': '#d4d4d4',           # VS Code 텍스트
                'bg_light': '#2d2d30',     # 약간 밝은 배경
                'bg_dark': '#0d1117',      # GitHub 다크 배경
                'fg_light': '#8c8c8c',     # 보조 텍스트
                'fg_muted': '#6e7681',     # 더 연한 텍스트
                'entry_bg': '#3c3c3c',     # 입력 필드 배경
                'entry_fg': '#ffffff',     # 입력 필드 텍스트
                'entry_border': '#404040', # 입력 필드 테두리
                'select_bg': '#264f78',    # VS Code 선택 배경
                'select_fg': '#ffffff',    # 선택된 텍스트
                'tree_bg': '#252526',      # 트리 배경
                'tree_fg': '#cccccc',      # 트리 텍스트
                'button_bg': '#0e639c',    # 버튼 배경
                'button_hover': '#1177bb', # 버튼 호버
                'border': '#3e3e42',       # 테두리 색상
                'accent': '#007acc',       # 액센트 색상
                'panel_bg': '#252526',     # 패널 배경
                'tab_active': '#1e1e1e',   # 활성 탭
                'tab_inactive': '#2d2d30'  # 비활성 탭
            }
        else:
            return {
                # 라이트 테마 - 깔끔하고 모던한 디자인
                'success': '#22c55e',      # Tailwind Green
                'warning': '#f59e0b',      # Tailwind Amber
                'danger': '#ef4444',       # Tailwind Red
                'info': '#3b82f6',         # Tailwind Blue
                'bg': '#ffffff',           # 순수 흰색
                'fg': '#1f2937',           # 진한 회색
                'bg_light': '#f8fafc',     # 아주 연한 회색
                'bg_dark': '#f1f5f9',      # 조금 더 진한 배경
                'fg_light': '#6b7280',     # 회색 텍스트
                'fg_muted': '#9ca3af',     # 연한 회색 텍스트
                'entry_bg': '#ffffff',     # 입력 필드 배경
                'entry_fg': '#1f2937',     # 입력 필드 텍스트
                'entry_border': '#d1d5db', # 입력 필드 테두리
                'select_bg': '#dbeafe',    # 선택 배경
                'select_fg': '#1e40af',    # 선택된 텍스트
                'tree_bg': '#ffffff',      # 트리 배경
                'tree_fg': '#1f2937',      # 트리 텍스트
                'button_bg': '#3b82f6',    # 버튼 배경
                'button_hover': '#2563eb', # 버튼 호버
                'border': '#e5e7eb',       # 테두리 색상
                'accent': '#3b82f6',       # 액센트 색상
                'panel_bg': '#f9fafb',     # 패널 배경
                'tab_active': '#ffffff',   # 활성 탭
                'tab_inactive': '#f3f4f6'  # 비활성 탭
            }
    
    def setup_styles(self):
        """스타일 테마 설정"""
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        
        # 메인 윈도우 배경 설정
        self.root.configure(bg=self.colors['bg'])
        
        # 상태별 스타일 정의
        style.configure('Success.TLabel', foreground=self.colors['success'], font=('Arial', 12, 'bold'), background=self.colors['bg'])
        style.configure('Warning.TLabel', foreground=self.colors['warning'], font=('Arial', 12, 'bold'), background=self.colors['bg'])
        style.configure('Danger.TLabel', foreground=self.colors['danger'], font=('Arial', 12, 'bold'), background=self.colors['bg'])
        style.configure('Info.TLabel', foreground=self.colors['info'], font=('Arial', 12, 'bold'), background=self.colors['bg'])
        
        # 기본 위젯 스타일
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TLabelFrame', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TLabelFrame.Label', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TButton', background=self.colors['bg_light'], foreground=self.colors['fg'])

        # 일부 Tk 빌드 호환 (옵션 미지원 시 무시)
        try:
            style.configure('TEntry', insertcolor=self.colors['fg'], fieldbackground=self.colors['entry_bg'], foreground=self.colors['entry_fg'])
        except Exception:
            pass

        style.configure('TCheckbutton', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TProgressbar', background=self.colors['info'])
        
        # 트리뷰 스타일
        style.configure('Treeview', background=self.colors['tree_bg'], foreground=self.colors['tree_fg'], 
                       fieldbackground=self.colors['tree_bg'], selectbackground=self.colors['select_bg'], 
                       selectforeground=self.colors['select_fg'])
        style.configure('Treeview.Heading', background=self.colors['bg_light'], foreground=self.colors['fg'])
        
        # 노트북 스타일 
        style.configure('TNotebook', background=self.colors['bg'])
        style.configure('TNotebook.Tab', background=self.colors['bg_light'], foreground=self.colors['fg'],
                       padding=[20, 10])
        
        # 팬드윈도우 스타일
        style.configure('TPanedwindow', background=self.colors['bg'])
        
    def setup_ui(self):
        """UI 구성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목과 테마 전환 버튼을 담을 프레임
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 5), sticky=(tk.W, tk.E))
        
        # 제목
        title_label = ttk.Label(title_frame, text="🔐 SSL Certificate Checker v3.0", 
                               font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # 테마 전환 버튼
        theme_btn = ttk.Button(title_frame, text="🌙 다크모드", command=self.toggle_theme, width=12)
        theme_btn.grid(row=0, column=1, sticky=tk.E, padx=(20, 0))
        
        title_frame.columnconfigure(0, weight=1)
        
        subtitle_label = ttk.Label(main_frame, text="Enhanced UI • Chain Visualization • Dark Theme Support", 
                                  font=('Arial', 10), foreground=self.colors['fg_light'])
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # 파일 선택 섹션
        self.setup_file_selection(main_frame, row=2)
        
        # 상태 표시 패널 (가장 중요한 정보)
        self.setup_status_panel(main_frame, row=3)
        
        # 메인 콘텐츠 영역
        self.setup_main_content(main_frame, row=4)
        
        # 하단 상태바 (self.status_var는 이미 __init__에서 생성됨)
        self.setup_status_bar(main_frame, row=5)
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
    
    def setup_file_selection(self, parent, row):
        """파일 선택 섹션"""
        file_frame = ttk.LabelFrame(parent, text="📁 인증서 파일 선택", padding="10")
        file_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=60, font=('Consolas', 10))
        file_entry.grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E))
        
        browse_btn = ttk.Button(file_frame, text="파일 선택", command=self.browse_file)
        browse_btn.grid(row=0, column=1, padx=(0, 5))
        
        # 다중 파일 선택 버튼
        multi_btn = ttk.Button(file_frame, text="다중 파일", command=self.browse_multiple_files, width=10)
        multi_btn.grid(row=0, column=2, padx=(0, 10))
        
        # 드래그 앤 드롭 라벨 (개선된 메시지)
        drop_label = ttk.Label(file_frame, text="💡 탐색기에서 인증서 파일을 드래그하거나 Ctrl+V로 붙여넣기 가능", 
                              font=('Arial', 9), foreground=self.colors['fg_light'])
        drop_label.grid(row=3, column=0, columnspan=3, pady=(5, 0), sticky=tk.W)
        
        # 드래그 앤 드롭 설정
        self.setup_drag_drop(file_frame)
        
        # 비밀번호 입력 (같은 프레임 내)
        ttk.Label(file_frame, text="PFX 비밀번호:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        pwd_frame = ttk.Frame(file_frame)
        pwd_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.password_var = tk.StringVar()
        pwd_entry = ttk.Entry(pwd_frame, textvariable=self.password_var, show="*", width=30)
        pwd_entry.grid(row=0, column=0, padx=(0, 10))
        
        self.show_pwd_var = tk.BooleanVar()
        show_pwd_check = ttk.Checkbutton(pwd_frame, text="표시", variable=self.show_pwd_var,
                                        command=lambda: pwd_entry.config(show="" if self.show_pwd_var.get() else "*"))
        show_pwd_check.grid(row=0, column=1, padx=(0, 10))
        
        # 검증 버튼
        verify_btn = ttk.Button(pwd_frame, text="🔍 인증서 검증", command=self.verify_certificate)
        verify_btn.grid(row=0, column=2, padx=(20, 0))
        
        file_frame.columnconfigure(0, weight=1)
    
    def setup_status_panel(self, parent, row):
        """상태 표시 패널 (최상단, 가장 중요)"""
        self.status_frame = ttk.Frame(parent)
        self.status_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 기본 상태
        self.show_ready_status()
    
    def show_ready_status(self):
        """준비 상태 표시"""
        for widget in self.status_frame.winfo_children():
            widget.destroy()
            
        ready_label = ttk.Label(self.status_frame, text="📋 인증서 파일을 선택하고 검증 버튼을 눌러주세요", 
                               font=('Arial', 14))
        ready_label.pack(pady=20)
    
    def show_chain_status(self, result):
        """체인 상태를 시각적으로 표시"""
        for widget in self.status_frame.winfo_children():
            widget.destroy()
        
        # 상태에 따른 색상과 아이콘 결정
        chain_info = result.get('chain_info', {})
        status = chain_info.get('status', 'unknown')
        
        if '완전한 체인' in status:
            if self.dark_mode:
                bg_color = '#1e3a1e'
                fg_color = '#75d975'
            else:
                bg_color = '#d4edda'
                fg_color = '#155724'
            icon = '✅'
            status_text = '완전한 인증서 체인'
        elif '불완전한 체인' in status or '단일 인증서' in status:
            if self.dark_mode:
                bg_color = '#3a2e1e'
                fg_color = '#ffcc66'
            else:
                bg_color = '#fff3cd'
                fg_color = '#856404'
            icon = '⚠️'
            status_text = '불완전한 인증서 체인'
        else:
            if self.dark_mode:
                bg_color = '#3a1e1e'
                fg_color = '#ff6666'
            else:
                bg_color = '#f8d7da'
                fg_color = '#721c24'
            icon = '❌'
            status_text = '체인 검증 실패'
        
        # 상태 패널 프레임
        status_panel = tk.Frame(self.status_frame, bg=bg_color, relief='solid', bd=2)
        status_panel.pack(fill='x', pady=(0, 10))
        
        # 아이콘과 상태 텍스트
        status_label = tk.Label(status_panel, text=f"{icon} {status_text}", 
                               bg=bg_color, fg=fg_color, font=('Arial', 16, 'bold'))
        status_label.pack(pady=15)
        
        # 추가 정보
        details = []
        if result.get('file_type') == '.pfx':
            details.append(f"📦 PFX 파일")
            if result.get('has_private_key'):
                details.append("🔑 개인키 포함")
        elif result.get('cert_count', 1) > 1:
            details.append(f"📜 인증서 {result.get('cert_count')}개")
        else:
            details.append("📄 단일 인증서")
            
        if details:
            detail_label = tk.Label(status_panel, text=" • ".join(details),
                                   bg=bg_color, fg=fg_color, font=('Arial', 12))
            detail_label.pack(pady=(0, 10))
    
    def setup_main_content(self, parent, row):
        """메인 콘텐츠 영역 (트리뷰 + 상세정보)"""
        # 수평 팬드 윈도우
        paned = ttk.PanedWindow(parent, orient='horizontal')
        paned.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 왼쪽: 트리 뷰
        self.setup_tree_view(paned)
        
        # 오른쪽: 상세 정보
        self.setup_detail_view(paned)
    
    def setup_tree_view(self, parent):
        """트리 뷰 설정"""
        tree_frame = ttk.LabelFrame(parent, text="🌳 인증서 체인 구조", padding="10")
        parent.add(tree_frame, weight=1)
        
        # 트리뷰 위젯
        self.tree = ttk.Treeview(tree_frame, height=20)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 스크롤바
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        # 컬럼 설정
        self.tree['columns'] = ('type', 'validity', 'key_info')
        self.tree.column('#0', width=300, minwidth=200)
        self.tree.column('type', width=100, minwidth=80)
        self.tree.column('validity', width=150, minwidth=120)
        self.tree.column('key_info', width=120, minwidth=100)
        
        # 헤더 설정
        self.tree.heading('#0', text='인증서 정보', anchor='w')
        self.tree.heading('type', text='타입', anchor='center')
        self.tree.heading('validity', text='유효성', anchor='center')
        self.tree.heading('key_info', text='키 정보', anchor='center')
        
        # 이벤트 바인딩
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # 기본 메시지
        self.tree.insert('', 'end', text='인증서를 선택하고 검증해주세요', values=('', '', ''))
    
    def setup_detail_view(self, parent):
        """상세 정보 뷰 설정"""
        detail_frame = ttk.LabelFrame(parent, text="📋 상세 정보", padding="10")
        parent.add(detail_frame, weight=1)
        
        # ===== FIX 2: Notebook 탭 위치는 옵션으로 지정(스타일이 아닌 위젯에서) =====
        self.notebook = ttk.Notebook(detail_frame)  # tabposition은 플랫폼에 따라 무시됨
        try:
            self.notebook = ttk.Notebook(detail_frame, tabposition='n')
        except Exception:
            self.notebook = ttk.Notebook(detail_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 기본 정보 탭
        self.info_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.info_frame, text="ℹ️ 기본 정보")
        
        self.info_text = tk.Text(self.info_frame, wrap='word', font=('Consolas', 10), 
                                height=20, state='disabled', bg=self.colors['tree_bg'], 
                                fg=self.colors['tree_fg'], insertbackground=self.colors['tree_fg'])
        info_scroll = ttk.Scrollbar(self.info_frame, orient="vertical", command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scroll.set)
        
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        info_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 확장 필드 탭
        self.ext_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ext_frame, text="🔧 확장 필드")
        
        self.ext_text = tk.Text(self.ext_frame, wrap='word', font=('Consolas', 9),
                               height=20, state='disabled', bg=self.colors['tree_bg'], 
                               fg=self.colors['tree_fg'], insertbackground=self.colors['tree_fg'])
        ext_scroll = ttk.Scrollbar(self.ext_frame, orient="vertical", command=self.ext_text.yview)
        self.ext_text.configure(yscrollcommand=ext_scroll.set)
        
        self.ext_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        ext_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 그리드 가중치 설정
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(0, weight=1)
        self.info_frame.columnconfigure(0, weight=1)
        self.info_frame.rowconfigure(0, weight=1)
        self.ext_frame.columnconfigure(0, weight=1)
        self.ext_frame.rowconfigure(0, weight=1)
    
    def setup_status_bar(self, parent, row):
        """하단 상태바"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 진행바
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # ===== FIX 3: self.status_var는 이미 존재 → 재사용 =====
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=('Arial', 9))
        status_label.grid(row=1, column=0, sticky=tk.W)
        
        # 버전 정보
        version_label = ttk.Label(status_frame, text="Enhanced UI • Pure Python", 
                                 font=('Arial', 9), foreground='gray')
        version_label.grid(row=1, column=2, sticky=tk.E)
        
        status_frame.columnconfigure(1, weight=1)
    
    def toggle_theme(self):
        """다크/라이트 테마 전환"""
        self.dark_mode = not self.dark_mode
        self.colors = self.get_color_theme()
        
        # 스타일 업데이트
        self.setup_styles()
        
        # Text 위젯 색상 업데이트 (방어)
        if hasattr(self, 'info_text'):
            try:
                self.info_text.configure(bg=self.colors['tree_bg'], fg=self.colors['tree_fg'], 
                                        insertbackground=self.colors['tree_fg'])
            except Exception:
                pass
        if hasattr(self, 'ext_text'):
            try:
                self.ext_text.configure(bg=self.colors['tree_bg'], fg=self.colors['tree_fg'], 
                                       insertbackground=self.colors['tree_fg'])
            except Exception:
                pass
        
        # 버튼 텍스트 업데이트 
        for child in self.root.winfo_children():
            self.update_theme_button_text(child)
            
        # 상태 패널이 있다면 다시 그리기
        if getattr(self, 'current_result', None):
            self.show_chain_status(self.current_result)
    
    def update_theme_button_text(self, widget):
        """테마 전환 버튼 텍스트 업데이트"""
        try:
            if isinstance(widget, ttk.Button):
                if widget.cget('text') in ['🌙 다크모드', '☀️ 라이트모드']:
                    widget.configure(text='☀️ 라이트모드' if self.dark_mode else '🌙 다크모드')
            
            # 자식 위젯들도 재귀적으로 처리
            for child in widget.winfo_children():
                self.update_theme_button_text(child)
        except:
            pass
    
    def setup_drag_drop(self, widget):
        """실제 작동하는 드래그 앤 드롭 설정"""
        if self.has_drag_drop:
            # tkinterdnd2를 사용한 실제 드래그 앤 드롭
            try:
                self.root.drop_target_register(DND_FILES)
                self.root.dnd_bind('<<Drop>>', self.on_drop_files_real)
                self.root.dnd_bind('<<DragEnter>>', self.on_drag_enter_real)
                self.root.dnd_bind('<<DragLeave>>', self.on_drag_leave_real)
            except Exception:
                pass
            drag_status = "✅ 실제 드래그 앤 드롭 활성화됨"
        else:
            # 대체 방법: 클립보드 모니터링
            self.setup_clipboard_monitoring()
            drag_status = "⚠️ tkinterdnd2 설치 권장 (pip install tkinterdnd2)"
        
        # ===== FIX 4: 혹시라도 누락 시 가드 =====
        if not hasattr(self, "status_var") or not isinstance(self.status_var, tk.StringVar):
            self.status_var = tk.StringVar(value="")
        self.status_var.set(drag_status)
        
        # 설명 라벨 업데이트
        for child in widget.winfo_children():
            if isinstance(child, ttk.Label) and "드래그" in child.cget('text'):
                if self.has_drag_drop:
                    child.configure(text="✅ Windows 파일탐색기에서 드래그 앤 드롭 가능!")
                else:
                    child.configure(text="💡 Ctrl+V 붙여넣기 또는 tkinterdnd2 설치로 드래그 앤 드롭")
    
    def setup_clipboard_monitoring(self):
        """클립보드 모니터링 설정 (드래그 앤 드롭 대체)"""
        # Ctrl+V로 파일 경로 붙여넣기 지원
        self.root.bind('<Control-v>', self.on_paste)
        self.root.bind('<Control-V>', self.on_paste)
    
    def on_drag_enter_real(self, event):
        """실제 드래그 진입"""
        if hasattr(self, 'status_var'):
            self.status_var.set("📥 인증서 파일을 여기에 드롭하세요!")
        
    def on_drag_leave_real(self, event):
        """실제 드래그 나감"""
        if hasattr(self, 'status_var'):
            self.status_var.set("준비됨 - SSL Certificate Checker v3.0")
    
    def on_drop_files_real(self, event):
        """실제 파일 드롭 처리 (tkinterdnd2) - 개선된 버전"""
        try:
            print(f"드롭 이벤트 받음: {event}")
            print(f"이벤트 데이터: {event.data}")
            
            # 다양한 형식의 드롭 데이터 처리
            files = []
            
            if hasattr(event, 'data'):
                data = event.data
                
                # 방법 1: 공백으로 분리
                if isinstance(data, str):
                    potential_files = data.split()
                    for file_path in potential_files:
                        clean_path = file_path.strip('{}').strip('"').strip("'")
                        if os.path.exists(clean_path) and os.path.isfile(clean_path):
                            files.append(clean_path)
                
                # 방법 2: tkinter splitlist 사용
                if not files:
                    try:
                        tk_files = self.root.tk.splitlist(data)
                        for file_path in tk_files:
                            clean_path = str(file_path).strip('{}').strip('"').strip("'")
                            if os.path.exists(clean_path) and os.path.isfile(clean_path):
                                files.append(clean_path)
                    except:
                        pass
                
                # 방법 3: 줄바꿈으로 분리 (일부 경우)
                if not files and '\n' in data:
                    for line in data.split('\n'):
                        clean_path = line.strip().strip('{}').strip('"').strip("'")
                        if os.path.exists(clean_path) and os.path.isfile(clean_path):
                            files.append(clean_path)
            
            print(f"파싱된 파일들: {files}")
            
            if not files:
                if hasattr(self, 'status_var'):
                    self.status_var.set("❌ 드롭된 파일을 찾을 수 없습니다")
                print("드롭된 파일 없음")
                return
            
            # 인증서 파일만 필터링
            cert_files = [f for f in files if self.is_certificate_file(f)]
            print(f"인증서 파일들: {cert_files}")
            
            if not cert_files:
                messagebox.showwarning("드롭 실패", 
                    f"인증서 파일이 없습니다.\n"
                    f"지원 형식: .pem, .crt, .cer, .pfx, .p12, .der\n"
                    f"드롭된 파일: {len(files)}개")
                if hasattr(self, 'status_var'):
                    self.status_var.set("❌ 인증서 파일 없음")
                return
            
            # 성공적으로 드롭된 경우
            self.process_dropped_files(cert_files)
            print("드롭 성공!")
            
        except Exception as e:
            print(f"드롭 처리 오류: {e}")
            messagebox.showerror("드롭 오류", f"파일 드롭 처리 중 오류:\n{str(e)}")
            if hasattr(self, 'status_var'):
                self.status_var.set("❌ 드롭 실패")
    
    def on_paste(self, event):
        """Ctrl+V 붙여넣기 이벤트 처리 (드래그 앤 드롭 대체)"""
        try:
            # 클립보드에서 텍스트 가져오기
            clipboard_text = self.root.clipboard_get()
            
            # 파일 경로인지 확인
            potential_files = []
            
            # 여러 줄로 된 파일 경로들 처리
            lines = clipboard_text.strip().split('\n')
            for line in lines:
                line = line.strip().strip('"').strip("'")
                if os.path.exists(line) and os.path.isfile(line):
                    potential_files.append(line)
            
            # 단일 경로 처리
            if not potential_files:
                clipboard_text = clipboard_text.strip().strip('"').strip("'")
                if os.path.exists(clipboard_text) and os.path.isfile(clipboard_text):
                    potential_files.append(clipboard_text)
            
            if potential_files:
                cert_files = [f for f in potential_files if self.is_certificate_file(f)]
                if cert_files:
                    self.process_dropped_files(cert_files)
                    return "break"  # 이벤트 전파 중단
                else:
                    self.status_var.set("클립보드의 파일이 인증서 형식이 아닙니다")
            else:
                # 일반 텍스트는 기본 처리
                pass
                
        except tk.TclError:
            # 클립보드가 비어있거나 텍스트가 아닌 경우
            pass
        except Exception as e:
            self.status_var.set(f"붙여넣기 오류: {str(e)[:50]}...")
    
    def process_dropped_files(self, cert_files):
        """드롭된/붙여넣은 파일 처리"""
        try:
            if len(cert_files) == 1:
                filepath = cert_files[0]
                self.file_path_var.set(filepath)
                self.status_var.set(f"✅ 파일 드롭됨: {os.path.basename(filepath)}")
                
                # PFX 파일인 경우 비밀번호 팝업
                if filepath.lower().endswith(('.pfx', '.p12')):
                    self.prompt_pfx_password(filepath)
                    
            elif len(cert_files) > 1:
                self.status_var.set(f"📁 다중 파일 드롭됨: {len(cert_files)}개")
                self.process_multiple_files(cert_files)
            
        except Exception as e:
            messagebox.showerror("파일 처리 오류", f"파일 처리 중 오류가 발생했습니다:\n{str(e)}")
    
    def is_certificate_file(self, filepath):
        """인증서 파일인지 확인 (확장자 + 파일 크기)"""
        try:
            # 파일 존재 여부 확인
            if not os.path.exists(filepath) or not os.path.isfile(filepath):
                return False
            
            # 확장자 확인
            cert_extensions = ['.pem', '.crt', '.cer', '.pfx', '.p12', '.der']
            if not any(filepath.lower().endswith(ext) for ext in cert_extensions):
                return False
            
            # 파일 크기 확인 (1MB ~ 50MB 사이)
            file_size = os.path.getsize(filepath)
            if file_size < 100 or file_size > 50 * 1024 * 1024:  # 100바이트 ~ 50MB
                return False
            
            # 기본적인 파일 내용 확인
            try:
                with open(filepath, 'rb') as f:
                    header = f.read(100)  # 첫 100바이트만 확인
                    
                # PEM 형식 확인
                if filepath.lower().endswith(('.pem', '.crt', '.cer')):
                    if b'-----BEGIN' not in header and b'-----' not in header:
                        # BASE64 인코딩된 내용이 있는지 확인
                        try:
                            header_str = header.decode('ascii', errors='ignore')
                            if not any(c.isalnum() for c in header_str):
                                return False
                        except:
                            return False
                
                # DER 형식 확인 (바이너리)
                elif filepath.lower().endswith('.der'):
                    # ASN.1 DER 형식은 0x30으로 시작
                    if not header.startswith(b'\x30'):
                        return False
                
                # PFX/P12 형식 확인
                elif filepath.lower().endswith(('.pfx', '.p12')):
                    # PKCS#12 매직 바이트 확인
                    if not (header.startswith(b'\x30') or b'PK' in header[:20]):
                        return False
                        
            except (IOError, OSError):
                return False
            
            return True
            
        except Exception:
            return False
    
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
            
            # PFX 파일인 경우 비밀번호 팝업
            if filename.lower().endswith(('.pfx', '.p12')):
                self.prompt_pfx_password(filename)
    
    def browse_multiple_files(self):
        """다중 파일 선택 다이얼로그"""
        file_types = [
            ("인증서 파일", "*.pem *.crt *.cer *.pfx *.p12 *.der"),
            ("PEM 파일", "*.pem"),
            ("CRT 파일", "*.crt *.cer"),
            ("PFX/P12 파일", "*.pfx *.p12"),
            ("DER 파일", "*.der"),
            ("모든 파일", "*.*")
        ]
        
        filenames = filedialog.askopenfilenames(
            title="SSL 인증서 파일 선택 (다중 선택)",
            filetypes=file_types
        )
        
        if filenames:
            cert_files = [f for f in filenames if self.is_certificate_file(f)]
            if cert_files:
                self.process_multiple_files(cert_files)
            else:
                messagebox.showwarning("파일 선택", "인증서 파일을 찾을 수 없습니다.")
    
    def prompt_pfx_password(self, filepath):
        """PFX 파일 비밀번호 입력 팝업"""
        if not filepath.lower().endswith(('.pfx', '.p12')):
            return
            
        # 비밀번호 입력 다이얼로그 생성
        password_dialog = tk.Toplevel(self.root)
        password_dialog.title("PFX 비밀번호 입력")
        password_dialog.geometry("450x250")
        password_dialog.resizable(False, False)
        password_dialog.transient(self.root)
        password_dialog.grab_set()
        
        # 다이얼로그를 부모 창 중앙에 위치
        password_dialog.update_idletasks()
        x = (password_dialog.winfo_screenwidth() // 2) - (password_dialog.winfo_width() // 2)
        y = (password_dialog.winfo_screenheight() // 2) - (password_dialog.winfo_height() // 2)
        password_dialog.geometry(f"+{x}+{y}")
        
        # 배경색 설정
        password_dialog.configure(bg=self.colors['bg'])
        
        # 제목
        title_label = tk.Label(password_dialog, text="🔐 PFX 파일 비밀번호", 
                              font=('Arial', 16, 'bold'), bg=self.colors['bg'], fg=self.colors['fg'])
        title_label.pack(pady=(20, 5))
        
        # 파일명 표시
        filename_label = tk.Label(password_dialog, text=f"파일: {os.path.basename(filepath)}", 
                                 font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['fg_light'],
                                 wraplength=400)
        filename_label.pack(pady=(0, 20))
        
        # 비밀번호 입력 프레임
        pwd_frame = tk.Frame(password_dialog, bg=self.colors['bg'])
        pwd_frame.pack(pady=15, padx=30, fill='x')
        
        tk.Label(pwd_frame, text="비밀번호:", font=('Arial', 12), bg=self.colors['bg'], fg=self.colors['fg']).pack(anchor='w')
        
        password_var = tk.StringVar()
        pwd_entry = tk.Entry(pwd_frame, textvariable=password_var, show="*", width=40,
                            font=('Arial', 12), bg=self.colors['entry_bg'], fg=self.colors['entry_fg'])
        pwd_entry.pack(fill='x', pady=(8, 0))
        pwd_entry.focus_set()
        
        # 비밀번호 표시 체크박스
        show_pwd_var = tk.BooleanVar()
        show_pwd_check = tk.Checkbutton(pwd_frame, text="비밀번호 표시", variable=show_pwd_var,
                                       bg=self.colors['bg'], fg=self.colors['fg'], font=('Arial', 10),
                                       command=lambda: pwd_entry.config(show="" if show_pwd_var.get() else "*"))
        show_pwd_check.pack(anchor='w', pady=(5, 0))
        
        # 버튼 프레임
        btn_frame = tk.Frame(password_dialog, bg=self.colors['bg'])
        btn_frame.pack(pady=25)
        
        result = {'password': None, 'cancelled': True}
        
        def on_ok():
            result['password'] = password_var.get()
            result['cancelled'] = False
            password_dialog.destroy()
        
        def on_cancel():
            result['cancelled'] = True
            password_dialog.destroy()
            
        def on_skip():
            result['password'] = ''  # 빈 비밀번호로 시도
            result['cancelled'] = False
            password_dialog.destroy()
        
        # 버튼들
        ok_btn = tk.Button(btn_frame, text="확인", command=on_ok, width=10,
                          bg=self.colors['success'], fg='white', font=('Arial', 11, 'bold'),
                          relief='flat', bd=0, padx=10, pady=5)
        ok_btn.pack(side='left', padx=8)
        
        skip_btn = tk.Button(btn_frame, text="비밀번호 없음", command=on_skip, width=14,
                            bg=self.colors['info'], fg='white', font=('Arial', 11),
                            relief='flat', bd=0, padx=10, pady=5)
        skip_btn.pack(side='left', padx=8)
        
        cancel_btn = tk.Button(btn_frame, text="취소", command=on_cancel, width=10,
                              bg=self.colors['fg_light'], fg='white', font=('Arial', 11),
                              relief='flat', bd=0, padx=10, pady=5)
        cancel_btn.pack(side='left', padx=8)
        
        # Enter/Escape 키 바인딩
        password_dialog.bind('<Return>', lambda e: on_ok())
        password_dialog.bind('<Escape>', lambda e: on_cancel())
        pwd_entry.bind('<Return>', lambda e: on_ok())
        
        # 다이얼로그가 닫힐 때까지 대기
        password_dialog.wait_window()
        
        # 결과 처리
        if not result['cancelled']:
            # 비밀번호를 메인 창의 비밀번호 필드에 설정
            self.password_var.set(result['password'])
            
            # 비밀번호가 설정되었다는 메시지 표시
            if result['password']:
                self.status_var.set("🔑 비밀번호 설정됨 - 검증 버튼을 눌러주세요")
            else:
                self.status_var.set("📝 비밀번호 없음으로 설정됨 - 검증 버튼을 눌러주세요")
                
            # 선택사항: 자동으로 검증 실행
            auto_verify = messagebox.askyesno("자동 검증", "PFX 비밀번호가 설정되었습니다.\n바로 인증서를 검증하시겠습니까?")
            if auto_verify:
                self.verify_certificate()
        else:
            # 취소된 경우 파일 선택도 취소
            self.file_path_var.set("")
            self.status_var.set("PFX 비밀번호 입력이 취소되었습니다")
    
    def process_multiple_files(self, file_paths):
        """다중 파일 처리"""
        if not file_paths:
            return
            
        # 결과 초기화
        self.analysis_results = []
        
        # 상태 업데이트
        self.status_var.set(f"다중 파일 분석 중... ({len(file_paths)}개)")
        self.progress.start()
        
        # 트리 초기화
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 별도 스레드에서 실행
        thread = threading.Thread(target=self.run_multiple_verification, args=(file_paths,))
        thread.daemon = True
        thread.start()
    
    def run_multiple_verification(self, file_paths):
        """다중 파일 검증 실행"""
        try:
            for i, filepath in enumerate(file_paths):
                try:
                    result = self.analyze_certificate(filepath)
                    result['file_path'] = filepath
                    result['file_name'] = os.path.basename(filepath)
                    self.analysis_results.append(result)
                    
                    # UI 업데이트 (중간 진행 상황)
                    progress_msg = f"분석 중... ({i+1}/{len(file_paths)}) {os.path.basename(filepath)}"
                    self.root.after(0, lambda msg=progress_msg: self.status_var.set(msg))
                    
                except Exception as e:
                    # 개별 파일 오류 처리
                    error_result = {
                        'file_path': filepath,
                        'file_name': os.path.basename(filepath),
                        'status': 'error',
                        'summary': f'파일 분석 실패: {str(e)}',
                        'chain_info': {'status': '❌ 분석 실패'}
                    }
                    self.analysis_results.append(error_result)
            
            # 완료 후 UI 업데이트
            self.root.after(0, self.display_multiple_results)
            
        except Exception as e:
            error_msg = f"다중 파일 분석 오류: {str(e)}"
            self.root.after(0, self.display_error, error_msg)
        finally:
            self.root.after(0, self.stop_progress)
    
    def display_multiple_results(self):
        """다중 파일 분석 결과 표시"""
        if not self.analysis_results:
            return
        
        # 상태 패널 - 다중 파일 요약
        self.show_multiple_files_status()
        
        # 트리뷰에 다중 파일 결과 표시
        self.populate_multiple_files_tree()
        
        # 상태 업데이트
        success_count = sum(1 for r in self.analysis_results if r.get('status') != 'error')
        self.status_var.set(f"✅ 다중 파일 분석 완료: {success_count}/{len(self.analysis_results)}개 성공")
    
    def show_multiple_files_status(self):
        """다중 파일 상태 표시"""
        for widget in self.status_frame.winfo_children():
            widget.destroy()
        
        # 결과 요약
        total_files = len(self.analysis_results)
        success_files = sum(1 for r in self.analysis_results if r.get('status') != 'error')
        complete_chains = sum(1 for r in self.analysis_results if '완전한 체인' in r.get('chain_info', {}).get('status', ''))
        
        # 상태 패널
        if self.dark_mode:
            bg_color = '#3c3c3c'
            fg_color = '#ffffff'
        else:
            bg_color = '#f8f9fa'
            fg_color = '#000000'
            
        status_panel = tk.Frame(self.status_frame, bg=bg_color, relief='solid', bd=2)
        status_panel.pack(fill='x', pady=(0, 10))
        
        # 제목
        title_label = tk.Label(status_panel, text=f"📊 다중 파일 분석 결과", 
                              bg=bg_color, fg=fg_color, font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # 요약 정보
        summary_text = f"총 {total_files}개 파일 • 성공 {success_files}개 • 완전한 체인 {complete_chains}개"
        summary_label = tk.Label(status_panel, text=summary_text,
                                bg=bg_color, fg=fg_color, font=('Arial', 12))
        summary_label.pack(pady=(0, 10))
    
    def populate_multiple_files_tree(self):
        """다중 파일 결과를 트리에 표시"""
        # 기존 아이템 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 최상위 노드
        summary_item = self.tree.insert('', 'end', 
                                      text=f"📊 다중 파일 분석 결과",
                                      values=('분석 요약', f'{len(self.analysis_results)}개 파일', ''))
        
        # 각 파일별 결과 추가
        for result in self.analysis_results:
            file_name = result.get('file_name', 'Unknown')
            file_path = result.get('file_path', '')
            
            if result.get('status') == 'error':
                # 오류 파일
                file_item = self.tree.insert(summary_item, 'end',
                                           text=f"❌ {file_name}",
                                           values=('오류', '분석 실패', ''))
                
                self.tree.insert(file_item, 'end',
                               text=f"  오류: {result.get('summary', 'Unknown error')}",
                               values=('', '', ''))
            else:
                # 정상 분석된 파일
                chain_status = result.get('chain_info', {}).get('status', '알 수 없음')
                cert_count = result.get('cert_count', 1)
                
                # 상태 아이콘
                if '완전한 체인' in chain_status:
                    status_icon = "✅"
                elif '불완전한 체인' in chain_status or '단일 인증서' in chain_status:
                    status_icon = "⚠️"
                else:
                    status_icon = "❓"
                
                file_item = self.tree.insert(summary_item, 'end',
                                           text=f"{status_icon} {file_name}",
                                           values=('파일', chain_status, f'{cert_count}개 인증서'))
                
                # 인증서 상세 정보 (간단히)
                certificates = result.get('certificates', [result])
                for cert_info in certificates[:3]:  # 최대 3개만 표시
                    cn = self.extract_cn_from_subject(cert_info.get('subject', ''))
                    validity = cert_info.get('validity_status', '')
                    validity_icon = self.get_validity_icon(validity)
                    
                    self.tree.insert(file_item, 'end',
                                   text=f"  📜 {cn}",
                                   values=('인증서', f'{validity_icon} {validity}', ''))
                
                if len(certificates) > 3:
                    self.tree.insert(file_item, 'end',
                                   text=f"  ... 및 {len(certificates) - 3}개 더",
                                   values=('', '', ''))
        
        # 요약 노드 확장
        self.tree.item(summary_item, open=True)
        self.tree.selection_set(summary_item)
    
    def verify_certificate(self):
        """인증서 검증 실행"""
        filepath = self.file_path_var.get().strip()
        
        if not filepath:
            messagebox.showerror("오류", "인증서 파일을 선택해주세요.")
            return
        
        if not os.path.exists(filepath):
            messagebox.showerror("파일 오류", "선택한 파일이 존재하지 않습니다.")
            return
        
        # 백그라운드에서 검증 실행
        self.start_verification(filepath)
    
    def start_verification(self, filepath):
        """백그라운드에서 검증 시작"""
        self.progress.start()
        self.status_var.set("인증서 분석 중...")
        
        # 트리 초기화
        for item in self.tree.get_children():
            self.tree.delete(item)
        
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
        """인증서 분석 (기존 로직 재사용)"""
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
                'extensions': '',
                'chain_info': {'status': '❌ 분석 실패'}
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
        result['file_type'] = os.path.splitext(filepath)[1].lower()
        result['certificates'] = []
        
        # 모든 인증서 정보 수집
        for i, cert_block in enumerate(cert_blocks):
            cert_obj = x509.load_pem_x509_certificate(cert_block)
            cert_info = self.extract_certificate_info(cert_obj)
            cert_info['position'] = i
            cert_info['cert_object'] = cert_obj
            result['certificates'].append(cert_info)
        
        # 체인 검증 수행
        if len(cert_blocks) > 1:
            chain_result = self.verify_certificate_chain(cert_blocks)
            result['chain_info'] = chain_result
        else:
            result['chain_info'] = {
                'status': '📄 단일 인증서',
                'details': '중간 인증서가 필요할 수 있습니다',
                'is_complete': False
            }
        
        return result
    
    def analyze_der_certificate(self, filepath):
        """DER 인증서 분석"""
        with open(filepath, 'rb') as f:
            cert_data = f.read()
        
        cert = x509.load_der_x509_certificate(cert_data)
        result = self.extract_certificate_info(cert)
        result['file_type'] = '.der'
        result['cert_count'] = 1
        result['certificates'] = [result.copy()]
        result['chain_info'] = {
            'status': '📄 단일 인증서',
            'details': '중간 인증서가 필요할 수 있습니다',
            'is_complete': False
        }
        return result
    
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
        result['file_type'] = '.pfx'
        result['has_private_key'] = private_key is not None
        result['cert_count'] = 1 + (len(additional_certificates) if additional_certificates else 0)
        result['certificates'] = []
        
        # 메인 인증서
        main_cert_info = self.extract_certificate_info(certificate)
        main_cert_info['position'] = 0
        main_cert_info['cert_type'] = 'leaf'
        main_cert_info['cert_object'] = certificate
        result['certificates'].append(main_cert_info)
        
        # 추가 인증서들
        if additional_certificates:
            for i, cert in enumerate(additional_certificates):
                cert_info = self.extract_certificate_info(cert)
                cert_info['position'] = i + 1
                cert_info['cert_type'] = 'ca'
                cert_info['cert_object'] = cert
                result['certificates'].append(cert_info)
            
            # PFX의 체인 검증
            all_certs = [certificate] + list(additional_certificates)
            pfx_chain_result = self.verify_pfx_chain(all_certs)
            result['chain_info'] = pfx_chain_result
        else:
            result['chain_info'] = {
                'status': '📄 단일 인증서',
                'details': '중간 CA가 포함되지 않음',
                'is_complete': False
            }
        
        return result
    
    def extract_certificate_info(self, cert):
        """인증서에서 정보 추출 (기존 로직 재사용)"""
        # 기본 정보
        subject = self.format_name(cert.subject)
        issuer = self.format_name(cert.issuer)
        serial = hex(cert.serial_number)[2:].upper()
        
        # 날짜 정보
        not_before = cert.not_valid_before
        not_after = cert.not_valid_after
        
        # timezone 정보 통일
        if not_before.tzinfo is None:
            not_before = not_before.replace(tzinfo=timezone.utc)
        if not_after.tzinfo is None:
            not_after = not_after.replace(tzinfo=timezone.utc)
        
        # 현재 시간과 비교
        now = datetime.now(timezone.utc)
        
        try:
            if not_after < now:
                days_left = (now - not_after).days
                validity_status = f"만료됨 ({days_left}일 전)"
                validity_color = 'danger'
            elif (not_after - now).days < 30:
                days_left = (not_after - now).days
                validity_status = f"곧 만료 ({days_left}일 남음)"
                validity_color = 'warning'
            else:
                days_left = (not_after - now).days
                validity_status = f"유효 ({days_left}일 남음)"
                validity_color = 'success'
        except Exception:
            validity_status = "유효성 확인 불가"
            validity_color = 'warning'
        
        # 공개키 정보
        public_key = cert.public_key()
        key_info = self.get_public_key_info(public_key)
        
        # SAN 도메인 추출
        san_domains = self.extract_san_domains(cert)
        
        # 인증서 용도
        usage = self.get_certificate_usage(cert)
        
        return {
            'subject': subject,
            'issuer': issuer,
            'serial': serial,
            'not_before': not_before,
            'not_after': not_after,
            'validity_status': validity_status,
            'validity_color': validity_color,
            'key_info': key_info,
            'san_domains': san_domains,
            'usage': usage,
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
                    if hasattr(name, 'value'):
                        domains.append(name.value)
                    else:
                        domains.append(str(name))
            return domains
        except (x509.ExtensionNotFound, AttributeError, Exception):
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
        except (x509.ExtensionNotFound, AttributeError, Exception):
            pass
        
        return ', '.join(usages) if usages else "용도 불명"
    
    def verify_certificate_chain(self, cert_blocks):
        """인증서 체인 검증 (기존 로직)"""
        try:
            certificates = []
            for cert_block in cert_blocks:
                cert = x509.load_pem_x509_certificate(cert_block)
                certificates.append(cert)
            
            chain_issues = []
            is_complete_chain = True
            
            # 체인 연결성 검사 - 개선된 로직
            for i in range(len(certificates) - 1):
                current_cert = certificates[i]
                next_cert = certificates[i + 1]
                
                current_issuer = self.format_name(current_cert.issuer)
                next_subject = self.format_name(next_cert.subject)
                
                # 개선된 연결성 검사 사용
                connection_status = self.check_certificate_connection(current_issuer, next_subject)
                
                if "연결됨" in connection_status:
                    chain_issues.append(f"✅ 인증서 {i+1} → {i+2}: {connection_status}")
                elif "부분 연결" in connection_status:
                    chain_issues.append(f"🟡 인증서 {i+1} → {i+2}: {connection_status}")
                    # 부분 연결은 경고로 처리하지만 체인 끊김은 아님
                else:
                    chain_issues.append(f"❌ 인증서 {i+1} → {i+2}: {connection_status}")
                    chain_issues.append(f"   현재 Issuer: {current_issuer}")
                    chain_issues.append(f"   다음 Subject: {next_subject}")
                    is_complete_chain = False
            
            # 루트 인증서 확인
            root_cert = certificates[-1]
            root_subject = self.format_name(root_cert.subject)
            root_issuer = self.format_name(root_cert.issuer)
            
            is_self_signed = (root_subject == root_issuer)
            
            if is_self_signed:
                chain_issues.append(f"✅ 루트 CA: 자체 서명 인증서 확인됨")
            else:
                chain_issues.append(f"⚠️ 루트 CA: 자체 서명이 아님 (상위 CA 필요할 수 있음)")
                is_complete_chain = False
            
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
        """PFX 인증서 체인 검증 (기존 로직)"""
        try:
            if len(certificates) < 2:
                return {'status': '❓ 단일 인증서', 'is_complete': False}
            
            # 간단한 체인 검증
            leaf_cert = certificates[0]
            ca_certs = certificates[1:]
            
            # 체인 연결 확인
            current_cert = leaf_cert
            chain_ok = True
            
            for ca_cert in ca_certs:
                current_issuer = self.format_name(current_cert.issuer)
                ca_subject = self.format_name(ca_cert.subject)
                
                if current_issuer == ca_subject:
                    current_cert = ca_cert
                else:
                    chain_ok = False
                    break
            
            # 마지막 인증서가 자체 서명인지 확인
            if chain_ok:
                root_subject = self.format_name(current_cert.subject)
                root_issuer = self.format_name(current_cert.issuer)
                
                if root_subject == root_issuer:
                    return {'status': '✅ 완전한 체인', 'is_complete': True}
                else:
                    return {'status': '⚠️ 불완전한 체인 (루트 CA 없음)', 'is_complete': False}
            else:
                return {'status': '⚠️ 불완전한 체인 (연결 오류)', 'is_complete': False}
                
        except Exception:
            return {'status': '❌ 체인 검증 실패', 'is_complete': False}
    
    def display_results(self, result):
        """결과를 새로운 UI에 표시"""
        self.current_result = result
        
        # 상태 패널 업데이트
        self.show_chain_status(result)
        
        # 트리뷰 업데이트
        self.populate_tree_view(result)
        
        # 상태 업데이트
        self.status_var.set("✅ 인증서 분석 완료")
    
    def populate_tree_view(self, result):
        """트리뷰에 인증서 정보를 계층적으로 표시"""
        # 기존 아이템 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        certificates = result.get('certificates', [result])
        
        if len(certificates) == 1:
            # 단일 인증서
            cert_info = certificates[0]
            self.add_single_certificate_to_tree(cert_info)
        else:
            # 체인 구조로 표시
            self.add_certificate_chain_to_tree(certificates, result)
        
        # 첫 번째 아이템 확장 및 선택
        if self.tree.get_children():
            first_item = self.tree.get_children()[0]
            self.tree.item(first_item, open=True)
            self.tree.selection_set(first_item)
            self.on_tree_select(None)
    
    def add_single_certificate_to_tree(self, cert_info):
        """단일 인증서를 트리에 추가"""
        subject_full = cert_info.get('subject', '')
        cn_match = self.extract_cn_from_subject(subject_full)
        
        validity_icon = self.get_validity_icon(cert_info.get('validity_status', ''))
        
        # 메인 인증서 아이템
        main_item = self.tree.insert('', 'end', 
                                   text=f"📄 {cn_match}",
                                   values=('단일 인증서', 
                                          f"{validity_icon} {cert_info.get('validity_status', '')}",
                                          cert_info.get('key_info', '')))
        
        # 상세 정보 추가
        self.add_certificate_details_to_tree(main_item, cert_info)
    
    def add_certificate_chain_to_tree(self, certificates, result):
        """인증서 체인을 계층적으로 트리에 추가"""
        # 체인 상태 정보
        chain_info = result.get('chain_info', {})
        chain_status = chain_info.get('status', '알 수 없음')
        
        # 최상위 체인 노드
        chain_icon = '✅' if '완전한 체인' in chain_status else ('⚠️' if '불완전' in chain_status else '❓')
        chain_item = self.tree.insert('', 'end', 
                                    text=f"{chain_icon} 인증서 체인",
                                    values=('체인 구조', chain_status, f'{len(certificates)}개 인증서'))
        
        # 각 인증서를 체인 순서대로 추가
        parent_item = chain_item
        
        for i, cert_info in enumerate(certificates):
            # 인증서 타입 결정
            if i == 0:
                icon = "🌟"
                cert_type = "리프 인증서 (End Entity)"
            else:
                subject = cert_info.get('subject', '')
                issuer = cert_info.get('issuer', '')
                
                if subject == issuer:
                    icon = "🏛️"
                    cert_type = "루트 CA (자체 서명)"
                else:
                    icon = "🏢"
                    cert_type = "중간 CA"
            
            # CN 추출
            cn_match = self.extract_cn_from_subject(cert_info.get('subject', ''))
            
            # 유효성 상태
            validity_icon = self.get_validity_icon(cert_info.get('validity_status', ''))
            
            # 체인 연결 표시 - 개선된 로직
            if i > 0:
                # 이전 인증서와의 연결 상태 확인
                prev_cert = certificates[i-1]
                prev_issuer = prev_cert.get('issuer', '')
                current_subject = cert_info.get('subject', '')
                
                # 연결성 검사 개선: 문자열 정규화 및 핵심 필드 비교
                connection = self.check_certificate_connection(prev_issuer, current_subject)
                
                # 연결 상태 표시
                self.tree.insert(parent_item, 'end',
                                  text=f"      ↓ {connection}",
                                  values=('체인 연결', '', ''))
            
            # 인증서 추가
            cert_item = self.tree.insert(parent_item, 'end',
                                       text=f"{icon} {cn_match}",
                                       values=(cert_type,
                                              f"{validity_icon} {cert_info.get('validity_status', '')}",
                                              cert_info.get('key_info', '')))
            
            # 인증서 상세 정보 추가
            self.add_certificate_details_to_tree(cert_item, cert_info)
            
        # 체인 검증 결과 추가
        if 'details' in chain_info:
            details_lines = chain_info['details'].split('\n')
            for line in details_lines:
                if line.strip():
                    self.tree.insert(chain_item, 'end',
                                   text=f"  {line}",
                                   values=('검증 결과', '', ''))
    
    def add_certificate_details_to_tree(self, parent_item, cert_info):
        """인증서 상세 정보를 트리에 추가"""
        # Issuer 정보
        issuer = cert_info.get('issuer', '')
        if issuer != cert_info.get('subject', ''):
            issuer_cn = self.extract_cn_from_subject(issuer)
            self.tree.insert(parent_item, 'end',
                           text=f"  📜 발급자: {issuer_cn}",
                           values=('발급자', '', ''))
        
        # SAN 도메인들
        san_domains = cert_info.get('san_domains', [])
        if san_domains:
            san_item = self.tree.insert(parent_item, 'end',
                                      text=f"  🌐 대상 도메인 ({len(san_domains)}개)",
                                      values=('SAN', '', ''))
            
            for domain in san_domains[:5]:  # 최대 5개만 표시
                self.tree.insert(san_item, 'end',
                               text=f"    • {domain}",
                               values=('도메인', '', ''))
            
            if len(san_domains) > 5:
                self.tree.insert(san_item, 'end',
                               text=f"    ... 및 {len(san_domains) - 5}개 더",
                               values=('', '', ''))
        
        # 인증서 용도
        usage = cert_info.get('usage', '')
        if usage and usage != '용도 불명':
            self.tree.insert(parent_item, 'end',
                           text=f"  🎯 용도: {usage}",
                           values=('용도', '', ''))
    
    def extract_cn_from_subject(self, subject_full):
        """Subject에서 CN 추출"""
        if 'CN=' in subject_full:
            try:
                return subject_full.split('CN=')[1].split(',')[0].strip()
            except:
                pass
        return subject_full if subject_full else 'Unknown'
    
    def get_validity_icon(self, validity_status):
        """유효성 상태에 따른 아이콘 반환"""
        if '유효' in validity_status and '곧' not in validity_status:
            return "✅"
        elif '곧 만료' in validity_status:
            return "⚠️"
        else:
            return "❌"
    
    def check_certificate_connection(self, prev_issuer, current_subject):
        """인증서 연결성 검사 - 개선된 로직"""
        if not prev_issuer or not current_subject:
            return "❓ 정보 불충분"
        
        # 1. 정확한 매칭 (기존 방식)
        if prev_issuer.strip() == current_subject.strip():
            return "🔗 연결됨"
        
        # 2. 정규화된 매칭 (공백, 순서 무시)
        def normalize_dn(dn_string):
            """DN 문자열을 정규화"""
            # 쉼표로 분리하고 각 부분을 정리
            parts = []
            for part in dn_string.split(','):
                part = part.strip()
                if '=' in part:
                    key, value = part.split('=', 1)
                    parts.append(f"{key.strip()}={value.strip()}")
            return sorted(parts)  # 순서 무관하게 정렬
        
        prev_normalized = normalize_dn(prev_issuer)
        current_normalized = normalize_dn(current_subject)
        
        if prev_normalized == current_normalized:
            return "🔗 연결됨 (정규화)"
        
        # 3. 핵심 필드만 비교 (CN 기준)
        def extract_cn(dn_string):
            """DN에서 CN만 추출"""
            for part in dn_string.split(','):
                part = part.strip()
                if part.upper().startswith('CN='):
                    return part.split('=', 1)[1].strip()
            return None
        
        prev_cn = extract_cn(prev_issuer)
        current_cn = extract_cn(current_subject)
        
        if prev_cn and current_cn and prev_cn == current_cn:
            return "🔗 연결됨 (CN)"
        
        # 4. 부분적 매칭 확인
        common_parts = set(prev_normalized) & set(current_normalized)
        if len(common_parts) >= 2:  # 최소 2개 필드가 일치
            return "🟡 부분 연결"
        
        # 5. 완전히 다른 경우
        return "⚠️ 연결 끊김"
    
    def on_tree_select(self, event):
        """트리 선택 이벤트"""
        selection = self.tree.selection()
        if not selection or not self.current_result:
            return
        
        selected_item = selection[0]
        # 선택된 아이템의 텍스트 등으로 위치 매핑을 해도 되지만,
        # 기본 구현은 첫 인증서를 상세보기로 표시
        certificates = self.current_result.get('certificates', [self.current_result])
        if certificates:
            cert_info = certificates[0]
            self.show_certificate_details(cert_info)
    
    def show_certificate_details(self, cert_info):
        """인증서 상세 정보 표시"""
        # 기본 정보 탭
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)
        
        details = []
        details.append("=== 인증서 기본 정보 ===\n")
        details.append(f"📋 Subject: {cert_info.get('subject', 'N/A')}")
        details.append(f"🏢 Issuer: {cert_info.get('issuer', 'N/A')}")
        details.append(f"🔢 Serial: {cert_info.get('serial', 'N/A')}")
        details.append("")
        details.append(f"📅 유효 기간:")
        
        not_before = cert_info.get('not_before')
        not_after = cert_info.get('not_after')
        if not_before and not_after:
            details.append(f"   시작: {not_before.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            details.append(f"   종료: {not_after.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        
        details.append(f"   상태: {cert_info.get('validity_status', 'N/A')}")
        details.append("")
        details.append(f"🔐 공개키: {cert_info.get('key_info', 'N/A')}")
        details.append(f"📋 용도: {cert_info.get('usage', 'N/A')}")
        
        san_domains = cert_info.get('san_domains', [])
        if san_domains:
            details.append("")
            details.append("🌐 도메인 (SAN):")
            for domain in san_domains:
                details.append(f"   • {domain}")
        
        self.info_text.insert(tk.END, '\n'.join(details))
        self.info_text.config(state='disabled')
        
        # 확장 필드 탭 (간단 버전)
        self.ext_text.config(state='normal')
        self.ext_text.delete(1.0, tk.END)
        
        cert_obj = cert_info.get('cert_object')
        if cert_obj:
            ext_details = []
            ext_details.append("=== 인증서 확장 필드 ===\n")
            
            try:
                for ext in cert_obj.extensions:
                    oid_name = getattr(ext.oid, '_name', str(ext.oid))
                    critical_str = 'Critical' if ext.critical else 'Non-Critical'
                    ext_details.append(f"• {oid_name} ({critical_str})")
                    
                    try:
                        ext_value = str(ext.value)
                        if len(ext_value) > 100:
                            ext_value = ext_value[:100] + "... (truncated)"
                        ext_details.append(f"  값: {ext_value}")
                    except:
                        ext_details.append(f"  값: <파싱 불가>")
                    
                    ext_details.append("")
            except:
                ext_details.append("확장 필드 정보를 읽을 수 없습니다.")
            
            self.ext_text.insert(tk.END, '\n'.join(ext_details))
        
        self.ext_text.config(state='disabled')
    
    def display_error(self, error_msg):
        """오류 표시"""
        messagebox.showerror("검증 오류", error_msg)
        self.status_var.set("❌ 검증 실패")
    
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
    
    # tkinterdnd2 상태 확인
    if HAS_TKINTERDND2:
        print("✅ tkinterdnd2 사용 가능 - 실제 드래그 앤 드롭 지원")
        root = TkinterDnD.Tk()  # TkinterDnD로 초기화
    else:
        print("⚠️ tkinterdnd2 없음 - 클립보드 붙여넣기만 지원")
        print("   설치 권장: pip install tkinterdnd2")
        root = tk.Tk()
    
    app = EnhancedSSLCertificateChecker(root)
    
    # 아이콘 설정 (선택사항)
    try:
        root.iconbitmap(default="")  # Windows에서 기본 아이콘 제거
    except:
        pass
    
    root.mainloop()


if __name__ == "__main__":
    main()
