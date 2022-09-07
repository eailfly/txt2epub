#!/usr/bin/python
import os
import regex as re
import glob
import chardet
import time


def detect_code(path):
    with open(path, 'rb') as file:
        data = file.read(20000)
        dicts = chardet.detect(data)
    return dicts["encoding"]


def trans_txt_code():
    ecode = detect_code(txtname)
    if ecode != 'utf-8' and ecode != 'UTF-8-SIG':
        if 'GB' or 'gb' in ecode:
            ecode = 'gbk'
        else:
            pass
        print("文件编码不是utf-8,开始转换.....")
        orig_f = open(txtname, 'r', encoding=ecode, errors="ignore")
        txt_content = orig_f.read()
        orig_f.close()
        target_f = open(txtname, 'w', encoding="utf-8", errors="ignore")
        target_f.write(txt_content)
        target_f.close()
        print("转换完成")
    else:
        print('文件编码是utf-8，无需转换')


if __name__ == '__main__':
    path = glob.glob('source/*.txt')
    filename = str(path)[9:-6]
    title_string = re.search(r'(?<=《)[^》]+', filename)[0]
    author_string = re.search(r'(?<=作者：).*', filename)[0]
    bookname = title_string
    txtname = 'source/' + filename + ".txt"
    jpgname = 'source/' + bookname + ".jpg"
    epubname = 'target/' + bookname + ".epub"

    print('书名: ' + bookname + '\n' + '作者: ' + author_string)

    start01 = time.perf_counter()

    print("开始文件转码.......")

    trans_txt_code()
    print('开始分章以及处理多余内容')
    with open(txtname, 'r', encoding="utf-8") as f:
        content = f.read()

    lines = content.rsplit("\n")
    new_content = []
    new_content.append("% " + title_string)
    new_content.append("% " + author_string)

    for line in lines:

        if line == "更多精校小说尽在知轩藏书下载：http://www.zxcs.me/" or line == "==========================================================" or line == title_string or line == title_string + " 作者：" + author_string or line == "作者：" + author_string or line == "作者: " + author_string:
            continue
        if line == "简介:" or line == "内容简介：" or line == "内容简介":
            new_content.append("### " + line + "\n")
            continue
        if re.match(r'^\s*(楔子|序章|序言|序|引子).*', line):
            new_content.append("## " + line + "\n")
            continue
        if re.match(r'^\s*[第][0123456789ⅠI一二三四五六七八九十零序〇百千两]*[卷].*', line):
            new_content.append("# " + line + "\n")
        if re.match(r'^\s*[卷][0123456789ⅠI一二三四五六七八九十零序〇百千两]*[ ].*', line):
            new_content.append("# " + line + "\n")
            continue

        if re.match(r'^\s*[第][0123456789ⅠI一二三四五六七八九十零序〇百千两]*[章].*', line):
            new_content.append("## " + line + "\n")
            continue

        new_content.append(line + "\n")
    new_content = "\n".join(new_content)

    with open(txtname, 'w', encoding="utf=8") as f:
        f.write(new_content)
    end01 = time.perf_counter()
    print('初始化用时：%s秒' % (end01 - start01))

    ## 生成epub文件
    start02 = time.perf_counter()
    print("开始生成EPUB文件........")
    # TODO: user customer fonts, make css change
    os.system('pandoc "%s" -o "%s" -t epub3 --css=./epub.css --epub-chapter-level=2 --epub-cover-image="%s"' % (
        txtname, epubname, jpgname))
    end02 = time.perf_counter()
    print('epub用时：%s秒' % (end02 - start02))

    print("完成，收工，撒花！！🎉🎉")
