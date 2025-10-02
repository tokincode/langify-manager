# Langify 번역 비교 도구 사용 가이드

## 📋 개요

Shopify Langify 앱의 Export/Import 파일을 비교하고 선택적으로 병합할 수 있는 웹 기반 도구입니다.

### 주요 기능
- 🔍 두 Langify export 파일 비교
- 📊 변경 사항 시각화 (삭제/추가/원문변경/번역변경)
- 🔀 선택적 병합 기능
- 📥 Excel/CSV 다운로드
- 🌐 웹 브라우저에서 간편하게 사용

## 🚀 시작하기

### 필요 사항
```bash
# Python 3.7 이상
# 필요한 라이브러리 설치
pip install streamlit pandas openpyxl
```

### 실행 방법
```bash
# 웹 애플리케이션 실행
streamlit run csv_compare_web.py

# 또는 배치 파일 실행 (Windows)
test_ui.bat
```

브라우저가 자동으로 열리며 `http://localhost:8501`에서 접속 가능합니다.

## 📖 사용 방법

### 1단계: 파일 업로드

#### File A - Current Live Export
- **용도**: 현재 라이브 스토어에 적용된 최신 번역 파일
- **중요**: 항상 가장 최신 버전을 사용해야 합니다
- **획득 방법**: Shopify 관리자 → Langify 앱 → Export

#### File B - Modified Export
- **용도**: 수정하고자 하는 번역이 포함된 파일
- **사례**:
  - 로컬에서 편집한 번역 파일
  - 번역가로부터 받은 업데이트 파일
  - 과거 백업 파일

### 2단계: 비교 분석

**Compare Files** 버튼 클릭 시 다음 항목을 자동 분석합니다:

#### Summary 탭
- 전체 변경 사항 요약
- 클릭 가능한 네비게이션 카드
- 상세 통계 정보

#### Deleted (A only) 탭
- Live에는 있지만 Modified에 없는 항목
- 삭제 예정인 번역들

#### Added (B only) 탭
- Modified에 새로 추가된 항목
- 신규 상품/컨텐츠의 번역

#### Source Changes 탭
- 원문 텍스트가 변경된 항목
- 예: "Hello" → "Hi there!"

#### Translation Changes 탭
- 번역만 변경된 항목
- 예: "안녕하세요" → "반갑습니다"

### 3단계: 결과 다운로드

#### 개별 CSV 다운로드
각 탭에서 **Download CSV** 버튼으로 해당 카테고리만 다운로드

#### Excel 리포트 다운로드
모든 분석 결과를 포함한 Excel 파일 (여러 시트)

### 4단계: 병합 파일 생성 (선택사항)

#### 병합 옵션 선택

**기본 옵션** (기본값: 모두 체크됨)
- ✅ **Keep items only in Live (A)**: Live에만 있는 항목 유지
- ✅ **Add new items from Modified (B)**: 새 항목 추가

**Source 변경 처리** (하나만 선택)
- ⬜ **Use File B's source (B is newer)**: B의 원문 적용
- ⬜ **Keep File A's source (A is newer)**: A의 원문 유지
- ⬜ **둘 다 선택 안함**: Source 변경사항 제외 (수동 검토 필요)

**추가 옵션**
- ✅ **Apply Translation changes**: 번역 변경사항 적용
- ✅ **Apply Both changes**: 원문+번역 모두 변경된 항목 적용

#### 병합 실행
1. **Generate Merged File** 버튼 클릭
2. 미리보기로 확인
3. **Download CSV** 또는 **Download Excel** 선택
4. Langify에 Import

## 💡 실전 사용 시나리오

### 시나리오 1: 로컬 번역 업데이트

```
1. Langify에서 현재 번역 Export → file_A.csv
2. file_A.csv를 다운로드하여 Excel에서 편집
3. 편집한 파일을 file_B.csv로 저장
4. 도구에 업로드:
   - File A: file_A.csv (원본)
   - File B: file_B.csv (수정본)
5. 비교 결과 확인
6. 병합 옵션:
   - Keep items in Live: ✅
   - Add new items: ✅
   - Source: Keep File A's source ✅ (원문은 유지)
   - Translation changes: ✅
   - Both changes: ✅
7. 병합 파일 다운로드 후 Langify Import
```

### 시나리오 2: 번역가 파일 통합

```
1. Langify에서 현재 번역 Export → current_live.csv
2. 번역가에게서 받은 파일 → translator_update.csv
3. 도구에 업로드:
   - File A: current_live.csv
   - File B: translator_update.csv
4. Translation Changes 탭에서 번역 변경사항 검토
5. 병합 옵션 선택 후 통합
6. Import 전 테스트 환경에서 검증
```

### 시나리오 3: 변경 이력 추적

```
1. 정기적으로 Export 백업 (예: 매주 월요일)
2. 변경 발생 후 새로 Export
3. 도구로 비교:
   - File A: 지난주 백업
   - File B: 이번주 Export
4. 무엇이 변경되었는지 확인
5. 변경 내역을 Excel 리포트로 저장
```

## ⚠️ 주의사항

### 파일 요구사항
- ✅ Langify Export CSV 형식 (4개 컬럼: ID, Name, Source, Translation)
- ✅ UTF-8 또는 CP949 인코딩
- ✅ 헤더 행 포함
- ✅ ID + Name 조합이 고유해야 함

### 병합 시 주의점
1. **항상 File A에 최신 Live 파일 사용**
2. Source 변경 옵션 신중하게 선택
3. 병합 결과를 Preview에서 확인
4. 프로덕션 적용 전 테스트 환경에서 검증
5. 백업 필수 (Import 전에 현재 버전 Export)

### 데이터 손실 방지
- Import 전에 현재 Langify 데이터 Export
- 소량 데이터로 먼저 테스트
- 병합 파일의 레코드 수 확인

## 🔧 트러블슈팅

### 파일 업로드 오류
- **증상**: "CSV files must have at least 4 columns" 오류
- **해결**: Langify에서 올바르게 Export했는지 확인

### 한글 깨짐
- **증상**: 한글이 깨져서 표시됨
- **해결**: 파일을 UTF-8 인코딩으로 저장

### 병합 파일 레코드 수 불일치
- **증상**: 예상보다 많거나 적은 레코드
- **해결**:
  - Summary 탭에서 각 카테고리 레코드 수 확인
  - 병합 옵션 재검토
  - Preview에서 미리 확인

### Source 옵션 선택 오류
- **증상**: "Please select only ONE source option" 오류
- **해결**: Use File B's source와 Keep File A's source 중 하나만 선택

## 📊 기술 세부사항

### 비교 로직
- **키**: ID + Name (2개 컬럼 조합)
- **변경 감지**: Source(3번째 컬럼), Translation(4번째 컬럼) 비교
- **Before/After**: 변경 전후 값 모두 표시

### 병합 로직
```
병합 파일 =
  변경되지 않은 레코드 (Live 기준)
  + 선택한 옵션에 따른 변경 사항
```

1. 기본적으로 모든 Live 레코드 포함
2. 사용자 선택에 따라 변경사항 적용
3. Source 변경은 use_a/use_b/skip 중 선택
4. 최종적으로 원본 컬럼 구조 유지

## 📚 추가 자료

### 관련 문서
- `README.md`: 프로젝트 개요 (영문)
- `사용법.md`: 일반 CSV 비교 도구 (CLI/VBA)
- `project_status.md`: 개발 진행 상황

### Langify 공식 문서
- [Langify 앱 사용법](https://apps.shopify.com/langify)
- Export/Import 기능 가이드

## 🆘 도움말

### 일반적인 질문

**Q: File A와 File B를 반대로 넣으면 어떻게 되나요?**
A: 비교는 되지만 병합 결과가 의도와 다를 수 있습니다. 항상 최신 Live를 File A에 넣으세요.

**Q: Source 변경 옵션을 둘 다 선택 안하면?**
A: 해당 레코드가 병합에서 제외되며 수동으로 처리해야 합니다.

**Q: Both Changes는 무엇인가요?**
A: 원문(Source)과 번역(Translation)이 모두 변경된 레코드입니다.

**Q: 병합 파일을 다시 비교할 수 있나요?**
A: 네, 병합 파일을 File B로 올려서 다시 비교 가능합니다.

---

**버전**: 2.0 (Merge 기능 포함)
**최종 업데이트**: 2025년 10월 2일
**문의**: 프로젝트 이슈 트래커
