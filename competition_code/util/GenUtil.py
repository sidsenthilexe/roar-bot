import csv
import numpy as np

class GenUtil:

    @staticmethod
    def load_file(path):
        with open(path, 'r') as f:
            return [int(r.strip()) for r in f]
