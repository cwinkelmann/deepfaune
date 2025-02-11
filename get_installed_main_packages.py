import pkg_resources

packages = [
    "torch",
    "torchvision",
    "ultralytics",
    "timm",
    "pandas",
    "numpy",
    "opencv-python",
    "pillow",
    "dill",
    "hachoir",
    "openpyxl",
]

output_file = "requirement_freeze.txt"

with open(output_file, "w") as f:
    for package in packages:
        try:
            version = pkg_resources.get_distribution(package).version
            f.write(f"{package}=={version}\n")
        except pkg_resources.DistributionNotFound:
            f.write(f"# {package} is not installed\n")

print(f"{output_file} has been generated with the exact package versions.")
