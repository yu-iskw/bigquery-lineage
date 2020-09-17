# bigquery-linaege
![CircleCI](https://circleci.com/gh/yu-iskw/bigquery-lineage.svg?style=svg&circle-token=f652ef2c59e8b69a71aa478a524bdc0e813d34e1)


## Install the module
```bash
$ pip install -e .
```

## How to use
`bql --help` enables us to show the help message.

```bash
# Collect data
bql data bigquery --output data --config ./bql-config.yml

# Build a graph
bql graph pydot --data_dir  ./data --fmt pdf --output graph.pdf --config ./bql-config.yml
```
