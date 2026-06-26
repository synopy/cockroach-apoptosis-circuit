import streamlit as st
import json
import time
import pandas as pd
from design_gRNA import design_gRNA, calculate_gc_content

st.set_page_config(
    page_title="Synthetic Genetic Circuit - gRNA Designer",
    page_icon="🧬",
    layout="wide"
)

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
min_efficiency = st.sidebar.slider("Minimum Efficiency Score", 0.0, 1.0, 0.50) 

st.markdown('<h1 class="cyber-title">🧬 SYNTHETIC GENETIC CIRCUIT</h1>', unsafe_allow_html=True)
st.markdown('<p class="cyber-subtitle">IN SILICO CRISPR-CAS9 TARGET FINDER FOR INTER-SPECIES BIOCONTAINMENT</p>', unsafe_allow_html=True)
st.markdown("---")

st.markdown("### 📋 Sequence Input Area")
raw_sequence = st.text_area(
    "Paste FASTA or Raw Nucleotide Sequence here:",
    value="ATCGTACGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGGATCGG", 
    height=150
)

if st.button("🚀 Run gRNA Design Pipeline", type="primary"):
    with st.spinner("Calculating GC Content & Binding Efficiency..."):
        
        results = design_gRNA(raw_sequence, gRNA_length=gRNA_len, min_efficiency=min_efficiency)
        
     
        
        adjusted_results = []
        for r in results:
            item = r.copy()
            
            
            if pam_sequence.upper() != "NGG":
                
                item["efficiency_score"] = round(max(0.0, item["efficiency_score"] - 0.25), 4)
                item["pam"] = pam_sequence.upper().replace("N", r["pam"][0])
            
            
            if "Hyper-Omnivore" in circuit_mode:
                item["efficiency_score"] = round(min(1.0, item["efficiency_score"] * 0.92), 4)
            elif "Custom" in circuit_mode:
                item["efficiency_score"] = round(min(1.0, item["efficiency_score"] * 0.75), 4)
            
            
            if item["efficiency_score"] >= min_efficiency:
                adjusted_results.append(item)
                
        results = sorted(adjusted_results, key=lambda x: x["efficiency_score"], reverse=True)
        time.sleep(0.5) 
    
    
    clean_seq = "".join([char for char in str(raw_sequence).upper() if char.isalpha()])
    actual_gc_avg = calculate_gc_content(clean_seq)

    
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
            
            chart_df = chart_df.rename(columns={"gene_id": "Gene ID", "efficiency_score": "Efficiency Score"})
            chart_data = chart_df[["Gene ID", "Efficiency Score"]].set_index("Gene ID")
            st.bar_chart(chart_data, color="#00ffcc", use_container_width=True)
            st.caption("ℹ️ Higher efficiency scores correlate with enhanced target cleavage precision.")
            
    else:
        st.warning("No gRNA candidates found matching the criteria. Try lowering the Minimum Efficiency Score!")
