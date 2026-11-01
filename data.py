import pandas as pd

def process_results(path):
    try:
        df = pd.read_csv(path)
    except Exception as e:
        raise ValueError(f"Cannot read CSV file: {e}")

    # 1. Clean column names
    df.columns = df.columns.str.strip().str.lower()
    
    # 2. Auto-detect subjects (5th column onwards)
    FIXED_COLS = 4  # roll_no, name, class, father_name
    all_cols = df.columns.tolist()
    
    if len(all_cols) < 5:
        raise ValueError(f"CSV must have at least 5 columns, found only {len(all_cols)}: {all_cols}")
    
    SUBJECTS = all_cols[FIXED_COLS:]
    
    # 3. Check required columns
    required = ["roll_no", "name"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}. Your columns are: {all_cols}")

    # 4. NEW VALIDATION - Check for empty values in roll_no, name
    if df["roll_no"].isnull().any() or (df["roll_no"].astype(str).str.strip() == "").any():
        empty_rows = df[df["roll_no"].isnull() | (df["roll_no"].astype(str).str.strip() == "")].index.tolist()
        raise ValueError(f"Empty roll_no found at rows: {[i+2 for i in empty_rows]} (Row 2 = first student)")
    
    if df["name"].isnull().any() or (df["name"].astype(str).str.strip() == "").any():
        empty_rows = df[df["name"].isnull() | (df["name"].astype(str).str.strip() == "")].index.tolist()
        raise ValueError(f"Empty name found at rows: {[i+2 for i in empty_rows]}")

    # 5. NEW VALIDATION - Check subjects for letters / empty / wrong numbers
    errors = []
    
    for subject in SUBJECTS:
        # Check if column is completely empty
        if df[subject].isnull().all():
            errors.append(f"Subject '{subject}' column is completely empty")
            continue
        
        # Check each cell
        for idx, value in df[subject].items():
            row_num = idx + 2  # +2 because CSV row 1 is header, pandas index 0 is row 2
            
            # Check empty
            if pd.isna(value) or str(value).strip() == "":
                errors.append(f"Row {row_num}: '{subject}' is empty for roll_no {df.loc[idx, 'roll_no']}")
                continue
            
            # Check if it's a letter
            try:
                num = float(str(value).strip())
            except ValueError:
                errors.append(f"Row {row_num}: '{subject}' has letter/text '{value}' instead of number (roll_no: {df.loc[idx, 'roll_no']})")
                continue
            
            # Check if marks are valid (0-100)
            if num < 0 or num > 100:
                errors.append(f"Row {row_num}: '{subject}' has invalid marks {num} (must be 0-100) for roll_no {df.loc[idx, 'roll_no']}")

    # If any errors, show them all at once
    if errors:
        error_msg = "CSV Validation Failed:\n" + "\n".join(errors[:15])  # show first 15 errors
        if len(errors) > 15:
            error_msg += f"\n... and {len(errors)-15} more errors"
        raise ValueError(error_msg)

    # 6. If validation passes, convert to numbers and calculate
    df[SUBJECTS] = df[SUBJECTS].apply(pd.to_numeric, errors="coerce")
    
    df["total"] = df[SUBJECTS].sum(axis=1)
    total_marks = len(SUBJECTS) * 100
    df["percentage"] = (df["total"] / total_marks * 100).round(2)
    df["grade"] = df["percentage"].apply(get_grade)
    df["result"] = df[SUBJECTS].min(axis=1).apply(lambda m: "Pass" if m >= 40 else "Fail")
    df["rank"] = df["total"].rank(ascending=False, method="min").astype(int)

    return df

def get_grade(p):
    if p >= 90: return "A+"
    if p >= 80: return "A"
    if p >= 70: return "B"
    if p >= 60: return "C"
    if p >= 40: return "D"
    return "F"