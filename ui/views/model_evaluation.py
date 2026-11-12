"""
Classical ML Dataset & Model Evaluation View
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
from core.ml.evaluator import ModelEvaluator
from ui.components import render_kpi_card

def render_model_evaluation_view():
    st.markdown("## Dataset & Classical Model Evaluation")
    st.markdown("Empirical benchmarking of supervised classical machine learning models (Logistic Regression, Linear SVM) with genuine telemetry.")

    st.markdown(
        """
        <div style="background-color: #EEF2FF; border: 1px solid #C7D2FE; border-radius: 6px; padding: 12px 16px; margin-bottom: 16px;">
            <span style="font-weight: 600; color: #3730A3;">Deterministic Classical ML Guarantee:</span>
            <span style="font-size: 13px; color: #4338CA;">
                This module operates solely with classical statistical classifiers (Scikit-Learn). 
                Zero deep learning, LLMs, or pre-trained generative AI models are utilized. All metrics are computed strictly from empirical cross-validation.
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. Dataset Management Panel
    st.markdown("#### 1. Dataset Management & Validation")
    data_source = st.radio("Dataset Source:", ["Load Bundled Benchmark Dataset (40 Samples)", "Upload Labeled CSV Dataset"], horizontal=True)

    df: pd.DataFrame = None

    if data_source == "Load Bundled Benchmark Dataset (40 Samples)":
        csv_path = "data/benchmark_dataset.csv"
        df = pd.read_csv(csv_path)
        st.caption(f"Loaded bundled benchmark dataset with **{len(df)} samples** (Columns: {list(df.columns)})")
    else:
        uploaded_csv = st.file_uploader("Upload Labeled Candidate CSV (requires text and label columns):", type=["csv"], key="ml_dataset_uploader")
        if uploaded_csv is not None:
            df = pd.read_csv(uploaded_csv)
            st.caption(f"Uploaded dataset with **{len(df)} rows**.")

    if df is None or len(df) == 0:
        st.info("Please load or upload a dataset to begin model benchmarking.")
        return

    # Dataset Preview
    with st.expander("Preview Dataset Records", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)

    # Column Mapping
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        text_column = st.selectbox("Text / Feature Column:", options=list(df.columns), index=1 if "text" in df.columns else 0)
    with col_c2:
        label_column = st.selectbox("Target Label Column:", options=list(df.columns), index=2 if "label" in df.columns else (1 if len(df.columns) > 1 else 0))
    with col_c3:
        test_split = st.slider("Test Split Proportion:", min_value=0.15, max_value=0.40, value=0.25, step=0.05)

    # 2. Model Selection & Training
    st.markdown("---")
    st.markdown("#### 2. Classical Classifier Benchmark")
    
    col_m1, col_m2 = st.columns([2, 1])
    with col_m1:
        model_choice = st.selectbox(
            "Select Classical Model Architecture:",
            ["Logistic Regression (L2 Regularized)", "Linear Support Vector Classifier (LinearSVC)"]
        )
        model_key = "linear_svm" if "Support Vector" in model_choice else "logistic_regression"

    with col_m2:
        st.write("") # Spacer
        train_btn = st.button("Train & Evaluate Model", type="primary", use_container_width=True)

    if train_btn:
        with st.spinner("Vectorizing text via TF-IDF and training classical classifier..."):
            try:
                evaluator = ModelEvaluator(model_type=model_key, test_size=test_split, random_state=42)
                eval_results = evaluator.train_and_evaluate(df, text_col=text_column, label_col=label_column)
                st.session_state["active_ml_evaluation"] = eval_results
                st.success("Model training and validation completed successfully.")
            except Exception as e:
                st.error(f"Model evaluation error: {str(e)}")

    # 3. Telemetry & Metrics Display
    eval_data = st.session_state.get("active_ml_evaluation")
    if eval_data:
        st.markdown("---")
        st.markdown("#### 3. Empirical Performance Telemetry")

        m = eval_data["metrics"]
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            render_kpi_card("Accuracy", f"{m['accuracy']}%", f"{eval_data['test_size']} test samples", "positive" if m['accuracy'] >= 75 else "neutral")
        with k2:
            render_kpi_card("Precision (Weighted)", f"{m['precision']}%", "Positive predictive value", "positive")
        with k3:
            render_kpi_card("Recall (Weighted)", f"{m['recall']}%", "True positive rate", "positive")
        with k4:
            render_kpi_card("F1-Score", f"{m['f1_score']}%", "Harmonic mean", "positive")

        # Visualizations Split: Confusion Matrix Heatmap vs Top TF-IDF Feature Coefficients
        col_cm, col_coef = st.columns([1, 1])

        with col_cm:
            st.markdown("##### 2x2 Confusion Matrix Heatmap")
            cm = np.array(eval_data["confusion_matrix"])
            classes = [str(c) for c in eval_data["classes"]]
            
            fig_cm = px.imshow(
                cm,
                text_auto=True,
                labels=dict(x="Predicted Class", y="Actual Class", color="Count"),
                x=classes,
                y=classes,
                color_continuous_scale="Blues"
            )
            fig_cm.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_cm, use_container_width=True)

        with col_coef:
            st.markdown("##### Top Feature Coefficients / TF-IDF Word Importance")
            top_pos = eval_data.get("top_positive_features", [])
            if top_pos:
                feat_df = pd.DataFrame(top_pos, columns=["N-Gram Token", "Coefficient"]).sort_values("Coefficient", ascending=True)
                fig_coef = px.bar(
                    feat_df,
                    x="Coefficient",
                    y="N-Gram Token",
                    orientation='h',
                    color_discrete_sequence=["#4F46E5"]
                )
                fig_coef.update_layout(
                    height=300,
                    margin=dict(l=20, r=20, t=10, b=20),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig_coef, use_container_width=True)
            else:
                st.info("Feature coefficients not directly available for this model configuration.")

        # Detailed Classification Report
        st.markdown("##### Detailed Classification Report")
        report_dict = eval_data.get("classification_report", {})
        report_rows = []
        for class_label, stats in report_dict.items():
            if isinstance(stats, dict):
                report_rows.append({
                    "Class": class_label,
                    "Precision": f"{round(stats.get('precision', 0) * 100, 1)}%",
                    "Recall": f"{round(stats.get('recall', 0) * 100, 1)}%",
                    "F1-Score": f"{round(stats.get('f1-score', 0) * 100, 1)}%",
                    "Support": int(stats.get("support", 0))
                })
        st.dataframe(pd.DataFrame(report_rows), use_container_width=True, hide_index=True)
