import os
import argparse
import subprocess
import datetime
import cv2
import json
import sys

# ✅ Rutas base
ROOT_DIR = os.path.abspath(os.path.dirname(__file__) + "/..")
POSES_DIR = os.path.join(ROOT_DIR, "poses")
MANOS_DIR = os.path.join(ROOT_DIR, "manos")
OUTPUT_DIR = os.path.join(ROOT_DIR, "outputs")
SCRIPT_INFER = os.path.join(ROOT_DIR, "scripts", "infer_with_pose.py")

# ✅ Nombres de archivo
VIDEO_BASE = os.path.join(MANOS_DIR, "video_base.mp4")
REF_IMAGE = os.path.join(MANOS_DIR, "mano_ref.png")

# ✅ Función: extraer imagen si no existe
def extraer_imagen_si_falta():
    if os.path.exists(REF_IMAGE):
        print("✅ Imagen de referencia ya existe.")
        return
    if not os.path.exists(VIDEO_BASE):
        print("❌ No se encontró el vídeo base:", VIDEO_BASE)
        sys.exit(1)

    print("🖼️ Extrayendo imagen del vídeo base...")

    cap = cv2.VideoCapture(VIDEO_BASE)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_index = total_frames // 2
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ret, frame = cap.read()
    if not ret:
        print("❌ No se pudo leer un frame válido.")
        sys.exit(1)
    cv2.imwrite(REF_IMAGE, frame)
    cap.release()
    print("✅ Imagen guardada como:", REF_IMAGE)

# ✅ Validar entradas necesarias
def generar_pose_vacia_si_falta(pose_path):
    if not os.path.isfile(pose_path):
        print(f"⚠️ Pose no encontrada: {pose_path}")
        print("🛠️ Generando archivo de pose vacío por defecto...")
        pose_vacia = [
            {
                "keypoints": [],
                "frame": 0
            }
        ]
        with open(pose_path, "w") as f:
            json.dump(pose_vacia, f)
        print(f"✅ Pose vacía generada: {pose_path}")

def validar_entradas(tecnica, pose_path):
    errores = []

    generar_pose_vacia_si_falta(pose_path)
    if not os.path.isfile(SCRIPT_INFER):
        errores.append(f"❌ Script de inferencia no existe: {SCRIPT_INFER}")

    if errores:
        for e in errores:
            print(e)
        sys.exit(1)

# ✅ Leer argumentos desde Action
parser = argparse.ArgumentParser(description="Generar video de técnica de cartomagia")
parser.add_argument("--tecnica", type=str, required=True)
parser.add_argument("--prompt", type=str, required=True)
parser.add_argument("--duracion", type=int, required=True)
parser.add_argument("--fps", type=int, required=True)
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--resolucion", type=str, default="512x512")
args = parser.parse_args()

# ✅ Rutas de entrada/salida
pose_file = os.path.join(POSES_DIR, f"{args.tecnica}.json")
output_file = os.path.join(OUTPUT_DIR, f"{args.tecnica}.mp4")
meta_file = os.path.join(OUTPUT_DIR, f"{args.tecnica}.json")

# ✅ Crear carpetas si no existen
os.makedirs(POSES_DIR, exist_ok=True)
os.makedirs(MANOS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ✅ Ejecutar chequeos
extraer_imagen_si_falta()
validar_entradas(args.tecnica, pose_file)

# ✅ Ejecutar el modelo
print(f"🚀 Generando vídeo para técnica: {args.tecnica}")
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

print("🔧 Ejecutando comando:", " ".join(cmd))
result = subprocess.run(cmd, check=True)

# ✅ Guardar metadatos
metadata = {
    "tecnica": args.tecnica,
    "prompt": args.prompt,
    "seed": args.seed,
    "duracion": args.duracion,
    "fps": args.fps,
    "resolucion": args.resolucion,
    "modelo": "AnimateDiff + Multi-ControlNet + IP-Adapter",
    "timestamp": datetime.datetime.now().isoformat()
    # ⛔️ NO incluir "video_url" aquí
}

with open(meta_file, "w") as f:
    json.dump(metadata, f, indent=4)

print("✅ Video generado en:", output_file)
print("📝 Metadatos guardados en:", meta_file)
