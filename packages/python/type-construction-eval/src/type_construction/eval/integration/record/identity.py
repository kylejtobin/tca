import hashlib

from pydantic import BaseModel, ConfigDict

from type_construction.eval.domain.evaluation.dataset import Dataset, IdentifiedDataset
from type_construction.eval.domain.evaluation.run import IdentifiedRun, Run
from type_construction.eval.domain.evaluation.type import DatasetVersion, SystemVersion
from type_construction.eval.domain.evaluation.value import DatasetRef, VersionRef
from type_construction.eval.domain.evaluation.version import IdentifiedVersion, Version


class DatasetIdentity(BaseModel):
    """A dataset as the record identifies it: by the digest of its cases in order, so a case
    added later is a new version and a decision taken on this one never moves."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    dataset: Dataset

    @property
    def version(self) -> DatasetVersion:
        return DatasetVersion(
            hashlib.sha256(self.dataset.cases.model_dump_json().encode()).hexdigest()
        )

    @property
    def ref(self) -> DatasetRef:
        return DatasetRef(name=self.dataset.name, version=self.version)

    @property
    def identified(self) -> IdentifiedDataset:
        return IdentifiedDataset(dataset=self.dataset, ref=self.ref)


class VersionIdentity(BaseModel):
    """A version as the record identifies it: by the digest of its name and its parts, so the
    display name identifies nothing."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    version: Version

    @property
    def identity(self) -> SystemVersion:
        return SystemVersion(
            hashlib.sha256(
                f"{self.version.name.root}:{self.version.parts.model_dump_json()}".encode()
            ).hexdigest()
        )

    @property
    def ref(self) -> VersionRef:
        return VersionRef(name=self.version.name, version=self.identity)

    @property
    def identified(self) -> IdentifiedVersion:
        return IdentifiedVersion(version=self.version, ref=self.ref)


class RunIdentity(BaseModel):
    """A run as a program stated it, as the record identifies it: the dataset by its content,
    and the oracle the identified dataset derives; its derivation is the run with its
    identities assigned."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    run: Run

    @property
    def dataset(self) -> IdentifiedDataset:
        return DatasetIdentity(dataset=self.run.dataset).identified

    @property
    def identified(self) -> IdentifiedRun:
        return IdentifiedRun(
            dataset=self.dataset,
            version=VersionIdentity(version=self.dataset.oracle).identified,
            repetitions=self.run.repetitions,
        )
