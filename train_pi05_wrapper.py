"""Wrapper to increase the distributed timeout before launching lerobot-train."""
import datetime
import os
import torch.distributed as dist

# Monkey-patch the default timeout before any init_process_group call
_original_init = dist.init_process_group

def _patched_init(*args, **kwargs):
    if "timeout" not in kwargs:
        kwargs["timeout"] = datetime.timedelta(minutes=60)
    return _original_init(*args, **kwargs)

dist.init_process_group = _patched_init

# Now run the actual training entry point
from lerobot.scripts.lerobot_train import main
main()
