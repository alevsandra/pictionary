#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

import torch.nn as nn
import torch.nn.functional as F


class CNN(nn.Module):
    def __init__(self, classes):
        super(CNN, self).__init__()

        self.conv1 = nn.Conv2d(1, 64, 3, 1, 1)
        self.conv2 = nn.Conv2d(64, 256, 3, 1, 1)
        self.conv3 = nn.Conv2d(256, 512, 3, 1, 1)

        self.fc1 = nn.Linear(512*3*3, 512)
        self.fc2 = nn.Linear(512, classes)

    def forward(self, x):
        x = F.max_pool2d(F.relu(self.conv1(x)), (2, 2))
        x = F.max_pool2d(F.relu(self.conv2(x)), (2, 2))
        x = F.max_pool2d(F.relu(self.conv3(x)), (2, 2))
        x = x.view(x.size(0), -1)
        x = self.fc1(x)
        x = self.fc2(x)
        return x


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
