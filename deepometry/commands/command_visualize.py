import os.path
import subprocess
import sys

import click
import pandas
import pkg_resources


@click.command(
    "visualize",
    help="""
    """
)
@click.argument(
    "features",
    required=True,
    type=click.Path(exists=True)
)
@click.argument(
    "metadata",
    required=False,
    type=click.Path(exists=True)
)
@click.option(
    "--output-directory",
    default=pkg_resources.resource_filename("deepometry", "data"),
    type=click.Path()
)
def command(features, metadata, output_directory):
    try:
        import tensorflow
    except ImportError:
        click.echo(
            "Tensorflow is required for visualization."
            " To install tensorflow, run `pip install tensorflow`."
        )
        sys.exit(127)

    _validate_tsv(features)
    features_df = pandas.read_csv(features, sep="\t")
    features_tf = tensorflow.Variable(features_df.values, name="features")

    with tensorflow.Session() as session:
        saver = tensorflow.train.Saver([features_tf])
        session.run(features_tf.initializer)
        saver.save(session, os.path.join(output_directory, "embedding.ckpt"))

    config = tensorflow.contrib.tensorboard.plugins.projector.ProjectorConfig()

    embedding = config.embeddings.add()
    embedding.tensor_name = features_tf.name

    if metadata:
        _validate_tsv(metadata)
        embedding.metadata_path = metadata

    tensorflow.contrib.tensorboard.plugins.projector.visualize_embeddings(
        tensorflow.summary.FileWriter(output_directory),
        config
    )

    click.echo(
        "Starting TensorBoard...\n"
        "Please open your web browser and navigate to the address provided:"
    )
    subprocess.call(["tensorboard", "--logdir", output_directory])


def _validate_tsv(path):
    ext = os.path.splitext(path)[-1]

    if ext != ".tsv":
        raise ValueError(
            "Unsupported extension '{:s}'. Expected '.tsv', got '{:s}'".format(ext, path)
        )