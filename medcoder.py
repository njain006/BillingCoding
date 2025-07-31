import streamlit as st
from openai import OpenAI
import json

# Initialize
st.set_page_config(page_title="MedCoder AI", page_icon="🩺")
st.title("🩺 MedCoder AI: Auto-Medical Coding")
st.caption("Generate accurate ICD-10/CPT codes from clinical notes")

# EMBEDDED SAMPLE NOTES
CLINICAL_NOTES = [
    {"note": "55yo male with type 2 diabetes presenting for routine follow-up. HbA1c 7.2%. Continued on metformin 1000mg BID. Discussed dietary modifications.", "icd10": ["E11.9"], "cpt": ["99213"]},
    {"note": "28yo female with acute streptococcal pharyngitis. Rapid strep positive. Prescribed penicillin VK 500mg TID x10 days. Advised symptomatic management.", "icd10": ["J02.0"], "cpt": ["99203", "87880"]},
    {"note": "72yo female with left hip osteoarthritis. Significant pain with ambulation. Scheduled for left total hip arthroplasty next month. Prescribed meloxicam 15mg daily.", "icd10": ["M16.12"], "cpt": ["99214", "73552"]},
    {"note": "6yo male with acute asthma exacerbation. Wheezing and tachypnea present. Administered albuterol nebulizer in office with improvement. Started on prednisolone.", "icd10": ["J45.901"], "cpt": ["99213", "94640"]},
    {"note": "Annual wellness visit for 42yo female. No new complaints. Review of systems negative. Mammogram scheduled. Vaccinations up-to-date.", "icd10": ["Z00.00"], "cpt": ["99396"]}
]

# API Setup
api_key = st.sidebar.text_input("Enter OpenAI API Key:", type="password")
model = st.sidebar.selectbox("Model", ["gpt-4-turbo", "gpt-3.5-turbo"], index=0)

# Sample Notes dropdown
sample_notes = [note["note"] for note in CLINICAL_NOTES]
selected_note = st.selectbox("Or choose sample note:", ["Enter custom note..."] + sample_notes)

# Input
note = st.text_area("Clinical Note:", height=200, 
                   value=selected_note if selected_note != "Enter custom note..." else "")

# Processing
if st.button("Generate Codes") and api_key and note:
    # Initialize client with API key
    client = OpenAI(api_key=api_key)
    
    # System prompt with medical coding rules
    system_prompt = """
    You are a medical coding specialist. Extract ONLY valid ICD-10 and CPT codes from clinical notes.
    Return JSON format: {"icd10": ["code1", "code2"], "cpt": ["code3", "code4"]}
    Rules:
    1. Use only official codes
    2. Never invent codes - return empty if uncertain
    3. Prioritize most specific codes
    4. Include all relevant codes
    """
    
    with st.spinner("🔍 Analyzing medical documentation..."):
        try:
            # Updated API call for OpenAI v1.x
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"CLINICAL NOTE:\n{note}\n\nJSON OUTPUT:"}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}  # Ensure JSON output
            )
            
            # Parse response
            output = response.choices[0].message.content.strip()
            codes = json.loads(output)
            
            # Display
            st.success("✅ Codes Generated")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("ICD-10 Codes")
                for code in codes.get("icd10", []):
                    st.code(code, language="none")
                    
            with col2:
                st.subheader("CPT Codes")
                for code in codes.get("cpt", []):
                    st.code(code, language="none")
            
            # Export
            st.download_button("📥 Download Claim", 
                               json.dumps(codes, indent=2), 
                               "medical_claim.json")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.text("Raw API Response:")
            st.text(output if 'output' in locals() else "No response")

st.info("💡 Tip: For best results, include assessment/diagnosis and procedures performed")