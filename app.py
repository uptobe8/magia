from flask import Flask, request, jsonify, abort
import subprocess
import os
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/api/video/generar', methods=['POST'])
def generar_video():
    try:
        data = request.get_json(force=True)

        tecnica = data.get("tecnica")
        prompt = data.get("prompt")
        duracion = data.get("duracion")
        fps = data.get("fps")
        resolucion = data.get("resolucion")
        seed = data.get("seed", 1234)

        if not all([tecnica, prompt, duracion, fps, resolucion]):
            return jsonify({"error": "Faltan parámetros obligatorios"}), 400

        output_dir = "outputs"
        output_video = f"{output_dir}/{tecnica}.mp4"
        metadata_path = f"{output_dir}/{tecnica}.json"

        os.makedirs(output_dir, exist_ok=True)

        # Ejecutar generate.py con los parámetros esperados
        subprocess.run([
            "python", "scripts/generate.py",
            "--tecnica", tecnica,
            "--prompt", prompt,
            "--duracion", str(duracion),
            "--fps", str(fps),
            "--resolucion", resolucion,
            "--seed", str(seed)
        ], check=True)

        if not os.path.exists(output_video):
            return jsonify({"error": "El video no se generó correctamente."}), 500

        metadata = {
            "tecnica": tecnica,
            "prompt": prompt,
            "duracion": duracion,
            "fps": fps,
            "resolucion": resolucion,
            "seed": seed,
            "modelo": "AnimateDiff + Multi-ControlNet + IP-Adapter",
            "commit_hash": "032fc0801140",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        # Guardar metadata localmente (opcional)
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        return jsonify({
            "video_url": f"https://tu-servidor.com/magia/outputs/{tecnica}.mp4",
            "metadata": metadata
        })

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Error al ejecutar generate.py: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
