import typing
import pandas as pd
import numpy as np

from flytekit import task, workflow
from flytekit.extend import TypeEngine 
# from flytekitplugins.whylogs import WhylogsDatasetProfileTransformer
import whylogs as ylog
from whylogs.core import DatasetProfileView


## DELETE START
from typing import Type
from flytekit import FlyteContext, BlobType
from flytekit.extend import T, TypeTransformer, TypeEngine
from flytekit.models.literals import Literal, Scalar, Blob, BlobMetadata
from flytekit.models.types import LiteralType

class WhylogsDatasetProfileTransformer(TypeTransformer[DatasetProfileView]):
    """
    Transforms whylogs Dataset Profiles to and from a Schema (typed/untyped)
    """

    # TODO Spark plugin is a SchemaType. How do I pick? Is blob right?
    _TYPE_INFO = BlobType(format="binary", dimensionality=BlobType.BlobDimensionality.SINGLE)

    def __init__(self):
        super(WhylogsDatasetProfileTransformer, self).__init__("whylogs-profile-transformer", t=DatasetProfileView)

    def get_literal_type(self, t: Type[DatasetProfileView]) -> LiteralType:
        return LiteralType(blob=self._TYPE_INFO)

    def to_literal(
        self,
        ctx: FlyteContext,
        python_val: DatasetProfileView,
        python_type: Type[DatasetProfileView],
        expected: LiteralType,
    ) -> Literal:
        remote_path = ctx.file_access.get_random_remote_directory()
        local_dir = ctx.file_access.get_random_local_path()
        python_val.write(local_dir)
        ctx.file_access.upload(local_dir, remote_path)
        return Literal(scalar=Scalar(blob=Blob(uri=remote_path, metadata=BlobMetadata(type=self._TYPE_INFO))))

    def to_python_value(self, ctx: FlyteContext, lv: Literal, expected_python_type: Type[DatasetProfileView]) -> T:
        local_dir = ctx.file_access.get_random_local_path()
        ctx.file_access.download(lv.scalar.blob.uri, local_dir)
        return DatasetProfileView.read(local_dir)

    # TODO where is this visible from?
    # TODO how can I test this out locally? Do I need to build a wheel of flytekit and use it from a real project?
    def to_html(self, ctx: FlyteContext, python_val: DatasetProfileView, expected_python_type: Type[DatasetProfileView]) -> str:
        return str(python_val.to_pandas().to_html())


TypeEngine.register(WhylogsDatasetProfileTransformer())
## DELETE START

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




