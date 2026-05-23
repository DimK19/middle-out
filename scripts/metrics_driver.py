from metrics import evaluate

result = evaluate(
    "DSC02435.tif",
    "DSC02435_02.jpg"
)

for key, value in result.items():
    print(f"{key}: {value}")
