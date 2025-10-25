import pickle
import subprocess
from tqdm import tqdm
import ipdb
import time
import sys

# 检查是否有足够的参数传入
if len(sys.argv) > 1:
    # 第一个参数（sys.argv[0]）是脚本名，所以我们使用sys.argv[1]
    lg = sys.argv[1]
    print(f"Received string: {lg}")
else:
    print("No string was passed in.")


# 打开文件用于读取
with open('visit_file.pkl', 'rb') as file:
    visit_files = pickle.load(file)

# languages = [i for i in visit_files.keys()]
# languages = ['go', 'java']
languages = [f'{lg}']

# 准备一个文件用于记录出错的子程序信息
error_log_filename = 'error_log.txt'

# 遍历每种语言及其对应的SHA值
for language in languages:
    if len(visit_files[language][0])>100:
        merged_names = visit_files[language][0][20:100]
    else:
        merged_names = visit_files[language][0][20:]
    # merged_names = visit_files[language][0][20:80]  # 获取当前语言的merged SHA列表
    if len(visit_files[language][1])>100:
        closed_names = visit_files[language][1][20:100] 
    else:
        closed_names = visit_files[language][1][20:]
    # closed_names = visit_files[language][1][20:40]  # 获取当前语言的closed SHA列表
    merged_names = visit_files[language][0][31:50]
    closed_names = visit_files[language][1][:50]
    
    # 处理merged_names和closed_names
    for sha_list, type_name in [(merged_names, "merged"), (closed_names, "closed")]:
        for sha in tqdm(sha_list, desc=f"Processing {language} {type_name} SHAs"):
            commit_path = f"PR/{language}-commits/{sha}-commit.txt"
            message_path = f"PR/{language}-commits/{sha}-message.txt"
            context_path = f"PR/{language}-commits/{sha}-context.txt"
            print(commit_path)
            listname = "__".join(sha.split('/'))
            # 构建命令
            command = [
                "python3", "run.py",
                "--ifcode", "commit",
                "--name", f"{language}__{listname}",
                "--commit", commit_path,
                "--commitmessage", message_path,
                "--originalfile", context_path
            ]
            start_time = time.time()

            # 调用外部Python程序
            result = subprocess.run(command, capture_output=True, text=True)
            
            # 检查子程序是否成功执行
            if result.returncode != 0:
                # 如果出错，将错误记录到文件中
                with open(error_log_filename, 'a') as error_file:
                    error_info = f"Error in {language}/{sha}: {result.stderr}\n"
                    error_file.write(error_info)

print("程序执行完成。")
