import argparse
import os

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
    width, height = map(int, args.resolution.lower().split("x"))

    print("🎬 Iniciando generación con AnimateDiff...")
    print(f"📌 Prompt: {args.prompt}")
    print(f"📌 Pose: {args.pose_json}")
    print(f"📌 Imagen ref: {args.ref_image}")
    print(f"📌 Resolución: {width}x{height}, FPS: {args.fps}, Duración: {args.duration}s")
    print(f"📌 Semilla: {args.seed}")

    # 👉 Aquí se hace la llamada real al modelo AnimateDiff
    # Esto es un ejemplo base, deberás adaptarlo a tu setup real

    command = f"""
    python animatediff/pipelines/run.py \
        --prompt "{args.prompt}" \
        --pose {args.pose_json} \
        --ref {args.ref_image} \
        --output {args.out} \
        --width {width} \
        --height {height} \
        --fps {args.fps} \
        --duration {args.duration} \
        --seed {args.seed}
    """

    print("🚀 Ejecutando comando:")
    print(command)
    os.system(command)

    print("✅ Generación finalizada.")

if __name__ == "__main__":
    main()
