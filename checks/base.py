# Base module for data validation checks - provides abstract base class for all check implementations
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List
import pandas as pd
from models import Finding

# Type alias for the tables dictionary structure used throughout the check framework
# Maps table names (strings) to their corresponding DataFrames
Tables = Dict[str, pd.DataFrame]

class BaseCheck(ABC):
    """
    Abstract base class for all data validation checks.
    
    Subclasses must implement the run() method to define custom validation logic.
    This framework allows standardized checks on database tables stored as DataFrames.
    """
    # Unique identifier for the check
    check_id: str = 'BASE'
    # Human-readable name of the check
    name: str = 'Base check'
    # Detailed description of what the check validates
    description: str = ''
    # Default severity level for findings (can be overridden per finding)
    severity_default: str = 'ERROR'

    @abstractmethod
    def run(self, tables: Tables) -> List[Finding]:
        """
        Execute the validation check on the provided tables.
        
        This method must be implemented by all subclasses to define custom validation logic.
        
        Args:
            tables: Dictionary mapping table names (str) to DataFrames. The check can access
                   required tables from this dictionary (e.g., tables['ASSETS']).
        
        Returns:
            List of Finding objects representing validation errors/warnings found. 
            Returns empty list if no issues are detected.
        """
        ...
