# TODO
## Testing
- Assert that all environment variables are present on all 
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
