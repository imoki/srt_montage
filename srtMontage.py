import os
import re
import pysrt
from pysrt import SubRipTime

# 将文件名列表按多少个个文件作为一个子列表进行分组
chunk_size =15  # 15个为一组，默认，可自定义

# 替换为你的srt字幕文件夹路径和输出文件路径
input_folder = "srtchapter/"    # 拼接前srt字幕文件所在文件夹，可自定义
outputPath = 'srtmerge/'    # 拼接后存放的字幕文件夹，可自定义

# 例如：
# chunk_size =3  # 多少个srt文件为一组。如3个为一组
# 拼接前：“第1章.srt”、“第2章.srt”、“第3章.srt”
# 拼接后：“章_1_2_3.srt”

# 合并
def merge_srt(sublist, output_file):
    with open(output_file, 'w', encoding='utf-8') as out:
        start_time = 0
        end_time = 0
        duration = 0
        num = 1
        fist_time = SubRipTime(0, 0, 0) # 时 分 秒
        second_time = SubRipTime(0, 0, 0)

        for filename in sublist:
            file_path = os.path.join(input_folder, filename)
            # 读取字幕
            subs = pysrt.open(file_path)
            # 遍历字幕行并获取持续时间
            for sub in subs:
                start_time = sub.start
                end_time = sub.end
                duration = end_time - start_time    # 持续时间
                text = sub.text
                # 修改起始终止时间，以便使拼接后时间按顺序排
                fist_time = second_time
                second_time = fist_time + duration

                out.write(str(num) + '\n')  # 写入内容行
                out.write(f'{fist_time} --> {second_time}\n')
                out.write(text + '\n\n')  # 写入内容行
                num += 1

# 自定义排序key函数，用于使得列表按章的顺序排序
def sort_key(item):
    # 提取数字部分
    match = re.search(r'(\d+)', item)
    if match:
        return int(match.group(1))
    else:
        return 0  # 对于无法匹配数字的项，返回0以使其排在前面

# 提取第*章，之间的数字
def extract_chapter_content(input_str):
    match = re.search(r'第(\d+)章(.*)', input_str)
    if match:
        number, content = match.groups()
        return int(number), content
    return None, None

# 合并后的名称格式转换为“章_1_2_3.srt”这样的格式
def convert_to_pattern(input_list):
    numbers = []
    for input_ in input_list:
        # 提取文件名和扩展名
        # filename, extension = input_.rsplit('.', 1)
        # print(filename)
        filenameNum, content = extract_chapter_content(input_)
        # 提取数字部分
        numbers.append(int(filenameNum))
    # 构建新的文件名
    new_filename = '章' + '_'.join(str(num) for num in numbers) + '.srt'
    return new_filename

if __name__ == "__main__":
    file_list = sorted(os.listdir(input_folder), key=lambda x: x[:-4])  # 按文件名排序，忽略.srt后缀
    # 按照自定义的排序key对file_list进行排序
    file_list = sorted(file_list, key=sort_key)
    
    # 根据chunk_size，定义多少个为一组
    sublists = []
    start_index = 0
    while start_index < len(file_list):
        sublists.append(file_list[start_index:start_index+chunk_size])
        start_index += chunk_size

    # 开始合并
    i = 0
    for sublist in sublists:  
        # 传入需要合并的列表
        output_file = convert_to_pattern(sublist)
        print(output_file)
        output_file = outputPath + output_file +".srt"
        merge_srt(sublist, output_file)
        i += 1

    