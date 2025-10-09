import argparse
import os
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description="Ejecuta AnimateDiff con pose y referencia")

    parser.add_argument('--prompt', type=str, required=True)
    parser.add_argument('--pose_json', type=str, required=True)
    parser.add_argument('--ref_image', type=str, required=True)
    parser.add_argument('--out', type=str, required=True)
    parser.add_argument('--duration', type=int, required=True)
    parser.add_argument('--fps', type=int, required=True)
    parser.add_argument('--resolution', type=str, default="512x512")
    parser.add_argument('--seed', type=int, default=42)

    args = parser.parse_args()

    # Separar resolución
    try:
        width, height = map(int, args.resolution.lower().split("x"))
    except ValueError:
        print("❌ Formato de resolución inválido. Usa formato '512x512'.")
        sys.exit(1)

    # Validar existencia de archivos clave
    if not os.path.isfile(args.pose_json):
        print(f"❌ Archivo de pose no encontrado: {args.pose_json}")
        sys.exit(1)

    if not os.path.isfile(args.ref_image):
        print(f"❌ Imagen de referencia no encontrada: {args.ref_image}")
        sys.exit(1)

    print("🎬 Iniciando generación con AnimateDiff...")
    print(f"📌 Prompt: {args.prompt}")
    print(f"📌 Pose: {args.pose_json}")
    print(f"📌 Imagen ref: {args.ref_image}")
    print(f"📌 Resolución: {width}x{height}, FPS: {args.fps}, Duración: {args.duration}s")
    print(f"📌 Semilla: {args.seed}")

    # Ejecutar comando con subprocess
    cmd = [
        "python", "animatediff/pipelines/run.py",
        "--prompt", args.prompt,
        "--pose", args.pose_json,
        "--ref", args.ref_image,
        "--output", args.out,
        "--width", str(width),
        "--height", str(height),
        "--fps", str(args.fps),
        "--duration", str(args.duration),
        "--seed", str(args.seed)
    ]

    print("🚀 Ejecutando comando:")
    print(" ".join(cmd))

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar AnimateDiff: {e}")
        sys.exit(1)

    print("✅ Generación finalizada.")

if __name__ == "__main__":
    main()
