# Bazaar Peer Review Grader

A Streamlit web application for teachers to analyze peer review data from group projects and identify "red flag" groups that may need intervention.

## Features

- **Automated Red Flag Detection**: Identifies groups with high workload disagreement, negative profits, or concerning feedback keywords
- **Workload Variance Analysis**: Calculates discrepancies between self-reported and peer-reported work percentages
- **Financial Integration**: Matches financial spreadsheets to groups and displays profit/loss
- **Detailed Feedback View**: Shows all qualitative feedback, work descriptions, and evidence links
- **Configurable Thresholds**: Adjust the workload variance threshold via a slider

## Installation

1. Navigate to the project directory:
```bash
cd /Users/jeffsolin/Software_Projects/bazaar_grader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Upload your data:
   - **Peer Review CSV**: Export from Google Forms
   - **Financial Files**: Excel or CSV files with naming format `{GroupID}-Income and Expense Tracking`

3. Review the dashboard:
   - Groups with red flags are marked with 🔴
   - Expand each group to see detailed analysis
   - Use the sidebar to filter and adjust settings

## Data Format

### Peer Review CSV
The app expects a CSV export from Google Forms with columns for:
- Student names (format: `GroupID - LastName, FirstName`)
- Percentage of work/effort for each team member
- Work descriptions (Design, Manufacturing, Sales, Marketing)
- Qualitative feedback (Challenges, Good Stuff, Advice)
- Evidence and photo URLs

### Financial Files
Excel or CSV files with naming convention: `{GroupID}-Income and Expense Tracking`
The app will attempt to extract profit/loss from these files automatically.

## Red Flag Criteria

Groups are flagged if ANY of the following conditions are met:

1. **High Workload Variance**: Difference between self-reported and peer-reported percentages exceeds threshold (default 15%)
2. **Negative Financial Profit**: The group lost money
3. **Red Flag Keywords**: Feedback contains words like "lazy", "absent", "rude", "nothing", "late"
4. **Percentage Math Errors**: Student percentages don't sum to 100%

## Customization

You can adjust the following in the sidebar:
- **Variance Threshold**: Set the percentage difference that triggers a flag
- **Show Only Red Flags**: Filter to display only problematic groups

## Tips

- Expand red-flagged groups first to quickly identify issues
- Use the workload distribution matrix to see discrepancies at a glance
- Click evidence and photo links to review student submissions
- The "He Said / She Said" feedback section shows conflicting accounts

## Troubleshooting

If financial data isn't loading:
- Verify filename format: `{GroupID}-Income and Expense Tracking`
- Ensure group ID in filename matches group ID in peer review data
- Check that the Excel/CSV file contains recognizable profit/income/expense data
