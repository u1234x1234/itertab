import time
import numpy as np
from itertab import PrettyTable

table = PrettyTable()
for epoch in range(15):
    metrics = {
        'epoch': epoch,
        'train': {
            'Accuracy': np.random.uniform(),
            'LogLoss': np.random.uniform(),
        },
    }
    table.add_row(metrics)
    table.clear_screen_and_print()

    time.sleep(0.3)
