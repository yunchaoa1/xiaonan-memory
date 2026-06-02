#!/usr/bin/env python3
"""陈烬生 LoRA 测试 — 2500步 vs 3000步 vs 无LoRA (UNETLoader版)"""
import json, time, requests, os, hashlib

COMFY = "http://172.26.112.1:18188"
OUTPUT_DIR = "/mnt/d/SDkecheng/output"

LORAS = [
    ("2500步", "陈烬生_lora_000002500.safetensors"),
    ("3000步", "陈烬生_lora_000003000.safetensors"),
    ("无LoRA", None),
]

PROMPTS = [
    ("正面站立", "天南陈烬生，正面站立全身照，双手自然垂放身侧，沉稳表情看向镜头，纯白背景，柔和光效"),
    ("侧身回眸", "天南陈烬生，侧身站立回眸看向镜头，一只手整理袖口，冷静威严神情"),
    ("坐姿沉思", "天南陈烬生，坐在办公椅上，单手放在桌面，若有所思的深沉表情，暖色调灯光，办公室背景"),
]

STEPS = 25
CFG = 4.5

def get_seed(lora_label, prompt_label):
    key = f"cjs_{lora_label}_{prompt_label}"
    return int(hashlib.md5(key.encode()).hexdigest()[:8], 16)

def build_prompt(lora_name, prompt_text, seed):
    p = {}
    # UNETLoader 加载 Z-Image Turbo (diffusion_models目录)
    p["1"] = {"class_type": "UNETLoader",
              "inputs": {"unet_name": "z-image-turbo-fp8-e4m3fn.safetensors", "weight_dtype": "default"}}
    p["2"] = {"class_type": "CLIPLoader",
              "inputs": {"clip_name": "z_image_qwen3_4b.safetensors", "type": "qwen_image"}}
    p["3"] = {"class_type": "VAELoader",
              "inputs": {"vae_name": "z_image_vae.safetensors"}}
    
    if lora_name is not None:
        p["4"] = {"class_type": "LoraLoader",
                  "inputs": {"model": ["1", 0], "clip": ["2", 0],
                              "lora_name": lora_name, "strength_model": 1.0, "strength_clip": 1.0}}
        model_src = ["4", 0]
        clip_src = ["4", 1]
    else:
        model_src = ["1", 0]
        clip_src = ["2", 0]
    
    p["5"] = {"class_type": "TextEncodeZImageOmni",
              "inputs": {"clip": clip_src, "prompt": prompt_text, "auto_resize_images": True}}
    p["6"] = {"class_type": "CLIPTextEncode",
              "inputs": {"clip": clip_src, "text": ""}}
    p["7"] = {"class_type": "EmptySD3LatentImage",
              "inputs": {"width": 1024, "height": 1024, "batch_size": 1}}
    p["8"] = {"class_type": "KSampler",
              "inputs": {"model": model_src, "positive": ["5", 0], "negative": ["6", 0],
                          "latent_image": ["7", 0], "seed": seed, "steps": STEPS, "cfg": CFG,
                          "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}}
    p["9"] = {"class_type": "VAEDecode",
              "inputs": {"samples": ["8", 0], "vae": ["3", 0]}}
    
    label = lora_name.replace(" ","_") if lora_name else "no_lora"
    p["10"] = {"class_type": "SaveImage",
               "inputs": {"images": ["9", 0], "filename_prefix": f"cjs_test_{label}"}}
    return p

def submit_and_wait(prompt, label, timeout=600):
    payload = {"prompt": prompt}
    try:
        r = requests.post(f"{COMFY}/prompt", json=payload, timeout=30)
    except Exception as e:
        print(f"  ❌ {label}: {e}")
        return None
    if r.status_code != 200:
        try:
            err = r.json()
            print(f"  ❌ {label}: {r.status_code} - {json.dumps(err.get('error',{}),ensure_ascii=False)[:200]}")
        except:
            print(f"  ❌ {label}: {r.status_code}")
        return None
    pid = r.json()["prompt_id"]
    print(f"  📤 {label} → pid={pid}")
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{COMFY}/history/{pid}", timeout=10)
        except:
            time.sleep(3)
            continue
        if r.status_code == 200 and pid in r.json():
            h = r.json()[pid]
            s = h.get("status", {})
            if s.get("completed"):
                for nid, out in h.get("outputs", {}).items():
                    if "images" in out and out["images"]:
                        img = out["images"][0]
                        fn = img["filename"]
                        sf = img.get("subfolder", "")
                        fp = os.path.join(OUTPUT_DIR, sf, fn) if sf else os.path.join(OUTPUT_DIR, fn)
                        print(f"  ✅ {label} → {fn}")
                        return fp
            elif s.get("status_str") == "error":
                print(f"  ❌ {label} 执行错误")
                return None
        time.sleep(2)
    print(f"  ⏰ {label} 超时")
    return None

# Main
print("=" * 60)
print("天南陈烬生 LoRA 测试 (UNETLoader)")
print(f"{STEPS}步 | CFG {CFG} | 1024×1024 | 2500→3000→无LoRA")
print("=" * 60)

results = {}
total = len(LORAS) * len(PROMPTS)
done = 0

for lora_label, lora_file in LORAS:
    print(f"\n--- {lora_label} ---")
    for ps_label, prompt_text in PROMPTS:
        seed = get_seed(lora_label, ps_label)
        api_prompt = build_prompt(lora_file, prompt_text, seed)
        fp = submit_and_wait(api_prompt, f"{lora_label}/{ps_label} (seed={seed})")
        done += 1
        results[f"{lora_label}|{ps_label}"] = fp
        print(f"  进度: {done}/{total}")

print("\n" + "=" * 60)
missing = [k for k,v in results.items() if v is None]
if missing:
    print(f"⚠️  失败: {len(missing)}")
    for m in missing:
        print(f"  {m}")
else:
    print(f"✅ 全部成功 ({total}/{total})")

with open("/home/adminneit/.openclaw/workspace/cjs_test_results.json", "w") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
