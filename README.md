# Langify Translation Comparison Tool

A powerful web-based tool for comparing and merging Shopify Langify app Export/Import files. Compare translation versions, track changes, and selectively merge updates with an intuitive interface.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🌟 Features

- **🔍 Comprehensive Comparison**: Compare two Langify export files side-by-side
- **📊 Change Visualization**: See deletions, additions, source changes, and translation updates
- **🔀 Selective Merge**: Choose which changes to include in the final import file
- **📥 Multiple Export Formats**: Download results as CSV or Excel
- **🌐 Bilingual Support**: Full English and Korean documentation
- **💻 User-Friendly Interface**: Web-based interface powered by Streamlit

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. Clone or download this repository:
```bash
git clone https://github.com/yourusername/langify-comparison-tool.git
cd langify-comparison-tool
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

#### Windows
```bash
run.bat
```

#### Linux/Mac
```bash
chmod +x run.sh
./run.sh
```

#### Manual
```bash
streamlit run app.py
```

The application will automatically open in your browser at `http://localhost:8501`

## 📖 Usage

### Step 1: Upload Files

- **File A (Current Live Export)**: Export your current live translations from Langify
- **File B (Modified Export)**: Your locally edited or updated translation file

### Step 2: Compare

Click the "Compare Files" button to analyze differences:
- **Deleted**: Items in Live but not in Modified
- **Added**: New items in Modified
- **Source Changes**: Original text modifications
- **Translation Changes**: Translation updates

### Step 3: Merge (Optional)

Select which changes to include:
- Keep deleted items
- Add new items
- Choose source version (A or B)
- Apply translation changes
- Apply combined changes

### Step 4: Download

Download the comparison report or merged file in CSV/Excel format and import back to Langify.

## 📚 Documentation

- **[English Guide](LANGIFY_GUIDE_EN.md)**: Complete usage guide with workflows and troubleshooting
- **[한국어 가이드](LANGIFY_GUIDE_KR.md)**: 완전한 사용 가이드 및 문제 해결

## 🔧 File Requirements

Your Langify export CSV files must have:
- **Column 1**: ID (unique identifier)
- **Column 2**: Name (translation key)
- **Column 3**: Source (original text)
- **Column 4**: Translation (translated text)

The tool uses **ID + Name** as the unique key for matching records.

## 💡 Common Workflows

### Workflow 1: Local Translation Updates
1. Export current translations from Langify → File A
2. Edit translations locally in Excel
3. Upload both files and compare
4. Merge changes and re-import to Langify

### Workflow 2: Track Changes Over Time
1. Export translations (version 1) → File A
2. Make changes in Shopify over time
3. Export translations (version 2) → File B
4. Compare to see what changed

### Workflow 3: Integrate Translator's Work
1. Export current live translations → File A
2. Receive updated file from translator → File B
3. Review translation changes
4. Selectively merge and import

## 🛠️ Technical Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas
- **Export**: openpyxl (Excel generation)

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 💬 Support

For issues, questions, or feature requests, please open an issue on GitHub.

## 📧 Contact

Project Link: [https://github.com/tokincode/langify-comparison-tool](https://github.com/tokincode/langify-comparison-tool)

---

**Version**: 2.0 (with Merge feature)
**Last Updated**: October 2025
**Made with** ❤️ **for Shopify Langify users**
