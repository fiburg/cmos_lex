import numpy as np

def get_contingency_table(prediction, truth):
    """
    Get the contingency table:

    Hits (a) | False Alarms (b)
    --------------------------------
    Misses(c)| Correct negatives (d)

    Args:
        prediction: camera values (without nan)
        truth: pyranometer values (without nan)

    Returns:
        a,b,c,d
    """
    a = len(np.where((prediction ==1) & (truth == 1))[0])
    b = len(np.where((prediction ==1) & (truth == 0))[0])
    c = len(np.where((prediction ==0) & (truth == 1))[0])
    d = len(np.where((prediction ==0) & (truth == 0))[0])
    return a,b,c,d

def get_shades_vs_no_shades(prediction,truth):

    prediction_shades = len(np.where((prediction ==1)))
    prediction_sun = len(np.where((prediction == 0)))
    truth_shades = len(np.where((truth == 1)))
    truth_sun = len(np.where((truth == 0)))

    return prediction_shades,prediction_sun, truth_shades, truth_sun

def forecast_rate(a,b,c,d):
    """
    Forecast rate r.

    Args:
        a: hits
        b: false alarms
        c: misses
        d: correct negatives

    Returns:
        Forecast rate r
    """
    denominator = np.add(a,b)
    divisor = np.sum([a,b,c,d])
    return np.divide(denominator,divisor)

def base_rate(a,b,c,d):
    """
    Base rate s.

    Args:
        a: hits
        b: false alarms
        c: misses
        d: correct negatives

    Returns:
        Base rate s
    """
    denominator = np.add(a,c)
    divisor = np.sum([a,b,c,d])
    return np.divide(denominator,divisor)


def hit_rate(a,b,c,d):
    """
    Hit rate H.

    Args:
        a: hits
        b: false alarms
        c: misses
        d: correct negatives

    Returns:
        Hit rate h
    """
    denominator = a
    divisor = np.add(a,c)
    return np.divide(denominator,divisor)

def false_alarm_rate(a,b,c,d):
    """
    False alarm rate F.

    Args:
        a: hits
        b: false alarms
        c: misses
        d: correct negatives

    Returns:
        False alarm rate F
    """
    denominator = b
    divisor = np.add(b,d)
    return np.divide(denominator,divisor)

def false_alarm_ratio(a,b,c,d):
    """
    False alarm ratio FAR.

    Args:
        a: hits
        b: false alarms
        c: misses
        d: correct negatives

    Returns:
        False alarm ratio FAR
    """
    denominator = b
    divisor = np.add(a,b)
    return np.divide(denominator,divisor)

def proportion_correct(a,b,c,d):
    """
    Proportion correct PC.

    Args:
        a: hits
        b: false alarms
        c: misses
        d: correct negatives

    Returns:
        Proportion correct PC
    """
    denominator = np.add(a,d)
    divisor = np.sum([a,b,c,d])
    return np.divide(denominator,divisor)

def heidke_skill_score(a,b,c,d):
    """
    Calculates the heidke skill score (HSS).
    The HSS ranges from minus infinity to 1.
    1 means a perfect skill, 0 means no skill.

    Args:
        a: hits
        b: false alarms
        c: misses
        d: correct negatives

    Returns:

    """
    ar = np.multiply(base_rate(a,b,c,d), forecast_rate(a,b,c,d))
    dr = (1 - base_rate(a,b,c,d)) * (1 - forecast_rate(a,b,c,d))

    denominator = np.sum([a,d,-ar,-dr])
    divisor = np.sum([a,b,c,d,-ar,-dr])
    return np.divide(denominator, divisor)

def peirce_skill_score(a,b,c,d):
    """
    Calculates the peirce skill score.
    Ranges from -1 to 1.
    Perfect score: 1
    No skill: 0

    Args:
        a: hits
        b: false alarms
        c: misses
        d: correct negatives

    Returns:

    """
    denominator = np.subtract(a*d,b*c)
    divisor = np.multiply((b+d),(a+c))
    return np.divide(denominator, divisor)

def rmse(predictions, targets):
    """
    calculates the rmse.


    Args:
        prediction: camera values (without nan)
        truth: pyranometer values (without nan)

    Returns:
        rmse
    """
    return np.sqrt(np.nanmean(np.power((np.subtract(predictions,targets)), 2)))