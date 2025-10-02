import streamlit as st
import pandas as pd
import io

def create_merged_file(df_a, df_b, comparison_result, include_deleted, include_added,
                       include_source_changes, include_translation_changes,
                       include_both_changes):
    """
    사용자 옵션에 따라 병합된 DataFrame을 생성합니다.

    Args:
        df_a: Original/Live DataFrame
        df_b: Modified DataFrame
        comparison_result: compare_dataframes의 결과
        include_deleted: A에만 있는 항목 포함 여부
        include_added: B에만 있는 항목 포함 여부
        include_source_changes: Source 변경 사항 포함 여부 ('use_a', 'use_b', 'skip')
        include_translation_changes: Translation 변경 사항 포함 여부
        include_both_changes: 양쪽 모두 변경된 항목 포함 여부

    Returns:
        Merged DataFrame
    """
    merged_records = []

    # 키 컬럼 설정 (항상 ID + Name)
    key_columns = df_a.columns[:2].tolist()

    # 키 생성
    df_a_copy = df_a.copy()
    df_b_copy = df_b.copy()
    df_a_copy['key'] = df_a_copy[key_columns].astype(str).agg('|'.join, axis=1)
    df_b_copy['key'] = df_b_copy[key_columns].astype(str).agg('|'.join, axis=1)

    # 처리된 키 추적
    processed_keys = set()

    # 1. A에만 있는 항목 (Deleted) - 선택 시 Live 버전 유지
    if include_deleted and not comparison_result['only_in_a'].empty:
        for _, row in comparison_result['only_in_a'].iterrows():
            merged_records.append(row.to_dict())
            # 키 추적 (항상 ID + Name)
            row_copy = row.copy()
            key = '|'.join([str(row_copy[col]) for col in df_a.columns[:2]])
            processed_keys.add(key)

    # 2. B에만 있는 항목 (Added) - 선택 시 Modified 버전 추가
    if include_added and not comparison_result['only_in_b'].empty:
        for _, row in comparison_result['only_in_b'].iterrows():
            merged_records.append(row.to_dict())
            # 키 추적 (항상 ID + Name)
            row_copy = row.copy()
            key = '|'.join([str(row_copy[col]) for col in df_b.columns[:2]])
            processed_keys.add(key)

    # 3. Source 변경 (col3_changes) - Before/After 컬럼을 원래 형식으로 복원
    if include_source_changes != 'skip' and not comparison_result['col3_changes'].empty:
        for _, row in comparison_result['col3_changes'].iterrows():
            record = {}

            # 키 컬럼들 복사
            for i, col in enumerate(df_b.columns[:len(key_columns)]):
                record[col] = row.iloc[i]

            # Source 처리: use_b이면 After, use_a이면 Before 사용
            if include_source_changes == 'use_b':
                # B의 Source 사용 (After)
                after_col = [c for c in row.index if '_After (File_B)' in c and df_b.columns[2] in c]
                if after_col:
                    record[df_b.columns[2]] = row[after_col[0]]
            elif include_source_changes == 'use_a':
                # A의 Source 사용 (Before)
                before_col = [c for c in row.index if '_Before (File_A)' in c and df_b.columns[2] in c]
                if before_col:
                    record[df_b.columns[2]] = row[before_col[0]]

            # Translation은 Unchanged 값 사용
            unchanged_col = [c for c in row.index if '(Unchanged)' in c and df_b.columns[3] in c]
            if unchanged_col:
                record[df_b.columns[3]] = row[unchanged_col[0]]

            merged_records.append(record)

            # 키 추적 (항상 ID + Name)
            key = '|'.join([str(record[col]) for col in df_b.columns[:2]])
            processed_keys.add(key)

    # 4. Translation 변경 (col4_changes)
    if include_translation_changes and not comparison_result['col4_changes'].empty:
        for _, row in comparison_result['col4_changes'].iterrows():
            record = {}

            # 키 컬럼들 복사
            for i, col in enumerate(df_b.columns[:len(key_columns)]):
                record[col] = row.iloc[i]

            # Source는 Unchanged 값 사용
            unchanged_col = [c for c in row.index if '(Unchanged)' in c and df_b.columns[2] in c]
            if unchanged_col:
                record[df_b.columns[2]] = row[unchanged_col[0]]

            # Translation은 After 값 사용
            after_col = [c for c in row.index if '_After (File_B)' in c and df_b.columns[3] in c]
            if after_col:
                record[df_b.columns[3]] = row[after_col[0]]

            merged_records.append(record)

            # 키 추적 (항상 ID + Name)
            key = '|'.join([str(record[col]) for col in df_b.columns[:2]])
            processed_keys.add(key)

    # 5. Both 변경 (both_changes)
    if include_both_changes and not comparison_result['both_changes'].empty:
        for _, row in comparison_result['both_changes'].iterrows():
            record = {}

            # 키 컬럼들 복사
            for i, col in enumerate(df_b.columns[:len(key_columns)]):
                record[col] = row.iloc[i]

            # Source와 Translation 모두 After 값 사용
            source_after_col = [c for c in row.index if '_After (File_B)' in c and df_b.columns[2] in c]
            if source_after_col:
                record[df_b.columns[2]] = row[source_after_col[0]]

            translation_after_col = [c for c in row.index if '_After (File_B)' in c and df_b.columns[3] in c]
            if translation_after_col:
                record[df_b.columns[3]] = row[translation_after_col[0]]

            merged_records.append(record)

            # 키 추적 (항상 ID + Name)
            key = '|'.join([str(record[col]) for col in df_b.columns[:2]])
            processed_keys.add(key)

    # 6. 변경되지 않은 항목들 (모든 키에서 처리되지 않은 것들)
    # Live 파일(A)의 모든 키 확인
    for _, row in df_a_copy.iterrows():
        if row['key'] not in processed_keys:
            # 변경되지 않은 항목이므로 Live 버전 사용
            record = {col: row[col] for col in df_a.columns}
            merged_records.append(record)

    # DataFrame 생성
    merged_df = pd.DataFrame(merged_records)

    # 컬럼 순서를 원본과 동일하게 유지
    merged_df = merged_df[df_a.columns.tolist()]

    return merged_df

def compare_dataframes(df_a, df_b):
    """
    두 DataFrame을 비교하여 차이점을 분석합니다.

    Args:
        df_a (DataFrame): Live/Current CSV 데이터 (A.csv)
        df_b (DataFrame): Modified CSV 데이터 (B.csv)
    """
    # 데이터 복사 (원본 보호)
    df_a = df_a.copy()
    df_b = df_b.copy()

    # 컬럼 확인
    if len(df_a.columns) < 4 or len(df_b.columns) < 4:
        raise ValueError("CSV files must have at least 4 columns.")

    # 키 컬럼 설정 (항상 ID + Name)
    key_columns = df_a.columns[:2].tolist()

    # 키 조합 생성
    df_a['key'] = df_a[key_columns].astype(str).agg('|'.join, axis=1)
    df_b['key'] = df_b[key_columns].astype(str).agg('|'.join, axis=1)

    # 1. A에만 있는 자료 (A - B)
    keys_only_in_a = set(df_a['key']) - set(df_b['key'])
    only_in_a = df_a[df_a['key'].isin(keys_only_in_a)].drop('key', axis=1)

    # 2. B에만 있는 자료 (B - A)
    keys_only_in_b = set(df_b['key']) - set(df_a['key'])
    only_in_b = df_b[df_b['key'].isin(keys_only_in_b)].drop('key', axis=1)

    # 3. 키는 동일하지만 3번째 또는 4번째 컬럼이 다른 경우
    common_keys = set(df_a['key']) & set(df_b['key'])

    col3_changes = []  # 3번째 컬럼 변경 사항
    col4_changes = []  # 4번째 컬럼 변경 사항
    both_changes = []  # 둘 다 변경된 사항

    for key in common_keys:
        row_a = df_a[df_a['key'] == key].iloc[0]
        row_b = df_b[df_b['key'] == key].iloc[0]

        # 3번째 컬럼 (인덱스 2) 또는 4번째 컬럼 (인덱스 3) 비교
        col3_diff = str(row_a.iloc[2]) != str(row_b.iloc[2])
        col4_diff = str(row_a.iloc[3]) != str(row_b.iloc[3])

        if col3_diff or col4_diff:
            # 공통 데이터 (키 컬럼들 - 항상 ID + Name)
            base_data = {col: row_a[col] for col in df_a.columns[:2] if col != 'key'}

            if col3_diff and col4_diff:
                # 둘 다 변경된 경우
                change_record = {
                    **base_data,
                    f'{df_a.columns[2]}_Before (File_A)': row_a.iloc[2],
                    f'{df_a.columns[2]}_After (File_B)': row_b.iloc[2],
                    f'{df_a.columns[3]}_Before (File_A)': row_a.iloc[3],
                    f'{df_a.columns[3]}_After (File_B)': row_b.iloc[3]
                }
                both_changes.append(change_record)
            elif col3_diff:
                # 3번째 컬럼만 변경
                change_record = {
                    **base_data,
                    f'{df_a.columns[2]}_Before (File_A)': row_a.iloc[2],
                    f'{df_a.columns[2]}_After (File_B)': row_b.iloc[2],
                    f'{df_a.columns[3]} (Unchanged)': row_a.iloc[3]
                }
                col3_changes.append(change_record)
            elif col4_diff:
                # 4번째 컬럼만 변경
                change_record = {
                    **base_data,
                    f'{df_a.columns[2]} (Unchanged)': row_a.iloc[2],
                    f'{df_a.columns[3]}_Before (File_A)': row_a.iloc[3],
                    f'{df_a.columns[3]}_After (File_B)': row_b.iloc[3]
                }
                col4_changes.append(change_record)

    col3_changes_df = pd.DataFrame(col3_changes)
    col4_changes_df = pd.DataFrame(col4_changes)
    both_changes_df = pd.DataFrame(both_changes)

    return {
        'only_in_a': only_in_a,
        'only_in_b': only_in_b,
        'col3_changes': col3_changes_df,
        'col4_changes': col4_changes_df,
        'both_changes': both_changes_df
    }

def main():
    st.set_page_config(
        page_title="Langify Translation Comparison Tool",
        page_icon="🌐",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # CSS to fix hover effects and prevent visual jumping
    st.markdown("""
    <style>
    /* Fix metric hover effects */
    [data-testid="metric-container"] {
        transition: none !important;
        transform: none !important;
    }

    [data-testid="metric-container"]:hover {
        transform: none !important;
        box-shadow: none !important;
        border: none !important;
    }

    /* Stabilize metric values */
    [data-testid="metric-container"] > div {
        transition: none !important;
        transform: none !important;
    }

    /* Fix button hover effects */
    .stButton > button {
        transition: background-color 0.2s ease !important;
        transform: none !important;
    }

    .stButton > button:hover {
        transform: none !important;
    }

    /* Prevent expander jumping */
    .streamlit-expanderHeader {
        transition: none !important;
    }

    /* Fix file uploader hover */
    [data-testid="stFileUploader"] {
        transition: none !important;
    }

    /* General anti-jump styling */
    .element-container {
        transition: none !important;
        transform: none !important;
    }

    /* Fix tab container */
    .stTabs [data-baseweb="tab-list"] {
        transition: none !important;
    }

    .stTabs [data-baseweb="tab"] {
        transition: none !important;
        transform: none !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        transform: none !important;
    }

    /* Expand content width for comparison results */
    .comparison-section {
        width: 100%;
        max-width: none !important;
    }

    /* Make dataframes wider */
    .stDataFrame {
        width: 100% !important;
    }

    /* Expand tab content */
    .stTabs [data-baseweb="tab-panel"] {
        width: 100% !important;
        max-width: none !important;
        padding: 1rem 0 !important;
    }

    /* Make main content area wider but controlled */
    .main .block-container {
        max-width: 1400px !important;
        width: 95% !important;
        padding-top: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin: 0 auto !important;
    }

    /* Override Streamlit's default container widths */
    .css-1d391kg, .css-1lcbmhc, .css-1outpf7 {
        max-width: 1400px !important;
        width: 95% !important;
        margin: 0 auto !important;
    }

    /* Specific targeting for content containers */
    div[data-testid="stAppViewContainer"] {
        max-width: none !important;
    }

    div[data-testid="stAppViewContainer"] > section {
        max-width: none !important;
    }

    /* Fix comparison display containers */
    div[data-testid="column"] {
        padding: 0.5rem !important;
    }

    /* Navigation Card 버튼을 정사각형 박스 형태로 스타일링 */
    div[data-testid="column"] button[key^="nav_card"] {
        height: 160px !important;
        min-height: 160px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
        transition: all 0.3s ease !important;
        white-space: pre-line !important;
        background: linear-gradient(135deg, #f5f7fa, #e8ecef) !important;
        color: #1f2937 !important;
        padding: 1.2rem !important;
        line-height: 1.4 !important;
    }

    div[data-testid="column"] button[key^="nav_card"]:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 8px 16px rgba(0,0,0,0.12) !important;
        background: linear-gradient(135deg, #e8ecef, #dce1e5) !important;
        cursor: pointer !important;
    }

    /* Navigation Card 개별 색상 - 상단 굵은 테두리 */
    button[key="nav_card1"] {
        border-top: 6px solid #ff4b4b !important;
    }

    button[key="nav_card2"] {
        border-top: 6px solid #09ab3b !important;
    }

    button[key="nav_card3"] {
        border-top: 6px solid #ff8c00 !important;
    }

    button[key="nav_card4"] {
        border-top: 6px solid #0066cc !important;
    }

    /* Analysis 섹션 스타일 조정 */
    div[data-testid="column"]:has(button[type="submit"]) h3 {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🌐 Langify Translation Comparison Tool")
    st.markdown("Compare Langify Export/Import files and track translation changes between versions")

    # 사이드바 정보
    st.sidebar.header("About")
    st.sidebar.info(
        "🌐 **Langify Translation Comparison**\n\n"
        "**Key**: ID + Name\n\n"
        "**Tracks**:\n"
        "- Source (Original text) changes\n"
        "- Translation updates\n"
        "- New/Deleted entries\n\n"
        "**Features**:\n"
        "✅ Side-by-side comparison\n"
        "✅ Selective merge options\n"
        "✅ Excel/CSV export"
    )

    # 파일 업로드 섹션
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        st.subheader("📁 Current Live Export (A)")
        st.caption("⚠️ LATEST export from your live Shopify store")
        file_a = st.file_uploader(
            "Choose file",
            type=['csv'],
            key="file_a",
            help="The current/live version of Langify export from your Shopify store",
            label_visibility="collapsed"
        )

        if file_a:
            df_a_preview = pd.read_csv(file_a, dtype=str)
            st.success(f"✅ Loaded: {len(df_a_preview)} records")

            with st.expander("Preview File A"):
                st.dataframe(df_a_preview.head(10))

    with col2:
        st.subheader("📁 Modified Export (B)")
        st.caption("📝 Export file with your modifications")
        file_b = st.file_uploader(
            "Choose file",
            type=['csv'],
            key="file_b",
            help="The modified/updated Langify export file with your changes",
            label_visibility="collapsed"
        )

        if file_b:
            df_b_preview = pd.read_csv(file_b, dtype=str)
            st.success(f"✅ Loaded: {len(df_b_preview)} records")

            with st.expander("Preview File B"):
                st.dataframe(df_b_preview.head(10))

    # 비교 버튼을 파일 업로드 영역에 통합
    with col3:
        st.markdown("### 🔍 Analysis")
        st.markdown("")  # 약간의 여백 추가

        # 파일이 모두 업로드되었을 때만 버튼 활성화
        if file_a and file_b:
            st.markdown("")  # 추가 여백
            compare_button = st.button(
                "▶ Compare Files",
                type="primary",
                use_container_width=True,
                help="Click to analyze differences between the two files"
            )
        else:
            st.markdown("")  # 추가 여백
            st.info("📤 Upload both Langify export files to enable comparison")
            compare_button = False

    # 비교 실행
    if file_a and file_b and compare_button:
        try:
            # 비교 실행 - 메모리에서 직접 처리
            with st.spinner('Analyzing differences...'):
                # DataFrame을 직접 사용하여 비교 수행
                result = compare_dataframes(df_a_preview, df_b_preview)

                # 결과를 세션 상태에 저장
                st.session_state['comparison_result'] = result

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    # 결과 영역을 완전히 분리하여 표시
    if 'comparison_result' in st.session_state and st.session_state['comparison_result'] is not None:
        result = st.session_state['comparison_result']

        st.markdown("---")
        st.success("✅ Analysis completed!")

        # 전체 결과를 탭으로 구성 (Summary 포함)
        tab_summary, tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Summary",
            "🗑️ Deleted (A only)",
            "➕ Added (B only)",
            "🔤 Source Changes",
            "🌐 Translation Changes"
        ])

        # Summary 탭
        with tab_summary:
            st.subheader("📊 Analysis Summary")

            # 클릭 가능한 시각적 메트릭 그레이 박스
            st.markdown("##### 📈 Visual Summary (Click to navigate)")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if st.button(
                    f"🗑️ Deleted\n{len(result['only_in_a'])} records\nOnly in File A",
                    key="nav_card1",
                    use_container_width=True,
                    help="Click to view records that exist only in File A (deleted items)"
                ):
                    st.components.v1.html("""
                        <script>
                            window.parent.document.querySelectorAll('button[data-baseweb="tab"]')[1].click();
                        </script>
                    """, height=0)

            with col2:
                if st.button(
                    f"➕ Added\n{len(result['only_in_b'])} records\nOnly in File B",
                    key="nav_card2",
                    use_container_width=True,
                    help="Click to view records that exist only in File B (new items)"
                ):
                    st.components.v1.html("""
                        <script>
                            window.parent.document.querySelectorAll('button[data-baseweb="tab"]')[2].click();
                        </script>
                    """, height=0)

            with col3:
                if st.button(
                    f"🔤 Source\n{len(result['col3_changes'])} records\nOriginal Text Changes",
                    key="nav_card3",
                    use_container_width=True,
                    help="Click to view source text changes"
                ):
                    st.components.v1.html("""
                        <script>
                            window.parent.document.querySelectorAll('button[data-baseweb="tab"]')[3].click();
                        </script>
                    """, height=0)

            with col4:
                if st.button(
                    f"🌐 Translation\n{len(result['col4_changes'])} records\nTranslation Changes",
                    key="nav_card4",
                    use_container_width=True,
                    help="Click to view translation text changes"
                ):
                    st.components.v1.html("""
                        <script>
                            window.parent.document.querySelectorAll('button[data-baseweb="tab"]')[4].click();
                        </script>
                    """, height=0)

            # 추가 분석 정보
            st.markdown("---")
            st.markdown("### 📈 Detailed Breakdown")

            total_a = len(result['only_in_a'])
            total_b = len(result['only_in_b'])
            total_modified = len(result['col3_changes']) + len(result['col4_changes']) + len(result['both_changes'])

            col1, col2 = st.columns(2)
            with col1:
                st.info(f"""
                **File A Analysis:**
                - Unique records: {total_a}
                - Modified records: {total_modified}
                - Retention rate: {(total_modified / (total_a + total_modified) * 100):.1f}%
                """)

            with col2:
                st.info(f"""
                **File B Analysis:**
                - New records: {total_b}
                - Modified records: {total_modified}
                - Growth rate: {(total_b / (total_b + total_modified) * 100):.1f}%
                """)

        with tab1:
            if not result['only_in_a'].empty:
                st.markdown("### 🗑️ Records Only in File A (Deleted)")

                # CSV 다운로드 기능
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("**📊 Sortable Grid View** (Click column headers to sort)")
                with col2:
                    csv_data = result['only_in_a'].to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv_data,
                        file_name="deleted_records.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

                st.dataframe(result['only_in_a'], use_container_width=True, height=400)
                st.info(f"📈 Total Deleted Records: {len(result['only_in_a'])}")
            else:
                st.info("No deleted records found")

        with tab2:
            if not result['only_in_b'].empty:
                st.markdown("### ➕ Records Only in File B (Added)")

                # CSV 다운로드 기능
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("**📊 Sortable Grid View** (Click column headers to sort)")
                with col2:
                    csv_data = result['only_in_b'].to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv_data,
                        file_name="added_records.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

                st.dataframe(result['only_in_b'], use_container_width=True, height=400)
                st.info(f"📈 Total Added Records: {len(result['only_in_b'])}")
            else:
                st.info("No added records found")

        with tab3:
            if not result['col3_changes'].empty:
                st.markdown("### 🔤 Source Changes")

                # Create enhanced dataframe with remarks
                display_df = result['col3_changes'].copy()

                # Check for Before/After columns and create remarks
                before_cols = [col for col in display_df.columns if '_Before (File_A)' in col]
                after_cols = [col for col in display_df.columns if '_After (File_B)' in col]

                if before_cols and after_cols:
                    # Create remarks column
                    remarks = []
                    for idx, row in display_df.iterrows():
                        change_details = []
                        for before_col in before_cols:
                            after_col = before_col.replace('_Before (File_A)', '_After (File_B)')
                            if after_col in display_df.columns:
                                field_name = before_col.replace('_Before (File_A)', '')
                                before_val = str(row[before_col])[:50] + "..." if len(str(row[before_col])) > 50 else str(row[before_col])
                                after_val = str(row[after_col])[:50] + "..." if len(str(row[after_col])) > 50 else str(row[after_col])
                                change_details.append(f"📝 {field_name}: '{before_val}' → '{after_val}'")
                        remarks.append(" | ".join(change_details))

                    display_df['🔍 Change Summary'] = remarks

                # CSV 다운로드 기능 추가
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("**📊 Sortable Grid View** (Click column headers to sort)")
                with col2:
                    csv_data = display_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv_data,
                        file_name="source_changes.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

                # Display enhanced dataframe
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    height=400,
                    column_config={
                        "🔍 Change Summary": st.column_config.TextColumn(
                            "Change Summary",
                            help="Summary of changes made",
                            width="large"
                        )
                    }
                )

                # Quick stats
                st.info(f"📈 Total Source Changes: {len(display_df)} records")

            else:
                st.info("No source changes found")

        with tab4:
            if not result['col4_changes'].empty:
                st.markdown("### 🌐 Translation Changes")

                # Create enhanced dataframe with remarks
                display_df = result['col4_changes'].copy()

                # Check for Before/After columns and create remarks
                before_cols = [col for col in display_df.columns if '_Before (File_A)' in col]
                after_cols = [col for col in display_df.columns if '_After (File_B)' in col]

                if before_cols and after_cols:
                    # Create remarks column for translations
                    remarks = []
                    for idx, row in display_df.iterrows():
                        change_details = []
                        for before_col in before_cols:
                            after_col = before_col.replace('_Before (File_A)', '_After (File_B)')
                            if after_col in display_df.columns:
                                field_name = before_col.replace('_Before (File_A)', '')
                                before_val = str(row[before_col])[:40] + "..." if len(str(row[before_col])) > 40 else str(row[before_col])
                                after_val = str(row[after_col])[:40] + "..." if len(str(row[after_col])) > 40 else str(row[after_col])
                                change_details.append(f"🌐 {field_name}: '{before_val}' → '{after_val}'")
                        remarks.append(" | ".join(change_details))

                    display_df['🔍 Translation Summary'] = remarks

                # CSV 다운로드 기능 추가
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("**📊 Sortable Grid View** (Click column headers to sort)")
                with col2:
                    csv_data = display_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv_data,
                        file_name="translation_changes.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

                # Display enhanced dataframe
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    height=400,
                    column_config={
                        "🔍 Translation Summary": st.column_config.TextColumn(
                            "Translation Summary",
                            help="Summary of translation changes",
                            width="large"
                        )
                    }
                )

                # Quick stats
                st.info(f"📈 Total Translation Changes: {len(display_df)} records")

            else:
                st.info("No translation changes found")

        # Excel 다운로드 및 Merge 기능
        st.markdown("---")
        st.subheader("📥 Download & Merge Options")

        # 메모리에서 Excel 파일 생성
        try:
            import io
            excel_buffer = io.BytesIO()

            # 결과 데이터를 사용하여 Excel 파일 생성
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                # 요약 시트
                total_modified = len(result['col3_changes']) + len(result['col4_changes']) + len(result['both_changes'])
                summary_data = {
                    'Category': [
                        '1. Records only in A (deleted)',
                        '2. Records only in B (added)',
                        '3-1. Source/Column3 changed only',
                        '3-2. Data/Column4 changed only',
                        '3-3. Both columns changed',
                        'Total modified records'
                    ],
                    'Count': [
                        len(result['only_in_a']),
                        len(result['only_in_b']),
                        len(result['col3_changes']),
                        len(result['col4_changes']),
                        len(result['both_changes']),
                        total_modified
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='0_Summary', index=False)

                # 각 분석 결과를 별도 시트에 저장
                if not result['only_in_a'].empty:
                    result['only_in_a'].to_excel(writer, sheet_name='1_Only_in_A_Deleted', index=False)
                if not result['only_in_b'].empty:
                    result['only_in_b'].to_excel(writer, sheet_name='2_Only_in_B_Added', index=False)
                if not result['col3_changes'].empty:
                    result['col3_changes'].to_excel(writer, sheet_name='3-1_Source_Changes', index=False)
                if not result['col4_changes'].empty:
                    result['col4_changes'].to_excel(writer, sheet_name='3-2_Data_Changes', index=False)
                if not result['both_changes'].empty:
                    result['both_changes'].to_excel(writer, sheet_name='3-3_Both_Changed', index=False)

            excel_buffer.seek(0)

            # 다운로드 버튼들
            col1, col2 = st.columns([1, 3])
            with col1:
                st.download_button(
                    label="📊 Download Excel Report",
                    data=excel_buffer.getvalue(),
                    file_name="langify_comparison_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"Excel generation error: {str(e)}")
            st.info("💡 You can still download individual CSV files from each tab above.")

        # Merge 기능 추가
        st.markdown("---")
        st.subheader("🔀 Create Merged Import File")
        st.markdown("Select which changes to include in the merged file for re-importing to Langify:")

        merge_col1, merge_col2 = st.columns(2)

        with merge_col1:
            st.markdown("**📋 Include in Merged File:**")
            include_deleted = st.checkbox(
                f"Keep items only in Live (A) - {len(result['only_in_a'])} records",
                value=True,
                help="Keep translations that exist in live but not in modified version"
            )
            include_added = st.checkbox(
                f"Add new items from Modified (B) - {len(result['only_in_b'])} records",
                value=True,
                help="Include new translations from modified file"
            )

            st.markdown(f"**Source Changes** - {len(result['col3_changes'])} records")
            st.caption("Choose which file has the latest source text:")
            source_from_b = st.checkbox(
                "Use File B's source (B is newer)",
                value=False,
                key="source_from_b",
                help="Apply source text changes from Modified file (B)"
            )
            source_from_a = st.checkbox(
                "Keep File A's source (A is newer)",
                value=False,
                key="source_from_a",
                help="Keep source text from Live file (A), ignore B's changes"
            )

        with merge_col2:
            st.markdown("**⚙️ Translation & Combined Changes:**")
            include_translation_changes = st.checkbox(
                f"Apply Translation changes - {len(result['col4_changes'])} records",
                value=True,
                help="Update translation changes from modified file"
            )
            include_both_changes = st.checkbox(
                f"Apply Both changes - {len(result['both_changes'])} records",
                value=True,
                help="Update records where both source and translation changed"
            )

        # Merge 실행 버튼
        if st.button("🔀 Generate Merged File", type="primary", use_container_width=False):
            # Source 옵션 검증
            if source_from_a and source_from_b:
                st.error("❌ Please select only ONE source option (either A or B, not both)")
            else:
                try:
                    # Source 변경 처리 방식 결정
                    if source_from_b:
                        include_source_changes = 'use_b'
                    elif source_from_a:
                        include_source_changes = 'use_a'
                    else:
                        include_source_changes = 'skip'  # Manual review 필요

                    # Merge 로직 실행
                    merged_df = create_merged_file(
                        df_a_preview, df_b_preview, result,
                        include_deleted, include_added,
                        include_source_changes, include_translation_changes,
                        include_both_changes
                    )

                    # 세션에 저장
                    st.session_state['merged_file'] = merged_df
                    st.success(f"✅ Merged file created successfully! Total records: {len(merged_df)}")

                    # Source 처리 상태 알림
                    if include_source_changes == 'skip' and len(result['col3_changes']) > 0:
                        st.warning(f"⚠️ {len(result['col3_changes'])} source changes were skipped (manual review required)")

                except Exception as e:
                    st.error(f"❌ Merge error: {str(e)}")

        # Merged 파일 다운로드
        if 'merged_file' in st.session_state and st.session_state['merged_file'] is not None:
            merged_df = st.session_state['merged_file']

            st.markdown("##### 📥 Download Merged File")

            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                # CSV 다운로드
                merged_csv = merged_df.to_csv(index=False)
                st.download_button(
                    label="📄 Download CSV",
                    data=merged_csv,
                    file_name="langify_merged_import.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            with col2:
                # Excel 다운로드
                merged_excel_buffer = io.BytesIO()
                merged_df.to_excel(merged_excel_buffer, index=False, engine='openpyxl')
                merged_excel_buffer.seek(0)

                st.download_button(
                    label="📊 Download Excel",
                    data=merged_excel_buffer.getvalue(),
                    file_name="langify_merged_import.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            # 미리보기
            with st.expander("👁️ Preview Merged File"):
                st.dataframe(merged_df.head(20), use_container_width=True)
                st.info(f"📊 Total records in merged file: {len(merged_df)}")

    # 사용법 안내
    with st.expander("📖 How to Use - Langify Export Comparison"):
        st.markdown("""
        ### Langify Export File Requirements
        - Export CSV files from Shopify Langify app
        - Files must have at least 4 columns (ID, Name, Source, Translation)
        - First row should contain headers
        - Supports UTF-8 and CP949 encoding

        ### Langify Column Structure
        - **Column 1**: ID (unique identifier for each translation entry)
        - **Column 2**: Name (translation key/field name)
        - **Column 3**: Source (original text, usually in default language)
        - **Column 4**: Translation (translated text in target language)

        ⚠️ **Unique Key**: ID + Name combination (columns 1 & 2)

        ### How It Works

        **Comparison Logic**
        - **Key**: ID + Name (tracks records by these two columns)
        - **Detects**:
          - Records deleted from live (only in A)
          - New records added (only in B)
          - Source text changes (original language updates)
          - Translation changes (target language updates)
          - Combined changes (both source and translation)

        ### Typical Workflows

        **Method 1: Local Translation Updates**
        1. Export current live translations from Langify → **File A (Current Live)**
        2. Download and edit translations locally in Excel/CSV editor
        3. Upload both files:
           - File A: Current Live Export
           - File B: Modified Export (your changes)
        4. Review comparison results in tabs
        5. Use Merge feature to selectively apply changes
        6. Download merged file and import back to Langify

        **Method 2: Track Historical Changes**
        1. Export translations from Langify (current version) → **File A**
        2. Make changes directly in Shopify/Langify over time
        3. Export translations again (updated version) → **File B**
        4. Upload and compare to see what changed

        ### Merge Feature 🔀

        **What it does:**
        - Combines changes from both files based on your selections
        - Preserves unchanged records automatically
        - Generates a ready-to-import CSV/Excel file

        **Options:**
        - ✅ **Keep items only in Live (A)**: Preserve records not in modified version
        - ✅ **Add new items from Modified (B)**: Include new translations
        - **Source Changes**: Choose which file has the latest source text
          - Use File B's source (B is newer)
          - Keep File A's source (A is newer)
          - Skip (manual review required)
        - ✅ **Apply Translation changes**: Update translations from modified file
        - ✅ **Apply Both changes**: Update records with both source & translation changes

        **Best Practice:**
        - Always use the **current live export as File A**
        - This ensures the merge base is accurate
        - Review comparison results before merging
        - Test merged file on a staging environment first

        ### Tips
        - Use "Preview" to check file contents before comparing
        - Download individual category CSVs from each tab
        - Save Excel report for detailed analysis
        - Use merge feature instead of manual Excel editing
        """)

if __name__ == "__main__":
    main()