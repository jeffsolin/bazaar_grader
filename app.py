import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import re

# Page configuration
st.set_page_config(
    page_title="Bazaar Peer Review Grader",
    page_icon="📊",
    layout="wide"
)

# Helper Functions
def extract_group_id(student_name):
    """Extract group ID from student name (e.g., '2A - Watts, BriAri' -> '2A')"""
    if pd.isna(student_name) or student_name == "":
        return None
    match = re.match(r'^([^-]+)', str(student_name).strip())
    return match.group(1).strip() if match else None

def parse_peer_review_data(df):
    """
    Transform wide-format peer review data into structured format.
    Returns a dict of groups with student evaluations.
    Only keeps the most recent submission per student (in case of duplicates).
    """
    # First, deduplicate: keep only the most recent submission per student
    df_sorted = df.sort_values('Timestamp', ascending=False)
    df_deduped = df_sorted.drop_duplicates(subset=['YOU - Group Member 1'], keep='first')

    groups = {}

    for idx, row in df_deduped.iterrows():
        # Extract submitter info
        submitter_name = row.get('YOU - Group Member 1', '')
        group_id = extract_group_id(submitter_name)

        if not group_id:
            continue

        if group_id not in groups:
            groups[group_id] = {
                'students': set(),
                'evaluations': [],
                'feedback': []
            }

        # Add submitter to students set
        groups[group_id]['students'].add(submitter_name)

        # Parse evaluations for all team members
        evaluation = {
            'submitter': submitter_name,
            'timestamp': row.get('Timestamp', ''),
            'percentages': {},
            'work_descriptions': {},
            'evidence_urls': [],
            'photo_urls': []
        }

        # Member 1 (submitter/self)
        member1_pct = row.get('Your percentage of work / effort', 0)
        evaluation['percentages'][submitter_name] = parse_percentage(member1_pct)
        evaluation['work_descriptions'][submitter_name] = {
            'design': row.get('Please explain what you did regarding DESIGN work on the project. ', ''),
            'manufacturing': row.get('Please explain what you did regarding MANUFACTURING work on the project. ', ''),
            'sales': row.get('Please explain what you did regarding SALES / MANAGEMENT work on the project. ', ''),
            'marketing': row.get('Please explain what you did regarding MARKETING / ADVERTISING work on the project. ', '')
        }

        # Member 2
        member2_name = row.get('Group Member 2', '')
        if member2_name and not pd.isna(member2_name):
            groups[group_id]['students'].add(member2_name)
            member2_pct = row.get('Group Member 2 percentage of work / effort', 0)
            evaluation['percentages'][member2_name] = parse_percentage(member2_pct)
            evaluation['work_descriptions'][member2_name] = {
                'design': row.get('Please explain what Group Member 2 did regarding DESIGN work on the project. ', ''),
                'manufacturing': row.get('Please explain what Group Member 2 did regarding MANUFACTURING work on the project. ', ''),
                'sales': row.get('Please explain what Group Member 2 did regarding SALES / MANAGEMENT work on the project. ', ''),
                'marketing': row.get('Please explain what Group Member 2 did regarding MARKETING / ADVERTISING work on the project. ', '')
            }

        # Member 3
        member3_name = row.get('Group Member 3', '')
        if member3_name and not pd.isna(member3_name):
            groups[group_id]['students'].add(member3_name)
            member3_pct = row.get('Group Member 3 percentage of work / effort', 0)
            evaluation['percentages'][member3_name] = parse_percentage(member3_pct)
            evaluation['work_descriptions'][member3_name] = {
                'design': row.get('Please explain what Group Member 3 did regarding DESIGN work on the project. ', ''),
                'manufacturing': row.get('Please explain what Group Member 3 did regarding MANUFACTURING work on the project. ', ''),
                'sales': row.get('Please explain what Group Member 3 did regarding SALES / MANAGEMENT work on the project. ', ''),
                'marketing': row.get('Please explain what Group Member 3 did regarding MARKETING / ADVERTISING work on the project. ', '')
            }

        # Member 4 (conditional)
        has_member4 = row.get('Did you have a 4th member of your group?', '')
        if has_member4 and str(has_member4).lower() == 'yes':
            member4_name = row.get('Group Member 4', '')
            if member4_name and not pd.isna(member4_name):
                groups[group_id]['students'].add(member4_name)
                member4_pct = row.get('Group Member 4 percentage of work / effort', 0)
                evaluation['percentages'][member4_name] = parse_percentage(member4_pct)
                evaluation['work_descriptions'][member4_name] = {
                    'design': row.get('Please explain what Group Member 4 did regarding DESIGN work on the project. ', ''),
                    'manufacturing': row.get('Please explain what Group Member 4 did regarding MANUFACTURING work on the project. ', ''),
                    'sales': row.get('Please explain what Group Member 4 did regarding SALES / MANAGEMENT work on the project. ', ''),
                    'marketing': row.get('Please explain what Group Member 4 did regarding MARKETING / ADVERTISING work on the project. ', '')
                }

        # Collect evidence URLs (per student submission)
        evidence_col = 'Evidence to include:\n- Evidence of effort or lack thereof\n- If you followed my advice and communicated over a group chat, Snap, GChat / etc, you can submit screenshots of your communications if needed (not required but can bolster a claim)\n- Include all files related to your work, especially Adobe Illustrator files.'
        evidence_urls = row.get(evidence_col, '')
        if evidence_urls and not pd.isna(evidence_urls):
            evaluation['evidence_urls'] = parse_urls(evidence_urls)

        # Collect photo URLs (per student submission)
        photo_col = 'Photos of your items\n- Include clear photos of each item that you either made yourself or strongly contributed to, INCLUDING your mini sheet item and your advanced item(s)'
        photo_urls = row.get(photo_col, '')
        if photo_urls and not pd.isna(photo_urls):
            evaluation['photo_urls'] = parse_urls(photo_urls)

        groups[group_id]['evaluations'].append(evaluation)

        # Collect feedback
        feedback = {
            'submitter': submitter_name,
            'challenges': row.get('Challenges', ''),
            'good_stuff': row.get('The Good Stuff', ''),
            'advice': row.get('One (or more) pieces of solid advice', '')
        }
        groups[group_id]['feedback'].append(feedback)

    return groups

def parse_percentage(value):
    """Convert percentage value to float"""
    if pd.isna(value) or value == '':
        return 0.0
    try:
        # Remove % sign if present
        value_str = str(value).replace('%', '').strip()
        return float(value_str)
    except:
        return 0.0

def parse_urls(url_string):
    """Extract URLs from comma-separated string"""
    if pd.isna(url_string) or url_string == '':
        return []
    urls = [url.strip() for url in str(url_string).split(',')]
    return [url for url in urls if url]

def convert_gdrive_to_thumbnail(url):
    """Convert Google Drive URL to thumbnail/viewable format"""
    # Extract file ID from various Google Drive URL formats
    import re

    # Pattern 1: /open?id=FILE_ID
    match = re.search(r'id=([a-zA-Z0-9_-]+)', url)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/thumbnail?id={file_id}&sz=w400"

    # Pattern 2: /file/d/FILE_ID
    match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', url)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/thumbnail?id={file_id}&sz=w400"

    # Return original if no match
    return url

def calculate_workload_variance(group_data):
    """
    Calculate workload variance for each student.
    Returns dict of {student: variance_score}
    """
    students = list(group_data['students'])
    evaluations = group_data['evaluations']

    variance_scores = {}

    for student in students:
        # Get all percentages assigned to this student
        percentages = []
        for eval in evaluations:
            if student in eval['percentages']:
                percentages.append(eval['percentages'][student])

        if len(percentages) > 1:
            # Calculate variance as max difference
            variance = max(percentages) - min(percentages)
            variance_scores[student] = variance
        else:
            variance_scores[student] = 0

    return variance_scores

def check_percentage_sum(group_data):
    """Check if percentages sum to 100 for each evaluation"""
    issues = []
    for eval in group_data['evaluations']:
        total = sum(eval['percentages'].values())
        if abs(total - 100) > 0.1:  # Allow small floating point errors
            issues.append({
                'submitter': eval['submitter'],
                'total': total
            })
    return issues

def detect_red_flag_keywords(text):
    """Check for red flag keywords in feedback"""
    if pd.isna(text) or text == '':
        return []

    red_flags = ['lazy', 'absent', 'rude', 'nothing', 'late', 'didn\'t', 'never', 'refused']
    text_lower = str(text).lower()

    found = []
    for flag in red_flags:
        if flag in text_lower:
            found.append(flag)

    return found

def highlight_keywords(text):
    """Highlight red flag keywords in text with red background"""
    if pd.isna(text) or text == '':
        return text

    red_flags = ['lazy', 'absent', 'rude', 'nothing', 'late', 'didn\'t', 'never', 'refused']

    highlighted_text = str(text)
    for keyword in red_flags:
        # Case-insensitive replacement with highlighted version
        import re
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        highlighted_text = pattern.sub(
            f'<span style="background-color: #ffcccc; padding: 2px 4px; border-radius: 3px; font-weight: bold;">{keyword}</span>',
            highlighted_text
        )

    return highlighted_text

def check_low_sales(group_data, student_financials):
    """
    Check if any student has significantly lower sales than groupmates.
    Returns list of (student_name, income, avg_income) tuples for low performers.
    """
    if not student_financials:
        return []

    students = list(group_data['students'])

    # Collect income data for all students in the group
    incomes = []
    student_income_map = {}

    for student in students:
        # Convert "GroupID - Last, First" to "First Last" for matching
        student_short = student.split(' - ')[1] if ' - ' in student else student

        if ', ' in student_short:
            parts = student_short.split(', ')
            if len(parts) == 2:
                excel_name = f"{parts[1]} {parts[0]}"
            else:
                excel_name = student_short
        else:
            excel_name = student_short

        # Try to find this student in financials
        if excel_name in student_financials:
            income = student_financials[excel_name]['income']
            incomes.append(income)
            student_income_map[student_short] = income
        else:
            # Try partial match
            for fin_name, fin_info in student_financials.items():
                excel_parts = excel_name.split()
                fin_parts = fin_name.split()
                if excel_parts and fin_parts and excel_parts[-1].lower() == fin_parts[-1].lower():
                    income = fin_info['income']
                    incomes.append(income)
                    student_income_map[student_short] = income
                    break

    if len(incomes) < 2:
        # Need at least 2 students to compare
        return []

    # Calculate average income
    avg_income = sum(incomes) / len(incomes)

    # Flag students with income < 50% of average (and average is meaningful)
    low_sellers = []
    if avg_income > 10:  # Only flag if average is at least $10
        for student_short, income in student_income_map.items():
            if income < avg_income * 0.5:  # Less than 50% of average
                low_sellers.append((student_short, income, avg_income))

    return low_sellers

def analyze_group_flags(group_data, financial_profit, variance_threshold, student_financials=None):
    """
    Analyze group and return red flag status and reasons.
    """
    flags = []

    # Check workload variance
    variance_scores = calculate_workload_variance(group_data)
    max_variance = max(variance_scores.values()) if variance_scores else 0

    if max_variance > variance_threshold:
        flags.append(f"High workload variance ({max_variance:.1f}%)")

    # Check for students not pulling their weight (below fair share)
    num_students = len(group_data['students'])
    expected_pct = 100.0 / num_students
    threshold_pct = expected_pct * 0.6  # Flag if below 60% of fair share

    # Calculate average percentage assigned to each student
    student_avg_pcts = {}
    for student in group_data['students']:
        percentages = []
        for eval in group_data['evaluations']:
            if student in eval['percentages']:
                percentages.append(eval['percentages'][student])
        if percentages:
            student_avg_pcts[student] = sum(percentages) / len(percentages)

    low_contributors = []
    for student, avg_pct in student_avg_pcts.items():
        if avg_pct < threshold_pct:
            student_short = student.split(' - ')[1] if ' - ' in student else student
            low_contributors.append((student_short, avg_pct, expected_pct))

    if low_contributors:
        for student_name, avg_pct, expected in low_contributors:
            flags.append(f"Low workload: {student_name} ({avg_pct:.1f}% vs expected {expected:.1f}%)")

    # Check financial profit
    if financial_profit is not None and financial_profit < 0:
        flags.append(f"Negative profit (${financial_profit:.2f})")

    # Check for low sales compared to group (if we have student financial data)
    if student_financials:
        low_sellers = check_low_sales(group_data, student_financials)
        if low_sellers:
            for student_name, income, avg_income in low_sellers:
                flags.append(f"Low sales: {student_name} (${income:.2f} vs avg ${avg_income:.2f})")

    # Check for keyword red flags in feedback
    keyword_flags = []
    for feedback in group_data['feedback']:
        for field in ['challenges', 'good_stuff', 'advice']:
            keywords = detect_red_flag_keywords(feedback.get(field, ''))
            if keywords:
                keyword_flags.extend(keywords)

    # Check in work descriptions
    for eval in group_data['evaluations']:
        for student, descriptions in eval['work_descriptions'].items():
            for work_type, desc in descriptions.items():
                keywords = detect_red_flag_keywords(desc)
                if keywords:
                    keyword_flags.extend(keywords)

    if keyword_flags:
        unique_keywords = list(set(keyword_flags))
        flags.append(f"Red flag keywords: {', '.join(unique_keywords)}")

    # Check percentage sum issues
    pct_issues = check_percentage_sum(group_data)
    if pct_issues:
        flags.append(f"Percentage sum errors ({len(pct_issues)} submissions)")

    is_red_flag = len(flags) > 0

    return is_red_flag, flags, variance_scores

def load_roster(roster_file):
    """
    Load student roster from CSV.
    Returns dict with group info and list of all students.
    """
    if roster_file is None:
        return None

    df = pd.read_csv(roster_file)

    roster = {
        'students': [],
        'groups': {},
        'periods': {}
    }

    for idx, row in df.iterrows():
        period = row['Period']
        group = row['Group']
        first_name = row['Student First Name']
        last_name = row['Student Last Name']

        # Format student name to match peer review format
        student_name = f"{group} - {last_name}, {first_name}"

        student_info = {
            'name': student_name,
            'first_name': first_name,
            'last_name': last_name,
            'group': group,
            'period': period
        }

        roster['students'].append(student_info)

        # Group by group ID
        if group not in roster['groups']:
            roster['groups'][group] = []
        roster['groups'][group].append(student_info)

        # Group by period
        if period not in roster['periods']:
            roster['periods'][period] = []
        roster['periods'][period].append(student_info)

    return roster

def get_missing_submissions(roster, groups):
    """
    Find students who haven't submitted peer reviews.
    Returns list of student info dicts.
    """
    if roster is None:
        return []

    # Get set of students who have submitted
    submitted_students = set()
    for group_data in groups.values():
        for eval in group_data['evaluations']:
            submitted_students.add(eval['submitter'])

    # Find missing students
    missing = []
    for student_info in roster['students']:
        if student_info['name'] not in submitted_students:
            missing.append(student_info)

    return missing

def extract_student_financials(uploaded_file):
    """
    Extract per-student financial data from Summary sheet.
    Returns dict of {student_name: {income, expenses, profit, inventory}}
    Student names in Excel are "First Last" format.
    """
    try:
        df = pd.read_excel(uploaded_file, sheet_name='Summary')

        student_financials = {}

        # Look for header row with "Group Member"
        header_row_idx = None
        for idx, row in df.iterrows():
            first_col = df.columns[0]
            cell_value = str(row[first_col]).lower()
            if 'group member' in cell_value:
                header_row_idx = idx
                break

        if header_row_idx is None:
            return {}

        # Student data starts right after header row
        for idx, row in df.iterrows():
            if idx <= header_row_idx:
                continue

            # Check if first column looks like a student name
            first_col = df.columns[0]
            student_name = str(row[first_col]).strip()

            if pd.isna(student_name) or student_name == '' or student_name == 'nan':
                continue

            # Skip summary/total rows
            if any(keyword in student_name.lower() for keyword in ['total', 'summary', 'grand']):
                continue

            try:
                # Extract financial data
                # Handle both numeric and string values (with $ signs)
                def parse_currency(val):
                    if pd.isna(val):
                        return 0
                    if isinstance(val, (int, float)):
                        return float(val)
                    # Remove $ and convert
                    val_str = str(val).replace('$', '').replace(',', '').strip()
                    try:
                        return float(val_str)
                    except:
                        return 0

                income = parse_currency(row[df.columns[1]]) if len(df.columns) > 1 else 0
                expenses = parse_currency(row[df.columns[2]]) if len(df.columns) > 2 else 0
                profit = parse_currency(row[df.columns[3]]) if len(df.columns) > 3 else 0
                inventory = parse_currency(row[df.columns[4]]) if len(df.columns) > 4 else 0

                # Store with "First Last" format
                student_financials[student_name] = {
                    'income': income,
                    'expenses': expenses,
                    'profit': profit,
                    'inventory': inventory
                }
            except Exception as e:
                continue

        return student_financials
    except:
        return {}

def load_financial_data(uploaded_files):
    """
    Load financial data from uploaded Excel/CSV files.
    Returns tuple: (group_financials, student_financials)
    - group_financials: dict of {group_id: profit_value}
    - student_financials: dict of {group_id: {student_name: {income, expenses, profit, inventory}}}
    """
    group_financials = {}
    student_financials = {}

    for uploaded_file in uploaded_files:
        filename = uploaded_file.name

        # Extract group ID from filename (e.g., "2A-Income and Expense Tracking.xlsx" -> "2A")
        match = re.match(r'^([^-]+)', filename)
        if not match:
            continue

        group_id = match.group(1).strip()

        try:
            # Load file - try to read Summary sheet first for Excel files
            if filename.endswith('.xlsx'):
                try:
                    # Try to read the Summary sheet specifically
                    df = pd.read_excel(uploaded_file, sheet_name='Summary')

                    # Extract student-level financials
                    student_financials[group_id] = extract_student_financials(uploaded_file)
                except:
                    # Fall back to default sheet
                    df = pd.read_excel(uploaded_file)
            elif filename.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                continue

            # Look for profit calculation
            profit = calculate_profit_from_financial_file(df)
            group_financials[group_id] = profit

        except Exception as e:
            st.sidebar.warning(f"Could not process {filename}: {str(e)}")

    return group_financials, student_financials

def calculate_profit_from_financial_file(df):
    """
    Calculate profit from financial spreadsheet.
    Expects Summary sheet with structure:
    - Row with "Total Profit" label in first column
    - Profit value in second column
    """
    # Strategy 1: Look for "Total Profit" row (matches actual Excel format)
    for idx, row in df.iterrows():
        # Check all columns for "Total Profit" text
        for col_idx, col in enumerate(df.columns):
            cell_value = str(row[col]).lower().strip()
            if 'total profit' in cell_value:
                # Get the value from the next column
                if col_idx + 1 < len(df.columns):
                    next_col = df.columns[col_idx + 1]
                    profit_value = row[next_col]
                    try:
                        return float(profit_value)
                    except:
                        pass

    # Strategy 2: Look for any cell containing "profit" in first column
    if len(df.columns) > 1:
        first_col = df.columns[0]
        second_col = df.columns[1]

        for idx, row in df.iterrows():
            label = str(row[first_col]).lower()
            if 'profit' in label and 'total' in label:
                try:
                    return float(row[second_col])
                except:
                    pass

    # Strategy 3: Look for "Total Income" and "Total Expenses" to calculate
    total_income = None
    total_expenses = None

    for idx, row in df.iterrows():
        for col_idx, col in enumerate(df.columns):
            cell_value = str(row[col]).lower().strip()

            if 'total income' in cell_value:
                if col_idx + 1 < len(df.columns):
                    next_col = df.columns[col_idx + 1]
                    try:
                        total_income = float(row[next_col])
                    except:
                        pass

            if 'total expense' in cell_value:
                if col_idx + 1 < len(df.columns):
                    next_col = df.columns[col_idx + 1]
                    try:
                        total_expenses = float(row[next_col])
                    except:
                        pass

    if total_income is not None and total_expenses is not None:
        return total_income - total_expenses

    # Strategy 4: Generic fallback - look for any "profit" label
    for idx, row in df.iterrows():
        for col_idx, col in enumerate(df.columns):
            cell_value = str(row[col]).lower()
            if 'profit' in cell_value or 'net' in cell_value:
                # Try to find a numeric value in the same row
                for check_col in df.columns[col_idx:]:
                    val = row[check_col]
                    if pd.notna(val):
                        try:
                            return float(val)
                        except:
                            pass

    return None

# Main App
def main():
    st.title("📊 Bazaar Peer Review Grader")
    st.markdown("---")

    # Sidebar for file uploads and settings
    with st.sidebar:
        st.header("Upload Data")

        # Student roster CSV
        roster_file = st.file_uploader(
            "Upload Student Roster CSV",
            type=['csv'],
            help="Upload the student roster with Period, Group, Student First Name, Student Last Name",
            key="roster"
        )

        # Main peer review CSV
        peer_review_file = st.file_uploader(
            "Upload Peer Review CSV",
            type=['csv'],
            help="Upload the Google Form responses CSV file",
            key="peer_review"
        )

        # Financial files
        financial_files = st.file_uploader(
            "Upload Financial Files",
            type=['xlsx', 'csv'],
            accept_multiple_files=True,
            help="Upload Excel/CSV files with format: {GroupID}-Income and Expense Tracking"
        )

        st.markdown("---")
        st.header("Settings")

        # Variance threshold slider
        variance_threshold = st.slider(
            "Workload Variance Threshold (%)",
            min_value=5,
            max_value=30,
            value=15,
            step=1,
            help="Flag groups where workload disagreement exceeds this percentage"
        )

        # Filter options
        show_only_red_flags = st.checkbox(
            "Show only Red Flag groups",
            value=False
        )

    # Main content area
    if peer_review_file is None:
        st.info("👈 Please upload the Peer Review CSV file to get started.")
        st.markdown("""
        ### How to use this app:
        1. Upload the Google Form peer evaluation CSV file
        2. (Optional) Upload financial Excel/CSV files for each group
        3. Adjust the variance threshold if needed
        4. Review groups marked with red flags
        5. Expand each group to see detailed evaluations and feedback
        """)
        return

    # Load and process data
    try:
        # Load roster if provided
        roster = load_roster(roster_file)

        df = pd.read_csv(peer_review_file)
        groups = parse_peer_review_data(df)

        # Load financial data
        group_financials = {}
        student_financials = {}
        if financial_files:
            group_financials, student_financials = load_financial_data(financial_files)

        # Get missing submissions
        missing_submissions = get_missing_submissions(roster, groups)

        # Display summary statistics
        st.header("Summary")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Groups", len(groups))

        with col2:
            if roster:
                st.metric("Total Students", len(roster['students']))
            else:
                total_students = sum(len(g['students']) for g in groups.values())
                st.metric("Total Students", total_students)

        with col3:
            total_submissions = sum(len(g['evaluations']) for g in groups.values())
            st.metric("Total Submissions", total_submissions)

        with col4:
            groups_with_financials = sum(1 for gid in groups.keys() if gid in group_financials)
            st.metric("Groups w/ Financials", groups_with_financials)

        # Show missing submissions if roster is loaded
        if roster and missing_submissions:
            st.warning(f"⚠️ **{len(missing_submissions)} students have not submitted their peer reviews**")
            with st.expander("View Missing Submissions", expanded=False):
                # Group missing by period
                missing_by_period = {}
                for student in missing_submissions:
                    period = student['period']
                    if period not in missing_by_period:
                        missing_by_period[period] = []
                    missing_by_period[period].append(student)

                for period in sorted(missing_by_period.keys()):
                    st.markdown(f"**Period {period}:**")
                    for student in missing_by_period[period]:
                        st.markdown(f"- {student['group']}: {student['first_name']} {student['last_name']}")

        st.markdown("---")

        # Analyze and display groups
        st.header("Group Analysis")

        # Sort groups by ID
        sorted_group_ids = sorted(groups.keys())

        for group_id in sorted_group_ids:
            group_data = groups[group_id]

            # Get financial profit
            financial_profit = group_financials.get(group_id, None)

            # Get student-level financials
            group_student_financials = student_financials.get(group_id, {})

            # Analyze red flags
            is_red_flag, flags, variance_scores = analyze_group_flags(
                group_data,
                financial_profit,
                variance_threshold,
                group_student_financials
            )

            # Filter if needed
            if show_only_red_flags and not is_red_flag:
                continue

            # Display group
            display_group(group_id, group_data, financial_profit, is_red_flag, flags, variance_scores, group_student_financials, variance_threshold)

    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        st.exception(e)

def display_group(group_id, group_data, financial_profit, is_red_flag, flags, variance_scores, student_financials=None, variance_threshold=15):
    """Display a group's information in an expander"""

    # Determine header color
    if is_red_flag:
        header_color = "🔴"
        status = "RED FLAG"
    else:
        header_color = "🟢"
        status = "OK"

    # Financial indicator
    if financial_profit is not None:
        if financial_profit >= 0:
            fin_indicator = f"💰 ${financial_profit:.2f}"
        else:
            fin_indicator = f"📉 ${financial_profit:.2f}"
    else:
        fin_indicator = "❓ No Financial Data"

    # Create expander (collapsed by default)
    with st.expander(f"{header_color} **Group {group_id}** | {status} | {fin_indicator}", expanded=False):

        # Show flags if any
        if flags:
            st.warning("**Red Flags Detected:**")
            for flag in flags:
                st.markdown(f"- {flag}")
            st.markdown("---")

        # Student list
        students = sorted(list(group_data['students']))
        st.markdown("**Students:**")
        for student in students:
            student_short = student.split(' - ')[1] if ' - ' in student else student
            st.markdown(f"- {student_short}")
        st.markdown("---")

        # Workload Analysis Table
        st.subheader("Workload Distribution Matrix")
        st.markdown("*Rows = students being evaluated | Columns = evaluators | Diagonal (★) = self-evaluation*")

        # Debug: show evaluation data
        if st.checkbox("Show debug info (evaluations)", value=False, key=f"debug_{group_id}"):
            st.write("**Evaluations data:**")
            for eval in group_data['evaluations']:
                st.write(f"Submitter: {eval['submitter']}")
                st.write(f"Percentages: {eval['percentages']}")
                st.write("---")

        # Create matrix showing who said what about whom
        # This should be a square matrix: all students x all students
        matrix_data = []

        # Create a map of who submitted evaluations
        evaluations_map = {}
        for eval in group_data['evaluations']:
            evaluations_map[eval['submitter']] = eval

        # Get short names for all students
        student_shorts = {}
        for student in students:
            student_short = student.split(' - ')[1] if ' - ' in student else student
            student_shorts[student] = student_short

        # Calculate expected contribution and threshold for highlighting
        num_students = len(students)
        expected_pct = 100.0 / num_students
        low_threshold = expected_pct * 0.6  # Same threshold as red flag detection

        for student_being_evaluated in students:
            student_eval_short = student_shorts[student_being_evaluated]
            row = {'Student': student_eval_short}

            # For each potential evaluator (all students in group)
            for evaluator in students:
                evaluator_short = student_shorts[evaluator]

                # Check if this evaluator submitted a form
                if evaluator in evaluations_map:
                    eval = evaluations_map[evaluator]
                    pct = eval['percentages'].get(student_being_evaluated, 0)

                    # Highlight low percentages in red
                    if pct < low_threshold:
                        pct_display = f"🔴 {pct}%"
                    else:
                        pct_display = f"{pct}%"

                    # Mark self-evaluation with a star
                    if evaluator == student_being_evaluated:
                        row[evaluator_short] = f"{pct_display} ★"
                    else:
                        row[evaluator_short] = pct_display
                else:
                    # Evaluator didn't submit
                    row[evaluator_short] = "-"

            # Add variance (highlight if above threshold)
            variance = variance_scores.get(student_being_evaluated, 0)
            if variance > variance_threshold:
                row['Variance'] = f"🔴 ±{variance:.1f}%"
            else:
                row['Variance'] = f"±{variance:.1f}%"

            matrix_data.append(row)

        if matrix_data:
            matrix_df = pd.DataFrame(matrix_data)
            # Set index to start at 1
            matrix_df.index = range(1, len(matrix_df) + 1)
            st.dataframe(matrix_df, use_container_width=True)

        st.markdown("---")

        # Student Financial Breakdown (if available)
        if student_financials:
            st.subheader("Individual Student Financials")

            fin_data = []
            all_incomes = []

            # First pass: collect all data
            for student in students:
                # Extract student name from format "GroupID - Last, First"
                student_short = student.split(' - ')[1] if ' - ' in student else student

                # Convert "Last, First" to "First Last" to match Excel format
                if ', ' in student_short:
                    parts = student_short.split(', ')
                    if len(parts) == 2:
                        excel_name = f"{parts[1]} {parts[0]}"  # "First Last"
                    else:
                        excel_name = student_short
                else:
                    excel_name = student_short

                # Try to match student name in financials
                student_fin = None

                # Try exact match first
                if excel_name in student_financials:
                    student_fin = student_financials[excel_name]
                else:
                    # Try partial match (last name or first name)
                    for fin_name, fin_info in student_financials.items():
                        # Check if last names match (first word of excel_name vs last word of fin_name)
                        excel_parts = excel_name.split()
                        fin_parts = fin_name.split()
                        if excel_parts and fin_parts and excel_parts[-1].lower() == fin_parts[-1].lower():
                            student_fin = fin_info
                            break

                if student_fin:
                    all_incomes.append(student_fin['income'])
                    fin_data.append({
                        'student_short': student_short,
                        'income': student_fin['income'],
                        'expenses': student_fin['expenses'],
                        'profit': student_fin['profit'],
                        'inventory': student_fin['inventory']
                    })

            # Calculate average income for highlighting
            avg_income = sum(all_incomes) / len(all_incomes) if all_incomes else 0
            low_sales_threshold = avg_income * 0.5

            # Second pass: format with highlighting
            formatted_data = []
            for item in fin_data:
                # Highlight low income
                if item['income'] < low_sales_threshold and avg_income > 10:
                    income_display = f"🔴 ${item['income']:.2f}"
                else:
                    income_display = f"${item['income']:.2f}"

                # Highlight negative profit
                if item['profit'] < 0:
                    profit_display = f"🔴 ${item['profit']:.2f}"
                else:
                    profit_display = f"${item['profit']:.2f}"

                formatted_data.append({
                    'Student': item['student_short'],
                    'Income': income_display,
                    'Expenses': f"${item['expenses']:.2f}",
                    'Profit': profit_display,
                    'Inventory Value': f"${item['inventory']:.2f}"
                })

            if formatted_data:
                fin_df = pd.DataFrame(formatted_data)
                # Set index to start at 1
                fin_df.index = range(1, len(fin_df) + 1)
                st.dataframe(fin_df, use_container_width=True)
            else:
                st.info("Individual student financial data not found in Summary sheet")

            st.markdown("---")

        # Work Descriptions
        st.subheader("Work Contributions")

        for eval in group_data['evaluations']:
            evaluator = eval['submitter'].split(' - ')[1] if ' - ' in eval['submitter'] else eval['submitter']
            st.markdown(f"**Evaluation by {evaluator}:**")

            for student, descriptions in eval['work_descriptions'].items():
                student_short = student.split(' - ')[1] if ' - ' in student else student

                with st.container():
                    st.markdown(f"*{student_short}:*")

                    work_summary = []
                    for work_type, desc in descriptions.items():
                        if desc and desc != '' and not pd.isna(desc):
                            highlighted_desc = highlight_keywords(desc)
                            work_summary.append(f"**{work_type.title()}:** {highlighted_desc}")

                    if work_summary:
                        for item in work_summary:
                            st.markdown(f"  - {item}", unsafe_allow_html=True)
                    else:
                        st.markdown("  - *(No description provided)*")

            # Show evidence links for this evaluator
            if eval.get('evidence_urls'):
                st.markdown(f"📎 **Evidence from {evaluator}:**")
                for url in eval['evidence_urls']:
                    st.markdown(f"  - [{url}]({url})")

            # Show photo thumbnails for this evaluator
            if eval.get('photo_urls'):
                st.markdown(f"📸 **Photos from {evaluator}:**")

                # Separate images by type
                image_urls = []
                heic_urls = []

                for url in eval['photo_urls']:
                    # Check if URL is likely a HEIC file
                    if '.heic' in url.lower() or 'heic' in url.lower():
                        heic_urls.append(url)
                    else:
                        image_urls.append(url)

                # Display regular images as thumbnails
                if image_urls:
                    cols = st.columns(min(len(image_urls), 4))  # Max 4 images per row
                    for idx, url in enumerate(image_urls):
                        with cols[idx % 4]:
                            thumbnail_url = convert_gdrive_to_thumbnail(url)
                            st.markdown(f"[![Photo]({thumbnail_url})]({url})")

                # Display HEIC files as links
                if heic_urls:
                    st.markdown("  *HEIC files (click to view):*")
                    for url in heic_urls:
                        st.markdown(f"  - [View HEIC photo]({url})")

            st.markdown("")

        st.markdown("---")

        # Feedback Section
        st.subheader("Feedback & Reflections")

        for feedback in group_data['feedback']:
            submitter = feedback['submitter'].split(' - ')[1] if ' - ' in feedback['submitter'] else feedback['submitter']

            st.markdown(f"**From {submitter}:**")

            if feedback.get('challenges'):
                highlighted = highlight_keywords(feedback['challenges'])
                st.markdown(f"*Challenges:* {highlighted}", unsafe_allow_html=True)

            if feedback.get('good_stuff'):
                highlighted = highlight_keywords(feedback['good_stuff'])
                st.markdown(f"*The Good Stuff:* {highlighted}", unsafe_allow_html=True)

            if feedback.get('advice'):
                highlighted = highlight_keywords(feedback['advice'])
                st.markdown(f"*Advice:* {highlighted}", unsafe_allow_html=True)

            st.markdown("")

if __name__ == "__main__":
    main()
