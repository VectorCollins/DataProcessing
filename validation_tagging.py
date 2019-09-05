#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
# 功能介绍：在训练数据中随机标记验证集支持xlsx/csv输入，csv输出
# 使用样例1-默认特定比例测试集：python validation_tagging.py 0.15,如缺少第三个参数则默认抽取百分之十的验证数据
# 使用样例2-抽取指定数量测试集：python validation_tagging.py 100
# 注意事项：默认情况每个意图验证集不少于一个，默认输入文件没有表头,如需设置表头请把37行的None改为0
# 作者信息：vector
"""

import sys, os, time, platform


def main():
    if len(sys.argv) < 2:
        raise Exception("未选择文件")
    elif len(sys.argv) < 3:
        frac_num = 0.1
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
    first_name = os.path.splitext(file_name)[0]
    last_name = os.path.splitext(file_name)[1].strip('.')

    check_pkg()
    import pandas as pd

    head = None # 输入文件无表头

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

    if df.shape[1] < 2:
        raise Exception("输入文件至少包含两列：意图列、数据列，请选择正确的文件重试")

    df =df.iloc[:,0:2]
    num = df.shape[0]
    df.columns=['intention','data']

    if any(list(df.duplicated('data'))):
        raise Exception("训练数据存在重复项，请手动处理重复项后重试")

    if min(list(df['intention'].value_counts())) < 2:
        raise Exception("每个意图至少包含两条训练数据，请补全数据后重试")

    rdf = df
    for i in range(10):
        rdf = rdf.sample(frac=1)

    base_valid = rdf.drop_duplicates('intention')
    base_train = rdf.drop_duplicates('intention', keep='last')

    rdf = rdf.append(base_valid)
    rdf = rdf.append(base_train)
    other = rdf.drop_duplicates(keep=False)

    if other.shape:
        ad = other
        for i in range(10):
            ad = ad.sample(frac=1)

        ad_valid = ad
        if frac_num:
            ad_valid = ad_valid.sample(frac=(frac_num*num-1)/(num-2))
            desc = 'frac_{}'.format(frac_num)
        elif sample_num:
            sample_num = min(ad_valid.shape[0], sample_num-1)
            ad_valid = ad_valid.sample(n=sample_num)
            desc = 'sample_{}'.format(sample_num+1)

        ad_train = ad
        ad_train = ad.append(ad_valid)
        ad_train = ad_train.drop_duplicates(keep=False)

        validation = base_valid.append(ad_valid).sort_values('intention')
        training = base_train.append(ad_train).sort_values('intention')
    else:
        raise Exception("数据过少，请手动划分")

    training['label'] = u"训练集"
    validation['label'] = u"测试集"

    train_file = u'训练集_{}条_{}_{}'.format(training.shape[0], desc, first_name+time.strftime('%Y%m%d%H%M', time.localtime(time.time()))+'.csv')
    valid_file = u'测试集_{}条_{}_{}'.format(validation.shape[0], desc, first_name+time.strftime('%Y%m%d%H%M', time.localtime(time.time()))+'.csv')
    training.to_csv(train_file, index=False, header=True if head==0 else False)
    validation.to_csv(valid_file, index=False, header=True if head==0 else False)

    file_open(train_file)
    file_open(valid_file)

    print("处理完成！\n输出文件名:\n", u"训练数据集: \n".format(train_file), u"测试数据集: ".format(valid_file))


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


def check_pkg():
    attach = "sudo " if sysstr != "Windows" else ""
    os.system(attach + "pip install --upgrade pip")
    for pkg in ["pandas", "xlrd"]:
        if str(os.popen("pip list").readlines()).find(pkg) == -1:
            print("正在安装必要python模块", pkg, "请稍等...")
            os.system("pip install " + pkg)
            print("相关模块已安装完成，开始数据处理...")


if __name__ == "__main__":
    sysstr = platform.system()
    main()