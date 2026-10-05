from datasets import load_dataset

dataset = load_dataset(
    "bennexx/WJTSentDiL",
    "main_data",
    split="train",
    streaming=True
)

print("First 10 rows:\n")

for i, row in enumerate(dataset.take(10)):
    print(i + 1, row)