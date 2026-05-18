#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import random
import argparse
import importlib
from multiprocessing import Pool, cpu_count

# ====== 复用 executor ======
import batch_process_comb_m as execu

# ==============================
# 配置映射表
# ==============================
MODULE_CONFIG_MAP = {
    "scene_s": "configs", 
    "scene_dt": "configs_comb",
    "scene_qp": "configs_comb_q"
}

SINGLE_SELECTED = {
    "barrier",
    "crosstalk",
    "distortion",
    "far_field",
    "noise",
    "strong_echo",
    "stutter",
}

IMPORTANT_DOUBLE_SELECTED = {
    "far_field_crosstalk",
    "far_field_noise",
    "far_field_stutter",
    "noise_stutter"  
    
}

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", required=True, help="输入原始 meta jsonl")
    ap.add_argument("--single-ratio", type=float, default=0.6)
    ap.add_argument("--important-ratio", type=float, default=0.24)
    ap.add_argument("--sampling-times", type=int, default=1)
    ap.add_argument("--num-variants", type=int, default=1)
    ap.add_argument("--mapper", default="linear")
    ap.add_argument("--speed-augment", action="store_true")
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--output-jsonl", default="extended_metadata.jsonl")
    
    # ======= 新增 DEBUG 参数 =======
    ap.add_argument("--debug", action="store_true", help="开启调试模式，打印详细映射关系")
    ap.add_argument("--debug-limit", type=int, default=5, help="debug 模式下每个组合打印多少条详细任务信息")
    
    return ap.parse_args()

def load_combination_modules(debug=False):
    all_combs = {}
    enabled_total = set()

    if debug: print("\n🔍 [DEBUG] 开始扫描组合定义模块...")

    for mod_name, config_dir in MODULE_CONFIG_MAP.items():
        try:
            mod = importlib.import_module(mod_name)
        except ImportError:
            print(f"⚠ 警告: 无法加载模块 {mod_name}，将跳过。")
            continue

        combs_in_mod = getattr(mod, "SCENE_COMBINATIONS", [])
        for c in combs_in_mod:
            name = c["name"]
            if name in all_combs:
                raise RuntimeError(f"❌ 重复组合名: {name}")
            
            # 标记溯源信息
            c["config_source"] = config_dir
            c["defined_in_module"] = mod_name
            all_combs[name] = c
            
            if debug:
                print(f"  [Found] 组合 '{name}' -> 定义于: {mod_name}.py -> 匹配路径: {config_dir}/{name}.json (或其子场景)")

        enabled = getattr(mod, "ENABLED_COMBINATIONS", [])
        enabled_total |= set(enabled)

    return all_combs, enabled_total

import ast  # 使用抽象语法树安全地解析字符串为字典

def safe_load_configs_from_path(dir_path):
    configs = {}
    abs_dir = os.path.abspath(dir_path)
    
    if not os.path.exists(abs_dir):
        return configs
    
    for filename in os.listdir(abs_dir):
        # 修改点：现在查找 .py 文件
        if filename.endswith(".py") and not filename.startswith("__"):
            scene_name = filename[:-3]  # 去掉 .py
            file_path = os.path.join(abs_dir, filename)
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # 技巧：从 .py 文件中提取配置内容
                    # 假设你的 .py 结尾是 CONFIG = {...} 这种格式，或者直接就是字典
                    # 如果你的 .py 文件里只有一行字典，用 ast.literal_eval 最安全
                    # 如果复杂，我们寻找字典特征
                    if "=" in content:
                        # 提取等号后面的部分
                        dict_str = content.split("=", 1)[1].strip()
                    else:
                        dict_str = content.strip()
                    
                    configs[scene_name] = ast.literal_eval(dict_str)
            except Exception as e:
                # 如果 ast 解析失败，尝试最暴力但有效的方法：直接执行（注意安全）
                try:
                    local_vars = {}
                    exec(content, {}, local_vars)
                    # 假设定义的变量名与文件名相关，或者直接取 local_vars 里唯一的字典
                    for v in local_vars.values():
                        if isinstance(v, dict):
                            configs[scene_name] = v
                            break
                except:
                    print(f"❌ 无法解析配置文件: {file_path}")
    return configs

    
def main():
    args = parse_args()
    random.seed(42)

    # ---------- 加载 meta ----------
    meta_dict = {}
    input_files = []
    with open(args.meta, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            obj = json.loads(line)
            meta_dict[obj["index"]] = obj
            audio_path = obj.get("audio_path")
            if audio_path and os.path.isfile(audio_path):
                input_files.append(audio_path)

    input_files = sorted(set(input_files))
    print(f"📥 载入音频数: {len(input_files)}")

    # ---------- 加载组合 ----------
    all_combs, enabled_total = load_combination_modules(debug=args.debug)

    # ---------- 安全过滤 ----------
    single_selected = SINGLE_SELECTED & enabled_total
    important_selected = IMPORTANT_DOUBLE_SELECTED & enabled_total
    other_selected = enabled_total - single_selected - important_selected

    single_combs = [all_combs[n] for n in sorted(single_selected)]
    important_combs = [all_combs[n] for n in sorted(important_selected)]
    other_combs = [all_combs[n] for n in sorted(other_selected)]

    # ---------- 分配逻辑 (省略部分重复逻辑以节省篇幅) ----------
    expanded_inputs = []
    for p in input_files:
        for _ in range(args.sampling_times): expanded_inputs.append(p)
    random.shuffle(expanded_inputs)

    total = len(expanded_inputs)
    n_single = int(total * args.single_ratio)
    n_important = int(total * args.important_ratio)
    single_slots = expanded_inputs[:n_single]
    important_slots = expanded_inputs[n_single:n_single + n_important]
    other_slots = expanded_inputs[n_single + n_important:]

    assignments = []
    def assign(slots, pool):
        for p in slots: yield p, random.choice(pool)
    if single_combs: assignments += list(assign(single_slots, single_combs))
    if important_combs: assignments += list(assign(important_slots, important_combs))
    if other_combs: assignments += list(assign(other_slots, other_combs))
    random.shuffle(assignments)

    # ---------- 加载多源场景配置 (硬隔离版) ----------
    full_scene_configs_map = {}
    
    needed_dirs = set(MODULE_CONFIG_MAP.values())
    print("\n📂 正在执行物理隔离加载...")
    for d in sorted(list(needed_dirs)): # 排序确保逻辑一致性
        # 这里弃用 execu.load_all_scene_configs，改用我们自己的 safe 函数
        full_scene_configs_map[d] = safe_load_configs_from_path(d)
        print(f"  - 目录 '{d}': 成功从磁盘直接读取了 {len(full_scene_configs_map[d])} 个场景文件")

    # 打印一个校验，看 distortion 在不同目录下的参数是否真的不同
    if "configs_comb" in full_scene_configs_map and "configs_comb_q" in full_scene_configs_map:
        val1 = full_scene_configs_map["configs_comb"].get("distortion", {}).get("params", {}).get("target_lufs")
        val2 = full_scene_configs_map["configs_comb_q"].get("distortion", {}).get("params", {}).get("target_lufs")
        print(f"\n🧪 参数隔离校验:")
        print(f"  - configs_comb   中的 distortion target_lufs: {val1}")
        print(f"  - configs_comb_q 中的 distortion target_lufs: {val2}")
        if val1 == val2:
            print("  ⚠️ 警告: 两个目录下的参数依然相同，请检查原始磁盘文件内容是否真的不一致！")
        else:
            print("  ✅ 隔离成功：不同目录下的同名场景已加载不同参数。")
    print("")
    # ---------- 构造任务 & 溯源打印 (优化版) ----------
    all_tasks = []
    printed_combs = set()  # 用于记录哪些组合已经打印过 Debug 信息

    print("\n🚧 构造任务中...")
    for input_path, comb in assignments:
        base = os.path.splitext(os.path.basename(input_path))[0]
        meta = meta_dict.get(base)
        
        c_name = comb["name"]
        config_source = comb["config_source"]
        current_scene_configs = full_scene_configs_map.get(config_source, {})

        # 改良后的 DEBUG 追踪：每个组合仅打印一次完整信息
        if args.debug and c_name not in printed_combs:
            print(f"\n{'='*30}")
            print(f"🔍 [DEBUG SOURCE] 组合名: {c_name}")
            print(f"  - 来源模块: {comb['defined_in_module']}.py")
            print(f"  - 配置目录: {config_source}/")
            print(f"  - 包含场景: {comb['scenes']}")
            
            for sn in comb['scenes']:
                content = current_scene_configs.get(sn, "❌ 未找到配置!")
                # 使用 json.dumps 打印完整且美观的 JSON 内容
                detail = json.dumps(content, indent=4, ensure_ascii=False)
                print(f"    --- 场景 '{sn}' 的完整配置内容 ---")
                print(detail)
            print(f"\n{'='*30}\n")
            printed_combs.add(c_name)

        # 合并效果链逻辑保持不变
        merged_chain = execu.merge_effect_chains(current_scene_configs, comb["scenes"], verbose=False)
        if not merged_chain: continue
        for v in range(args.num_variants):
            out_dir = os.path.join(execu.OUTPUT_DIR, c_name, base)
            fname = f"{base}_{c_name}_{args.mapper}_{v+1}.wav"
            all_tasks.append({
                "input_path": input_path,
                "output_path": os.path.join(out_dir, fname),
                "effect_chain": merged_chain,
                "mapper_name": args.mapper,
                "meta_info": meta,
                "comb_name": c_name,
                "scene_names": comb["scenes"],
                "variant_id": v + 1,
                "base_name": base,
                "speed_augment": args.speed_augment,
            })

    print(f"\n✅ 任务构造完成，总计: {len(all_tasks)}")
    if args.debug: print("💡 [Tips] 请检查上方打印的配置片段，确认其 'params' 里的数值是否为您修改后的值。")

    # ---------- 执行部分 (保持原样) ----------
    jsonl_entries = []
    with Pool(processes=min(args.workers, cpu_count()), initializer=execu.init_worker) as pool:
        for result in pool.imap_unordered(execu.process_single_task, all_tasks):
            if result.get("success") and result.get("jsonl_entry"):
                jsonl_entries.append(result["jsonl_entry"])

    if jsonl_entries:
        jsonl_entries.sort(key=lambda x: x["index"])
        with open(args.output_jsonl, "w", encoding="utf-8") as f:
            for entry in jsonl_entries: f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"✅ 写入增强 jsonl: {args.output_jsonl}")

if __name__ == "__main__":
    main()