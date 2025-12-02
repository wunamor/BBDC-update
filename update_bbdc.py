import os
import json
import sys
import re
from pathlib import Path

# ================= 配置部分 (模块化结构) =================

DEFAULT_CONFIG = {
    # 1. 系统/元数据配置
    "system": {
        "auto_run": False  # 是否跳过询问直接运行
    },

    # 2. 文件路径配置
    "files": {
        "bbdc_path": "BBDC.txt",
        "anki_path": "Anki.txt",
        "output_path": "BBDC_updated.txt"
    },

    # 3. Anki 文件解析模板
    "anki_template": {
        "delimiter": "\t",  # 分隔符
        "word_index": 0,  # 单词列索引 (0-based)
        "meaning_index": 1  # 意思列索引 (0-based)
    },

    # 4. BBDC 文件解析模板
    "bbdc_template": {
        "delimiter": ",",
        "word_index": 1,
        "meaning_index": 2
    },

    # 5. 替换规则开关
    "switches": {
        "replace_sb": False,  # sb -> somebody
        "replace_sth": False  # sth -> something
    }
}


def get_app_path():
    """获取应用程序基础路径"""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent.absolute()


BASE_PATH = get_app_path()
CONFIG_FILE = BASE_PATH / 'config' / 'defaultConfig.json'


# ================= 辅助函数 =================

def unescape_string(s):
    if s == r'\t': return '\t'
    if s == r'\n': return '\n'
    return s


def escape_string_for_display(s):
    if s == '\t': return r'\t'
    if s == '\n': return r'\n'
    return s


def load_config():
    """加载配置，支持结构检查"""
    if not CONFIG_FILE.parent.exists():
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        print(f"✅ 首次运行，已创建默认配置文件: {CONFIG_FILE}")
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 简单检查配置结构是否是旧版本 (旧版本没有 'files' 这个key)
        if 'files' not in config:
            print("⚠️ 检测到旧版配置文件，已重置为新版模块化结构。")
            input("请先保存好原先配置，按下回车后将会覆盖原先旧的配置")
            # 可以在这里做迁移逻辑，但为了简化直接重置

            save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()

        return config
    except Exception as e:
        print(f"⚠️ 配置文件读取出错，使用默认配置: {e}")
        return DEFAULT_CONFIG.copy()


def save_config(config):
    """保存配置"""
    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ 无法保存配置: {e}")
        return False


def ask_bool(prompt, default_val):
    default_str = "Y" if default_val else "n"
    while True:
        choice = input(f"{prompt} [默认: {default_str}]: ").strip().lower()
        if choice == '': return default_val
        if choice in ('y', 'yes'): return True
        if choice in ('n', 'no'): return False
        print("❌ 输入错误，请输入 y 或 n")


def ask_val(desc, current_val, is_index=False):
    display_val = current_val
    if is_index:
        display_val = current_val + 1
    else:
        display_val = escape_string_for_display(current_val)

    val = input(f"{desc} [默认: {display_val}]: ").strip().strip('"')

    if val == '':
        return current_val

    if is_index:
        try:
            return int(val) - 1
        except ValueError:
            print(f"⚠️ 输入无效，使用默认值")
            return current_val
    else:
        return unescape_string(val)


def get_user_input(config):
    """获取用户配置，适配嵌套结构"""
    # 检查是否自动运行
    if config['system'].get('auto_run', False):
        print(f"✅ 使用保存的默认配置")
        return config

    # 深拷贝以防止修改原对象（虽然这里不是必须，但好习惯）
    import copy
    new_config = copy.deepcopy(config)

    print("\n=== 1. 文件路径设置 ===")
    files = new_config['files']
    files['bbdc_path'] = ask_val('BBDC 文件路径', files['bbdc_path'])
    files['anki_path'] = ask_val('Anki 文件路径', files['anki_path'])
    files['output_path'] = ask_val('最终结果路径', files['output_path'])

    print("\n=== 2. Anki 模板设置 (直接回车使用默认) ===")
    anki_tpl = new_config['anki_template']
    print(f"当前 Anki 格式: 分隔符='{escape_string_for_display(anki_tpl['delimiter'])}'")

    if ask_bool("是否修改 Anki 文件解析模板？(y/N)", False):
        anki_tpl['delimiter'] = ask_val("Anki 列分隔符 (支持 \\t, , 等)", anki_tpl['delimiter'])
        anki_tpl['word_index'] = ask_val("英文单词在第几列", anki_tpl['word_index'], is_index=True)
        anki_tpl['meaning_index'] = ask_val("中文释义在第几列", anki_tpl['meaning_index'], is_index=True)

    print("\n=== 3. 功能开关 ===")
    switches = new_config['switches']
    switches['replace_sb'] = ask_bool("将 'sb' 替换为 'somebody'？", switches['replace_sb'])
    switches['replace_sth'] = ask_bool("将 'sth' 替换为 'something'？", switches['replace_sth'])

    # 更新系统设置
    new_config['system']['auto_run'] = ask_bool("以后默认使用此配置不再询问？", False)

    return new_config


def replace_sth_sb(text, do_sb, do_sth):
    if not text: return text
    if do_sb:
        text = re.sub(r'\bsb\b', 'somebody', text, flags=re.IGNORECASE)
    if do_sth:
        text = re.sub(r'\bsth\b', 'something', text, flags=re.IGNORECASE)
    return text


def parse_file_flexible(filepath, template):
    """
    智能解析函数 (适配传入 template 字典)
    """
    delimiter = template['delimiter']
    word_idx = template['word_index']
    meaning_idx = template['meaning_index']

    data_dict = {}
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"文件未找到: {filepath}")

    print(
        f"正在读取 {path.name} (分隔符: '{escape_string_for_display(delimiter)}', 单词列: {word_idx + 1}, 意思列: {meaning_idx + 1})")

    skipped = 0
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue

            parts = line.split(delimiter)

            max_idx = max(word_idx, meaning_idx)
            if len(parts) <= max_idx:
                skipped += 1
                continue

            english = parts[word_idx].strip()

            # --- 智能拼接逻辑 (多余列拼接到意思后) ---
            meaning_parts = []
            meaning_parts.append(parts[meaning_idx].strip())  # 先加主意思

            for i, part in enumerate(parts):
                if i == word_idx or i == meaning_idx:
                    continue
                meaning_parts.append(part.strip())

            final_chinese = delimiter.join(meaning_parts)
            # --------------------------------------

            data_dict[english] = final_chinese

    if skipped > 0:
        print(f"⚠️ 注意：有 {skipped} 行因列数不足被跳过。")
    return data_dict


def update_bbdc_file(config, anki_dict):
    # 从嵌套配置中解构变量
    files = config['files']
    bbdc_tpl = config['bbdc_template']
    switches = config['switches']

    bbdc_path = Path(files['bbdc_path'])
    output_path = Path(files['output_path'])

    delimiter = bbdc_tpl['delimiter']
    word_idx = bbdc_tpl['word_index']
    meaning_idx = bbdc_tpl['meaning_index']

    if not bbdc_path.exists():
        raise FileNotFoundError(f"BBDC 文件未找到: {bbdc_path}")

    print("正在合并处理...")

    with open(bbdc_path, 'r', encoding='utf-8') as f_in, \
            open(output_path, 'w', encoding='utf-8') as f_out:

        count = 0
        replaced_count = 0

        for line in f_in:
            original_line = line.strip()
            if not original_line:
                f_out.write('\n')
                continue

            parts = original_line.split(delimiter)

            max_idx = max(word_idx, meaning_idx)
            if len(parts) <= max_idx:
                f_out.write(original_line + '\n')
                continue

            english = parts[word_idx].strip()
            chinese = parts[meaning_idx].strip()

            # 1. 处理 sth/sb
            english_processed = replace_sth_sb(english, switches['replace_sb'], switches['replace_sth'])

            # 2. 匹配 Anki
            final_chinese = chinese
            if english_processed in anki_dict:
                final_chinese = anki_dict[english_processed]
                replaced_count += 1
            elif english in anki_dict:
                final_chinese = anki_dict[english]
                replaced_count += 1

            # 3. 写入 (保留原行其他信息)
            parts[word_idx] = english_processed
            parts[meaning_idx] = final_chinese

            new_line = delimiter.join(parts)
            f_out.write(new_line + '\n')
            count += 1

    print(f"处理完毕。共处理 {count} 行，更新了 {replaced_count} 个释义。")


def main():
    """主逻辑函数"""
    try:
        config = load_config()
        config = get_user_input(config)
        save_config(config)

        # 传入 Anki 模板部分
        anki_dict = parse_file_flexible(
            config['files']['anki_path'],
            config['anki_template']
        )

        update_bbdc_file(config, anki_dict)

        print(f"\n✅ 成功！结果已保存到：{os.path.abspath(config['files']['output_path'])}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n💥 错误：{e}")


if __name__ == '__main__':
    print("=" * 15 + " 开始执行 " + "=" * 15)

    # 1. 运行主程序
    main()

    # 2. 【修改点】无论成功还是失败，最后都会停在这里等待用户回车
    print("\n" + "=" * 15 + " 执行结束 " + "=" * 15)
    input("按回车键退出程序...")