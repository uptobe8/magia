import os
import argparse
import subprocess
import datetime
import cv2
import json
import sys

# Rutas base
ROOT_DIR = os.path.abspath(os.path.dirname(__file__) + "/..")
POSES_DIR = os.path.join(ROOT_DIR, "poses")
MANOS_DIR = os.path.join(ROOT_DIR, "manos")
OUTPUT_DIR = os.path.join(ROOT_DIR, "outputs")
SCRIPT_INFER = os.path.join(ROOT_DIR, "scripts", "infer_with_pose.py")

# Archivos
VIDEO_BASE = os.path.join(MANOS_DIR, "video_base.mp4")
REF_IMAGE = os.path.join(MANOS_DIR, "mano_ref.png")

def extraer_imagen_si_falta():
    if os.path.exists(REF_IMAGE):
        return
    if not os.path.exists(VIDEO_BASE):
        print("❌ No se encontró el vídeo base:", VIDEO_BASE)
        sys.exit(1)
    cap = cv2.VideoCapture(VIDEO_BASE)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 2)
    ret, frame = cap.read()
    if not ret:
        print("❌ No se pudo extraer el frame.")
        sys.exit(1)
    cv2.imwrite(REF_IMAGE, frame)
    cap.release()

def validar_entradas(tecnica, pose_path):
    errores = []
    if not os.path.isfile(pose_path):
        errores.append(f"❌ Falta: {pose_path}")
    if not os.path.isfile(SCRIPT_INFER):
        errores.append(f"❌ Falta: {SCRIPT_INFER}")
    if errores:
        for e in errores:
            print(e)
        sys.exit(1)

# Argumentos
parser = argparse.ArgumentParser()
parser.add_argument("--tecnica", required=True)
parser.add_argument("--prompt", required=True)
parser.add_argument("--duracion", type=int, required=True)
parser.add_argument("--fps", type=int, required=True)
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--resolucion", default="512x512")
args = parser.parse_args()

# Rutas dinámicas
pose_file = os.path.join(POSES_DIR, f"{args.tecnica}.json")
output_file = os.path.join(OUTPUT_DIR, f"{args.tecnica}.mp4")
meta_file = os.path.join(OUTPUT_DIR, f"{args.tecnica}.json")

# Crear carpetas
os.makedirs(POSES_DIR, exist_ok=True)
os.makedirs(MANOS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Preparación
extraer_imagen_si_falta()
validar_entradas(args.tecnica, pose_file)

# Ejecutar modelo
cmd = [
    "python", SCRIPT_INFER,
    "--prompt", args.prompt,
    "--pose_json", pose_file,
    "--ref_image", REF_IMAGE,
    "--out", output_file,
    "--duration", str(args.duracion),
    "--fps", str(args.fps),
    "--resolution", args.resolucion,
    "--seed", str(args.seed)
]
subprocess.run(cmd, check=True)

# Guardar metadata
metadata = {
    "tecnica": args.tecnica,
    "prompt": args.prompt,
    "seed": args.seed,
    "duracion": args.duracion,
    "fps": args.fps,
    "resolucion": args.resolucion,
    "modelo": "AnimateDiff + Multi-ControlNet + IP-Adapter",
    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    "commit_hash": "032fc0801140",
    "video_url": f"https://tu-servidor.com/magia/outputs/{args.tecnica}.mp4"
}
with open(meta_file, "w") as f:
    json.dump(metadata, f, indent=2)
