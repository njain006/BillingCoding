import streamlit as st
from openai import OpenAI
import json

# ----------------------------
# App Configuration
# ----------------------------
st.set_page_config(page_title="MedCoder AI", page_icon="🩺")
st.title("🩺 MedCoder AI: Auto-Medical Coding")
st.caption("Generate accurate ICD-10 & CPT codes from clinical documentation.")

# ----------------------------
# Sample Notes
# ----------------------------
CLINICAL_NOTES = [
    {
        "note": "55yo male with type 2 diabetes presenting for routine follow-up. HbA1c 7.2%. Continued on metformin 1000mg BID. Discussed dietary modifications.",
        "icd10": ["E11.9"], "cpt": ["99213"]
    },
    {
        "note": "28yo female with acute streptococcal pharyngitis. Rapid strep positive. Prescribed penicillin VK 500mg TID x10 days. Advised symptomatic management.",
        "icd10": ["J02.0"], "cpt": ["99203", "87880"]
    },
    {
        "note": "72yo female with left hip osteoarthritis. Significant pain with ambulation. Scheduled for left total hip arthroplasty next month. Prescribed meloxicam 15mg daily.",
        "icd10": ["M16.12"], "cpt": ["99214", "73552"]
    },
    {
        "note": "6yo male with acute asthma exacerbation. Wheezing and tachypnea present. Administered albuterol nebulizer in office with improvement. Started on prednisolone.",
        "icd10": ["J45.901"], "cpt": ["99213", "94640"]
    },
    {
        "note": "Annual wellness visit for 42yo female. No new complaints. Review of systems negative. Mammogram scheduled. Vaccinations up-to-date.",
        "icd10": ["Z00.00"], "cpt": ["99396"]
    }
]

# ----------------------------
# Sidebar API Config
# ----------------------------
st.sidebar.header("🔐 API Settings")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")
model = st.sidebar.selectbox("OpenAI Model", ["gpt-4-turbo", "gpt-3.5-turbo"], index=0)

# ----------------------------
# User Input
# ----------------------------
sample_options = ["Enter custom note..."] + [item["note"] for item in CLINICAL_NOTES]
selected_note = st.selectbox("📋 Choose or enter a clinical note", sample_options)

note_input = st.text_area(
    label="✍️ Clinical Note Input",
    height=200,
    value=selected_note if selected_note != "Enter custom note..." else ""
)

# ----------------------------
# System Prompt Template
# ----------------------------
system_prompt = """
You are a certified medical coding specialist. Your task is to extract valid ICD-10 and CPT codes from a given clinical note.

Output must follow this exact JSON format:
{
  "icd10": ["code1", "code2"],
  "cpt": ["code3", "code4"]
}

Rules:
1. Use only official and valid codes.
2. Do NOT hallucinate codes—return empty arrays only if nothing is clearly stated or implied.
3. Be specific and accurate.
4. Include multiple relevant codes if necessary, even for standard visit procedures.
"""

# ----------------------------
# Code Generation Function
# ----------------------------
def get_medical_codes(note: str, key: str, model: str) -> dict:
    client = OpenAI(api_key=key)
    response = client.chat.completions.create(
        model=model,
        temperature=0.4,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"CLINICAL NOTE:\n{note}\n\nJSON OUTPUT:"}
        ]
    )
    return json.loads(response.choices[0].message.content.strip())

# ----------------------------
# Trigger & Display
# ----------------------------
if st.button("🚀 Generate Codes"):
    if not api_key:
        st.warning("Please enter your OpenAI API Key.")
    elif not note_input.strip():
        st.warning("Please enter a clinical note.")
    else:
        with st.spinner("🔍 Analyzing the clinical note..."):
            try:
                result = get_medical_codes(note_input, api_key, model)
                st.success("✅ Medical codes generated successfully!")

                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("ICD-10 Codes")
                    for icd in result.get("icd10", []):
                        st.code(icd, language="none")

                with col2:
                    st.subheader("CPT Codes")
                    for cpt in result.get("cpt", []):
                        st.code(cpt, language="none")

                st.download_button("📥 Download as JSON", json.dumps(result, indent=2), "medical_claim.json")

            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.text("⚠️ Could not parse output. Check your API key or prompt formatting.")

# ----------------------------
# Help Sections
# ----------------------------
with st.expander("ℹ️ Tips for Best Results"):
    st.markdown("""
    - Clearly describe diagnoses, medications, and procedures.
    - Use standard clinical terminology.
    - Include patient context (e.g., age, follow-up, acute issue).
    """)

with st.expander("🧾 Sample Output Format"):
    st.json({"icd10": ["E11.9"], "cpt": ["99213"]})
