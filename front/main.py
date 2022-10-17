from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import pandas
import uvicorn
import os

DATA_DIRECTORY = "./data"
app = FastAPI()
app.mount("/static", StaticFiles(directory="./front/static"), name="static")

with open("./front/index.html", "r", encoding="utf-8") as f:
    index_template = f.read()

with open("./front/views/table.html", "r", encoding="utf-8") as f:
    table_template = f.read()


@app.get("/", response_class=HTMLResponse)
async def root():
    csvs = [file.replace('.csv','') for file in os.listdir(DATA_DIRECTORY) if file.endswith('.csv')]
    anchors = "".join([f"<a href='/{file}'>{file}</a>" for file in csvs])
    return index_template.format(anchors=anchors or "Any csv yet")

@app.get("/{pair}", response_class=HTMLResponse)
async def pair_table(pair: str):
    pair = pair.upper().replace('/','')
    file = pandas.read_csv(f"{DATA_DIRECTORY}/{pair}.csv")
    return table_template.format(table=file.to_html(classes='fl-table'),pair=pair)


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, log_level="info", host="0.0.0.0")