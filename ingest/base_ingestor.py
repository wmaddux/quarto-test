__version__ = "1.4.1"
from abc import ABC, abstractmethod

class BaseIngestor(ABC):
    @property
    @abstractmethod
    def name(self):
        """Returns the name of the ingestor for logging."""
        pass

    @abstractmethod
    def run_ingest(self, node_id, node_data, conn, run_id):
        """Standard method to parse data and insert into SQLite."""
        pass