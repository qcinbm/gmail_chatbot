from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import load_dataset
import torch

# Chọn model base
model_id = "meta-llama/Meta-Llama-3-8B"

tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token

# Load dataset
dataset = load_dataset("wikitext", "data.xlxs")

# Tokenize
def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=128)

tokenized_datasets = dataset.map(tokenize_function, batched=True)

# Load model
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.bfloat16, device_map="auto")

# Cấu hình train
training_args = TrainingArguments(
    output_dir="./llama3-finetuned",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    num_train_epochs=1,
    save_strategy="epoch",
    logging_dir="./logs",
    fp16=False,
    bf16=True,  # bật nếu GPU hỗ trợ
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["validation"],
)

# Train
trainer.train()

prompt = "Extract order number and delivery date from: 'Thank you for your order #12345. Estimated delivery Aug 15.'"
output = tokenizer.decode(model.generate(tokenizer(prompt, return_tensors="pt").input_ids, max_length=50)[0])
print(output)

