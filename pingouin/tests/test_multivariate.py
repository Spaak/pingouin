import numpy as np
from unittest import TestCase
from pingouin import read_dataset
from pingouin.multivariate import multivariate_normality, multivariate_ttest

data = read_dataset('multivariate')
dvs = ['Fever', 'Pressure', 'Aches']
X = data[data['Condition'] == 'Drug'][dvs]
Y = data[data['Condition'] == 'Placebo'][dvs]
# With missing values
X_na = X.copy()
X_na.iloc[4, 2] = np.nan
# Rank deficient
X_rd = X.copy()
X_rd['Bad'] = 1.08 * X_rd['Fever'] - 0.5 * X_rd['Pressure']


class TestMultivariate(TestCase):
    """Test multivariate.py.
    Tested against the R package MVN.
    """

    def test_multivariate_normality(self):
        """Test function multivariate_normality."""
        np.random.seed(123)
        # With 2 variables
        mean, cov, n = [4, 6], [[1, .5], [.5, 1]], 30
        Z = np.random.multivariate_normal(mean, cov, n)
        normal, p = multivariate_normality(Z, alpha=.05)
        # Compare with the Matlab Robust Corr toolbox
        assert normal
        assert np.round(p, 3) == 0.752
        # With 3 variables
        normal, p = multivariate_normality(data[dvs], alpha=.01)
        assert round(p, 3) == 0.717
        # With missing values
        multivariate_normality(X_na, alpha=.05)
        # Rank deficient
        multivariate_normality(X_rd)

    def test_multivariate_ttest(self):
        """Test function multivariate_ttest.
        Tested against the R package Hotelling and real-statistics.com.
        """
        np.random.seed(123)
        # With 2 variables
        mean, cov, n = [4, 6], [[1, .5], [.5, 1]], 30
        Z = np.random.multivariate_normal(mean, cov, n)
        # One-sample test
        multivariate_ttest(Z, Y=None, paired=False)
        multivariate_ttest(Z, Y=[4, 5], paired=False)
        # With 3 variables
        # Two-sample independent
        stats = multivariate_ttest(X, Y)
        assert round(stats.at['hotelling', 'F'], 3) == 1.327
        assert stats.at['hotelling', 'df1'] == 3
        assert stats.at['hotelling', 'df2'] == 32
        assert round(stats.loc['hotelling', 'pval'], 3) == 0.283
        # Paired test with NaN values
        stats = multivariate_ttest(X_na, Y, paired=True)
        assert stats.at['hotelling', 'df1'] == 3
        assert stats.at['hotelling', 'df2'] == X.shape[0] - 1 - X.shape[1]
