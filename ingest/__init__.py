import os
from .metadata_ingestor_ci import MetadataIngestor
from .node_stats_ingest_ci import NodeStatsIngestor
from .namespace_stats_ingest_ci import NamespaceStatsIngestor
from .set_stats_ingest_ci import SetStatsIngestor
from .security_stats_ingest_ci import SecurityStatsIngestor
from .config_ingest_ci import ConfigIngestor
from .features_ingest_ci import FeaturesIngestor
from .system_info_ingest_ci import SystemInfoIngestor

__version__ = "1.5.4"

# Standardized execution order
INGESTORS = [
    MetadataIngestor(),
    SystemInfoIngestor(),
    FeaturesIngestor(),
    ConfigIngestor(),
    NodeStatsIngestor(),
    NamespaceStatsIngestor(),
    SetStatsIngestor(),
    SecurityStatsIngestor()
]