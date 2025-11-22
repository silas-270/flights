def get_signal(estimate, actual):
    threshold = estimate * 0.1 # Create Signal at 10% diff
    multiplier = 1 # Amount of Options per 1% Diff

    if abs(estimate - actual) < threshold:
        return 0
    else:
        option_amount = round(abs(estimate / actual) * multiplier)
        return  option_amount * (-1 if estimate < actual else 1)