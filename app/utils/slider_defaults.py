def get_slider_defaults(range_data, pad=0.2):
    """Calculates default slider values based on a data range.

    Args:
        range_data (tuple[float, float]): A tuple containing the min and max values.
        pad (float, optional): Padding factor to extend the slider range beyond
            the min and max values. Defaults to 0.2.

    Returns:
        dict: A dictionary with keys 'lsl', 'usl', 'slider_min', and 'slider_max'.
    """
    min_val, max_val = range_data
    padding = (max_val - min_val) * pad
    slider_min = min_val - padding
    slider_max = max_val + padding
    return {
        'lsl': min_val,
        'usl': max_val,
        'slider_min': slider_min,
        'slider_max': slider_max,
    }

def make_marks(min_val, max_val):
    mid = (min_val + max_val) / 2
    marks = {
        min_val: "Min (observed)",
        mid: f"Middle",
        max_val: "Max"
    }
    return marks
