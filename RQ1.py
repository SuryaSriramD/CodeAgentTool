import os

def check_inconsistency(content):
    # 示例的简化逻辑，需要根据实际需求进行调整
    return "inconsistency" in content

def check_vulnerability(content):
    # 示例的简化逻辑，需要根据实际需求进行调整
    return "vulnerable" in content

def check_format_inconsistency(content):
    # 示例的简化逻辑，需要根据实际需求进行调整
    return "formatting inconsistency" in content

def extract_content_between(head, tail, content):
    start = content.find(head) + len(head)
    end = content.find(tail, start)
    return content[start:end].strip()

def save_content_and_revised_code(folder_name, prefix, content):
    with open(f"{prefix}-{folder_name}.txt", "w") as f:
        f.write(content)
    revised_code = extract_content_between("Revised Code:", "", content)
    with open(f"{prefix}-CR-{folder_name}.txt", "w") as f:
        f.write(revised_code)

def analyze_folder(folder_path):
    CAlist, VAlist, FAlist = [], [], []
    sublist = next(os.walk(folder_path))[1]

    for subfolder in sublist:
        file_path = os.path.join(folder_path, subfolder, "manual.md")
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                content = file.read()

                # Semantic Consistency Analysis
                sca_content = extract_content_between("Semantic Consistency Analysis:", "Security Analysis:", content)
                if check_inconsistency(sca_content):
                    CAlist.append(subfolder)
                    save_content_and_revised_code(subfolder, "CA", sca_content)

                # Security Analysis
                sa_content = extract_content_between("Security Analysis:", "Format Analysis:", content)
                if check_vulnerability(sa_content):
                    VAlist.append(subfolder)
                    save_content_and_revised_code(subfolder, "VA", sa_content)

                # Format Analysis
                fa_content = extract_content_between("Format Analysis:", "Code Alignment/Revision Suggestions:", content)
                if check_format_inconsistency(fa_content):
                    FAlist.append(subfolder)
                    save_content_and_revised_code(subfolder, "FA", fa_content)

    return CAlist, VAlist, FAlist, sublist

def save_list_to_file(list_name, file_name):
    with open(file_name, "w") as file:
        for item in list_name:
            file.write(item + "\n")

# 示例使用
folder_path = "WareHouse"  # 需要根据实际文件夹位置进行调整
CAlist, VAlist, FAlist, sublist = analyze_folder(folder_path)

save_list_to_file(CAlist, "CAlist.txt")
save_list_to_file(VAlist, "VAlist.txt")
save_list_to_file(FAlist, "FAlist.txt")
