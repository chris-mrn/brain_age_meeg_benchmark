from benchopt import BaseSolver, safe_import_context

# Protect the import with `safe_import_context()`. This allows:
# - skipping import to speed up autocompletion in CLI.
# - getting requirements info when all dependencies are not installed.
with safe_import_context() as import_ctx:
    import numpy as np
    import coffeine
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import RidgeCV
    from sklearn.feature_selection import VarianceThreshold
    from benchopt.stopping_criterion import SingleRunCriterion


# The benchmark solvers must be named `Solver` and
# inherit from `BaseSolver` for `benchopt` to work properly.
class Solver(BaseSolver):

    # Name to select the solver in the CLI and to display the results.
    name = 'SPoC'

    stopping_criterion = SingleRunCriterion()

    def set_objective(self, X, y, frequency_bands):
        # Pipeline parameters
        # frequency_bands = {"all": (1, 35)}
        rank = 20
        scale = 1
        reg = 0

        self.X, self.y = X, y

        filter_bank_transformer = coffeine.make_filter_bank_transformer(
            names=list(frequency_bands),
            method='spoc',
            projection_params=dict(scale=scale, n_compo=rank, reg=reg)
        )
        self.model = make_pipeline(
            filter_bank_transformer,
            VarianceThreshold(1e-10),
            StandardScaler(),
            RidgeCV(alphas=np.logspace(-5, 10, 100))
        )

    def run(self, n_iter):
        # This is the function that is called to evaluate the solver.
        # It runs the algorithm for a given a number of iterations `n_iter`.
        print('Begin to fit:')
        self.model.fit(self.X, self.y)
        print('Fit done!')
        # import ipdb; ipdb.set_trace()

    def get_result(self):
        # Return the result from one optimization run.
        # The outputs of this function are the arguments of `Objective.compute`
        # This defines the benchmark's API for solvers' results.
        # it is customizable for each benchmark.
        return self.model
