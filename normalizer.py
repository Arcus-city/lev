from datetime import datetime, timezone
from .models import Measurement


def normalize(source_name, protocol, measurements):
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source_name,
        "protocol": protocol,
        "measurements": [
            {
                "name": m.name,
                "value": m.value,
                "unit": m.unit,
                "quality": m.quality,
            }
            for m in measurements
        ],
    }
