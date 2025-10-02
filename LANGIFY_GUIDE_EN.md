# Langify Translation Comparison Tool - User Guide

## 📋 Overview

A web-based tool for comparing and selectively merging Shopify Langify app Export/Import files.

### Key Features
- 🔍 Compare two Langify export files
- 📊 Visualize changes (deletions/additions/source changes/translation changes)
- 🔀 Selective merge functionality
- 📥 Excel/CSV downloads
- 🌐 Easy to use in web browser

## 🚀 Getting Started

### Requirements
```bash
# Python 3.7 or higher
# Install required libraries
pip install streamlit pandas openpyxl
```

### How to Run
```bash
# Start the web application
streamlit run csv_compare_web.py

# Or use batch file (Windows)
test_ui.bat
```

Browser will automatically open at `http://localhost:8501`.

## 📖 How to Use

### Step 1: Upload Files

#### File A - Current Live Export
- **Purpose**: Latest translation file currently applied on live store
- **Important**: Always use the most recent version
- **How to get**: Shopify Admin → Langify App → Export

#### File B - Modified Export
- **Purpose**: File containing translations you want to modify
- **Examples**:
  - Locally edited translation file
  - Updated file from translator
  - Historical backup file

### Step 2: Comparison Analysis

Click **Compare Files** button to automatically analyze:

#### Summary Tab
- Overview of all changes
- Clickable navigation cards
- Detailed statistics

#### Deleted (A only) Tab
- Items in Live but not in Modified
- Translations to be deleted

#### Added (B only) Tab
- New items in Modified
- Translations for new products/content

#### Source Changes Tab
- Items with changed source text
- Example: "Hello" → "Hi there!"

#### Translation Changes Tab
- Items with only translation changed
- Example: "Hello" → "Hola"

### Step 3: Download Results

#### Individual CSV Downloads
Use **Download CSV** button in each tab to download that category only

#### Excel Report Download
Download Excel file containing all analysis results (multiple sheets)

### Step 4: Generate Merged File (Optional)

#### Select Merge Options

**Basic Options** (Default: All checked)
- ✅ **Keep items only in Live (A)**: Preserve items only in Live
- ✅ **Add new items from Modified (B)**: Include new items

**Source Change Handling** (Choose one only)
- ⬜ **Use File B's source (B is newer)**: Apply B's source
- ⬜ **Keep File A's source (A is newer)**: Keep A's source
- ⬜ **Both unchecked**: Exclude source changes (manual review required)

**Additional Options**
- ✅ **Apply Translation changes**: Apply translation modifications
- ✅ **Apply Both changes**: Apply items with both source & translation changed

#### Execute Merge
1. Click **Generate Merged File** button
2. Review in Preview
3. Select **Download CSV** or **Download Excel**
4. Import to Langify

## 💡 Real-World Scenarios

### Scenario 1: Local Translation Updates

```
1. Export current translations from Langify → file_A.csv
2. Download file_A.csv and edit in Excel
3. Save edited file as file_B.csv
4. Upload to tool:
   - File A: file_A.csv (original)
   - File B: file_B.csv (modified)
5. Review comparison results
6. Merge options:
   - Keep items in Live: ✅
   - Add new items: ✅
   - Source: Keep File A's source ✅ (keep original text)
   - Translation changes: ✅
   - Both changes: ✅
7. Download merged file and Import to Langify
```

### Scenario 2: Integrate Translator's File

```
1. Export current translations from Langify → current_live.csv
2. Receive file from translator → translator_update.csv
3. Upload to tool:
   - File A: current_live.csv
   - File B: translator_update.csv
4. Review translation changes in Translation Changes tab
5. Select merge options and combine
6. Validate in test environment before import
```

### Scenario 3: Track Change History

```
1. Regularly export backups (e.g., every Monday)
2. After changes, export again
3. Compare using tool:
   - File A: Last week's backup
   - File B: This week's export
4. See what changed
5. Save change history as Excel report
```

## ⚠️ Important Notes

### File Requirements
- ✅ Langify Export CSV format (4 columns: ID, Name, Source, Translation)
- ✅ UTF-8 or CP949 encoding
- ✅ Header row included
- ✅ ID + Name combination must be unique

### Merge Precautions
1. **Always use latest Live file as File A**
2. Choose Source change option carefully
3. Review merge results in Preview
4. Validate in test environment before production
5. Backup required (Export current version before Import)

### Prevent Data Loss
- Export current Langify data before Import
- Test with small dataset first
- Verify record count in merged file

## 🔧 Troubleshooting

### File Upload Error
- **Symptom**: "CSV files must have at least 4 columns" error
- **Solution**: Verify correct Export from Langify

### Character Encoding Issues
- **Symptom**: Non-English characters appear garbled
- **Solution**: Save file with UTF-8 encoding

### Merged File Record Count Mismatch
- **Symptom**: More or fewer records than expected
- **Solution**:
  - Check record counts for each category in Summary tab
  - Review merge options
  - Verify in Preview

### Source Option Selection Error
- **Symptom**: "Please select only ONE source option" error
- **Solution**: Select only one between "Use File B's source" and "Keep File A's source"

## 📊 Technical Details

### Comparison Logic
- **Key**: ID + Name (combination of 2 columns)
- **Change Detection**: Compare Source (3rd column) and Translation (4th column)
- **Before/After**: Display both pre and post change values

### Merge Logic
```
Merged file =
  Unchanged records (based on Live)
  + Changes according to selected options
```

1. Include all Live records by default
2. Apply changes based on user selection
3. Source changes: choose use_a/use_b/skip
4. Maintain original column structure in final output

## 📚 Additional Resources

### Related Documentation
- `README.md`: Project overview
- `사용법.md`: General CSV comparison tool (CLI/VBA) - Korean
- `project_status.md`: Development progress

### Official Langify Documentation
- [Langify App Usage](https://apps.shopify.com/langify)
- Export/Import Feature Guide

## 🆘 Help

### Frequently Asked Questions

**Q: What happens if I swap File A and File B?**
A: Comparison will work but merge results may differ from intention. Always put latest Live as File A.

**Q: What if I don't select either Source option?**
A: Those records will be excluded from merge and require manual processing.

**Q: What are "Both Changes"?**
A: Records where both Source and Translation have been modified.

**Q: Can I compare the merged file again?**
A: Yes, you can upload the merged file as File B for another comparison.

**Q: How do I know which file is newer for Source changes?**
A: If you exported File A recently from live store and edited File B locally, then A is newer for Source. If you edited Product descriptions in Shopify after exporting File A, then B is newer.

**Q: Can I undo a merge?**
A: The tool doesn't modify your original files. You can always re-run the comparison and merge with different options.

**Q: What's the difference between this and the CLI tool?**
A: This web tool is specifically designed for Langify workflows with merge functionality. The CLI tool (`csv_compare.py`) is a general-purpose CSV comparison utility.

---

**Version**: 2.0 (with Merge feature)
**Last Updated**: October 2, 2025
**Support**: Project Issue Tracker
