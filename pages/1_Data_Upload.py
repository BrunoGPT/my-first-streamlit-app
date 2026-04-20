import csv
import re
from io import BytesIO, StringIO
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

# =========================================================
# PAGE STYLE
# =========================================================

st.set_page_config(page_title="Data Upload", layout="wide")

st.markdown(
    """
    <style>
    .main {
        padding-top: 1.2rem;
    }

    h1, h2, h3 {
        color: #1f2a44;
        font-weight: 700;
    }

    .soft-box {
        background-color: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 16px;
    }

    .summary-card {
        background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
        border: 1px solid #dbe7f3;
        border-radius: 14px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        min-height: 110px;
    }

    .summary-label {
        font-size: 0.95rem;
        color: #475569;
        margin-bottom: 8px;
    }

    .summary-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e3a5f;
    }

    .section-title {
        margin-top: 1.2rem;
        margin-bottom: 0.5rem;
        font-size: 1.35rem;
        font-weight: 700;
        color: #1f2a44;
    }

    .small-note {
        color: #64748b;
        font-size: 0.95rem;
        margin-top: -6px;
        margin-bottom: 18px;
    }

    div.stButton > button {
        border-radius: 10px;
        border: 1px solid #d1d5db;
        padding: 0.55rem 1rem;
        font-weight: 600;
    }

    div.stDownloadButton > button {
        border-radius: 10px;
        border: 1px solid #d1d5db;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }

    div[data-testid="stMetric"] {
        background-color: #f8fafc;
        border: 1px solid #e5e7eb;
        padding: 14px;
        border-radius: 12px;
    }

    hr {
        margin-top: 1.2rem;
        margin-bottom: 1.2rem;
    }

    .preview-caption {
        font-size: 0.95rem;
        color: #5f6b7a;
        margin: 0.2rem 0 0.6rem 0;
    }

    .preview-table-wrap {
        max-height: 430px;
        overflow: auto;
        border: 1px solid #e5e7eb;
        border-radius: 0.8rem;
        background: #ffffff;
    }

    .preview-table-wrap table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.92rem;
    }

    .preview-table-wrap thead th {
        position: sticky;
        top: 0;
        background: #f8fafc;
        z-index: 1;
    }

    .preview-table-wrap th,
    .preview-table-wrap td {
        border: 1px solid #e5e7eb;
        padding: 0.45rem 0.6rem;
        text-align: left;
        white-space: nowrap;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# PAGE SETUP
# =========================================================

st.title("Data Upload")
st.markdown(
    """
    <div class="small-note">
    Upload the GNPS Integral Table and the metadata table, choose the preprocessing
    steps you want to apply, and run the processing.
    </div>
    """,
    unsafe_allow_html=True,
)

BASE_DIR = Path(__file__).resolve().parent.parent
INTEGRAL_HELP_PATH = BASE_DIR / "Assets" / "Integral_table.png"
LIBRARY_HELP_PATH = BASE_DIR / "Assets" / "Library.png"
METADATA_HELP_PATH = BASE_DIR / "Assets" / "metadata_print.png"
EXAMPLE_DATA_DIR = BASE_DIR / "example_data"
MODEL_INTEGRAL_PATH = EXAMPLE_DATA_DIR / "Model_Integral_Table.xlsx"
MODEL_METADATA_PATH = EXAMPLE_DATA_DIR / "Model_Metadata.xlsx"
MODEL_LIBRARY_PATH = EXAMPLE_DATA_DIR / "Model_Library.xlsx"

# =========================================================
# CONSTANTS AND PATTERNS
# =========================================================

NON_ALNUM_PATTERN = re.compile(r"[^a-z0-9]+")
RTS_PATTERN = re.compile(r"^\s*([0-9]+(?:[.,][0-9]+)?)\s*\(([\d]+(?:[.,][\d]+)?)%\)\s*$")

FILENAME_CANDIDATES = [
    "filename",
    "file_name",
    "samplefile",
    "sample_file",
    "samplefilename",
    "sample_filename",
    "name",
]

SAMPLETYPE_CANDIDATES = [
    "attribute_sampletype",
    "sampletype",
    "sample_type",
    "type",
    "class",
    "sampleclass",
]

LIBRARY_OUTPUT_COLUMNS = [
    "#Scan#",
    "RT_Query",
    "MQScore",
    "Compound_Name",
    "npclassifier_superclass",
    "npclassifier_class",
    "npclassifier_pathway",
    "Kovats_Index_calculated",
    "Balance_score(percentage)",
]

LIBRARY_NUMERIC_COLUMNS = {
    "#Scan#": "int",
    "RT_Query": "float",
    "MQScore": "float",
    "Kovats_Index_calculated": "float",
    "Balance_score(percentage)": "float",
}

# =========================================================
# HELPERS
# =========================================================


def normalize_text(value):
    if value is None:
        return ""
    return str(value).strip().lower()



def normalize_key(value):
    if value is None:
        return ""

    text = str(value).strip().strip('"').strip("'")
    if text == "":
        return ""

    text = text.replace("\\", "/").split("/")[-1]
    text = Path(text).stem
    text = text.lower().strip()
    text = NON_ALNUM_PATTERN.sub("", text)
    return text



def normalize_header_key(value):
    return NON_ALNUM_PATTERN.sub("", normalize_text(value))



def to_number(value):
    if value is None:
        return np.nan

    if isinstance(value, bool):
        return np.nan

    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)

    text = str(value).strip()
    if text == "":
        return np.nan

    text = text.replace(" ", "")

    if text.endswith("%"):
        text = text[:-1]

    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        text = text.replace(",", ".")

    try:
        return float(text)
    except ValueError:
        return np.nan



def split_rts_value(value):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return np.nan, np.nan

    text = str(value).strip()
    match = RTS_PATTERN.match(text)
    if match:
        rt_min = float(match.group(1).replace(",", "."))
        balance_score = float(match.group(2).replace(",", "."))
        return rt_min, balance_score

    number = to_number(value)
    return number, np.nan



def normalize_scan_key(value):
    number = to_number(value)

    if pd.notna(number):
        if float(number).is_integer():
            return str(int(number))
        return format(float(number), ".15g")

    text = str(value).strip() if value is not None else ""
    return text



def to_percentage_number(value):
    number = to_number(value)
    if pd.isna(number):
        return np.nan

    if 0 <= number <= 1:
        return number * 100.0

    return number



def coerce_library_numeric_value(value, kind):
    number = to_number(value)
    if pd.isna(number):
        return np.nan

    if kind == "int":
        return int(round(number))
    return float(number)



def keep_integer_if_whole(value):
    if isinstance(value, float) and np.isfinite(value) and float(value).is_integer():
        return int(value)
    return value



def decode_uploaded_text(uploaded_file):
    raw_bytes = uploaded_file.getvalue()
    encodings = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]

    last_error = None
    for encoding in encodings:
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError as error:
            last_error = error

    raise ValueError(f"Could not decode file '{uploaded_file.name}'.") from last_error



def detect_uploaded_delimiter(uploaded_file, text):
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix == ".tsv":
        return "\t"

    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters="\t,;")
        return dialect.delimiter
    except csv.Error:
        return "\t"



def read_feature_table(uploaded_file):
    suffix = Path(uploaded_file.name).suffix.lower()
    uploaded_file.seek(0)

    if suffix in [".xlsx", ".xls"]:
        raw_df = pd.read_excel(uploaded_file, header=None, engine="openpyxl")
    else:
        raw_df = pd.read_csv(uploaded_file, header=None, sep=None, engine="python")

    transposed = raw_df.T.reset_index(drop=True)

    if transposed.empty:
        raise ValueError("The GNPS Integral Table is empty.")

    header = transposed.iloc[0].tolist()
    data = transposed.iloc[1:].reset_index(drop=True)
    data.columns = header
    data.columns = [str(col).strip() for col in data.columns]

    remove_names = {"Rel. Max Integral:", "Sample\\Best Order:"}
    keep_columns = [col for col in data.columns if col not in remove_names]
    data = data[keep_columns].copy()

    if "RTS:" in data.columns:
        rt_values = data["RTS:"].apply(split_rts_value)
        data["RT_min"] = rt_values.apply(lambda x: x[0])
        data["Balance_score"] = rt_values.apply(lambda x: x[1])
        data = data.drop(columns=["RTS:"])

    if "Balance_score" in data.columns:
        data["Balance_score"] = pd.to_numeric(data["Balance_score"], errors="coerce")

    if "RT_min" in data.columns:
        data["RT_min"] = pd.to_numeric(data["RT_min"], errors="coerce")

    return data



def read_metadata_table(uploaded_file):
    suffix = Path(uploaded_file.name).suffix.lower()
    uploaded_file.seek(0)

    if suffix in [".xlsx", ".xls"]:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    else:
        df = pd.read_csv(uploaded_file, sep=None, engine="python")

    if df.empty:
        raise ValueError("The metadata table is empty.")

    df.columns = [str(col).strip() for col in df.columns]
    return df



def read_library_search_table(uploaded_file):
    suffix = Path(uploaded_file.name).suffix.lower()
    uploaded_file.seek(0)

    if suffix in [".xlsx", ".xls"]:
        df = pd.read_excel(uploaded_file, engine="openpyxl", dtype=object)
    else:
        text = decode_uploaded_text(uploaded_file)
        delimiter = detect_uploaded_delimiter(uploaded_file, text)
        df = pd.read_csv(StringIO(text), sep=delimiter, dtype=object)

    if df.empty:
        raise ValueError("The Library Search file is empty.")

    df.columns = [str(col).strip() for col in df.columns]

    header_map = {normalize_header_key(col): col for col in df.columns}
    selected_columns = []
    for required_col in LIBRARY_OUTPUT_COLUMNS:
        normalized_name = normalize_header_key(required_col)
        matched_col = header_map.get(normalized_name)
        if matched_col is None:
            raise ValueError(f'Column "{required_col}" was not found in the Library Search file.')
        selected_columns.append(matched_col)

    out = df[selected_columns].copy()
    out.columns = LIBRARY_OUTPUT_COLUMNS

    for col_name, kind in LIBRARY_NUMERIC_COLUMNS.items():
        out[col_name] = out[col_name].apply(lambda value: coerce_library_numeric_value(value, kind))

    out["Balance_score(percentage)"] = out["Balance_score(percentage)"].apply(keep_integer_if_whole)

    return out



def find_best_column(columns, candidates):
    normalized = {normalize_header_key(col): col for col in columns}
    for candidate in candidates:
        if candidate in normalized:
            return normalized[candidate]

    for norm_col, original_col in normalized.items():
        for candidate in candidates:
            if candidate in norm_col:
                return original_col

    return None



def classify_sample_type(value):
    text = normalize_text(value)

    if any(token in text for token in ["blank", "blk"]):
        return "blank"

    if any(token in text for token in ["sample", "specimen", "treatment", "case"]):
        return "sample"

    if any(token in text for token in ["pool", "qc", "quality", "control", "std", "standard"]):
        return "other"

    return "unknown"



def match_feature_columns_to_metadata(feature_df, metadata_df):
    filename_col = find_best_column(metadata_df.columns, FILENAME_CANDIDATES)
    sampletype_col = find_best_column(metadata_df.columns, SAMPLETYPE_CANDIDATES)

    if filename_col is None:
        filename_col = metadata_df.columns[0]

    if sampletype_col is None:
        raise ValueError(
            "Could not identify the sample type column in the metadata table. "
            "Please make sure it contains something like 'ATTRIBUTE_sampletype'."
        )

    metadata_map = {}
    for _, row in metadata_df.iterrows():
        file_key = normalize_key(row[filename_col])
        sample_type = classify_sample_type(row[sampletype_col])

        if file_key != "":
            metadata_map[file_key] = sample_type

    sample_cols = []
    blank_cols = []
    other_cols = []
    unknown_cols = []

    for col in feature_df.columns:
        col_key = normalize_key(col)

        if col_key == "":
            continue

        if col_key in metadata_map:
            matched_type = metadata_map[col_key]
        else:
            matched_type = None
            for meta_key, meta_type in metadata_map.items():
                if meta_key and (meta_key in col_key or col_key in meta_key):
                    matched_type = meta_type
                    break

        if matched_type == "sample":
            sample_cols.append(col)
        elif matched_type == "blank":
            blank_cols.append(col)
        elif matched_type == "other":
            other_cols.append(col)
        else:
            unknown_cols.append(col)

    return sample_cols, blank_cols, other_cols, unknown_cols, filename_col, sampletype_col



def build_feature_column_metadata_map(feature_columns, metadata_df, filename_col):
    metadata_rows = []
    metadata_exact_map = {}

    for _, row in metadata_df.iterrows():
        file_key = normalize_key(row[filename_col])
        if file_key != "":
            row_dict = row.to_dict()
            metadata_rows.append((file_key, row_dict))
            metadata_exact_map[file_key] = row_dict

    column_metadata_map = {}

    for col in feature_columns:
        col_key = normalize_key(col)
        if col_key == "":
            continue

        matched_row = metadata_exact_map.get(col_key)

        if matched_row is None:
            for meta_key, row_dict in metadata_rows:
                if meta_key and (meta_key in col_key or col_key in meta_key):
                    matched_row = row_dict
                    break

        if matched_row is not None:
            column_metadata_map[col] = matched_row

    return column_metadata_map



def coerce_numeric_columns(df, columns):
    out = df.copy()
    for col in columns:
        out[col] = out[col].apply(to_number)
    return out



def add_blank_metrics(df, sample_cols, blank_cols):
    out = df.copy()
    numeric_cols = sample_cols + blank_cols
    out = coerce_numeric_columns(out, numeric_cols)

    if sample_cols:
        out["Sample_mean"] = out[sample_cols].mean(axis=1, skipna=True)
    else:
        out["Sample_mean"] = np.nan

    if blank_cols:
        out["Blank_mean"] = out[blank_cols].mean(axis=1, skipna=True)
    else:
        out["Blank_mean"] = 0.0

    ratio = []
    for _, row in out.iterrows():
        sample_mean = row["Sample_mean"]
        blank_mean = row["Blank_mean"]

        if pd.isna(sample_mean) or sample_mean <= 0:
            if pd.isna(blank_mean) or blank_mean <= 0:
                ratio.append(np.nan)
            else:
                ratio.append(np.inf)
        else:
            ratio.append(blank_mean / sample_mean)

    out["Ratio"] = ratio
    return out



def apply_blank_removal(df, cutoff):
    if "Ratio" not in df.columns:
        return df.copy()

    keep_mask = (df["Ratio"].isna()) | (df["Ratio"] <= cutoff)
    return df[keep_mask].copy()



def apply_balance_filter(df, threshold):
    if "Balance_score" not in df.columns:
        return df.copy()

    out = df.copy()
    out["Balance_score"] = pd.to_numeric(out["Balance_score"], errors="coerce")
    return out[out["Balance_score"] >= threshold].copy()



def apply_attribute_occurrence_filter(df, sample_cols, column_metadata_map, attribute_col, min_count):
    subgroup_to_columns = {}

    for col in sample_cols:
        row_dict = column_metadata_map.get(col)
        if row_dict is None:
            continue

        subgroup_value = row_dict.get(attribute_col)
        subgroup_text = str(subgroup_value).strip() if subgroup_value is not None else ""

        if subgroup_text == "" or subgroup_text.lower() == "nan":
            continue

        subgroup_to_columns.setdefault(subgroup_text, []).append(col)

    if not subgroup_to_columns:
        return df.copy(), {}, 0

    numeric_df = coerce_numeric_columns(df, sample_cols)
    keep_mask = []

    for _, row in numeric_df.iterrows():
        keep_feature = False

        for subgroup_cols in subgroup_to_columns.values():
            present_count = int(((row[subgroup_cols] > 0) & row[subgroup_cols].notna()).sum())
            if present_count >= min_count:
                keep_feature = True
                break

        keep_mask.append(keep_feature)

    keep_mask = pd.Series(keep_mask, index=df.index)
    filtered_df = df.loc[keep_mask].copy()
    removed_count = int((~keep_mask).sum())
    subgroup_sizes = {group_name: len(cols) for group_name, cols in subgroup_to_columns.items()}

    return filtered_df, subgroup_sizes, removed_count



def calculate_missing_percentage(df, sample_cols):
    if not sample_cols:
        return 0.0

    temp = df[sample_cols].copy()
    for col in sample_cols:
        temp[col] = temp[col].apply(to_number)

    missing_mask = temp.isna() | (temp <= 0)

    if missing_mask.size == 0:
        return 0.0

    return float(missing_mask.to_numpy().mean() * 100.0)



def find_lowest_positive_value(df, columns):
    lowest = None

    for col in columns:
        series = df[col].apply(to_number)
        positives = series[series > 0]

        if not positives.empty:
            col_min = positives.min()
            if lowest is None or col_min < lowest:
                lowest = col_min

    return lowest



def impute_missing_values(df, sample_cols, fallback_tables=None, seed=42):
    out = df.copy()
    fallback_tables = fallback_tables or []
    rng = np.random.default_rng(seed)

    reference_value = find_lowest_positive_value(out, sample_cols)

    if reference_value is None:
        for fallback_df in fallback_tables:
            reference_value = find_lowest_positive_value(fallback_df, sample_cols)
            if reference_value is not None:
                break

    if reference_value is None or reference_value <= 0:
        return out, None, 0

    imputed_count = 0

    for col in sample_cols:
        numeric_col = out[col].apply(to_number)
        missing_mask = numeric_col.isna() | (numeric_col <= 0)
        n_missing = int(missing_mask.sum())

        if n_missing > 0:
            random_values = rng.uniform(1e-9, 1.0 - 1e-9, size=n_missing) * reference_value
            numeric_col.loc[missing_mask] = random_values
            imputed_count += n_missing

        out[col] = numeric_col

    return out, reference_value, imputed_count



def apply_tic_normalization(df, sample_cols):
    out = df.copy()
    out = coerce_numeric_columns(out, sample_cols)

    for col in sample_cols:
        column_sum = out[col].sum(skipna=True)
        if pd.notna(column_sum) and column_sum > 0:
            out[col] = (out[col] / column_sum) * 100

    return out



def apply_center_scaling(df, sample_cols):
    out = df.copy()
    out = coerce_numeric_columns(out, sample_cols)

    values = out[sample_cols].copy()
    row_means = values.mean(axis=1, skipna=True)
    row_stds = values.std(axis=1, skipna=True, ddof=0).replace(0, np.nan)

    centered_scaled = values.sub(row_means, axis=0).div(row_stds, axis=0)
    centered_scaled = centered_scaled.fillna(0)

    out[sample_cols] = centered_scaled
    return out



def apply_normalization(df, sample_cols, method):
    method_clean = normalize_text(method)

    if method_clean in ["", "none"]:
        return df.copy(), "None"

    if method_clean == "tic":
        return apply_tic_normalization(df, sample_cols), "TIC"

    if method_clean in ["center scaling", "center-scaling", "centerscaling"]:
        return apply_center_scaling(df, sample_cols), "Center scaling"

    return df.copy(), "None"



def format_balance_score(value):
    number = to_number(value)
    if pd.isna(number):
        return ""
    return f"{int(round(number))}%"



def format_ratio_value(value):
    number = to_number(value)
    if pd.isna(number):
        return ""
    if np.isinf(number):
        return "inf"
    return f"{number:.4f}"



def build_features_blank_output(df, sample_cols, blank_cols):
    preferred = [col for col in ["No:", "RT_min", "Balance_score"] if col in df.columns]
    metrics = [col for col in ["Blank_mean", "Sample_mean", "Ratio"] if col in df.columns]
    ordered_cols = preferred + metrics + blank_cols + sample_cols
    ordered_cols = [col for col in ordered_cols if col in df.columns]
    return df[ordered_cols].copy()



def build_features_sample_output(df, sample_cols):
    preferred = [col for col in ["No:", "RT_min", "Balance_score"] if col in df.columns]
    metrics = [col for col in ["Blank_mean", "Sample_mean", "Ratio"] if col in df.columns]
    ordered_cols = preferred + metrics + sample_cols
    ordered_cols = [col for col in ordered_cols if col in df.columns]
    return df[ordered_cols].copy()



def extract_scan_key_set(df):
    if df.empty:
        return set()

    scan_col = None
    for candidate in ["No:", "#Scan#"]:
        if candidate in df.columns:
            scan_col = candidate
            break

    if scan_col is None:
        first_col = df.columns[0] if len(df.columns) > 0 else None
        raise ValueError(
            "The scan column was not found in the expected first position. "
            f"Expected 'No:' or '#Scan#', but found '{first_col}'."
        )

    scan_keys = set()
    for value in df[scan_col]:
        key = normalize_scan_key(value)
        if key != "":
            scan_keys.add(key)

    return scan_keys



def build_annotation_tables(
    library_df,
    sample_scan_keys,
    balance_scan_keys,
    attribute_scan_keys,
    apply_balance_filter_to_annotation=False,
    balance_threshold=None,
):
    all_features_clean_df = library_df.copy()

    scan_keys_series = library_df["#Scan#"].apply(normalize_scan_key)
    features_after_blank_removal_df = library_df.loc[scan_keys_series.isin(sample_scan_keys)].copy()

    balance_mask = scan_keys_series.isin(balance_scan_keys)
    attribute_mask = scan_keys_series.isin(attribute_scan_keys)

    if apply_balance_filter_to_annotation and balance_threshold is not None:
        annotation_balance_series = pd.to_numeric(
            library_df["Balance_score(percentage)"].apply(to_percentage_number),
            errors="coerce",
        )
        balance_mask = balance_mask & (annotation_balance_series >= balance_threshold)
        attribute_mask = attribute_mask & (annotation_balance_series >= balance_threshold)

    features_after_balance_filter_df = library_df.loc[balance_mask].copy()
    features_after_attribute_filter_df = library_df.loc[attribute_mask].copy()

    return {
        "all_features_clean_df": all_features_clean_df,
        "features_after_blank_removal_df": features_after_blank_removal_df,
        "features_after_balance_filter_df": features_after_balance_filter_df,
        "features_after_attribute_filter_df": features_after_attribute_filter_df,
        "n_all_features_clean": len(all_features_clean_df),
        "n_annotation_after_blank": len(features_after_blank_removal_df),
        "n_annotation_after_balance": len(features_after_balance_filter_df),
        "n_annotation_after_attribute": len(features_after_attribute_filter_df),
        "n_sample_scan_keys": len(sample_scan_keys),
        "n_balance_scan_keys": len(balance_scan_keys),
        "n_attribute_scan_keys": len(attribute_scan_keys),
    }



def format_for_display_or_export(df):
    out = df.copy()

    if "Balance_score" in out.columns:
        out["Balance_score"] = out["Balance_score"].apply(format_balance_score)

    if "Ratio" in out.columns:
        out["Ratio"] = out["Ratio"].apply(format_ratio_value)

    return out



def render_preview_table(
    df: pd.DataFrame,
    max_rows: int = 50,
    height: int = 430,
    preview_label: str = "Preview shown below (first 50 rows).",
):
    display_df = format_for_display_or_export(df).head(max_rows)
    st.markdown(f"<div class='preview-caption'>{preview_label}</div>", unsafe_allow_html=True)
    html_table = display_df.to_html(index=False, escape=False)
    st.markdown(
        f"<div class='preview-table-wrap' style='max-height:{height}px'>{html_table}</div>",
        unsafe_allow_html=True,
    )



def dataframe_to_csv_bytes(df):
    export_df = format_for_display_or_export(df)
    return export_df.to_csv(index=False).encode("utf-8")



def dataframes_to_excel_bytes(sheet_map):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, df in sheet_map.items():
            safe_name = re.sub(r"[\\/*?:\[\]]", "_", str(sheet_name))[:31]
            export_df = format_for_display_or_export(df)
            export_df.to_excel(writer, sheet_name=safe_name, index=False)

    output.seek(0)
    return output.getvalue()



def process_tables(
    feature_file,
    metadata_file,
    blank_cutoff,
    balance_threshold,
    do_blank_removal,
    do_balance_filter,
    do_attribute_filter,
    attribute_filter_column,
    attribute_filter_min_count,
    do_imputation,
    do_normalization,
    normalization_method,
    library_search_file=None,
    do_annotation=False,
):
    feature_df = read_feature_table(feature_file)
    metadata_df = read_metadata_table(metadata_file)

    sample_cols, blank_cols, other_cols, unknown_cols, filename_col, sampletype_col = (
        match_feature_columns_to_metadata(feature_df, metadata_df)
    )
    sample_column_metadata_map = build_feature_column_metadata_map(sample_cols, metadata_df, filename_col)

    if not sample_cols:
        raise ValueError(
            "No sample columns were identified. Please check the metadata and the GNPS Integral Table column names."
        )

    enriched_df = add_blank_metrics(feature_df, sample_cols, blank_cols)

    after_blank_df = enriched_df.copy()
    removed_by_blank_df = enriched_df.iloc[0:0].copy()
    blank_removal_message = None

    if do_blank_removal:
        if blank_cols:
            ratio_numeric = pd.to_numeric(after_blank_df["Ratio"], errors="coerce")
            keep_mask = ratio_numeric.isna() | (ratio_numeric <= blank_cutoff)
            after_blank_df = after_blank_df.loc[keep_mask].copy()
            removed_by_blank_df = enriched_df.loc[~keep_mask].copy()
        else:
            blank_removal_message = (
                "Blank removal was requested, but no blank columns were identified. "
                "The step was skipped."
            )

    features_blank_df = build_features_blank_output(removed_by_blank_df, sample_cols, blank_cols)
    features_sample_before_balance_df = build_features_sample_output(after_blank_df, sample_cols)

    after_balance_df = after_blank_df.copy()
    if do_balance_filter:
        after_balance_df = apply_balance_filter(after_balance_df, balance_threshold)

    features_sample_after_balance_df = build_features_sample_output(after_balance_df, sample_cols)

    after_attribute_df = after_balance_df.copy()
    attribute_filter_message = None
    attribute_subgroup_sizes = {}
    removed_by_attribute_count = 0

    if do_attribute_filter:
        if attribute_filter_column is None or attribute_filter_column not in metadata_df.columns:
            attribute_filter_message = (
                "Attribute occurrence filtering was requested, but no valid metadata attribute was selected. "
                "The step was skipped."
            )
        else:
            after_attribute_df, attribute_subgroup_sizes, removed_by_attribute_count = apply_attribute_occurrence_filter(
                after_balance_df,
                sample_cols,
                sample_column_metadata_map,
                attribute_filter_column,
                attribute_filter_min_count,
            )

            if not attribute_subgroup_sizes:
                attribute_filter_message = (
                    "Attribute occurrence filtering was requested, but no subgroup values were found for the selected "
                    "metadata attribute among the identified sample columns. The step was skipped."
                )
                after_attribute_df = after_balance_df.copy()
                removed_by_attribute_count = 0

    features_sample_after_attribute_df = build_features_sample_output(after_attribute_df, sample_cols)

    missing_percentage = calculate_missing_percentage(after_attribute_df, sample_cols)

    imputed_df = after_attribute_df.copy()
    imputation_reference = None
    imputed_count = 0
    imputation_message = None

    if do_imputation:
        fallback_tables = [after_attribute_df, after_balance_df, after_blank_df, enriched_df]
        imputed_df, imputation_reference, imputed_count = impute_missing_values(
            after_attribute_df,
            sample_cols,
            fallback_tables=fallback_tables,
            seed=42,
        )

        if imputation_reference is None:
            imputation_message = (
                "Imputation was requested, but no positive values were found in the processed "
                "sample columns. The imputation step was skipped."
            )

    features_sample_imputed_df = build_features_sample_output(imputed_df, sample_cols)

    normalized_df = imputed_df.copy()
    normalization_method_applied = "None"

    if do_normalization:
        normalized_df, normalization_method_applied = apply_normalization(
            imputed_df,
            sample_cols,
            normalization_method,
        )

    features_sample_normalized_df = build_features_sample_output(normalized_df, sample_cols)

    annotation_results = {
        "annotation_requested": do_annotation,
        "annotation_generated": False,
        "annotation_message": None,
        "library_search_filename": library_search_file.name if library_search_file is not None else None,
        "all_features_clean_df": pd.DataFrame(columns=LIBRARY_OUTPUT_COLUMNS),
        "features_after_blank_removal_df": pd.DataFrame(columns=LIBRARY_OUTPUT_COLUMNS),
        "features_after_balance_filter_df": pd.DataFrame(columns=LIBRARY_OUTPUT_COLUMNS),
        "features_after_attribute_filter_df": pd.DataFrame(columns=LIBRARY_OUTPUT_COLUMNS),
        "n_all_features_clean": 0,
        "n_annotation_after_blank": 0,
        "n_annotation_after_balance": 0,
        "n_annotation_after_attribute": 0,
        "n_sample_scan_keys": 0,
        "n_balance_scan_keys": 0,
        "n_attribute_scan_keys": 0,
    }

    if do_annotation:
        if library_search_file is None:
            annotation_results["annotation_message"] = (
                "Annotation table was requested, but no Library Search file was uploaded. "
                "The step was skipped."
            )
        else:
            try:
                library_df = read_library_search_table(library_search_file)
                sample_scan_keys = extract_scan_key_set(features_sample_before_balance_df)
                balance_scan_keys = extract_scan_key_set(features_sample_after_balance_df)
                attribute_scan_keys = extract_scan_key_set(features_sample_after_attribute_df)

                built_annotation = build_annotation_tables(
                    library_df,
                    sample_scan_keys,
                    balance_scan_keys,
                    attribute_scan_keys,
                    apply_balance_filter_to_annotation=do_balance_filter,
                    balance_threshold=balance_threshold if do_balance_filter else None,
                )

                annotation_results.update(built_annotation)
                annotation_results["annotation_generated"] = True
            except Exception as error:
                annotation_results["annotation_message"] = (
                    f"Annotation table generation failed and was skipped: {error}"
                )

    results = {
        "feature_df": feature_df,
        "metadata_df": metadata_df,
        "sample_cols": sample_cols,
        "blank_cols": blank_cols,
        "other_cols": other_cols,
        "unknown_cols": unknown_cols,
        "filename_col": filename_col,
        "sampletype_col": sampletype_col,
        "features_blank_df": features_blank_df,
        "features_sample_before_balance_df": features_sample_before_balance_df,
        "features_sample_after_balance_df": features_sample_after_balance_df,
        "features_sample_after_attribute_df": features_sample_after_attribute_df,
        "features_sample_imputed_df": features_sample_imputed_df,
        "features_sample_normalized_df": features_sample_normalized_df,
        "missing_percentage": missing_percentage,
        "imputation_reference": imputation_reference,
        "imputed_count": imputed_count,
        "blank_removal_message": blank_removal_message,
        "attribute_filter_message": attribute_filter_message,
        "imputation_message": imputation_message,
        "n_original_features": len(feature_df),
        "n_after_blank": len(after_blank_df),
        "n_blank_features": len(removed_by_blank_df),
        "n_after_balance": len(after_balance_df),
        "n_after_attribute": len(after_attribute_df),
        "removed_by_attribute_count": removed_by_attribute_count,
        "attribute_filter_requested": do_attribute_filter,
        "attribute_filter_column": attribute_filter_column,
        "attribute_filter_min_count": attribute_filter_min_count,
        "attribute_subgroup_sizes": attribute_subgroup_sizes,
        "normalization_method_applied": normalization_method_applied,
        "blank_removal_requested": do_blank_removal,
        "balance_filter_requested": do_balance_filter,
        "imputation_requested": do_imputation,
        "do_normalization": do_normalization,
    }

    results.update(annotation_results)
    return results


# =========================================================
# SESSION STATE
# =========================================================

if "processing_results" not in st.session_state:
    st.session_state["processing_results"] = None

if "use_example_dataset" not in st.session_state:
    st.session_state["use_example_dataset"] = False

# =========================================================
# INPUTS
# =========================================================


def load_example_file(file_path):
    if not file_path.exists():
        raise FileNotFoundError(f"Example file not found: {file_path.name}")

    buffer = BytesIO(file_path.read_bytes())
    buffer.name = file_path.name
    return buffer

upload_col1, upload_col2, upload_col3 = st.columns([1, 1, 1])

with upload_col1:
    feature_file = st.file_uploader(
        "Upload the GNPS Integral Table",
        type=["csv", "xlsx", "xls"],
        key="feature_table_uploader",
    )

with upload_col2:
    metadata_file = st.file_uploader(
        "Upload the metadata table",
        type=["csv", "xlsx", "xls", "txt"],
        key="metadata_table_uploader",
    )

    st.caption(
        "⚠️ If you plan to use blank removal, the metadata table should contain a sample-type column "
        "such as `ATTRIBUTE_sampletype` so the app can distinguish analytical samples from blanks."
    )

with upload_col3:
    library_search_file = st.file_uploader(
        "Upload the Library Search file (optional)",
        type=["csv", "tsv", "txt", "xlsx", "xls"],
        key="library_search_uploader",
        help=(
            "Optional file used to generate annotation tables. The app will look for the columns "
            "#Scan#, RT_Query, MQScore, Compound_Name, npclassifier_superclass, "
            "npclassifier_class, npclassifier_pathway, Kovats_Index_calculated, and "
            "Balance_score(percentage)."
        ),
    )

with st.expander("🔎 Need help finding these files?", expanded=False):
    st.markdown(
        "Use the tabs below for a quick guide to the required and optional input files."
    )

    tab1, tab2, tab3 = st.tabs(
        ["1. GNPS Integral Table", "2. Library-search table", "3. Metadata sheet"]
    )

    with tab1:
        st.markdown("**1. GNPS Integral Table**")
        st.markdown(
            "The GNPS Integral Table is generated after the first step of the GNPS workflow "
            "(**Data Processing - Deconvolution**) is completed."
        )
        st.markdown(
            """
1. Open the results from the **Data Processing / Deconvolution** step in GNPS.  
2. Locate the exported table corresponding to the **integral table** output.  
3. Download that file and upload it here as the main quantitative input table.
            """
        )

        if INTEGRAL_HELP_PATH.exists():
            st.image(
                str(INTEGRAL_HELP_PATH),
                caption="Where to find the GNPS Integral Table",
                use_container_width=True,
            )
        else:
            st.warning("Integral_table.png was not found in the Assets folder.")

    with tab2:
        st.markdown("**2. Library-search table**")
        st.markdown(
            "The library-search table contains the hits returned by the GNPS workflow. "
            "In practice, this corresponds to the **View All Library Hits** output generated "
            "after the second step of the workflow (**Library Search / Networking**)."
        )
        st.markdown(
            """
1. Open the results from the **Library Search / Networking** step in GNPS.  
2. Find the table corresponding to **View All Library Hits**.  
3. Download that file and upload it here only if you want annotation matching.
            """
        )

        if LIBRARY_HELP_PATH.exists():
            st.image(
                str(LIBRARY_HELP_PATH),
                caption="Where to find the library-search table",
                use_container_width=True,
            )
        else:
            st.warning("Library.png was not found in the Assets folder.")

    with tab3:
        st.markdown("**3. Metadata sheet**")
        st.markdown(
            "The metadata sheet describes the samples included in the analysis and should follow "
            "the [GNPS metadata structure](https://ccms-ucsd.github.io/GNPSDocumentation/metadata/)."
        )
        st.markdown(
            "Sample names in the metadata must match the sample columns in the GNPS Integral Table."
        )
        st.markdown(
            """
Typical metadata should include:
- a sample filename column
- sample-type information
- any additional attributes needed for downstream filtering or grouping
            """
        )

        if METADATA_HELP_PATH.exists():
            st.image(
                str(METADATA_HELP_PATH),
                caption="Example of the expected metadata structure",
                use_container_width=True,
            )
        else:
            st.warning("metadata_print.png was not found in the Assets folder.")

st.markdown('<div class="section-title">🧪 Try an example dataset</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="small-note">
    Load a small example dataset to test the preprocessing workflow before uploading your own files.
    </div>
    """,
    unsafe_allow_html=True,
)

example_col1, example_col2 = st.columns([1, 1])

with example_col1:
    if st.button("Load example dataset", key="load_example_dataset"):
        st.session_state["use_example_dataset"] = True

with example_col2:
    if st.session_state["use_example_dataset"]:
        if st.button("Stop using example dataset", key="clear_example_dataset"):
            st.session_state["use_example_dataset"] = False

if st.session_state["use_example_dataset"]:
    missing_example_files = [
        path.name
        for path in [MODEL_INTEGRAL_PATH, MODEL_METADATA_PATH, MODEL_LIBRARY_PATH]
        if not path.exists()
    ]

    if missing_example_files:
        st.error(
            "Example dataset could not be loaded because the following file(s) were not found: "
            + ", ".join(missing_example_files)
        )
        st.session_state["use_example_dataset"] = False
    else:
        st.success(
            "Example dataset is active. The app will use Model_Integral_Table, "
            "Model_Metadata, and Model_Library until you click 'Stop using example dataset'."
        )

        st.markdown("**Preview of the example files**")
        st.caption("Preview only: showing the first 10 rows of each example file.")

        preview_tab1, preview_tab2, preview_tab3 = st.tabs(
            ["GNPS Integral Table", "Metadata", "Library-search table"]
        )

        with preview_tab1:
            integral_preview = pd.read_excel(MODEL_INTEGRAL_PATH)
            st.caption(f"{integral_preview.shape[0]} rows × {integral_preview.shape[1]} columns")
            render_preview_table(integral_preview, max_rows=10, height=320, preview_label="Preview shown below (first 10 rows).")
            st.download_button(
                "Download full GNPS Integral Table",
                data=MODEL_INTEGRAL_PATH.read_bytes(),
                file_name=MODEL_INTEGRAL_PATH.name,
                mime="application/octet-stream",
                key="download_example_integral",
            )

        with preview_tab2:
            metadata_preview = pd.read_excel(MODEL_METADATA_PATH)
            st.caption(f"{metadata_preview.shape[0]} rows × {metadata_preview.shape[1]} columns")
            render_preview_table(metadata_preview, max_rows=10, height=320, preview_label="Preview shown below (first 10 rows).")
            st.download_button(
                "Download full metadata table",
                data=MODEL_METADATA_PATH.read_bytes(),
                file_name=MODEL_METADATA_PATH.name,
                mime="application/octet-stream",
                key="download_example_metadata",
            )

        with preview_tab3:
            library_preview = pd.read_excel(MODEL_LIBRARY_PATH)
            st.caption(f"{library_preview.shape[0]} rows × {library_preview.shape[1]} columns")
            render_preview_table(library_preview, max_rows=10, height=320, preview_label="Preview shown below (first 10 rows).")
            st.download_button(
                "Download full library-search table",
                data=MODEL_LIBRARY_PATH.read_bytes(),
                file_name=MODEL_LIBRARY_PATH.name,
                mime="application/octet-stream",
                key="download_example_library",
            )

st.markdown('<div class="section-title">Processing options</div>', unsafe_allow_html=True)

opt1, opt2, opt3, opt4, opt5, opt6 = st.columns(6)

with opt1:
    do_blank_removal = st.checkbox(
        "Blank removal",
        value=False,
        help="Removes features whose blank-to-sample ratio is above the selected cutoff.",
    )

with opt2:
    do_balance_filter = st.checkbox(
        "Balance filter",
        value=False,
        help="Keeps only features whose Balance_score is at or above the selected threshold.",
    )

with opt3:
    do_attribute_filter = st.checkbox(
        "Attribute filter",
        value=False,
        help=(
            "Keeps only features that are present in at least the selected number of samples within at least "
            "one subgroup of the chosen metadata attribute. This step runs before imputation."
        ),
    )

with opt4:
    do_imputation = st.checkbox(
        "Imputation",
        value=False,
        help=(
            "Replaces missing or zero values in the processed sample table with random values below the lowest "
            "observed positive value."
        ),
    )

with opt5:
    do_normalization = st.checkbox(
        "Normalization",
        value=False,
        help="Applies the selected normalization method to the processed sample table.",
    )

with opt6:
    do_annotation = st.checkbox(
        "Annotation",
        value=False,
        help=(
            "Matches scan IDs from the processed GNPS Integral Table outputs against the optional Library Search file and "
            "returns the matching identifications."
        ),
    )

blank_cutoff = 0.30
balance_threshold = 65
attribute_filter_column = None
attribute_filter_min_count = 3
normalization_method = "None"

if do_blank_removal:
    st.number_input(
        "Cutoff threshold for blank removal",
        min_value=0.0,
        max_value=1.0,
        value=0.30,
        step=0.05,
        format="%.2f",
        key="blank_cutoff_input",
        help="Features with blank/sample ratio above this value are removed from the sample table.",
    )
    blank_cutoff = st.session_state["blank_cutoff_input"]

if do_balance_filter:
    st.number_input(
        "Minimum balance score (%)",
        min_value=0,
        max_value=100,
        value=65,
        step=1,
        key="balance_threshold_input",
        help="Only features with Balance_score greater than or equal to this value are kept.",
    )
    balance_threshold = st.session_state["balance_threshold_input"]

if do_attribute_filter:
    metadata_attribute_options = []
    if metadata_file is not None:
        try:
            metadata_preview_df = read_metadata_table(metadata_file)
            metadata_attribute_options = list(metadata_preview_df.columns)
        except Exception:
            metadata_attribute_options = []

    if metadata_attribute_options:
        attribute_filter_column = st.selectbox(
            "Metadata attribute",
            options=metadata_attribute_options,
            index=0,
            key="attribute_filter_column_select",
            help="Choose the metadata column whose subgroup levels will be used to count feature occurrence.",
        )
    else:
        st.info("Upload a valid metadata table to choose the attribute occurrence filter column.")

    st.number_input(
        "Minimum detections within a subgroup",
        min_value=1,
        value=3,
        step=1,
        key="attribute_filter_min_count_input",
        help=(
            "A feature is kept if it is present in at least this number of samples within at least one subgroup "
            "of the selected metadata attribute. Presence is defined using the pre-imputation values."
        ),
    )
    attribute_filter_min_count = st.session_state["attribute_filter_min_count_input"]

if do_annotation:
    if do_balance_filter:
        st.caption(
            f"The annotation step matches the scan IDs from the processed GNPS Integral Table outputs against the "
            f"Library Search file and applies the same balance cutoff used in the Balance filter ({balance_threshold}%). "
            "Multiple matches per feature are preserved as separate rows."
        )
    else:
        st.caption(
            "The annotation step matches the scan IDs from the processed GNPS Integral Table outputs against the "
            "Library Search file and returns all matching identifications without applying a Library Search balance cutoff. "
            "Multiple matches per feature are preserved as separate rows."
        )

if do_normalization:
    normalization_method = st.selectbox(
        "Normalization method",
        options=["None", "TIC", "Center scaling"],
        index=0,
        key="normalization_method_select",
        help="Select how the processed sample table should be normalized after imputation.",
    )

st.write("")
run_processing = st.button("Run processing")

# =========================================================
# PROCESSING
# =========================================================

if run_processing:
    active_feature_file = feature_file
    active_metadata_file = metadata_file
    active_library_search_file = library_search_file

    if st.session_state["use_example_dataset"]:
        try:
            active_feature_file = load_example_file(MODEL_INTEGRAL_PATH)
            active_metadata_file = load_example_file(MODEL_METADATA_PATH)
            active_library_search_file = load_example_file(MODEL_LIBRARY_PATH)
        except FileNotFoundError as error:
            st.session_state["processing_results"] = None
            st.error(str(error))
            st.stop()

    if active_feature_file is None or active_metadata_file is None:
        st.warning("Please upload both the GNPS Integral Table and the metadata table, or load the example dataset.")
    else:
        try:
            results = process_tables(
                feature_file=active_feature_file,
                metadata_file=active_metadata_file,
                blank_cutoff=blank_cutoff,
                balance_threshold=balance_threshold,
                do_blank_removal=do_blank_removal,
                do_balance_filter=do_balance_filter,
                do_attribute_filter=do_attribute_filter,
                attribute_filter_column=attribute_filter_column,
                attribute_filter_min_count=attribute_filter_min_count,
                do_imputation=do_imputation,
                do_normalization=do_normalization,
                normalization_method=normalization_method,
                library_search_file=active_library_search_file,
                do_annotation=do_annotation,
            )
            st.session_state["processing_results"] = results
            st.success("Processing completed successfully!")

        except Exception as error:
            st.session_state["processing_results"] = None
            st.error(f"Processing failed: {error}")

# =========================================================
# RESULTS
# =========================================================

results = st.session_state["processing_results"]

if results is None:
    required_inputs_ready = (
        (feature_file is not None and metadata_file is not None)
        or st.session_state["use_example_dataset"]
    )

    if required_inputs_ready:
        st.success("Required files loaded. Ready to run preprocessing.")
    else:
        st.info("Upload both tables or load the example dataset, choose the processing steps, and click 'Run processing'.")
else:
    st.markdown("---")

    if results["blank_removal_message"]:
        st.warning(results["blank_removal_message"])

    if results["attribute_filter_message"]:
        st.warning(results["attribute_filter_message"])

    if results["imputation_message"]:
        st.warning(results["imputation_message"])

    if results["annotation_message"]:
        st.warning(results["annotation_message"])

    st.markdown('<div class="section-title">Processing summary</div>', unsafe_allow_html=True)

    summary_items = [
        ("Original features", results["n_original_features"]),
        ("Blank features", results["n_blank_features"]),
        ("After blank removal", results["n_after_blank"]),
        ("After balance score filter", results["n_after_balance"]),
    ]

    if results["attribute_filter_requested"]:
        summary_items.append(("After attribute filter", results["n_after_attribute"]))

    summary_columns = st.columns(len(summary_items))

    for column, (label, value) in zip(summary_columns, summary_items):
        with column:
            st.markdown(
                f"""
                <div class="summary-card">
                    <div class="summary-label">{label}</div>
                    <div class="summary-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")

    with st.container(border=True):
        st.write("**Column classification summary**")
        st.markdown(f"- Sample columns identified: **{len(results['sample_cols'])}**")
        st.markdown(f"- Blank columns identified: **{len(results['blank_cols'])}**")
        st.markdown(f"- Other/control columns identified: **{len(results['other_cols'])}**")
        st.markdown(f"- Unmatched columns: **{len(results['unknown_cols'])}**")

    if results["attribute_filter_requested"]:
        with st.container(border=True):
            st.write("**Attribute occurrence filter summary**")
            st.markdown(f"- Metadata attribute used: **{results['attribute_filter_column']}**")
            st.markdown(f"- Minimum detections required: **{results['attribute_filter_min_count']}**")
            st.markdown(f"- Features before attribute filter: **{results['n_after_balance']}**")
            st.markdown(f"- Features after attribute filter: **{results['n_after_attribute']}**")
            st.markdown(f"- Features removed by attribute filter: **{results['removed_by_attribute_count']}**")
            if results["attribute_subgroup_sizes"]:
                subgroup_text = ", ".join(
                    f"{group_name} ({group_size})"
                    for group_name, group_size in sorted(results["attribute_subgroup_sizes"].items())
                )
                st.markdown(f"- Subgroups used: **{subgroup_text}**")

    if results["imputation_requested"]:
        with st.container(border=True):
            st.write("**Imputation summary**")
            st.markdown(
                f"- Missing values in processed sample table: **{results['missing_percentage']:.1f}%**"
            )

            if results["imputation_reference"] is not None:
                st.markdown(
                    f"- Lowest positive value used for imputation: **{results['imputation_reference']:.6g}**"
                )
            else:
                st.markdown("- Lowest positive value used for imputation: **not available**")

            st.markdown(f"- Number of imputed values: **{results['imputed_count']}**")

    if results["do_normalization"]:
        with st.container(border=True):
            st.write("**Normalization summary**")
            st.markdown(
                f"- Normalization method applied: **{results['normalization_method_applied']}**"
            )

    if results["annotation_requested"]:
        with st.container(border=True):
            st.write("**Annotation summary**")
            st.markdown(
                f"- Library Search file: **{results['library_search_filename'] or 'not provided'}**"
            )
            st.markdown(
                f"- Sample scans used for matching: **{results['n_sample_scan_keys']}**"
            )
            st.markdown(
                f"- Balance-filtered scans used for matching: **{results['n_balance_scan_keys']}**"
            )
            if results["attribute_filter_requested"]:
                st.markdown(
                    f"- Attribute-filtered scans used for matching: **{results['n_attribute_scan_keys']}**"
                )
            st.markdown(
                f"- Rows in all_features_clean: **{results['n_all_features_clean']}**"
            )
            st.markdown(
                f"- Rows in features_after_blank_removal: **{results['n_annotation_after_blank']}**"
            )
            st.markdown(
                f"- Rows in features_after_balance_filter: **{results['n_annotation_after_balance']}**"
            )
            if results["attribute_filter_requested"]:
                st.markdown(
                    f"- Rows in features_after_attribute_filter: **{results['n_annotation_after_attribute']}**"
                )

    st.markdown("---")
    st.markdown('<div class="section-title">Output tables</div>', unsafe_allow_html=True)

    workbook_sheets = {
        "Provided_GNPS_Integral_Table": results["feature_df"],
        "Metadata": results["metadata_df"],
        "Blank_Features": results["features_blank_df"],
        "Sample_Features": results["features_sample_before_balance_df"],
        "Sample_features_Balance": results["features_sample_after_balance_df"],
    }

    if results["attribute_filter_requested"]:
        workbook_sheets["Sample_features_Attribute"] = results["features_sample_after_attribute_df"]

    if results["imputation_reference"] is not None:
        workbook_sheets["Sample_features_imputed"] = results["features_sample_imputed_df"]

    if results["do_normalization"]:
        workbook_sheets["Sample_features_normalized"] = results["features_sample_normalized_df"]

    if results["annotation_generated"]:
        workbook_sheets["Annotation_All_Features"] = results["all_features_clean_df"]
        workbook_sheets["Annotation_After_Blank"] = results["features_after_blank_removal_df"]
        workbook_sheets["Annotation_After_Balance"] = results["features_after_balance_filter_df"]
        if results["attribute_filter_requested"]:
            workbook_sheets["Annotation_After_Attribute"] = results["features_after_attribute_filter_df"]

    with st.expander("Feature-blank table", expanded=False):
        st.write(
            "Features removed by the blank-removal cutoff. These are the features that do not remain in the feature-sample table after the blank-removal step."
        )

        if results["features_blank_df"].empty:
            st.info(
                "No features were assigned to the feature-blank table with the current blank-removal settings."
            )
        else:
            render_preview_table(results["features_blank_df"], max_rows=50, height=430)

        st.download_button(
            "Download feature-blank table (CSV)",
            data=dataframe_to_csv_bytes(results["features_blank_df"]),
            file_name="integral_blank_table.csv",
            mime="text/csv",
            key="download_feature_blank",
        )

    with st.expander("Feature-sample table after blank removal", expanded=False):
        st.write("Preview of the processed sample table before the balance score filter.")
        render_preview_table(results["features_sample_before_balance_df"], max_rows=50, height=430)
        st.download_button(
            "Download feature-sample table after blank removal (CSV)",
            data=dataframe_to_csv_bytes(results["features_sample_before_balance_df"]),
            file_name="integral_sample_after_blank_removal.csv",
            mime="text/csv",
            key="download_feature_sample_before_balance",
        )

    with st.expander("Feature-sample table after balance score filter", expanded=False):
        st.write("Preview of the processed sample table after the balance score filter.")
        render_preview_table(results["features_sample_after_balance_df"], max_rows=50, height=430)
        st.download_button(
            "Download feature-sample table after balance score filter (CSV)",
            data=dataframe_to_csv_bytes(results["features_sample_after_balance_df"]),
            file_name="integral_sample_after_balance_filter.csv",
            mime="text/csv",
            key="download_feature_sample_after_balance",
        )

    if results["attribute_filter_requested"]:
        with st.expander("Feature-sample table after attribute occurrence filter", expanded=False):
            st.write(
                "Preview of the processed sample table after applying the metadata-driven subgroup occurrence filter and before imputation."
            )
            render_preview_table(results["features_sample_after_attribute_df"], max_rows=50, height=430)
            st.download_button(
                "Download feature-sample table after attribute occurrence filter (CSV)",
                data=dataframe_to_csv_bytes(results["features_sample_after_attribute_df"]),
                file_name="integral_sample_after_attribute_filter.csv",
                mime="text/csv",
                key="download_feature_sample_after_attribute",
            )

    if results["imputation_requested"]:
        with st.expander("Feature-sample table after imputation", expanded=False):
            st.write("Preview of the processed sample table after imputation.")
            render_preview_table(results["features_sample_imputed_df"], max_rows=50, height=430)
            st.download_button(
                "Download feature-sample table after imputation (CSV)",
                data=dataframe_to_csv_bytes(results["features_sample_imputed_df"]),
                file_name="integral_sample_after_imputation.csv",
                mime="text/csv",
                key="download_feature_sample_imputed",
            )

    if results["do_normalization"]:
        with st.expander("Feature-sample table after normalization", expanded=False):
            st.write("Preview of the processed sample table after normalization.")
            render_preview_table(results["features_sample_normalized_df"], max_rows=50, height=430)
            st.download_button(
                "Download feature-sample table after normalization (CSV)",
                data=dataframe_to_csv_bytes(results["features_sample_normalized_df"]),
                file_name="integral_sample_after_normalization.csv",
                mime="text/csv",
                key="download_feature_sample_normalized",
            )

    if results["annotation_requested"]:
        with st.expander("Annotation table: all library matches", expanded=False):
            st.write(
                "This table contains the selected columns from the Library Search file, preserving all identifications."
            )

            if results["all_features_clean_df"].empty:
                st.info("No annotation rows are available.")
            else:
                render_preview_table(results["all_features_clean_df"], max_rows=50, height=430)

            st.download_button(
                "Download annotation table: all library matches (CSV)",
                data=dataframe_to_csv_bytes(results["all_features_clean_df"]),
                file_name="annotation_all_features_clean.csv",
                mime="text/csv",
                key="download_annotation_all",
            )

        with st.expander("Annotation table after blank removal", expanded=False):
            st.write(
                "Library Search matches whose #Scan# values are present in the feature-sample table after blank removal. Multiple matches per feature are retained."
            )

            if results["features_after_blank_removal_df"].empty:
                st.info("No annotation rows matched the feature-sample table after blank removal.")
            else:
                render_preview_table(results["features_after_blank_removal_df"], max_rows=50, height=430)

            st.download_button(
                "Download annotation table after blank removal (CSV)",
                data=dataframe_to_csv_bytes(results["features_after_blank_removal_df"]),
                file_name="annotation_after_blank_removal.csv",
                mime="text/csv",
                key="download_annotation_after_blank",
            )

        with st.expander("Annotation table after balance score filter", expanded=False):
            if results["balance_filter_requested"]:
                st.write(
                    "Library Search matches whose #Scan# values are present in the balance-filtered GNPS Integral Table. The same balance cutoff used in the Balance filter is applied to the library matches as well. Multiple matches per entry are retained."
                )
            else:
                st.write(
                    "Library Search matches whose #Scan# values are present in the processed GNPS Integral Table at this step. No Library Search balance cutoff is applied because the Balance filter is disabled. Multiple matches per entry are retained."
                )

            if results["features_after_balance_filter_df"].empty:
                st.info("No annotation rows matched the balance-filtered GNPS Integral Table with the current settings.")
            else:
                render_preview_table(results["features_after_balance_filter_df"], max_rows=50, height=430)

            st.download_button(
                "Download annotation table after balance score filter (CSV)",
                data=dataframe_to_csv_bytes(results["features_after_balance_filter_df"]),
                file_name="annotation_after_balance_filter.csv",
                mime="text/csv",
                key="download_annotation_after_balance",
            )

        if results["attribute_filter_requested"]:
            with st.expander("Annotation table after attribute occurrence filter", expanded=False):
                if results["balance_filter_requested"]:
                    st.write(
                        "Library Search matches whose #Scan# values are present in the attribute-filtered GNPS Integral Table. The same balance cutoff used in the Balance filter is applied to the library matches as well. Multiple matches per entry are retained."
                    )
                else:
                    st.write(
                        "Library Search matches whose #Scan# values are present in the attribute-filtered GNPS Integral Table. No Library Search balance cutoff is applied because the Balance filter is disabled. Multiple matches per entry are retained."
                    )

                if results["features_after_attribute_filter_df"].empty:
                    st.info("No annotation rows matched the attribute-filtered GNPS Integral Table with the current settings.")
                else:
                    render_preview_table(results["features_after_attribute_filter_df"], max_rows=50, height=430)

                st.download_button(
                    "Download annotation table after attribute occurrence filter (CSV)",
                    data=dataframe_to_csv_bytes(results["features_after_attribute_filter_df"]),
                    file_name="annotation_after_attribute_filter.csv",
                    mime="text/csv",
                    key="download_annotation_after_attribute",
                )

    st.download_button(
        "Download all output tables (.xlsx)",
        data=dataframes_to_excel_bytes(workbook_sheets),
        file_name="all_output_tables.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_all_output_tables_excel",
    )




