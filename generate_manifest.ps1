import os

output_file = "manifest.md"
source_dir = "."  # Current directory

# 1. Clean up existing manifest
if os.path.exists(output_file):
    os.remove(output_file)

# 2. Process files
with open(output_file, "a", encoding="utf-8") as f_out:
    for root, dirs, files in os.walk(source_dir):
        # Exclude noise folders
        if any(x in root for x in ['taxoflow_venv', '.git', '__pycache__']):
            continue
            
        for file in files:
            if file.endswith(".py") and file != "generate_manifest.py":
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, source_dir)
                
                print(f"Processing: {relative_path}")
                
                # Header and Code Block Start
                f_out.write(f"## FILE: {relative_path}\n\n")
                f_out.write("```python\n")
                
                # Stream content
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f_in:
                    f_out.write(f_in.read())
                
                # Close Block
                f_out.write("\n```\n\n")

print(f"\nSuccess! Manifest created: {os.path.abspath(output_file)}")