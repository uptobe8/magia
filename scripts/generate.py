import os
import argparse
import subprocess
import datetime

# ✅ Configuración base del entorno
ROOT_DIR = os.path.abspath(os.path.dirname(__file__) + "/..")
POSES_DIR = os.path.join(ROOT_DIR, "poses")
MANO_REF = os.path.join(ROOT_DIR, "manos", "mano_ref.png")
OUTPUT_DIR = os.path.join(ROOT_DIR, "outputs")
SCRIPT_INFER = os.path.join(ROOT_DIR, "scripts", "infer_with_pose.py")

# ✅ Función para asegurarse de que todo existe
def validar_entradas(tecnica, pose_path, ref_image):
    errores = []

    if not os.path.isfile(pose_path):
        errores.append(f"❌ Pose no encontrada: {pose_path}")
    if not os.path.isfile(ref_image):
        errores.append(f"❌ Imagen de referencia no encontrada: {ref_image}")
    if not os.path.isfile(SCRIPT_INFER):
        errores.append(f"❌ Script de inferencia no existe: {SCRIPT_INFER}")

    if errores:
        for e in errores:
            print(e)
        exit(1)

# ✅ Parsear argumentos desde la acción
parser = argparse.ArgumentParser(description="Generar video de técnica de cartomagia")

parser.add_argument("--tecnica", type=str, required=True, help="Nombre de la técnica (ej. doble_volteo)")
parser.add_argument("--duracion", type=int, required=True, help="Duración del video en segundos")
parser.add_argument("--fps", type=int, required=True, help="FPS del video")
parser.add_argument("--seed", type=int, default=42, help="Semilla para reproducibilidad")
parser.add_argument("--resolucion", type=str, default="512x512", help="Resolución del video")

args = parser.parse_args()

# ✅ Construir rutas
pose_file = os.path.join(POSES_DIR, f"{args.tecnica}.json")
output_file = os.path.join(OUTPUT_DIR, f"{args.tecnica}.mp4")

# ✅ Validar entradas
validar_entradas(args.tecnica, pose_file, MANO_REF)

# ✅ Ejecutar el modelo con infer_with_pose.py
print(f"🚀 Generando vídeo para técnica: {args.tecnica}")
cmd = [
    "python", SCRIPT_INFER,
    "--prompt", f"Técnica de cartomagia: {args.tecnica}",
    "--pose_json", pose_file,
    "--ref_image", MANO_REF,
    "--out", output_file,
    "--duration", str(args.duracion),
    "--fps", str(args.fps),
    "--resolution", args.resolucion,
    "--seed", str(args.seed)
]

print("🔧 Ejecutando comando:", " ".join(cmd))
subprocess.run(cmd, check=True)

# ✅ Guardar metadatos de la ejecución
metadata = {
    "tecnica": args.tecnica,
    "seed": args.seed,
    "duracion": args.duracion,
    "fps": args.fps,
    "resolucion": args.resolucion,
    "modelo": "AnimateDiff",
    "timestamp": datetime.datetime.now().isoformat()
}

with open(os.path.join(OUTPUT_DIR, f"{args.tecnica}.json"), "w") as meta_file:
    import json
    json.dump(metadata, meta_file, indent=4)

print("✅ Video generado en:", output_file)
print("📝 Metadatos guardados.")
