def get_slider_defaults(range_data, pad=0.2):
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
