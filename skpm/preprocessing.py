import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin, check_is_fitted


def _cummean(x):
    return np.cumsum(x) / (1 + np.arange(len(x)))


strategies = {
    "mean": _cummean,
    "sum": np.cumsum,
}


class TraceAggregator(TransformerMixin, BaseEstimator):
    def __init__(self, strategy="mean", case_id="case_id", ignore="timestamp") -> None:
        self.case_id = case_id
        self.ignore = ignore
        self.strategy = strategies[strategy]

    def fit(self, X, y=None):
        if not isinstance(self.ignore, ((list, tuple))):
            self.ignore = [self.ignore]

        # make sure all columns but case_id and *ignore are numeric
        self.features_ = X.select_dtypes(exclude=["object"]).columns
        self.features_ = list(set(self.features_) - set([self.case_id, *self.ignore]))
        self.n_features_ = len(self.features_)
        return self

    def transform(self, X, y=None):
        check_is_fitted(self, "features_")

        X[self.features_] = X.groupby(self.case_id, group_keys=False, as_index=False)[
            self.features_
        ].transform(self.strategy)

        for case in X[self.case_id].unique():
            mask = X[self.case_id] == case
            X.loc[mask, self.cols] = self.strategy(X.loc[mask, self.features_])

        return X
