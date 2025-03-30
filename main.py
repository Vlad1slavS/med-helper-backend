from fastapi import FastAPI
from voice_message_process import voice_controller
from text_message_proccess import text_controller
from fastapi.responses import JSONResponse
from datetime import datetime

app = FastAPI(title="Медицинский анализатор")

@app.get("/api")
async def get_status():
    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")  # Текущее время в формате UTC
    return JSONResponse(content={"status": "ok", "time": current_time})

# Подключаем роутеры с префиксом "/api"
app.include_router(voice_controller.router, prefix="/api")
app.include_router(text_controller.router, prefix="/api")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)