# Realize - Graphical Representations & Process Diagrams

## 1. System Pipeline Architecture

```mermaid
flowchart TD
    subgraph Input_Sources [Input Sources]
        A1[Candidate Resumes: PDF / DOCX]
        A2[Job Description: Text / PDF / DOCX]
    end

    subgraph Document_Parser [Parser & Preprocessing Engine]
        B1[PyMuPDF / docx Text Ingestion]
        B2[Regex Header Segmenter]
        B3[NLTK Normalizer & Tokenizer]
    end

    subgraph Feature_Extractors [Deterministic Feature Extractors]
        C1[Skill Taxonomy Matcher & Alias Mapper]
        C2[TF-IDF N-Gram Vectorizer & Cosine Similarity]
        C3[Chronological Date Interval Merger]
        C4[Tiered Degree & Major Evaluator]
        C5[Project Keyword & Responsibility Matcher]
    end

    subgraph Scoring_Core [Explainable Scoring Core]
        D1[Composite Weight Aggregator]
        D2[Missing Section Re-normalizer]
        D3[Mathematical Trace & Evidence Builder]
    end

    subgraph User_Interface [Realize Multi-Page UI]
        E1[Dashboard KPI Grid & Distributions]
        E2[Candidate Deep Dive & Evidence View]
        E3[Bulk Screening Matrix & CSV Export]
        E4[Plotly Radar & Factor Comparison]
        E5[ReportLab Downloadable PDF Generator]
    end

    A1 --> B1
    A2 --> B1
    B1 --> B2
    B2 --> B3
    B3 --> C1
    B3 --> C2
    B3 --> C3
    B3 --> C4
    B3 --> C5
    C1 --> D1
    C2 --> D1
    C3 --> D1
    C4 --> D1
    C5 --> D1
    D1 --> D2
    D2 --> D3
    D3 --> E1
    D3 --> E2
    D3 --> E3
    D3 --> E4
    D3 --> E5
```

---

## 2. Chronological Date Interval Coalescing Flow

```mermaid
flowchart LR
    A[Raw Date Strings: 'Jan 2020 - Mar 2022', 'Dec 2021 - Present'] --> B[Convert to Normalized Date Intervals: [Start, End]]
    B --> C[Sort Intervals by Start Date]
    C --> D{Does Interval i Overlap with Interval i-1?}
    D -- Yes --> E[Merge Intervals: [Start_prev, max(End_prev, End_curr)]]
    D -- No --> F[Append as Distinct Tenure Interval]
    E --> G[Sum Total Elapsed Non-overlapping Months]
    F --> G
    G --> H[Convert to Total Verified Experience Years]
```

---

## 3. Dynamic Re-normalization Decision Tree

```mermaid
flowchart TD
    Start[Calculate Component Scores] --> Check{Any Component Flagged Missing?}
    Check -- No --> Normal[Apply Standard Configured Weights: Sum = 100%]
    Check -- Yes --> Renorm[Remove Missing Dimension from Active Set A]
    Renorm --> Recalc[Compute Scale Factor: 1.0 / Sum(w_active)]
    Recalc --> Scale[Scale Remaining Active Weights: w_new = w_old * Factor]
    Scale --> Warn[Flag Incomplete Assessment with Confidence Metric]
    Normal --> Finish[Emit Final Composite Score & Full Audit Trace]
    Warn --> Finish
```

---

## 4. Multi-Page Navigation Wireframe Hierarchy

```mermaid
graph LR
    Root[Realize Enterprise Navigation]
    Root --> P1[1. Executive Analytics Dashboard]
    Root --> P2[2. Single Resume Analysis Workspace]
    Root --> P3[3. Bulk Resume Screening & Ranking]
    Root --> P4[4. Candidate Comparison Matrix]
    Root --> P5[5. Skills Taxonomy & Demand Analytics]
    Root --> P6[6. Executive Evaluation Reports - PDF Export]
    Root --> P7[7. Classical ML Dataset & Model Evaluation]
    Root --> P8[8. System Configuration & Weight Tuning]
```
