# Developer Guide - Bazaar Peer Review Grader

## Project Overview
Streamlit web app for analyzing group project peer evaluations and financial data. Automatically detects "red flag" groups with workload imbalances, low sales, negative profits, or concerning feedback.

## Quick Start

### Local Development
```bash
cd /Users/jeffsolin/Software_Projects/bazaar_grader
streamlit run app.py
```

### Making Changes
1. Edit files locally (usually `app.py`)
2. Test locally with `streamlit run app.py`
3. Commit in GitHub Desktop
4. Push to GitHub (click "Push origin")
5. Streamlit Cloud auto-deploys in 1-2 minutes

## File Structure

```
/Users/jeffsolin/Software_Projects/bazaar_grader/
├── app.py                          # Main application (850+ lines)
├── requirements.txt                # Python dependencies
├── README.md                       # User guide
├── TESTING.md                      # Testing instructions
├── SUMMARY.md                      # Feature summary
├── DEVELOPER_GUIDE.md             # This file
├── .gitignore                      # Git ignore rules
├── test_data.csv                   # Test peer review data
├── 2A-Income and Expense Tracking.xlsx  # Test financial data (good group)
├── 5B-Income and Expense Tracking.xlsx  # Test financial data (red flags)
└── 6C-Income and Expense Tracking.xlsx  # Test financial data (borderline)
```

## Key Technical Details

### Data Flow
1. **Input**: Google Form CSV (wide format) + Excel files (financial data)
2. **Processing**:
   - Parse peer reviews → extract groups, percentages, feedback
   - Load Excel Summary sheets → extract group/student financials
   - Calculate variance, detect red flags
3. **Output**: Interactive dashboard with expandable groups

### Core Functions in app.py

**Data Parsing**
- `parse_peer_review_data(df)` - Lines 22-150
  - Transforms wide-format CSV to structured evaluations
  - Deduplicates submissions (keeps most recent)
  - Extracts percentages, work descriptions, feedback, evidence URLs

- `extract_student_financials(excel_file, group_id)` - Lines 152-220
  - Reads Excel Summary sheet
  - Matches student names between CSV ("Last, First") and Excel ("First Last")
  - Returns per-student income, expenses, profit, inventory

**Red Flag Detection**
- `analyze_group_flags(...)` - Lines 320-450
  - Checks workload variance > threshold
  - Checks low workload (< 60% of fair share)
  - Checks negative profit
  - Checks red flag keywords in feedback
  - Returns list of flags

- `check_low_sales(...)` - Lines 452-490
  - Flags students with income < 50% of group average
  - Only flags if avg income > $10 (avoids false positives)

**Visual Highlighting**
- `highlight_keywords(text)` - Lines 229-245
  - Wraps red flag keywords in pink background HTML spans
  - Keywords: lazy, absent, rude, nothing, late, didn't, never, refused

- Workload matrix highlighting - Lines 890-912
  - 🔴 emoji for percentages below threshold
  - 🔴 emoji for variance above threshold

- Financial table highlighting - Lines 978-988
  - 🔴 emoji for low income (< 50% of average)
  - 🔴 emoji for negative profit

**Display Functions**
- `display_group(...)` - Lines 808-1100
  - Renders group expander with all info
  - Workload distribution matrix
  - Individual student financials
  - Work contributions and feedback
  - Evidence/photo links

### Important Variables

**Red Flag Thresholds**
- `variance_threshold` - Default 15%, adjustable 5-30% (line 688)
- `low_workload_threshold` - 60% of fair share (line 380)
- `low_sales_threshold` - 50% of group average income (line 465)

**Data Formats**
- Peer review CSV: Wide format (1 row per student, columns for each teammate)
- Student names in CSV: "GroupID - Last, First" (e.g., "2A - Watts, BriAri")
- Student names in Excel: "First Last" (e.g., "BriAri Watts")
- Excel files: `{GroupID}-Income and Expense Tracking.xlsx`

## Common Issues & Solutions

### Issue: Student financials not showing
**Cause**: Name mismatch between CSV and Excel
**Solution**: Check that Excel has "First Last" format and CSV has "GroupID - Last, First"

### Issue: Duplicate submissions
**Cause**: Student submitted multiple times or test entries exist
**Solution**: App auto-deduplicates (keeps most recent by timestamp)

### Issue: Workload matrix shows all same percentages
**Cause**: Might be actual perfect agreement (like Group 2A)
**Solution**: Verify by checking individual submissions - if everyone actually agrees, this is correct

### Issue: HEIC photos not showing thumbnails
**Cause**: Google Drive HEIC files can't be converted to thumbnails via URL
**Solution**: App shows HEIC files as clickable links instead of thumbnails

### Issue: App crashes on Streamlit Cloud
**Cause**: Usually missing dependency or file path issue
**Solution**: Check logs in Streamlit Cloud dashboard, verify requirements.txt

## Test Data Details

### test_data.csv
- 11 realistic submissions using actual student names from roster
- 3 groups with different scenarios:
  - **Group 2A**: Perfect team, all agree on contributions (23-27% each)
  - **Group 5B**: Dysfunctional - Alex underperformed (8-18%), Evan overworked (50%+)
  - **Group 6C**: Borderline - Kris slightly low (15-18%), triggers at lower thresholds

### Financial Excel Files
- **2A**: +$325 profit, balanced sales
- **5B**: -$167 profit, Alex's low sales trigger red flag
- **6C**: +$105 profit, small variance

## Real Data Locations

**DO NOT COMMIT THESE FILES TO GITHUB** (they're in .gitignore)

- Full roster: `/Users/jeffsolin/Downloads/SY26 LTMaker Bazaar Roster for CSV Export - Sheet1.csv`
  - 137 students across periods 2, 5, 6, 7, 8

- Period 2 submissions: `/Users/jeffsolin/Downloads/SY26 LTMaker Bazaar Peer Evaluation (Responses) - Form Responses 1 (1).csv`

- Period 2 financials: `/Users/jeffsolin/Downloads/Period 2 Excel/`
  - Example: `2A-Income and Expense Tracking.xlsx`

## Deployment Info

### GitHub
- **Repository**: https://github.com/YOUR_USERNAME/bazaar_grader
- **Visibility**: Must be PUBLIC for free Streamlit Cloud
- **Branch**: main

### Streamlit Cloud
- **Dashboard**: https://share.streamlit.io/
- **App URL**: https://YOUR_USERNAME-bazaar-grader.streamlit.app (or similar)
- **Auto-deployment**: Watches GitHub repo, rebuilds on push (1-2 min)

### Update Workflow
```bash
# 1. Make changes locally
# 2. Test
streamlit run app.py

# 3. Commit & push (via GitHub Desktop or CLI)
git add .
git commit -m "Description of changes"
git push

# 4. Wait for Streamlit Cloud to auto-deploy
```

## Dependencies (requirements.txt)

```
streamlit>=1.28.0
pandas>=2.0.0
openpyxl>=3.1.0
numpy>=1.24.0
```

## Future Enhancement Ideas

- [ ] Export red flag groups to PDF/Excel
- [ ] AI sentiment analysis of feedback (Claude/GPT API)
- [ ] Inline photo display (not just links)
- [ ] Email notifications for red-flagged groups
- [ ] Historical tracking across semesters
- [ ] Auto-grading based on contribution percentages
- [ ] Mobile-friendly UI optimization
- [ ] Percentage math error detection (don't sum to 100%)

## Privacy & Security Notes

- App processes uploads in-memory (no data stored on server)
- Users must upload files each session
- .gitignore prevents committing real student data
- Test data uses real names but fake evaluations
- Google Drive links respect original permission settings

## Key Code Sections to Know

### Adding a New Red Flag Type
1. Add detection logic in `analyze_group_flags()` (around line 320)
2. Add flag to returned list
3. Add highlighting in `display_group()` if needed

### Changing Threshold Defaults
- Variance: Line 688 (slider default value)
- Low workload: Line 380 (60% factor)
- Low sales: Line 465 (50% factor)

### Modifying UI Layout
- Main layout: Lines 650-800
- Group expander: Lines 808-1100
- Summary stats: Lines 600-650

### Debugging Tips
- Run locally with: `streamlit run app.py`
- Check Streamlit Cloud logs for deployment errors
- Use `st.write()` for quick debugging output
- Use `st.exception(e)` to show full stack traces

## Contact & Support

For issues with this app, check:
1. This guide
2. TESTING.md for expected behavior
3. README.md for user instructions
4. Streamlit Cloud logs for deployment issues

---

**Last Updated**: December 17, 2025
**Created By**: Claude Code
**For**: SY26 LTMaker Bazaar Project Grading
