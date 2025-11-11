import os
import json
import sys
# 配置文件路径 (放在脚本同目录)
# CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), './config/defaultConfig.json')

# config keys
config_keys = ['bbdc_path', 'anki_path', 'output_path',
            'sb_do_replace', 'sth_do_replace', 'use_default']
default_config = {
    "use_default": False,
    "bbdc_path": "BBDC.txt",
    "anki_path": "Anki.txt",
    "output_path": "BBDC_updated.txt",
    "sb_do_replace": False,
    "sth_do_replace": False,
}

def get_base_path():
    """获取应用程序的正确基础路径（适用于打包和非打包环境）"""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # 打包后的可执行文件路径
        return os.path.dirname(sys.executable)
    else:
        # 源代码运行路径
        return os.path.dirname(os.path.abspath(__file__))

# 获取正确路径
base_path = get_base_path()
CONFIG_FILE = os.path.join(base_path, 'config', 'defaultConfig.json')

# 加载文件配置
def load_config():
    """加载配置文件，如果不存在则创建默认配置"""
    if not os.path.exists(CONFIG_FILE):
        # 首次运行，创建默认配置
        save_config(default_config)
        print(f"✅ 首次运行，已创建默认配置文件: {CONFIG_FILE}")
        return default_config

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        # 确保配置包含所有必要字段
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
        return config
    except Exception as e:
        print(f"⚠️ 配置文件损坏，使用默认配置: {e}")
        return default_config

# 保存配置文件
def save_config(config):
    """保存配置到文件"""
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ 无法保存配置: {e}")
        return False

def get_user_input(default_config):
    # 如果使用默认配置
    if default_config['use_default']:
        print(f"✅ 使用默认配置 默认配置路径：{os.path.abspath(CONFIG_FILE)}, "
              f"\n如果需要关闭自动使用默认配置，那么将 'use_default' 改为 false 即可"
              f"\ndefaultConfig 的值：")
        for key in config_keys:
            print(f'{key}: {default_config[key]}')
        return default_config

    """获取用户输入的文件路径，并询问是否替换 sth/sb"""
    print("请输入文件路径（直接回车使用默认文件名）：")
    bbdc_path = input(f"BBDC 文件路径 [默认: {default_config['bbdc_path']}]: ").strip().strip('"')
    anki_path = input(f"Anki 文件路径 [默认: {default_config['anki_path']}]: ").strip().strip('"')
    output_path = input(f"最终结果的文件路径 [默认: {default_config['output_path']}]: ").strip().strip('"')

    if not bbdc_path:
        bbdc_path = default_config['bbdc_path']
    if not anki_path:
        anki_path = default_config['anki_path']
    if not output_path:
        output_path = default_config['output_path']

    # 询问是否替换 sth / sb
    sb_replace_choice = input("是否将 'sb' 替换为 'somebody'？(Y/n)"
                              f" [默认: {getYesOrNo(default_config['sb_do_replace'])}"
                              "]: ")
    sth_replace_choice = input("是否将 'sth' 替换为 'something' ？(Y/n)"
                               f" [默认: {getYesOrNo(default_config['sth_do_replace'])}"
                               "]: ")

    sb_do_replace = isMatch(sb_replace_choice, default_config['sb_do_replace'])
    sth_do_replace = isMatch(sth_replace_choice, default_config['sth_do_replace'])
    # 是否开启默认配置
    use_default_choice = input("下一次是否默认使用该配置？(Y/n) [默认: n]: ").strip().lower()
    use_default = isMatch(use_default_choice, default_config['use_default'])

    # 更新 default_config
    default_config.update({k: locals()[k] for k in config_keys})
    return default_config

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

def update_bbdc_file(config, anki_dict):
    bbdc_path = config['bbdc_path']
    output_path = config['output_path']
    sb_do_replace = config['sb_do_replace']
    sth_do_replace = config['sth_do_replace']

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

def getYesOrNo(flag):
    return "Y" if flag else "n"

# 是否与原来的匹配
def isMatch(input_str, default_value):
    str = input_str.strip().lower()
    if str == '':
        return default_value
    if str in ('y', 'yes'): return True
    if str in ('n', 'no'): return False
    raise Exception(f"输入异常 期望输入 'y','yes','n','no'(大小写不区分) 实际输入{input_str}")

def main():
    try:
        # 获取默认配置
        default_config = load_config()
        # 获取用户输入配置
        config = get_user_input(default_config)
        # 保存配置
        save_config(config)
        anki_dict = parse_anki_file(config['anki_path'])

        update_bbdc_file(config, anki_dict)
        print(f"\n✅ 处理完成！结果已保存到：{config['output_path']}")
    except FileNotFoundError as e:
        print(f"\n❌ 错误：{e}")
    except Exception as e:
        print(f"\n💥 未知错误：{e}")

if __name__ == '__main__':
    main()
    input("输入回车结束程序")