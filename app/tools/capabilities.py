
from enum import Enum


class ToolCapability(str, Enum):
    READ = "read"
    ANALYZE = "analyze"
    INTERNAL_WRITE = "internal_write"
    EXTERNAL_ACTION = "external_action"
    FINANCIAL_ACTION = "financial_action"

