# Testing the Bazaar Grader - Updated Version

## Quick Start

1. **Launch the app:**
   ```bash
   cd /Users/jeffsolin/Software_Projects/bazaar_grader
   streamlit run app.py
   ```

2. **Upload test data in this order:**
   - **Student Roster**: Upload `/Users/jeffsolin/Downloads/SY26 LTMaker Bazaar Roster for CSV Export - Sheet1.csv`
   - **Peer Review CSV**: Upload `test_data.csv`
   - **Financial Files**: Upload all three Excel files:
     - `2A-Income and Expense Tracking.xlsx`
     - `5B-Income and Expense Tracking.xlsx`
     - `6C-Income and Expense Tracking.xlsx`

## Expected Results

### Summary Dashboard
- **Total Groups**: 3
- **Total Students**: 137 (from roster) or 11 (submitted)
- **Total Submissions**: 11
- **Groups w/ Financials**: 3
- **Missing Submissions Warning**: Should show 126 students haven't submitted, grouped by period

### Group 2A (Period 2): 🟢 GREEN - Excellent Group
- **Status**: No flags (all green)
- **Financial**: +$325.00 profit
- **Variance**: ~2-3% (very low disagreement)
- **Students**: BriAri Watts, Chiebuka Nwaezeigwe, Vernon Cole, Jaz Gonzalez-Valdez
- **Details**:
  - All 4 students submitted
  - Everyone agrees on percentages (23-27%)
  - Positive feedback throughout
  - Individual student profits: $72-93 each
- **Expected Behavior**: Should NOT be red-flagged at any threshold

### Group 5B (Period 5): 🔴 RED FLAG - Major Problems
- **Status**: Multiple red flags
- **Financial**: -$167.00 profit (NEGATIVE)
- **Variance**: ~35-44% disagreement on Alex
- **Students**: Alex Deakins, Evan Klein, Brayden Chen
- **Details**:
  - Alex claims 18% but others say 8%
  - Evan did 47-52% of work (almost half!)
  - Contains keywords: "absent", "didn't follow through", "never did it"
  - Negative individual profits for all students
- **Expected Flags**:
  - ✅ High workload variance (35-44%)
  - ✅ Negative profit (-$167)
  - ✅ Red flag keywords: "absent", "didn't", "never"
  - ✅ Percentage sum errors

### Group 6C (Period 6): ⚠️ ORANGE - Moderate Issues
- **Status**: Depends on variance threshold
- **Financial**: +$105.00 profit
- **Variance**: ~15-19% disagreement
- **Students**: Joey Lopez, Ritchie Dang, Theo Nelson, Kris Diaz
- **Details**:
  - Kris underperformed (claims 18%, others say 15%)
  - Joey and Ritchie did most of work (30-35% each)
  - Positive profit but concerns about engagement
  - Individual student profits: $20-35 each
- **Expected Behavior**:
  - At 15% threshold: Should be flagged
  - At 20% threshold: Should NOT be flagged

## New Features to Test

### 1. Roster Upload
- [ ] Upload roster CSV
- [ ] Verify "Total Students" changes from 11 to 137
- [ ] Check "Missing Submissions" warning appears

### 2. Missing Submissions
- [ ] Expand "View Missing Submissions"
- [ ] Verify students grouped by period (2, 5, 6, 7, 8)
- [ ] Check that submitted students (2A, 5B, 6C members) are NOT in missing list
- [ ] Verify format: "Group: FirstName LastName"

### 3. Individual Student Financials
- [ ] Expand Group 2A
- [ ] Look for "Individual Student Financials" section
- [ ] Verify table shows Income, Expenses, Profit, Inventory for each student
- [ ] Check Group 5B shows negative profits for students
- [ ] Verify Group 6C shows varied individual profits

### 4. Workload Distribution Matrix
- [ ] Check matrix shows evaluator names as columns
- [ ] Verify "(self)" label appears for self-evaluations
- [ ] Check "Variance" column shows disagreement
- [ ] Group 5B: Alex should have high variance

### 5. Red Flag Detection
- [ ] Group 2A: Should be GREEN with no flags
- [ ] Group 5B: Should be RED with multiple flags listed
- [ ] Try adjusting variance threshold slider:
  - At 10%: Group 6C should flag
  - At 20%: Only Group 5B should flag
- [ ] Toggle "Show only Red Flag groups" - should hide 2A (and maybe 6C)

### 6. Work Descriptions & Feedback
- [ ] Verify all design/manufacturing/sales/marketing descriptions appear
- [ ] Check "Challenges", "Good Stuff", "Advice" sections populate
- [ ] Evidence and Photo links should be clickable

## Troubleshooting

### If missing submissions don't show:
- Make sure you uploaded the roster CSV FIRST
- Check that student names in roster match format in peer review CSV

### If individual financials don't appear:
- Verify Excel files have "Summary" sheet
- Check that student names in Excel match roster format (FirstName LastName or LastName, FirstName)
- Names in test data: "Jaz Gonzalez-Valdez" should match in both files

### If groups don't match periods:
- Group 2A = Period 2
- Group 5B = Period 5
- Group 6C = Period 6

## Real Data Testing

When you have real student submissions:
1. Upload the actual roster CSV
2. Upload the Google Form export
3. Upload financial Excel files matching group IDs
4. Look for red flags and investigate concerning groups first
5. Use variance threshold to tune sensitivity
6. Export/screenshot problematic groups for grading records
