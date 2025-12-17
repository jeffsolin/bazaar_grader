# Bazaar Peer Review Grader - Complete Summary

## What This App Does

The Bazaar Peer Review Grader helps teachers quickly identify problematic group projects by automatically analyzing peer evaluations and financial data. It flags groups with:
- High disagreement about who did the work
- Negative profits
- Concerning feedback keywords (lazy, absent, etc.)
- Math errors in percentage reporting

## Files in This Project

### Core Application
- **`app.py`** - Main Streamlit application (800+ lines)
- **`requirements.txt`** - Python dependencies

### Documentation
- **`README.md`** - User guide and installation instructions
- **`TESTING.md`** - Comprehensive testing guide with expected results
- **`SUMMARY.md`** - This file

### Test Data (in project directory)
- **`test_data.csv`** - 11 realistic peer review submissions using actual student names
- **`2A-Income and Expense Tracking.xlsx`** - Financial data for Group 2A (+$325 profit)
- **`5B-Income and Expense Tracking.xlsx`** - Financial data for Group 5B (-$167 profit, RED FLAG)
- **`6C-Income and Expense Tracking.xlsx`** - Financial data for Group 6C (+$105 profit)

### Real Data (in Downloads folder)
- **`/Users/jeffsolin/Downloads/SY26 LTMaker Bazaar Roster for CSV Export - Sheet1.csv`** - 137 students across 5 periods
- **`/Users/jeffsolin/Downloads/SY26 LTMaker Bazaar Peer Evaluation (Responses) - Form Responses 1.csv`** - Google Form template
- **`/Users/jeffsolin/Downloads/2A-Income and Expense Tracking.xlsx`** - Real financial data example

## Key Features Implemented

### 1. Data Processing
- ✅ Parses Google Form CSV exports (wide format → student evaluations)
- ✅ Extracts group IDs from student names (e.g., "2A - Watts, BriAri")
- ✅ Handles conditional 4th group member
- ✅ Loads multiple financial Excel files with Summary sheet parsing
- ✅ Extracts both group-level and student-level financial data

### 2. Roster Management
- ✅ Upload student roster to track all students by period and group
- ✅ Identify missing submissions
- ✅ Display missing students grouped by period
- ✅ Calculate accurate submission percentages

### 3. Red Flag Detection
The app automatically flags groups when:
- **Workload variance** exceeds threshold (default 15%, configurable 5-30%)
- **Financial profit** is negative
- **Keywords found** in feedback: lazy, absent, rude, nothing, late, didn't, never, refused
- **Percentage math errors**: Student percentages don't sum to 100%

### 4. Dashboard UI Components

#### Summary Statistics
- Total groups analyzed
- Total students (from roster if provided)
- Total submissions received
- Groups with financial data uploaded
- Missing submissions warning

#### Group Analysis Sections
Each group expander shows:
1. **Header**: Color-coded status (🔴 RED / 🟢 GREEN) + profit indicator
2. **Red Flags**: List of detected issues (if any)
3. **Workload Distribution Matrix**: Shows who rated whom at what percentage
4. **Individual Student Financials**: Income, expenses, profit, inventory per student
5. **Work Contributions**: Design, manufacturing, sales, marketing descriptions
6. **Feedback & Reflections**: Challenges, good stuff, advice from each student
7. **Evidence Links**: Clickable Google Drive URLs for files and photos

### 5. Interactive Controls
- **Variance Threshold Slider**: Adjust sensitivity (5-30%)
- **Show Only Red Flags**: Filter to problematic groups
- **Expandable Sections**: Groups auto-expand if flagged

## Test Data Scenarios

### Group 2A - Perfect Team ✅
- **Outcome**: GREEN, no flags
- **Story**: All 4 students agree on contributions (23-27%), positive feedback, good profit
- **Use Case**: Shows what a healthy group looks like

### Group 5B - Dysfunctional Team 🚨
- **Outcome**: RED, multiple flags
- **Story**: Alex absent and lazy (8-18%), Evan did 50%+ of work, negative profit, harsh feedback
- **Use Case**: Demonstrates clear intervention needed

### Group 6C - Mild Issues ⚠️
- **Outcome**: Depends on threshold setting
- **Story**: Kris underperformed slightly (15-18%), others compensated, small profit
- **Use Case**: Shows borderline case that may need conversation

## Technical Details

### Data Formats

**Peer Review CSV (Google Form Export)**
- Wide format: 1 row per student, evaluates all teammates
- Columns include percentages, work descriptions, feedback, evidence URLs
- Student names format: `GroupID - LastName, FirstName`

**Student Roster CSV**
- Columns: Period, Group, Student First Name, Student Last Name
- Used for tracking missing submissions

**Financial Excel Files**
- Filename format: `{GroupID}-Income and Expense Tracking.xlsx`
- Must have "Summary" sheet with:
  - Row with "Total Profit" + value
  - Per-student rows (rows 5+) with: Name | Income | Expenses | Profit | Inventory

### Algorithms

**Workload Variance Calculation**
```
For each student:
  - Collect all percentages assigned to them (including self-evaluation)
  - Variance = max(percentages) - min(percentages)
  - Flag if variance > threshold
```

**Red Flag Keyword Detection**
- Case-insensitive search in all text fields
- Keywords: lazy, absent, rude, nothing, late, didn't, never, refused
- Checks both feedback sections and work descriptions

## How to Use

### Setup
```bash
cd /Users/jeffsolin/Software_Projects/bazaar_grader
pip install -r requirements.txt
streamlit run app.py
```

### Workflow
1. Upload student roster CSV (optional but recommended)
2. Upload Google Form peer evaluation CSV
3. Upload financial Excel files for groups
4. Review summary statistics
5. Check missing submissions (if roster uploaded)
6. Investigate red-flagged groups first
7. Adjust variance threshold if needed
8. Expand groups to see detailed analysis

### For Real Data Collection
1. Students complete Google Form peer evaluation
2. Export responses to CSV
3. Teacher uploads financial Excel files from student projects
4. Upload both to this app
5. Review flagged groups
6. Use detailed breakdowns for grading decisions

## Future Enhancement Ideas

- **Export functionality**: Save red flag groups to PDF/Excel
- **AI analysis**: Use Claude/GPT API to summarize feedback sentiment
- **Photo display**: Show images inline instead of just links
- **Email notifications**: Alert students in red-flagged groups
- **Historical tracking**: Compare group performance across semesters
- **Peer review rubric**: Auto-calculate grades based on contributions
- **Anonymous mode**: Redact names for peer review
- **Mobile-friendly**: Optimize UI for tablet/phone grading

## Dependencies

- `streamlit` >= 1.28.0 - Web app framework
- `pandas` >= 2.0.0 - Data manipulation
- `openpyxl` >= 3.1.0 - Excel file reading
- `numpy` >= 1.24.0 - Numerical operations

## Support

For issues or questions:
- Check `TESTING.md` for troubleshooting
- Review `README.md` for usage instructions
- Examine test data for format examples

---

**Created**: December 13, 2025
**For**: SY26 LTMaker Bazaar Project Grading
**Periods**: 2, 5, 6, 7, 8 (137 total students)
