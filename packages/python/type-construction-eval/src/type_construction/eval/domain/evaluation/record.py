from pydantic import BaseModel, ConfigDict

from type_construction.eval.domain.evaluation.type import DatasetName, RecordFolder, RelativePath


class DatasetLogs(BaseModel):
    """Where every log ever made on one dataset lives: one directory under the record root,
    named by the dataset, so two versions are found in one place and told apart by a
    column."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    dataset: DatasetName

    @property
    def path(self) -> RelativePath:
        return RelativePath(f"{RecordFolder.LOGS}/{self.dataset.root}")
