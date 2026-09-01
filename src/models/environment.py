import platform
import sys

import numpy
import pandas
import sklearn


print("=" * 70)
print("RECLAIM — ENVIRONMENT INFORMATION")
print("=" * 70)

print("\nPython")
print("-" * 70)
print(sys.version)

print("\nPlatform")
print("-" * 70)
print(platform.platform())

print("\nPackage Versions")
print("-" * 70)

print(f"NumPy:         {numpy.__version__}")
print(f"Pandas:        {pandas.__version__}")
print(f"Scikit-learn:  {sklearn.__version__}")

print("\n" + "=" * 70)
print("Environment check complete")
print("=" * 70)