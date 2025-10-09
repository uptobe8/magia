
import os
import argparse
import json
import subprocess
from datetime import datetime

def log(msg):
    print(f"[generate.py] {msg}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tecnica", type=str, required=True, help="Nombre exacto de la técnica")
    parser.add_argument("--prompt", type=str, required=True, help="Descripción textual de la técnica")
    parser.add_argument("--duracion", type=int, required=True, help="Duración del video en segundos")
    parser.add_argument("--fps", type=int, required=True, help="Frames por segundo")
    parser.add_argument("--seed", type=int, default=42, help="Seed para generación determinista")
    parser.add_argument("--resolucion", type=str, required=True, help="Resolución en formato '512x512'")
    args = parser.parse_args()

    tecnica_slug = args.tecnica.lower().replace(" ", "_")
    pose_path = f"poses/{tecnica_slug}.json"
    mano_ref_path = "manos/mano_ref.png"
    output_path = f"outputs/{tecnica_slug}.mp4"
    metadata_path = f"outputs/{tecnica_slug}.json"

    # Validaciones
    if not os.path.exists(pose_path):
        raise FileNotFoundError(f"No se encontró el archivo de pose: {pose_path}")
    if not os.path.exists(mano_ref_path):
        raise FileNotFoundError(f"No se encontró la imagen de referencia de manos: {mano_ref_path}")

    log(f"Iniciando generación para la técnica: {args.tecnica}")

    # Ejecutar el modelo AnimateDiff con pose control
    command = [
        "python", "scripts/infer_with_pose.py",
        "--prompt", args.prompt,
        "--pose_json", pose_path,
        "--ref_image", mano_ref_path,
        "--out", output_path,
        "--duration", str(args.duracion),
        "--fps", str(args.fps),
        "--resolution", args.resolucion,
        "--seed", str(args.seed)
    ]

    log("Ejecutando comando:")
    log(" ".join(command))

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        log("Error al generar el video:")
        log(result.stderr)
        raise RuntimeError("Falló la generación del video.")

    # Guardar metadata
    metadata = {
        "tecnica": args.tecnica,
        "prompt": args.prompt,
        "seed": args.seed,
        "duracion": args.duracion,
        "fps": args.fps,
        "resolucion": args.resolucion,
        "modelo": "AnimateDiff-v1.1",
        "output_file": output_path,
        "timestamp": datetime.utcnow().isoformat()
    }

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    log("Video generado correctamente.")
    log(f"Ruta del video: {output_path}")
    log(f"Metadata guardada en: {metadata_path}")

if __name__ == "__main__":
    main()
