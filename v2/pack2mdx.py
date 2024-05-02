"""
打包 mdx 文件
"""

import glob
import logging
import os
import re

import main

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
os.chdir(CURRENT_PATH)


rule_path = os.path.join(CURRENT_PATH, r"rule")
INDEX_PATH = os.path.join(CURRENT_PATH, r"index")
PROCESS_PATH = os.path.join(CURRENT_PATH, r"process")


def check_pack_file():
    """检查打包文件"""
    # 合并所有词条
    source_dir = os.path.join(CURRENT_PATH, "process")
    process_pack_file = os.path.join(source_dir, "pack_process.txt")
    release_pack_file = os.path.join(source_dir, "pack_release.txt")
    # 获取所有 .txt 文件的路径
    source_files = glob.glob(os.path.join(source_dir, "*.txt"))
    for file in source_files:
        with open(file, "r", encoding="utf-8") as source_file, open(
            process_pack_file, "a", encoding="utf-8"
        ) as pack_process_file:
            pack_process_file.write(source_file.read())

    # 清理重复行
    process_pack_set = set()
    with open(process_pack_file, "r", encoding="utf-8") as input_file, open(
        release_pack_file, "w", encoding="utf-8"
    ) as output_file:
        process_pack_file_text = input_file.read()
        # 将需要打包的文件按照一个词条占一行的原则，删除那些完全一样的行
        process_pack_file_text = process_pack_file_text.replace("\n", "")
        process_pack_file_text = process_pack_file_text.replace("</>", "</>\n")
        process_pack_file_lines = process_pack_file_text.split("\n")
        for line in process_pack_file_lines:
            process_pack_set.add(line)
        release_pack_list = list(process_pack_set)

        # 不符合mdx文件格式规范会导致打包时报错
        error_line_reg = re.compile(r'^<section class="description">')
        for line in release_pack_list:
            if re.search(error_line_reg, line) is not None:
                logging.critical("%s", line)
                continue
            line = line.replace(
                '<section class="description">', '\n<section class="description">'
            )
            if "</a>" in line:
                line = line.replace("</a>", "</a>\n")
            line = line.replace("</section></>", "</section>\n</>\n")
            output_file.writelines(line)
    return process_pack_file, release_pack_file


def pack2mdx():
    """使用 mdict-utils 打包为mdx文件"""
    process_pack_file, release_pack_file = check_pack_file()

    release_path = os.path.join(CURRENT_PATH, "release_pub")
    title_file = os.path.join(release_path, "title.html")
    description_file = os.path.join(release_path, "description.html")
    mdx_file = os.path.join(release_path, "NonJishoKei.mdx")
    pack_config = f"--title {title_file} --description {description_file}"
    pack_cmd = f"mdict {pack_config} -a {release_pack_file} {mdx_file}"
    # 打包
    os.system(pack_cmd)
    # 删除过程文件
    os.remove(process_pack_file)
    os.remove(release_pack_file)


main.inflect_nonjishokei()
pack2mdx()
