
### Project preparations

1. Run `pip install -r requirements.txt`
2. `cd implementation-indexing/utils`
3. Run `python nltk_downloader.py` to download needed nltk data
4. If you get "error: invalid path" during `git pull`, run `git config core.protectNTFS false`

### How to run indexer

To store word data for each document we first need to run the indexer.

1. Run `python run-indexer.py`
    - If this is the first run we need to create db tables with `--init_tables=1` (default 0)
    - `--clear_tables=1`to clear tables data before starting indexing (default 0)

### How to run data retrieval
1. Run `python run-sqlite-search.py "query"`
2. Run `python run-basic-search.py "query"`