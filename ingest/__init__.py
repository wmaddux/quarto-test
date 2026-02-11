__version__ = "1.4.1"
# ingest/__init__.py

from .node_stats_ingest_ci import NodeStatsIngestor
from .namespace_stats_ingest_ci import NamespaceStatsIngestor
from .config_ingest_ci import ConfigIngestor
from .system_info_ingest_ci import SystemInfoIngestor
from .features_ingest_ci import FeaturesIngestor
from .metadata_ingestor_ci import MetadataIngestor

INGESTORS = [
    NodeStatsIngestor(),
    NamespaceStatsIngestor(),
    ConfigIngestor(),
    SystemInfoIngestor(),
    FeaturesIngestor(),
    MetadataIngestor()  # Add this
]