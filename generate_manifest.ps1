import os

# Updated to target the specific sub-folder
# source_dir = os.path.join("taxoflow-agents", "urban_pulse_v2")
source_dir = "urban_pulse_v2"
output_file = "manifest_v2.md"

# 1. Safety check: ensure the target directory actually exists
if not os.path.exists(source_dir):
    print(f"Error: The directory '{source_dir}' was not found.")
    exit()

# 2. Clean up existing manifest
if os.path.exists(output_file):
    os.remove(output_file)

# 3. Process files
print(f"Scanning directory: {source_dir}...\n")

with open(output_file, "a", encoding="utf-8") as f_out:
    for root, dirs, files in os.walk(source_dir):
        # Exclude noise folders
        if any(x in root for x in ['taxoflow_venv', '.git', '__pycache__']):
            continue
            
        for file in files:
            # Check for .py files and ignore the script itself
            if file.endswith(".py") and file != "generate_manifest.py":
                file_path = os.path.join(root, file)
                # Keep relative path based on the source_dir for cleaner headers
                relative_path = os.path.relpath(file_path, source_dir)
                
                print(f"Processing: {relative_path}")
                
                # Header and Code Block Start
                f_out.write(f"## FILE: {relative_path}\n\n")
                f_out.write("```python\n")
                
                # Stream content
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f_in:
                        f_out.write(f_in.read())
                except Exception as e:
                    f_out.write(f"# Error reading file: {e}")
                
                # Close Block
                f_out.write("\n```\n\n")

print(f"\nSuccess! Manifest created: {os.path.abspath(output_file)}")