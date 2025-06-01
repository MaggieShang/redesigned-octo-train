#!/bin/bash

# 无限循环
while true
    do
    # 运行 Python 脚本
    python3 data_product.py
    python3 data_analysis.py

    # 等待 20 秒
    sleep 20
    done
