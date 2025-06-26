# main.py - Corrected Version
import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
from datetime import datetime

# Import your modules
from AnalyzeJD import analyze_job_description
from GenBool import generate_boolean, generate_simple_boolean
from TechExplainer import explain_technologies

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def main():
    st.set_page_config(
        page_title="DeepScreen - AI Job Analysis",
        page_icon="🧠",
        layout="wide"
    )

    # Header
    st.title("🧠 DeepScreen - AI-Powered Job Analysis")
    st.markdown("*Transform job descriptions into actionable insights for smarter resume screening*")

    # Initialize session state
    if "results" not in st.session_state:
        st.session_state.results = {}
    if "job_description" not in st.session_state:
        st.session_state.job_description = ""

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Analysis Options")

        analysis_mode = st.selectbox(
            "Analysis Mode:",
            ["Standard", "Comprehensive", "Quick"]
        )

        boolean_type = st.selectbox(
            "Boolean Query Type:",
            ["Multiple Strategies", "Simple Query"]
        )

        st.markdown("---")
        st.markdown("**💡 Tips:**")
        st.markdown("- Use 'Comprehensive' for detailed analysis")
        st.markdown("- 'Multiple Strategies' gives you 4 different boolean queries")
        st.markdown("- Export results for team collaboration")

    # Tabs Layout
    tab1, tab2, tab3 = st.tabs(["📋 Job Description", "📄 Summary", "🔍 Boolean Query"])

    with tab1:
        st.subheader("View / Edit Job Description")
        job_description = st.text_area(
            "Paste the complete job description here:",
            value=st.session_state.job_description,
            height=400,
            placeholder="Copy and paste your job description here..."
        )
        st.session_state.job_description = job_description

        if job_description:
            word_count = len(job_description.split())
            st.caption(f"📊 Word count: {word_count}")

            if word_count < 20:
                st.warning("⚠️ Job description seems short. Consider adding more details for better analysis.")

        # Place all buttons in one horizontal row
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            analyze_btn = st.button("🔍 Analyze JD", use_container_width=True, key="analyze_btn")
        with col_btn2:
            boolean_btn = st.button("🔎 Generate Boolean", use_container_width=True, key="boolean_btn")
        with col_btn3:
            tech_btn = st.button("⚙️ Explain Tech", use_container_width=True, key="tech_btn")

        # Processing logic moved immediately after buttons
        if analyze_btn:
            if not job_description.strip():
                st.error("❌ Please enter a job description first!")
            else:
                with st.spinner("🤖 Analyzing job description..."):
                    result = analyze_job_description(job_description)
                    st.session_state.results["analysis"] = result
                if "❌" not in result["summary"]:
                    st.success("✅ Analysis Complete!")
                else:
                    st.error("Analysis failed. Please check your API key and try again.")

        if boolean_btn:
            if not job_description.strip():
                st.error("❌ Please enter a job description first!")
            else:
                with st.spinner("🔎 Generating Boolean queries..."):
                    if boolean_type == "Multiple Strategies":
                        result = generate_boolean(job_description)
                    else:
                        result = generate_simple_boolean(job_description)
                    st.session_state.results["boolean"] = result
                if "❌" not in result["boolean_string"]:
                    st.success("✅ Boolean Queries Generated!")
                else:
                    st.error("Boolean generation failed. Please try again.")

        if tech_btn:
            if not job_description.strip():
                st.error("❌ Please enter a job description first!")
            else:
                with st.spinner("⚙️ Analyzing technologies..."):
                    result = explain_technologies(job_description)
                    st.session_state.results["technologies"] = result
                if "❌" not in result["explanations"]:
                    st.success("✅ Technology Analysis Complete!")
                else:
                    st.error("Technology analysis failed. Please try again.")

        # Show results inline immediately after processing
        if "analysis" in st.session_state.results and st.session_state.results["analysis"]:
            st.markdown("---")
            st.subheader("📄 Analysis Result Preview")
            st.markdown(st.session_state.results["analysis"].get("summary", "No summary available."))

        if "boolean" in st.session_state.results and st.session_state.results["boolean"]:
            st.markdown("---")
            st.subheader("🔍 Boolean Query Preview")
            st.markdown(st.session_state.results["boolean"].get("boolean_string", "No boolean query generated."))

        if "technologies" in st.session_state.results and st.session_state.results["technologies"]:
            st.markdown("---")
            st.subheader("⚙️ Technology Explanations Preview")
            st.markdown(st.session_state.results["technologies"].get("explanations", "No explanation generated."))

    with tab2:
        st.subheader("📄 Job Analysis Results")
        if "analysis" in st.session_state.results:
            st.markdown(st.session_state.results["analysis"].get("summary", "No summary available."))

    with tab3:
        st.subheader("🔍 Boolean Search Queries")
        if "boolean" in st.session_state.results:
            st.markdown(st.session_state.results["boolean"].get("boolean_string", "No boolean query generated."))

            if "multiple_queries" in st.session_state.results["boolean"]:
                queries = st.session_state.results["boolean"]["multiple_queries"]
                if queries:
                    st.markdown("**Quick Copy:**")
                    for query_type, data in queries.items():
                        if data.get("query"):
                            st.code(data["query"], language="text")

    # Export Section
    if st.session_state.results:
        st.markdown("---")
        st.header("📤 Export & Share")

        col_export1, col_export2, col_export3 = st.columns(3)

        with col_export1:
            if st.button("📋 Copy All Results", use_container_width=True):
                all_results = compile_all_results()
                st.text_area("All Results (Copy this):", value=all_results, height=200)

        with col_export2:
            if st.button("💾 Download JSON", use_container_width=True):
                report_data = {
                    "timestamp": datetime.now().isoformat(),
                    "job_description": job_description,
                    "results": st.session_state.results
                }

                st.download_button(
                    "📥 Download Report",
                    data=json.dumps(report_data, indent=2),
                    file_name=f"deepscreen_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json"
                )

        with col_export3:
            st.button("📧 Share Results", disabled=True, help="Coming soon!", use_container_width=True)

    st.markdown("---")
    st.markdown("*🚀 DeepScreen v2.0 - Built with Streamlit & OpenAI GPT-4*")

def compile_all_results():
    results = st.session_state.results
    compiled = f"# DeepScreen Analysis Report\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    if "analysis" in results:
        compiled += "## Job Description Analysis\n"
        compiled += f"{results['analysis'].get('summary', '')}\n\n"

    if "boolean" in results:
        compiled += "## Boolean Search Queries\n"
        compiled += f"{results['boolean'].get('boolean_string', '')}\n\n"

    if "technologies" in results:
        compiled += "## Technology Explanations\n"
        compiled += f"{results['technologies'].get('explanations', '')}\n\n"

    return compiled

if __name__ == "__main__":
    main()
