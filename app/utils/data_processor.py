import polars as pl

def calculate_control_stats(df: pl.DataFrame) -> dict:
    """
    Calculates stats that can be computed without user input
    Parameters:
        df (pl.DataFrame): Input DataFrame with a numeric 'value' column representing the process data.
    Returns:
        dict: A dictionary containing:
            - 'mean': Mean of the 'value' column.
            - 'std_dev': Standard deviation of the 'value' column.
            - 'ucl': Upper Control Limit (mean + 3 * std_dev).
            - 'lcl': Lower Control Limit (mean - 3 * std_dev).
            - 'uwl': Upper Warning Limit (mean + 2 * std_dev).
            - 'lwl': Lower Warning Limit (mean - 2 * std_dev).
            - 'uzl': Upper Zone A Limit (mean + 1 * std_dev).
            - 'lzl': Lower Zone A Limit (mean - 1 * std_dev).
    Notes:
        Assumes the 'value' column exists and contains numeric data.
    """
    mean = df['value'].mean()
    std_dev = df['value'].std()
    min_value = df['value'].min()
    max_value = df['value'].max()
    count = df['value'].count()
    
    return {
        'mean': mean,
        'std_dev': std_dev,
        'min': min_value,
        'max': max_value,
        'count': count,
        'range': max_value - min_value,
        'ucl': mean + 3 * std_dev,
        'lcl': mean - 3 * std_dev,
        'uwl': mean + 2 * std_dev,  # Upper Warning Limit
        'lwl': mean - 2 * std_dev,  # Lower Warning Limit
        'uzl': mean + std_dev,      # Upper Zone A Limit
        'lzl': mean - std_dev,      # Lower Zone A Limit
    }

def add_control_rules(df: pl.DataFrame, stats: dict, active_rules: dict = None) -> pl.DataFrame:
    """Add flag columns indicating if each data point (row) breaks any of the active control chart rules.
    
    Args:
        df: Polars DataFrame
        stats: output of `calculate_control_stats()`
        active_rules: Dictionary with active rules {1: True/False, 2: True/False, ...}
                      If None, all rules are active
    Returns:
        df: a Polars Dataframe with the flag columns added
    """
    # If active_rules is None, assume all rules are active
    if active_rules is None:
        active_rules = {i: True for i in range(1, 9)}
    
    val_diff = pl.col('value').diff()
    in_zone_c = pl.col('value').is_between(stats['lzl'], stats['uzl'])


    rule_1_counter = pl.when(pl.col("value").is_between(stats['lcl'], stats['ucl'])).then(0).otherwise(1)

    # Rule 2: 9 consecutive points on the same 
    mean_diff = (pl.col("value") - stats['mean'])
    mean_diff_sign = mean_diff.sign()
    rule_2_counter = mean_diff_sign.rolling_sum(window_size=9)

    # Rule 3: six points in a row steadily increasing or decreasing
    rule_3_counter = val_diff.sign().rolling_sum(window_size=6).abs()

    # Rule 4 - alternating pattern - 14 points in a row alternating up and down
    rule_4_counter = pl.col('value') \
        .diff() \
        .sign() \
        .diff() \
        .abs() \
        .rolling_sum(window_size=14) \
        .truediv(2)
    
    # Rule 5: Two out of three points in a row in Zone A (2 sigma) or beyond 
    # They have to be on the same side of the centerline!!
    flag_zone_a_upper = pl.when(pl.col("value") > stats['uwl']).then(1).otherwise(0)
    flag_zone_a_lower = pl.when(pl.col("value") < stats['lwl']).then(1).otherwise(0)
    rule_5_counter_upper = flag_zone_a_upper.rolling_sum(window_size=3)
    rule_5_counter_lower = flag_zone_a_lower.rolling_sum(window_size=3)

    # Rule 6: Four out of five points in a row in Zone B or beyond
    rule_6_flag = pl.when(pl.col("value").is_between(stats['lzl'], stats['uzl'])).then(0).otherwise(1)
    rule_6_counter = rule_6_flag.rolling_sum(window_size=5)

    # Rule 7: Fifteen points in a row within Zone C (the one closest to the centreline) 
    rule_7_flag = pl.when(pl.col("value").is_between(stats['lzl'], stats['uzl'])).then(1).otherwise(0)
    rule_7_counter = rule_7_flag.rolling_sum(window_size=15)

    # Rule 8: Eight points in a row with none in Zone C (that is, 8 points beyond 1 sigma)
    # either side of the centerline (unlike rule 5)
    rule_8_flag = pl.when(~in_zone_c).then(1).otherwise(0)
    rule_8_counter = rule_8_flag.rolling_sum(window_size=8)

    # Base columns with all rules set to OK
    rule_columns = {
        'rule_1': pl.lit("OK"),
        'rule_2': pl.lit("OK"),
        'rule_3': pl.lit("OK"),
        'rule_4': pl.lit("OK"),
        'rule_5': pl.lit("OK"),
        'rule_6': pl.lit("OK"),
        'rule_7': pl.lit("OK"),
        'rule_8': pl.lit("OK")
    }
    
    # Only apply active rules
    if active_rules.get(1, True):
        rule_columns['rule_1'] = pl.when(rule_1_counter > 0).then(pl.lit("Broken")).otherwise(pl.lit("OK"))
    
    if active_rules.get(2, True):
        rule_columns['rule_2'] = pl.when((rule_2_counter.abs() == 9)).then(pl.lit("Broken")).otherwise(pl.lit("OK"))
    
    if active_rules.get(3, True):
        rule_columns['rule_3'] = pl.when(rule_3_counter == 6).then(pl.lit("Broken")).otherwise(pl.lit("OK"))
    
    if active_rules.get(4, True):
        rule_columns['rule_4'] = pl.when(rule_4_counter == 14).then(pl.lit("Broken")).otherwise(pl.lit("OK"))
    
    if active_rules.get(5, True):
        rule_columns['rule_5'] = pl.when((rule_5_counter_upper >= 2) | (rule_5_counter_lower >= 2)).then(pl.lit("Broken")).otherwise(pl.lit("OK"))
    
    if active_rules.get(6, True):
        rule_columns['rule_6'] = pl.when(rule_6_counter == 4).then(pl.lit("Broken")).otherwise(pl.lit("OK"))
    
    if active_rules.get(7, True):
        rule_columns['rule_7'] = pl.when(rule_7_counter == 15).then(pl.lit("Broken")).otherwise(pl.lit("OK"))
    
    if active_rules.get(8, True):
        rule_columns['rule_8'] = pl.when(rule_8_counter == 8).then(pl.lit("Broken")).otherwise(pl.lit("OK"))

    return df.with_columns(**rule_columns)

def calculate_capability(mu, sigma, USL=None, LSL=None):
    """
    Calculate Cp, Cpu, Cpl, and Cpk process capability indices.
    Args:
        mu (float): Process mean (data-driven)
        sigma (float): Process standard deviation (data-driven)
        USL (float, optional): Upper specification limit (user-provided)
        LSL (float, optional): Lower specification limit (user-provided)
    Returns:
        dict: A dictionary containing Cp, Cpu, Cpl, and Cpk indices.
              Returns None if USL, LSL, or sigma is zero.
    """
    
    if USL is None or LSL is None or sigma == 0:
        return None
    cp = (USL - LSL) / (6 * sigma)
    cpu = (USL - mu) / (3 * sigma)
    cpl = (mu - LSL) / (3 * sigma)
    cpk = min(cpu, cpl)
    
    capability = {
        'cp': cp,
        'cpu': cpu,
        'cpl': cpl,
        'cpk': cpk
    }
    
    return capability
