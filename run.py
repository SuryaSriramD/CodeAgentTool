# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========
# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========
import argparse
import logging
import os
import sys

from camel.typing import ModelType

root = os.path.dirname(__file__)
sys.path.append(root)

# from chatdev.chat_chain import ChatChain
from codeagent.chat_chain import ChatChain


def get_config(company):
    """
    return configuration json files for ChatChain
    user can customize only parts of configuration json files, other files will be left for default
    Args:
        company: customized configuration name under CompanyConfig/

    Returns:
        path to three configuration jsons: [config_path, config_phase_path, config_role_path]
    """
    config_dir = os.path.join(root, "CompanyConfig", company)
    default_config_dir = os.path.join(root, "CompanyConfig", "Default")

    config_files = [
        "ChatChainConfig.json",
        "PhaseConfig.json",
        "RoleConfig.json"
    ]

    config_paths = []

    for config_file in config_files:
        company_config_path = os.path.join(config_dir, config_file)
        default_config_path = os.path.join(default_config_dir, config_file)

        if os.path.exists(company_config_path):
            config_paths.append(company_config_path)
        else:
            config_paths.append(default_config_path)

    return tuple(config_paths)


parser = argparse.ArgumentParser(description='argparse')
parser.add_argument('--config', type=str, default="Default",
                    help="Name of config, which is used to load configuration under CompanyConfig/")
parser.add_argument('--org', type=str, default="",
                    help="Name of organization, your software will be generated in WareHouse/name_org_timestamp")
parser.add_argument('--task', type=str, default="",
                    help="please load initial instruct and files")
parser.add_argument('--ifcode', type=str, default="code",
                    help="code review or commit review")
parser.add_argument('--name', type=str, default="sha-codereview",
                    help="Name of code review report, will be stored in WareHouse/name_org_timestamp")
parser.add_argument('--commit', type=str, default="commit path",
                    help="commit path")
parser.add_argument('--commitmessage', type=str, default="",
                    help="commit message path")
parser.add_argument('--originalfile', type=str, default="",
                    help="originalfile")
parser.add_argument('--model', type=str, default="GPT_4",
                    help="GPT Model, choose from {'GPT_3_5_TURBO','GPT_4','GPT_4_32K'}")
parser.add_argument('--path', type=str, default="",
                    help="Your file directory, CodeAgent will build upon your software in the Incremental mode")
parser.add_argument('--PRinfo', type=str, default="",
                    help="repoowner reponame githubtoken")
parser.add_argument('--AcName', type=str, default="",
                    help="Action Name")
args = parser.parse_args()

if args.ifcode=="code":
    task_initial_instruct= """
    I hava a code, potentially have some bugs inside, please
    generate the right one to me to fix it.
    I would like a detailed code review based on the following aspect:
    problems or potential bugs analysis: 
    Conduct a potential bugs of the code. Provide details of any such findings like potential bugs or risks.
    The final feedback should be structured as follows:
    bug analysis: [Your detailed analysis and suggestions]
    code revision suggestion: [Your proposed code revisions or alignment suggestions, if any]
    """
else:
    task_initial_instruct = """
    I have a code, which includes the commit message, and the corresponding original file, these file are connected like this 
    code <PAD> commit message <PAD> original file. 
    If there is commit message is null, please don't do Semantic Consistency Analysis. if orignial file is null, please don't do Format Analysis.
    I would like a detailed code review based on the following three aspects:

    Semantic Consistency Analysis:
    Please analyze the semantic consistency between the code changes in side the code and the commit message. Check if the changes in the codes accurately reflect the description provided in the commit message. Highlight any inconsistencies that might lead to confusion or potential hidden malicious code.
    Security Analysis:
    Please perform a comprehensive security review on the provided code or recent code modifications, focusing on critical areas that could lead to vulnerabilities or other reasons easy to cause vulnerabilities. Please give me one paragraph review feedback. This review should include validating user input to prevent SQL injection, XSS, and command injection risks. Also, ensure robust memory management in lower-level languages to avoid buffer overflows. The analysis must cover authentication and authorization processes, along with how sensitive data is managed, to prevent unauthorized access and data breaches. Proper handling of errors and exceptions is vital to avoid leaking sensitive information and causing service interruptions. Examine all dependencies, APIs, and configurations, including third-party libraries, for potential vulnerabilities. Be vigilant against CSRF attacks, code injection, race conditions, memory leaks, and poor resource management. Ensure security configurations are strong, particularly avoiding weak defaults and ensuring encrypted communications. Pay special attention to path traversal, file inclusion vulnerabilities, unsafe deserialization, XXE attacks, SSRF, and unsafe redirects. Ensure no deprecated functions, hardcoded sensitive data, or code leakages are present. For mobile and cloud-based applications, additional focus should be on mobile code security and cloud service configuration integrity. After completing the analysis, provide a summarized paragraph of any vulnerabilities found.
    Format Analysis:
    Assess if the format of the code aligns with the writing style and format of the original file. Evaluate the impact of any formatting inconsistencies on the overall readability and maintainability of the project.
    For each of the above aspects, please provide a clear analysis and any necessary suggestions for improvement. If you find any issues, especially in the code, provide specific suggestions or rewritten code snippets to guide the commit contributor on how to make the necessary revisions.

    

    The final feedback should be structured as follows:
    Semantic Consistency Analysis: [Your detailed analysis and suggestions]
    Security Analysis: [Your conclusion and if any security problem, please provide detailed analysis and suggestions]
    Format Analysis: [Your detailed analysis and suggestions]
    Code Alignment/Revision Suggestions: [Your proposed code revisions for the commit or suggestions, if any]
    revised code: [Your revised commit, if any]
    """


    #     task_initial_instruct = """
    # I have a code, which includes the commit message, and the corresponding original file, these file are connected like this 
    # code <PAD> commit message <PAD> original file. 
    # If there is commit message is null, please don't do Semantic Consistency Analysis. if orignial file is null, please don't do Format Analysis.
    # I would like a detailed code review based on the following three aspects:

    # Semantic Consistency Analysis:
    # Please analyze the semantic consistency between the code changes in side the code and the commit message. Check if the changes in the codes accurately reflect the description provided in the commit message. Highlight any inconsistencies that might lead to confusion or potential hidden malicious code.
    # Security Analysis:
    # Conduct a vulnerability analysis of the code. Identify if any modifications could potentially introduce security vulnerabilities, attacks, or bugs. Provide details of any such findings.
    # Format Analysis:
    # Assess if the format of the code aligns with the writing style and format of the original file. Evaluate the impact of any formatting inconsistencies on the overall readability and maintainability of the project.
    # For each of the above aspects, please provide a clear analysis and any necessary suggestions for improvement. If you find any issues, especially in the code, provide specific suggestions or rewritten code snippets to guide the commit contributor on how to make the necessary revisions.

    

    # The final feedback should be structured as follows:
    # Semantic Consistency Analysis: [Your detailed analysis and suggestions]
    # Security Analysis: [Your detailed analysis and suggestions]
    # Format Analysis: [Your detailed analysis and suggestions]
    # Code Alignment/Revision Suggestions: [Your proposed code revisions for the commit or suggestions, if any]
    # revised code: [Your revised commit, if any]
    # """

    # if you don't find any vulnerability, please say no vulnerability findings, if you find something, please describe in details:
        # 1. **Insufficient Input Validation**: Check for vulnerabilities like SQL injection, Cross-Site Scripting (XSS), and command injection in new or modified code, especially where user input is processed.
        # 2. **Buffer Overflows**: Particularly in lower-level languages, ensure that memory management is handled securely to prevent overflows.
        # 3. **Authentication and Authorization Flaws**: Evaluate any changes in authentication and authorization logic for potential weaknesses that could allow unauthorized access or privilege escalation.
        # 4. **Sensitive Data Exposure**: Assess handling and storage of sensitive information like passwords, private keys, or personal data to prevent exposure.
        # 5. **Improper Error and Exception Handling**: Ensure that errors and exceptions are handled appropriately without revealing sensitive information or causing service disruption.
        # 6. **Vulnerabilities in Dependency Libraries or Components**: Review updates or changes in third-party libraries or components for known vulnerabilities.
        # 7. **Cross-Site Request Forgery (CSRF)**: Verify that adequate protection mechanisms are in place against CSRF attacks.
        # 8. **Unsafe Use of APIs**: Check for the use of insecure encryption algorithms or other risky API practices.
        # 9. **Code Injection**: Look for vulnerabilities related to dynamic code execution.
        # 10. **Configuration Errors**: Ensure that no insecure configurations or settings like open debug ports or default passwords have been introduced.
        # 11. **Race Conditions**: Analyze for potential data corruption or security issues arising from race conditions.
        # 12. **Memory Leaks**: Identify any changes that could potentially lead to memory leaks and resource exhaustion.
        # 13. **Improper Resource Management**: Check resource management, such as proper closure of file handles or database connections.
        # 14. **Inadequate Security Configurations**: Assess for any insecure default settings or unencrypted communications.
        # 15. **Path Traversal and File Inclusion Vulnerabilities**: Examine for risks that could allow unauthorized file access or execution.
        # 16. **Unsafe Deserialization**: Look for issues that could allow the execution of malicious code or tampering with application logic.
        # 17. **XML External Entity (XXE) Attacks**: Check if XML processing is secure against XXE attacks.
        # 18. **Inconsistent Error Handling**: Review error messages to ensure they do not leak sensitive system details.
        # 19. **Server-Side Request Forgery (SSRF)**: Analyze for vulnerabilities that could be exploited to attack internal systems.
        # 20. **Unsafe Redirects and Forwards**: Check for vulnerabilities leading to phishing or redirection attacks.
        # 21. **Use of Deprecated or Unsafe Functions and Commands**: Identify usage of any such functions and commands in the code.
        # 22. **Code Leakages and Hardcoded Sensitive Information**: Look for hardcoded passwords, keys, or other sensitive data in the code.
        # 23. **Unencrypted Communications**: Verify that data transmissions are securely encrypted to prevent interception and tampering.
        # 24. **Mobile Code Security Issues**: For mobile applications, ensure proper handling of permission requests and secure data storage.
        # 25. **Cloud Service Configuration Errors**: Review any cloud-based configurations for potential data leaks or unauthorized access.
        # Please provide a detailed analysis of these code changes based on the above aspects, highlighting any identified vulnerabilities and suggesting specific improvements.
            

_file = []
with open(args.commit, 'r') as f:
    lines = f.readlines()
    for line in lines:
        _file.append(line)
    _file.append('<PAD>')

if args.commitmessage!="":
    with open(args.commitmessage, 'r') as f:
        lines = f.readlines()
        for line in lines:
            _file.append(line)
        _file.append('<PAD>')

if args.originalfile!="":
    with open(args.originalfile , 'r') as f:
        lines = f.readlines()
        for line in lines:
            _file.append(line)


args.task = task_initial_instruct +" ".join(_file)
from transformers import GPT2Tokenizer

"""
GPT3.5 Max Token: 4096
GPT4 Max Token: 8000 
GPT-4_32K Max Token: 32,768
"""
if args.model=="GPT_3_5_TURBO":
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    encoded_input = tokenizer.encode(args.task)
    if len(encoded_input) > 3000:
        encoded_input = encoded_input[:3000]
    args.task = tokenizer.decode(encoded_input)
elif args.model=="GPT_4":
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    encoded_input = tokenizer.encode(args.task)
    if len(encoded_input) > 4000:
        encoded_input = encoded_input[:4000]
    args.task = tokenizer.decode(encoded_input)




# Start CodeAgent

# ----------------------------------------
#          Init ChatChain
# ----------------------------------------
config_path, config_phase_path, config_role_path = get_config(args.config)
args2type = {'GPT_3_5_TURBO': ModelType.GPT_3_5_TURBO, 'GPT_4': ModelType.GPT_4, 'GPT_4_32K': ModelType.GPT_4_32k}
chat_chain = ChatChain(config_path=config_path,
                       config_phase_path=config_phase_path,
                       config_role_path=config_role_path,
                       task_prompt=args.task,
                       project_name=args.name,
                       org_name=args.org,
                       model_type=args2type[args.model],
                       code_path=args.path,
                       PRinfo = args.PRinfo,
                       AcName = args.AcName)

# ----------------------------------------
#          Init Log
# ----------------------------------------
logging.basicConfig(filename=chat_chain.log_filepath, level=logging.INFO,
                    format='[%(asctime)s %(levelname)s] %(message)s',
                    datefmt='%Y-%d-%m %H:%M:%S', encoding="utf-8")

# ----------------------------------------
#          Pre Processing
# ----------------------------------------

chat_chain.pre_processing()

# ----------------------------------------
#          Personnel Recruitment
# ----------------------------------------

chat_chain.make_recruitment()

# ----------------------------------------
#          Chat Chain
# ----------------------------------------

chat_chain.execute_chain()

# ----------------------------------------
#          Post Processing
# ----------------------------------------

chat_chain.post_processing()
