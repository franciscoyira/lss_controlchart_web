def get_slider_defaults(range_data, pad=0.2):
    min_val, max_val = range_data
    span = max_val - min_val
    # Constant data has zero range; fall back to a span based on the value
    # itself so the slider still has room to move
    if span == 0:
        span = max(abs(max_val), 1)
    padding = span * pad
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
        mid: "Middle",
        max_val: "Max"
    }
    return marks
