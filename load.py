"""
Load gene list data and predictions into a Postgres database.
"""
import argparse
from pred.config import parse_config, CONFIG_FILENAME, DataType
from pred.load.download import download_and_convert, download_models
from pred.load.loaddatabase import create_sql_pipeline, create_sql_builder, create_sql_for_model_files, \
    create_sql_for_predictions,  SqlRunner


def update_progress(message):
    """
    :param message: str message to print out
    """
    print(message)


def run_all_command(config):
    """
    Download, convert and load files in config into the database.
    :param config: pred.Config: global configuration containing what data to download/convert/load.
    """
    download_files_command(config)
    run_sql_command(config)


def download_files_command(config):
    """
    Download, convert files in config.
    :param config: pred.Config: global configuration containing what data to download/convert/load.
    """
    update_progress("STAGE: Downloading files.")
    download_and_convert(config, update_progress)


def download_models_command(config):
    """
    Subset of download_files_command - just download models based on track_url.
    :param config: pred.Config: global configuration containing which models to download.
    """
    update_progress("STAGE: Downloading tracks.")
    download_models(config, update_progress)


def run_sql_command(config):
    """
    Load local files into the database based on config.
    :param config: pred.Config: global configuration containing what data to download/convert/load.
    """
    update_progress("STAGE: Creating SQL files.")
    sql_pipeline = create_sql_pipeline(config, update_progress)
    update_progress("STAGE: Executing SQL files.")
    run_sql_pipeline(config, sql_pipeline)


def run_sql_models_command(config):
    """
    Load just models into the database based on config.
    This is a subset of run_sql_command.
    :param config: pred.Config: global configuration containing what data to download/convert/load.
    """
    update_progress("STAGE: Creating model SQL files.")
    sql_builder = create_sql_builder()
    create_sql_for_model_files(config, sql_builder)
    update_progress("STAGE: Executing model SQL files.")
    run_sql_pipeline(config, sql_builder.sql_pipeline)


def run_sql_predictions(config):
    """
    Load just predictions into the databse based on config.
    :param config: pred.Config: global configuration containing what data to download/convert/load.
    """
    update_progress("STAGE: Creating predictions SQL files.")
    sql_builder = create_sql_builder()
    create_sql_for_predictions(config, sql_builder, DataType.PREDICTION, update_progress)
    update_progress("STAGE: Executing predictions SQL files.")
    run_sql_pipeline(config, sql_builder.sql_pipeline)


def run_sql_preferences(config):
    """
    Load just preferences into the databse based on config.
    :param config: pred.Config: global configuration containing what data to download/convert/load.
    """
    print("SQL PREFERENCES")
    update_progress("STAGE: Creating preferences SQL files.")
    sql_builder = create_sql_builder()
    create_sql_for_predictions(config, sql_builder, DataType.PREFERENCE, update_progress)
    update_progress("STAGE: Executing preferences SQL files.")
    run_sql_pipeline(config, sql_builder.sql_pipeline)


def run_sql_pipeline(config, sql_pipeline):
    """
    Run all the sql commands in sql_pipeline against the database.
    :param config: pred.Config: global configuration containing what data to download/convert/load.
    :param sql_pipeline: loaddatabase.SQLPipeline: list of sql commands to be run
    """
    runner = SqlRunner(config, update_progress)
    sql_pipeline.run(runner.execute)
    runner.close()


if __name__ == '__main__':
    funcs = {
        'all': run_all_command,
        'download': download_files_command,
        'download_models': download_models_command,
        'run_sql': run_sql_command,
        'run_sql_models' : run_sql_models_command,
        'run_sql_predictions': run_sql_predictions,
        'run_sql_preferences': run_sql_preferences,
    }
    parser = argparse.ArgumentParser(description='Loads prediction database based on imadsconf.yaml')
    parser.add_argument('command', choices=funcs.keys())
    args = parser.parse_args()
    funcs[args.command](parse_config(CONFIG_FILENAME))
