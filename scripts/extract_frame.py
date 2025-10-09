import cv2
import os

# Ruta del vídeo base
video_path = os.path.join("..", "manos", "video_base.mp4")
# Ruta de salida para la imagen
output_path = os.path.join("..", "manos", "mano_ref.png")

# Abrir el vídeo
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("❌ No se pudo abrir el vídeo:", video_path)
    exit(1)

# Obtener número total de frames
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Elegir un frame del medio del vídeo
target_frame = total_frames // 2
cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)

# Leer ese frame
ret, frame = cap.read()

if not ret:
    print("❌ No se pudo leer el frame del vídeo")
    exit(1)

# Guardar el frame como imagen PNG
cv2.imwrite(output_path, frame)
print("✅ Imagen extraída y guardada en:", output_path)

# Cerrar
cap.release()