import os

def get_user_input():
    """获取用户输入的文件路径，并询问是否替换 sth/sb"""
    print("请输入文件路径（直接回车使用默认文件名）：")
    bbdc_path = input("BBDC 文件路径 [默认: BBDC.txt]: ").strip().strip('"')
    anki_path = input("Anki 文件路径 [默认: Anki.txt]: ").strip().strip('"')

    if not bbdc_path:
        bbdc_path = "BBDC.txt"
    if not anki_path:
        anki_path = "Anki.txt"

    # 询问是否替换 sth / sb
    sb_replace_choice = input("是否将 'sb' 替换为 'somebody'？(Y/n) [默认: Y]: ").strip().lower()
    sth_replace_choice = input("是否将 'sth' 替换为 'something' ？(Y/n) [默认: Y]: ").strip().lower()
    sb_do_replace = sb_replace_choice in ('', 'y', 'yes')
    sth_do_replace = sth_replace_choice in ('', 'y', 'yes')

    return bbdc_path, anki_path, sb_do_replace, sth_do_replace

def replace_sth_sb(text, sb_do_replace, sth_do_replace):
    # 注意：为了避免误替换（如 "absb" 中的 sb），可考虑用单词边界，但简单场景直接替换即可
    if sb_do_replace:
        text = text.replace('sb', 'somebody')
    if sth_do_replace:
        text = text.replace('sth', 'something')
    return text

def parse_anki_file(filepath):
    """解析 Anki.txt 文件"""
    anki_dict = {}
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Anki 文件未找到: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) >= 2:
                english = parts[0].strip()
                chinese = parts[1].strip()
                anki_dict[english] = chinese
    return anki_dict

def update_bbdc_file(bbdc_path, anki_dict, output_path, sb_do_replace, sth_do_replace):
    """读取 BBDC.txt，先替换 sth/sb（如果启用），再用 Anki 更新释义"""
    if not os.path.exists(bbdc_path):
        raise FileNotFoundError(f"BBDC 文件未找到: {bbdc_path}")
    with open(bbdc_path, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            original_line = line.strip()
            if not original_line:
                f_out.write('\n')
                continue

            if ',' not in original_line:
                f_out.write(original_line + '\n')
                continue

            idx_part, rest = original_line.split(',', 1)

            if ',' not in rest:
                f_out.write(original_line + '\n')
                continue

            english, chinese = rest.split(',', 1)
            english = english.strip()
            chinese = chinese.strip()

            # ✅ 在这里立即进行 sth/sb 替换（仅对 BBDC 原始内容）
            english = replace_sth_sb(english, sb_do_replace, sth_do_replace)
            # chinese = replace_sth_sb(chinese, True)

            # 如果 Anki 中有这个英文短语，就替换中文释义（使用 Anki 的原始内容，不替换 sth/sb）
            if english in anki_dict:
                new_chinese = anki_dict[english]
                # 注意：Anki 的释义不进行 sth/sb 替换（按你的需求，只替换 BBDC 的原始内容）
                new_line = f"{idx_part},{english},{new_chinese}"
            else:
                new_line = f"{idx_part},{english},{chinese}"

            f_out.write(new_line + '\n')

def main():
    try:
        bbdc_path, anki_path, sb_do_replace, sth_do_replace = get_user_input()
        anki_dict = parse_anki_file(anki_path)

        bbdc_dir = os.path.dirname(os.path.abspath(bbdc_path))
        output_path = os.path.join(bbdc_dir, "BBDC_updated.txt")

        update_bbdc_file(bbdc_path, anki_dict, output_path, sb_do_replace, sth_do_replace)

        print(f"\n✅ 处理完成！结果已保存到：{output_path}")
        input("输入回车结束程序")
    except FileNotFoundError as e:
        print(f"\n❌ 错误：{e}")
    except Exception as e:
        print(f"\n💥 未知错误：{e}")

if __name__ == '__main__':
    main()