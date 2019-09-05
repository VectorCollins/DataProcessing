#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
# 功能介绍：数据随机抽样(默认400)，支持xlsx/csv输入，xlsx输出
# 使用样例1-默认抽取400条：python random_sampling.py filename.xlsx
# 使用样例2-抽取指定数量的数据：python random_sampling.py filename.csv 200
# 使用样例3-抽取给定比例的数据：python random_sampling.py filename.csv 0.15
# 表头说明：默认输入文件有单行表头，如需忽略表头，请注释第40行并删除第41行首井号
# 作者信息：vector
"""

import sys, os, time, platform


def main():
    frac_num = sample_num = 0
    if len(sys.argv) < 2:
        raise Exception("未选择文件")
    elif len(sys.argv) < 3:
        sample_num = 400
    else:
        try:
            tmp_num = eval(sys.argv[2])
        except (NameError, SyntaxError):
            raise Exception("请输入抽样比例或抽样条数")
            
        if 0 < tmp_num <= 1:
            frac_num = tmp_num
        elif tmp_num > 1:
            sample_num = tmp_num
        else:
            raise Exception("请输入正确的抽样比例或抽样条数")

    file_name = sys.argv[1]

    check_pkg()
    import pandas as pd
    
    head = 0     # 输入文件有表头
    #head = None # 输入文件无表头

    first_name = os.path.splitext(file_name)[0]
    last_name = os.path.splitext(file_name)[1].strip('.')
    
    if last_name == 'xlsx':
        try:
            df = pd.DataFrame(pd.read_excel(file_name, header=head))
        except FileNotFoundError:
            raise Exception("没有在当前目录找到文件 ".format(file_name))
    elif last_name == 'csv':
        try:
            df = pd.DataFrame(pd.read_csv(file_name, sep=',', encoding='utf-8', header=head))
        except UnicodeDecodeError:
            try:
                df = pd.DataFrame(pd.read_csv(file_name, sep=',', encoding='GB18030', header=head))
            except UnicodeDecodeError:
                raise Exception("未识别合法字符集，请将文件转为UTF-8格式后重试")
        except FileNotFoundError:
            raise Exception("没有在当前目录找到文件 ".format(file_name))
    else:
        raise Exception("仅支持xlsx或csv格式文件的处理")
        
    for i in range(10):
        df = df.sample(frac=1)
    
    if frac_num:
        df = df.sample(frac=frac_num)
        desc = 'frac_{}'.format(frac_num)
    elif sample_num:
        sample_num = min(df.shape[0], sample_num)
        df = df.sample(n=sample_num)
        desc = 'sample_{}'.format(sample_num)
        
    out_file = '{}_{}'.format(desc, first_name+time.strftime('%Y%m%d%H%M', time.localtime(time.time()))+'.xlsx')
    writer = pd.ExcelWriter(out_file)
    df.to_excel(writer, 'Sheet1', index=False, header=True if head==0 else False)
    writer.save()
    file_open(out_file)
    print("处理完成！\n输出文件名: ", out_file)


def check_pkg():
    attach = "sudo " if sysstr != "Windows" else ""
    os.system(attach + "pip install --upgrade pip")
    for pkg in ["pandas", "xlrd"]:
        if str(os.popen("pip list").readlines()).find(pkg) == -1:
            print("正在安装必要python模块", pkg, "请稍等...")
            os.system("pip install " + pkg)
            print("相关模块已安装完成，开始数据处理...")


def file_open(filename):
    if sysstr == "Windows":
        os.startfile(filename)
    elif sysstr == "Linux":
        os.system("xdg-open " + filename)
    elif sysstr == "Darwin":
        import subprocess
        subprocess.call(["open", filename])
    else:
        print("不能识别操作系统，无法自动打开文件。")


if __name__ == '__main__':
    sysstr = platform.system()
    main()