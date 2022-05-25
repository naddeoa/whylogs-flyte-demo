import typing
import pandas as pd
import numpy as np

from flytekit import task, workflow
from flytekit.extend import TypeEngine 
import whylogs as ylog
from whylogs.core import DatasetProfileView

@task
def generate_normal_df(n: int, mean: float, sigma: float) -> pd.DataFrame:
    return pd.DataFrame({"numbers": np.random.normal(mean, sigma, size=n)})


@task
def compute_stats(df: pd.DataFrame) -> typing.Tuple[float, float]:
    return float(df["numbers"].mean()), float(df["numbers"].std())


@task
def profile(df: pd.DataFrame) -> DatasetProfileView:
    result = ylog.log(df)
    profile = result.profile().view()
    return profile


@workflow
def wf(n: int = 200, mean: float = 0.0, sigma: float = 1.0) -> typing.Tuple[float, float]:
    df = generate_normal_df(n=n, mean=mean, sigma=sigma)
    profile(df=df)
    return compute_stats(df=df)



# %%
# Execute the Workflow, simply by invoking it like a function and passing in
# the necessary parameters
#
# .. note::
#
#   One thing to remember, currently we only support ``Keyword arguments``. So
#   every argument should be passed in the form ``arg=value``. Failure to do so
#   will result in an error
if __name__ == "__main__":
    print(f"Running my_wf() { wf() }")




