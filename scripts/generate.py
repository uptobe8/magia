import os
import sys
import argparse
import subprocess
import datetime
import json
import re

# ✅ Configuración base del entorno
ROOT_DIR = os.path.abspath(os.path.dirname(__file__) + "/..")
POSES_DIR = os.path.join(ROOT_DIR, "poses")
MANO_REF = os.path.join(ROOT_DIR, "manos", "mano_ref.png")
OUTPUT_DIR = os.path.join(ROOT_DIR, "outputs")
SCRIPT_INFER = os.path.join(ROOT_DIR, "scripts", "infer_with_pose.py")

# ✅ Asegurar que la carpeta de salida existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ✅ Validar entradas requeridas
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
        sys.exit(1)

# ✅ Punto de entrada principal
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generar video de técnica de cartomagia")

    parser.add_argument("--tecnica", type=str, required=True, help="Nombre de la técnica (ej. doble_volteo)")
    parser.add_argument("--duracion", type=int, required=True, help="Duración del video en segundos")
    parser.add_argument("--fps", type=int, required=True, help="FPS del video")
    parser.add_argument("--seed", type=int, default=42, help="Semilla para reproducibilidad")
    parser.add_argument("--resolucion", type=str, default="512x512", help="Resolución del video")

    args = parser.parse_args()

    # ✅ Sanitizar nombre de la técnica para evitar errores en nombres de archivos
    tecnica_slug = re.sub(r"[^\w\-]", "_", args.tecnica.lower())

    pose_file = os.path.join(POSES_DIR, f"{tecnica_slug}.json")
    output_file = os.path.join(OUTPUT_DIR, f"{tecnica_slug}.mp4")
    metadata_file = os.path.join(OUTPUT_DIR, f"{tecnica_slug}.json")

    validar_entradas(args.tecnica, pose_file, MANO_REF)

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

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al generar el video: {e}")
        sys.exit(1)

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

    with open(metadata_file, "w") as meta_file:
        json.dump(metadata, meta_file, indent=4)

    print("✅ Video generado en:", output_file)
    print("📝 Metadatos guardados en:", metadata_file)
