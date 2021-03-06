import click
from flask import Flask
from flask_caching import Cache
from waitress import serve

import loader
from controllers import AthenaController
from view import register_filters
from version import get_latest_version


def create_flask_app(database: str, table_name: str, output_location: str) -> Flask:
    app = Flask('lakeview')
    app.config.from_mapping({
        'DEBUG': False,
        'CACHE_TYPE': 'simple',
        'CACHE_DEFAULT_TIMEOUT': 86400,
        'CACHE_THRESHOLD': 500,
    })

    cache = Cache(app)

    # Setup inventory
    db = loader.Inventory(athena_database=database, athena_table=table_name, output_location=output_location)

    # Register flask filters
    register_filters(app)
    controller = AthenaController(db, cache)
    app.register_blueprint(controller.as_blueprint())
    return app



BANNER = """

██╗      █████╗ ██╗  ██╗███████╗██╗   ██╗██╗███████╗██╗    ██╗
██║     ██╔══██╗██║ ██╔╝██╔════╝██║   ██║██║██╔════╝██║    ██║
██║     ███████║█████╔╝ █████╗  ██║   ██║██║█████╗  ██║ █╗ ██║
██║     ██╔══██║██╔═██╗ ██╔══╝  ╚██╗ ██╔╝██║██╔══╝  ██║███╗██║
███████╗██║  ██║██║  ██╗███████╗ ╚████╔╝ ██║███████╗╚███╔███╔╝
╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝  ╚═══╝  ╚═╝╚══════╝ ╚══╝╚══╝ 
"""


@click.command()
@click.option('--database', default='default', help='Name of the Athena database to use')
@click.option('--table', default='inventory', help='Name of the Athena table containing the S3 inventory')
@click.option('--output-location', required=True, help='s3 URI to write Athena outputs to')
@click.option('--host', default='0.0.0.0', help='host to bind the webserver to')
@click.option('--port', default=5000, help='port to bind the webserver to')
def cli(database, table, output_location, host, port):
    latest_version = get_latest_version()
    app = create_flask_app(database, table, output_location)
    print(BANNER)
    print(f'Athena database = {database}')
    print(f'Athena table    = {table}')
    print(f'Output location = {output_location}')
    print(f'Listen host     = {host}')
    print(f'Listen port     = {port}\n\n')
    if latest_version:
        print(f'[WARNING] a newer version exists: {latest_version}\n')
    serve(app, host=host, port=port)


if __name__ == '__main__':
    cli()
