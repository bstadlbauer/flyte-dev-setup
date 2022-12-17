# TODO
## Testing
- Assert that all environment variables are present on all pods
- Check if annotations can be set
- Make sure secrets are passed on
- Check whether labels and annotations can be passed on to `DaskCluster` subresource from `DaskJob`

## Configuration:
- If secret annotations should be passed on to workers and scheduler? 

## Docs:
- Default image will be used when none is given
- Additional worker groups are not supported yet, as those would require submitting two CRs
- Autoscaler won't work as this would require submitting an additional CR
- If limits are set, `--nthreads` and `--memory-limit` are set
– https://kubernetes.dask.org/en/latest/kubecluster.html?highlight=--nthreads#best-practices
- Recommended to set limits! 

## Questions to Dan: 
- Are there integration or e2e tests?
- Documentation does not show up? 
- Re-locking deps for docs and package on Linux
- How to deal with interruptable nodes? At the moment no way to make scheduler and runner non-interruptable
- Setting namespace won't work, overridden by plugin manager 

Docs:
checking consistency... /Users/bstadlbauer/workspace/bstadlbauer/flytekit/docs/source/extras.sklearn.rst: WARNING: document isn't included in any toctree
/Users/bstadlbauer/workspace/bstadlbauer/flytekit/docs/source/plugins/vaex.rst: WARNING: document isn't included in any toctree


## Game plan: 
- [ ] `flyteidl`:
  - [ ] Merge PR;  create release
- [ ] `flyteplugins`
  - [ ] Bump version of `flyteidl` in flyteplugins
  - [ ] Merge PR - create release
- [ ] `flytepropeller`:
  - [ ] Bump version of `flyteidl` and `flyteplugins`
  - [ ] Merge PR
  - [ ] Create release
- [ ] `flytekit`: 
    - [ ] Update `flyteidl` dependency in `flytekitplugins-dask`
    - [ ] Re-lock dependencies in `flyteplugins-dask` (on Linux)
    - [ ] Re-lock `doc-requirements.txt` to als include `dask[distributed]` (on Linux)
    - [ ] Check if docs built correctly (only work on Linux due to `cuda` dependency)
    - [ ] Reset version in `flytekitplugins-dask`
    - [ ] Create release
- [ ] `flytesnacks`:
  - Merge docs PR


## New changes to `flyteidl`
  1. All members are lowercase
  2. Renamed `nWorkers` to `number_of_workers`
  3. Converted `number_of_workers` from `int32` to `uint32` 