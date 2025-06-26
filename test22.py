# main.py - Updated with Collapsible Job Description Input
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
    if "minimize_input" not in st.session_state:
        st.session_state.minimize_input = False

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

        # Add minimize toggle in sidebar
        st.markdown("---")
        if st.checkbox("📝 Minimize Job Input", value=st.session_state.minimize_input):
            st.session_state.minimize_input = True
        else:
            st.session_state.minimize_input = False

    # Dynamic layout based on whether input is minimized
    if not st.session_state.minimize_input or not st.session_state.job_description:
        # Full input mode - show large input area
        col1, col2 = st.columns([1.2, 1])

        with col1:
            st.header("📋 Job Description Input")
            job_description = st.text_area(
                "Paste the complete job description here:",
                value=st.session_state.job_description,
                height=400,
                placeholder="Copy and paste your job description here..."
            )

            # Update session state
            st.session_state.job_description = job_description

            # Validation
            if job_description:
                word_count = len(job_description.split())
                st.caption(f"📊 Word count: {word_count}")

                if word_count < 20:
                    st.warning("⚠️ Job description seems short. Consider adding more details for better analysis.")

                # Auto-minimize suggestion after pasting
                if word_count > 50 and not st.session_state.minimize_input:
                    st.info(
                        "💡 **Tip:** You can minimize this input section from the sidebar to get more space for results!")

            # Action buttons
            col_btn1, col_btn2, col_btn3 = st.columns(3)

            with col_btn1:
                analyze_btn = st.button("🔍 Analyze JD", use_container_width=True, type="primary")

            with col_btn2:
                boolean_btn = st.button("🔎 Generate Boolean", use_container_width=True)

            with col_btn3:
                tech_btn = st.button("⚙️ Explain Tech", use_container_width=True)

        with col2:
            st.header("📊 Results")
            results_container = st.container()

    else:
        # Minimized input mode - show compact header with action buttons
        st.header("📋 Job Description")

        # Compact job description display
        with st.expander("📝 View/Edit Job Description", expanded=False):
            job_description = st.text_area(
                "Job Description:",
                value=st.session_state.job_description,
                height=200,
                help="Expand to edit the job description"
            )
            st.session_state.job_description = job_description

            if job_description:
                word_count = len(job_description.split())
                st.caption(f"📊 Word count: {word_count}")

        # Action buttons in a single row
        st.markdown("### 🔧 Analysis Tools")
        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)

        with col_btn1:
            analyze_btn = st.button("🔍 Analyze JD", use_container_width=True, type="primary")

        with col_btn2:
            boolean_btn = st.button("🔎 Generate Boolean", use_container_width=True)

        with col_btn3:
            tech_btn = st.button("⚙️ Explain Tech", use_container_width=True)

        with col_btn4:
            if st.button("📝 Show Input", use_container_width=True):
                st.session_state.minimize_input = False
                st.rerun()

        # Full width results section
        st.markdown("---")
        st.header("📊 Analysis Results")
        results_container = st.container()
        job_description = st.session_state.job_description

    # Processing logic (same for both layouts)
    with results_container:
        # Job Description Analysis
        if analyze_btn:
            if not job_description.strip():
                st.error("❌ Please enter a job description first!")
            else:
                with st.spinner("🤖 Analyzing job description..."):
                    result = analyze_job_description(job_description)
                    st.session_state.results["analysis"] = result

                if "❌" not in result["summary"]:
                    st.success("✅ Analysis Complete!")

                    # Auto-minimize after successful analysis
                    if not st.session_state.minimize_input:
                        st.session_state.minimize_input = True
                        st.rerun()

                    # Show quick stats
                    if result["structured_data"]:
                        data = result["structured_data"]
                        col_stat1, col_stat2 = st.columns(2)

                        with col_stat1:
                            st.metric("Must-Have Skills", len(data.get("must_have_skills", [])))

                        with col_stat2:
                            st.metric("Nice-to-Have Skills", len(data.get("nice_to_have_skills", [])))
                else:
                    st.error("Analysis failed. Please check your API key and try again.")

        # Display analysis results
        if "analysis" in st.session_state.results:
            with st.expander("📋 Job Analysis Results", expanded=True):
                st.markdown(st.session_state.results["analysis"]["summary"])

        # Boolean Query Generation
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

                    # Auto-minimize after successful generation
                    if not st.session_state.minimize_input:
                        st.session_state.minimize_input = True
                        st.rerun()
                else:
                    st.error("Boolean generation failed. Please try again.")

        # Display boolean results
        if "boolean" in st.session_state.results:
            with st.expander("🔎 Boolean Search Queries", expanded=True):
                st.markdown(st.session_state.results["boolean"]["boolean_string"])

                # Show individual queries if available
                if "multiple_queries" in st.session_state.results["boolean"]:
                    queries = st.session_state.results["boolean"]["multiple_queries"]
                    if queries:
                        st.markdown("**Quick Copy:**")
                        for query_type, data in queries.items():
                            if data.get("query"):
                                st.code(data["query"], language="text")

        # Technology Explanations
        if tech_btn:
            if not job_description.strip():
                st.error("❌ Please enter a job description first!")
            else:
                with st.spinner("⚙️ Analyzing technologies..."):
                    result = explain_technologies(job_description)
                    st.session_state.results["technologies"] = result

                if "❌" not in result["explanations"]:
                    st.success("✅ Technology Analysis Complete!")

                    # Auto-minimize after successful analysis
                    if not st.session_state.minimize_input:
                        st.session_state.minimize_input = True
                        st.rerun()

                    # Show tech count
                    if result["tech_list"]:
                        st.metric("Technologies Found", len(result["tech_list"]))
                else:
                    st.error("Technology analysis failed. Please try again.")

        # Display technology results
        if "technologies" in st.session_state.results:
            with st.expander("⚙️ Technology Explanations", expanded=True):
                st.markdown(st.session_state.results["technologies"]["explanations"])

    # Export Section (always full width)
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

    # Footer
    st.markdown("---")
    st.markdown("*🚀 DeepScreen v2.0 - Built with Streamlit & OpenAI GPT-4*")


def compile_all_results():
    """Compile all results into a single text for copying"""
    results = st.session_state.results
    compiled = f"# DeepScreen Analysis Report\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    if "analysis" in results:
        compiled += "## Job Description Analysis\n"
        compiled += f"{results['analysis']['summary']}\n\n"

    if "boolean" in results:
        compiled += "## Boolean Search Queries\n"
        compiled += f"{results['boolean']['boolean_string']}\n\n"

    if "technologies" in results:
        compiled += "## Technology Explanations\n"
        compiled += f"{results['technologies']['explanations']}\n\n"

    return compiled


if __name__ == "__main__":
    main()