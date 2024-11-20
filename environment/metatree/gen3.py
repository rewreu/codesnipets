from collections import Counter
def is_balanced(y, threshold=0.1):
    counter = Counter(y)
    total = sum(counter.values())
    for cls_count in counter.values():
        if abs(cls_count / total - 0.5) > threshold:
            return False
    return True

def has_few_missing_values(X, threshold=0.1):
    missing_fraction = X.isnull().mean()
    return all(missing_fraction < threshold)

from sklearn.feature_selection import VarianceThreshold
def has_high_variance(X, threshold=0.01):
    selector = VarianceThreshold(threshold=threshold)
    return selector.fit(X).get_support().sum() > 0

import pandas as pd
def has_low_correlation(X, threshold=0.9):
    corr_matrix = X.corr().abs()
    upper_triangle = corr_matrix.where(
        pd.np.triu(pd.np.ones(corr_matrix.shape), k=1).astype(bool))
    return not (upper_triangle > threshold).any().any()

from sklearn.model_selection import cross_val_score
def evaluate_model(model, X, y, scoring='accuracy', cv=5, threshold=0.7):
    scores = cross_val_score(model, X, y, scoring=scoring, cv=cv)
    return scores.mean() >= threshold
def has_reliable_feature_importance(model, threshold=0.01):
    return (model.feature_importances_ > threshold).sum() > 0

from sklearn.metrics import accuracy_score
def has_good_out_of_sample_performance(model, X_test, y_test, threshold=0.7):
    y_pred = model.predict(X_test)
    return accuracy_score(y_test, y_pred) >= threshold

for dataset in datasets:
    if not is_balanced(dataset['target']) or not has_few_missing_values(dataset['features']):
        continue
    # Proceed with modeling

from sklearn.tree import DecisionTreeClassifier

for dataset in datasets:
    X, y = dataset['features'], dataset['target']
    if is_balanced(y) and has_few_missing_values(X):
        model = DecisionTreeClassifier()
        model.fit(X, y)
        
        if not evaluate_model(model, X, y):
            print("Model not performing well on dataset:", dataset['name'])
