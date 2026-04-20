from pathlib import Path
import streamlit as st

st.set_page_config(page_title="GCMetaPrep | Home", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "Assets" / "logo.svg"
INTEGRAL_HELP_PATH = BASE_DIR / "Assets" / "Integral_table.png"
LIBRARY_HELP_PATH = BASE_DIR / "Assets" / "Library.png"
METADATA_HELP_PATH = BASE_DIR / "Assets" / "metadata_print.png"

st.markdown(
    """
    <style>
    .main {
        padding-top: 1.2rem;
    }

    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2rem;
        max-width: 980px;
    }

    h1, h2, h3 {
        color: #1f2a44;
        font-weight: 700;
    }

    .section-title {
        margin-top: 1.2rem;
        margin-bottom: 0.45rem;
        font-size: 1.65rem;
        font-weight: 700;
        color: #1f2a44;
    }

    .subsection-title {
        margin-top: 0.9rem;
        margin-bottom: 0.35rem;
        font-size: 1.65rem;
        font-weight: 700;
        color: #1f2a44;
    }

    .plain-text {
        color: #475569;
        font-size: 1rem;
        line-height: 1.75;
    }

    .plain-text a,
    .essentials-card a,
    .callout-note a,
    .attention-note a {
        color: #0f5cc0;
        text-decoration: none;
        font-weight: 600;
    }

    .plain-text a:hover,
    .essentials-card a:hover,
    .callout-note a:hover,
    .attention-note a:hover {
        text-decoration: underline;
    }

    .callout-note {
        margin-top: 0.95rem;
        margin-bottom: 1rem;
        padding: 0.8rem 1rem;
        border-left: 4px solid #2563eb;
        background: #f4f8ff;
        color: #334155;
        border-radius: 8px;
        line-height: 1.65;
    }

    .essentials-card {
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 0.6rem;
        background: #edf4fb;
        border: 1px solid #d7e5f2;
    }

    .essentials-title {
        font-size: 1.03rem;
        font-weight: 700;
        color: #1f2a44;
        margin-bottom: 0.6rem;
    }

    .essentials-card ul {
        margin: 0;
        padding-left: 1.15rem;
        color: #475569;
        line-height: 1.7;
    }

    .essentials-card li {
        margin-bottom: 0.5rem;
    }

    .step-card {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 18px;
        min-height: 120px;
    }

    .step-number {
        display: inline-block;
        width: 30px;
        height: 30px;
        border-radius: 999px;
        background-color: #e8efff;
        color: #1d4ed8;
        font-weight: 700;
        text-align: center;
        line-height: 30px;
        margin-bottom: 10px;
    }

    .step-title {
        font-size: 1.02rem;
        font-weight: 700;
        color: #1f2a44;
        margin-bottom: 6px;
    }

    .step-text {
        font-size: 0.97rem;
        line-height: 1.6;
        color: #475569;
    }

    .attention-note {
        margin-top: 0.75rem;
        padding: 0.9rem 1rem;
        border-left: 4px solid #f59e0b;
        background: #fff8ef;
        color: #7c4a03;
        border-radius: 8px;
        line-height: 1.7;
    }

    .help-text {
        color: #475569;
        font-size: 0.98rem;
        line-height: 1.7;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="
        font-size: 3.8rem;
        font-weight: 700;
        color: #1f2a44;
        margin-top: 1.2rem;
        margin-bottom: 0.8rem;
        line-height: 1.18;
        padding-top: 0.2rem;
    ">
        Welcome to GCMetaPrep
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns([1, 2.4, 1])
with col2:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=700)
    else:
        st.warning("Logo file not found. Check the file name and path in the Assets folder.")

st.markdown('<div class="section-title">About this app</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="plain-text">
        GCMetaPrep is a point-and-click interface for preprocessing <strong>GC-MS metabolomics tables</strong>
        generated from <strong>GNPS workflows</strong>.<br>
        It was designed to make routine preparation steps more accessible.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="subsection-title">What the app does</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="plain-text">
        Load a GNPS Integral Table containing GC-MS metabolomic features together with a metadata table,
        apply selected preprocessing steps, optionally include a library-search table for annotation matching,
        and export processed tables for downstream analysis.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="subsection-title">Recommended before starting</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="plain-text">
        Review the <a href="https://ccms-ucsd.github.io/GNPSDocumentation/gcanalysis/" target="_blank">GNPS GC-MS guide</a>
        to confirm that your input tables follow the expected structure.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-title">📘 Data preparation essentials</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="essentials-card">
        <div class="essentials-title">Required inputs</div>
        <ul>
            <li><strong>Required:</strong> GNPS Integral Table and metadata table</li>
            <li><strong>Optional:</strong> library-search table for annotation matching</li>
            <li>Metadata should follow the expected <a href="https://ccms-ucsd.github.io/GNPSDocumentation/metadata/" target="_blank">GNPS metadata structure</a></li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("🔎 Need help finding these files?"):
    st.markdown(
        """
        <div class="help-text">
            Open the tab corresponding to the file you need help locating.
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["GNPS Integral Table", "Library-search table", "Metadata sheet"])

    with tab1:
        st.markdown("**1. GNPS Integral Table**")
        st.markdown(
            """
            <div class="help-text">
                The GNPS Integral Table is generated after the first step of the GNPS workflow
                (<strong>Data Processing - Deconvolution</strong>) is completed.
            </div>
            """,
            unsafe_allow_html=True,
        )

        if INTEGRAL_HELP_PATH.exists():
            st.image(str(INTEGRAL_HELP_PATH), use_container_width=True)
        else:
            st.info("Integral-table screenshot not found. Check the file name in the Assets folder.")

    with tab2:
        st.markdown("**2. Library-search table**")
        st.markdown(
            """
            <div class="help-text">
                The table containing all hits found by the GNPS workflow is the
                <strong>View All Library Hits</strong> table, generated after the second step of the GNPS workflow
                (<strong>Library Search/Networking</strong>).
            </div>
            """,
            unsafe_allow_html=True,
        )

        if LIBRARY_HELP_PATH.exists():
            st.image(str(LIBRARY_HELP_PATH), use_container_width=True)
        else:
            st.info("Library-table screenshot not found. Check the file name in the Assets folder.")

    with tab3:
        st.markdown("**3. Metadata sheet**")
        st.markdown(
            """
            <div class="help-text">
            The metadata sheet describes the samples included in the analysis and should follow the
            <a href="https://ccms-ucsd.github.io/GNPSDocumentation/metadata/" target="_blank">GNPS metadata structure</a>.<br>
            See an example of the expected metadata structure below:
                </div>
            """,
            unsafe_allow_html=True,
        )

        if METADATA_HELP_PATH.exists():
            st.image(str(METADATA_HELP_PATH), use_container_width=True)
        else:
            st.info("Metadata screenshot not found. Check the file name in the Assets folder.")

st.markdown('<div class="section-title">Workflow overview</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        """
        <div class="step-card">
            <div class="step-number">1</div>
            <div class="step-title">Upload</div>
            <div class="step-text">
                Upload the GNPS Integral Table, metadata table, and optional library-search table.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """
        <div class="step-card">
            <div class="step-number">2</div>
            <div class="step-title">Configure</div>
            <div class="step-text">
                Choose the preprocessing steps needed for your dataset.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        """
        <div class="step-card">
            <div class="step-number">3</div>
            <div class="step-title">Process</div>
            <div class="step-text">
                Run the selected operations and inspect the processed tables.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        """
        <div class="step-card">
            <div class="step-number">4</div>
            <div class="step-title">Download</div>
            <div class="step-text">
                Download the output tables as CSV files or as a single Excel workbook.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="section-title">Outputs</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="plain-text">
        Depending on the selected steps, the app can generate blank-filtered, balance-filtered,
        attribute-filtered, imputed, normalized, and annotation tables.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="callout-note">
        💡 <strong>Next step:</strong> Use the page menu on the left to continue to the data upload and preprocessing workflow.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="attention-note">
        ⚠️ <strong>Please note:</strong>
        <ul>
            <li>GCMetaPrep works on processed tabular outputs and does not replace raw-data processing.</li>
            <li>Filtering, imputation, and normalization choices should be interpreted carefully in the context of the study design.</li>
            <li><strong>We value your feedback.</strong> Suggestions, comments, and issue reports are helpful for improving the app and clarifying the workflow.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True,
)