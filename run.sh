conda activate ChatDev_conda_env
#!/bin/bash
export OPENAI_API_KEY="sk-ijklmnopqrstuvwxijklmnopqrstuvwxijklmnop"
# cd CodeAgent/WareHouse/FiveKeyWords_THUNLP_20230825072339
# cd ${1}
cd CompanyConfig/Default
python3 ../../run.py --config "ChatChainConfig.json" ${1} ${2} ${3} ${4}

# export OPENAI_API_KEY="your_openai_api_key_here"
# nohup python3 main.py "python" > output-python.log 2>&1 &
# sleep 100
# conda deactivate


# conda activate ChatDev_conda_env
# export OPENAI_API_KEY="your_openai_api_key_here"
# nohup python3 main.py "java" > output-java.log 2>&1 &
# sleep 100
# conda deactivate

# conda activate ChatDev_conda_env
# export OPENAI_API_KEY="your_openai_api_key_here"
# nohup python3 main.py "go" > output-go.log 2>&1 &
# sleep 100
# conda deactivate

# conda activate ChatDev_conda_env
# export OPENAI_API_KEY="your_openai_api_key_here"
# cd ${1}
cd CompanyConfig/Default
python3 ../../run.py --config "ChatChainConfig.json" ${1} ${2} ${3} ${4}


# export OPENAI_API_KEY="your_openai_api_key_here"
# nohup python3 main.py "c++" > output-c++.log 2>&1 &
# sleep 100
# conda deactivate

# conda activate ChatDev_conda_env
# export OPENAI_API_KEY="your_openai_api_key_here"
# nohup python3 main.py "javascript" > output-javascript.log 2>&1 &
# sleep 100
# conda deactivate

# conda activate ChatDev_conda_env
# export OPENAI_API_KEY="your_openai_api_key_here"
nohup python3 main.py "c" > output-c.log 2>&1 &
# sleep 100
# conda deactivate

# conda activate ChatDev_conda_env
# export OPENAI_API_KEY="your_openai_api_key_here"
# cd ${1}
cd CompanyConfig/Default
python3 ../../run.py --config "ChatChainConfig.json" ${1} ${2} ${3} ${4}


# export OPENAI_API_KEY="your_openai_api_key_here"

# conda activate ChatDev_conda_env
# export OPENAI_API_KEY="your_openai_api_key_here"
nohup python3 main.py "php" > output-php.log 2>&1 &
# sleep 100
# conda deactivate

# conda activate ChatDev_conda_env
# export OPENAI_API_KEY="your_openai_api_key_here"
nohup python3 main.py "ruby" > output-ruby.log 2>&1 &
# sleep 100
# conda deactivate