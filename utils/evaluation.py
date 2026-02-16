import numpy as np
def precision_at_k(actual, predicted, k): 
    predicted = predicted[:k]
    return len(set(predicted) & set(actual)) / k
