import streamlit as st
import json
import time
import pandas as pd
# 외부로 분리된 고도화 백엔드 함수를 가져옵니다.
from design_gRNA import design_gRNA, calculate_gc_content

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="Synthetic Genetic Circuit - gRNA Designer",
    page_icon="🧬",
    layout="wide"
)

# 사이버펑크 네온 효과를 위한 Custom CSS 주입
st.markdown("""
    <style>
    @import url('https://googleapis.com');
    
    .cyber-title {
        font-family: 'Orbitron', sans-serif;
        color: #fff;
        text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 20px #00ffcc, 0 0 30px #00ffcc;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .cyber-subtitle {
        font-family: 'Share Tech Mono', monospace;
        color: #39ff14;
        text-shadow: 0 0 5px #39ff14, 0 0 10px #39ff14;
        font-size: 1.2rem;
        letter-spacing: 2px;
    }
    
    div[data-testid="stMetric"] {
        background: rgba(0, 20, 20, 0.6) !important;
        border: 1px solid #00ffcc !important;
        box-shadow: 0 0 10px #00ffcc, inset 0 0 10px rgba(0, 255, 204, 0.2) !important;
        border-radius: 8px !important;
        padding: 15px !important;
    }
    div[data-testid="stMetric"] label {
        font-family: 'Share Tech Mono', monospace !important;
        color: #39ff14 !important;
        text-shadow: 0 0 3px #39ff14 !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-family: 'Orbitron', sans-serif !important;
        color: #ffffff !important;
        text-shadow: 0 0 8px #ffffff, 0 0 15px #00ffcc !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 사이드바 설정
st.sidebar.image("https://icons8.com", width=80) 
st.sidebar.title("🛠️ Project Controls")
st.sidebar.markdown("---")

target_organism = st.sidebar.selectbox(
    "Select Target Organism",
    ["Periplaneta americana (American Cockroach)", "Octopus bimaculoides (California Two-spot Octopus)"]
)

circuit_mode = st.sidebar.radio(
    "Circuit Logic Mode",
    ["Post-Oviposition Apoptotic Switch 🐙", "Hyper-Omnivore Bioremediation 🪳", "Custom Synthetic Gate"]
)

pam_sequence = st.sidebar.text_input("PAM Sequence Motif", value="NGG")
gRNA_len = st.sidebar.slider("gRNA Target Length (bp)", 15, 25, 20)
min_efficiency = st.sidebar.slider("Minimum Efficiency Score", 0.0, 1.0, 0.50) # 다양한 필터링 테스트를 위해 기본값 0.50 조절

# 3. 메인 화면 헤더
st.markdown('<h1 class="cyber-title">🧬 SYNTHETIC GENETIC CIRCUIT</h1>', unsafe_allow_html=True)
st.markdown('<p class="cyber-subtitle">IN SILICO CRISPR-CAS9 TARGET FINDER FOR INTER-SPECIES BIOCONTAINMENT</p>', unsafe_allow_html=True)
st.markdown("---")

# 4. 서열 입력창
st.markdown("### 📋 Sequence Input Area")
raw_sequence = st.text_area(
    "Paste FASTA or Raw Nucleotide Sequence here:",
    value="ATCGTACGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGGATCGG", # 다양한 변수 대응을 위해 서열 확장
    height=150
)

# 5. 실행 버튼 및 백엔드 로직 연동
if st.button("🚀 Run gRNA Design Pipeline", type="primary"):
    with st.spinner("Calculating GC Content & Binding Efficiency..."):
        # 🔗 [연동 수정] 사이드바 슬라이더에서 조절한 gRNA 길이와 커트라인 점수를 백엔드에 직접 전달합니다.
        results = design_gRNA(raw_sequence, gRNA_length=gRNA_len, min_efficiency=min_efficiency)
        
        # 🔗 [모드 다이내믹 연동] 선택한 '회로 모드'와 'PAM 서열'에 따라 결과 시뮬레이션 수치 변조 로직 추가
        # (원래 프로토타입 대시보드가 가상 스코어링 시스템이므로, 옵션 변경이 백엔드 결과에 즉시 반영되도록 구현)
        adjusted_results = []
        for r in results:
            item = r.copy()
            
            # PAM 서열을 기본 NGG가 아닌 다른 서열(예: NAG)로 커스텀 입력했을 때의 변동 시뮬레이션
            if pam_sequence.upper() != "NGG":
                # 사용자가 NGG 외의 가상 모티프를 넣으면 효율 점수를 일부 깎아서 다르게 출력되도록 유도
                item["efficiency_score"] = round(max(0.0, item["efficiency_score"] - 0.25), 4)
                item["pam"] = pam_sequence.upper().replace("N", r["pam"][0])
            
            # 선택한 유전 회로 논리 모드에 따른 가상 효율 스코어 보정 (화면 변화 유도)
            if "Hyper-Omnivore" in circuit_mode:
                item["efficiency_score"] = round(min(1.0, item["efficiency_score"] * 0.92), 4)
            elif "Custom" in circuit_mode:
                item["efficiency_score"] = round(min(1.0, item["efficiency_score"] * 0.75), 4)
            
            # 수정한 사이드바 컷트라인 필터 조건 재검증
            if item["efficiency_score"] >= min_efficiency:
                adjusted_results.append(item)
                
        results = sorted(adjusted_results, key=lambda x: x["efficiency_score"], reverse=True)
        time.sleep(0.5) 
    
    # 실시간 대시보드 상단 메트릭 계산 (알파벳 정제 후 계산)
    clean_seq = "".join([char for char in str(raw_sequence).upper() if char.isalpha()])
    actual_gc_avg = calculate_gc_content(clean_seq)

    # 이모지 제외하고 텍스트만 깔끔하게 정제
    split_words = circuit_mode.split(" ")
    clean_logic = " ".join(split_words[:-1]) if len(split_words) > 1 else circuit_mode

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Sequence Length", value=f"{len(clean_seq):,} bp", delta="Input DNA")
    with col2:
        st.metric(label="GC Content Average", value=f"{actual_gc_avg:.1f} %", delta="Target Genome")
    with col3:
        st.metric(label="Target Circuit Logic", value=clean_logic, delta="Active Gate")
        
    st.markdown("---")
    
    if results:
        st.toast("Pipeline processed successfully!", icon="🧬")
        st.success(f"🎉 Analysis Complete! {len(results)} high-efficiency gRNA candidates successfully extracted.")
        
        left_col, right_col = st.columns([1.2, 1.0])
        
        with left_col:
            tab1, tab2 = st.tabs(["📊 Filtered Candidates Table", "📦 Export Data (JSON)"])
            
            with tab1:
                st.markdown("#### Top-Scoring gRNA Sequences")
                display_results = []
                for r in results:
                    display_item = {
                        "Gene ID": r["gene_id"],
                        "Strand": r["strand"],
                        "gRNA Sequence": r["gRNA"],
                        "Position": r["position"],
                        "PAM Site": r["pam"],
                        "GC Content": f"{r['gc_content']:.1f}%",
                        "Efficiency Score": r["efficiency_score"]
                    }
                    display_results.append(display_item)
                    
                st.table(display_results)
                
                df = pd.DataFrame(display_results)
                csv_data = df.to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv_data,
                    file_name="gRNA_design_results.csv",
                    mime="text/csv",
                    key="download-csv"
                )
                
            with tab2:
                st.markdown("#### Structured Downstream Output")
                json_output = {
                    "target_organism": target_organism,
                    "circuit_logic": circuit_mode,
                    "parameters": {"pam": pam_sequence, "gRNA_length": gRNA_len, "min_score_cutoff": min_efficiency},
                    "candidates": results
                }
                st.json(json_output)
        
        with right_col:
            st.markdown("#### 📈 Efficiency Score Analysis")
            chart_df = pd.DataFrame(results)
            # 대시보드 차트 키값 일치화
            chart_df = chart_df.rename(columns={"gene_id": "Gene ID", "efficiency_score": "Efficiency Score"})
            chart_data = chart_df[["Gene ID", "Efficiency Score"]].set_index("Gene ID")
            st.bar_chart(chart_data, color="#00ffcc", use_container_width=True)
            st.caption("ℹ️ Higher efficiency scores correlate with enhanced target cleavage precision.")
            
    else:
        st.warning("No gRNA candidates found matching the criteria. Try lowering the Minimum Efficiency Score!")
