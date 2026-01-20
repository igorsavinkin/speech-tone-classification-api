from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.queue import InMemoryQueue
from app.schemas import ClassifyRequest, ClassifyResponse, HumanLabelRequest, TaskResponse
from app.services.model import SimpleSentimentModel
from app.services.tasks import TaskService
from app.strategies.majority_vote import MajorityVoteStrategy

app = FastAPI(title="Human-in-the-Loop Validation System")

queue = InMemoryQueue()
model = SimpleSentimentModel()
aggregator = MajorityVoteStrategy(min_votes=3)
service = TaskService(queue=queue, model=model, aggregator=aggregator)


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>HITL Validation Demo</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 40px; max-width: 720px; color: #111; }
          textarea { width: 100%; height: 140px; margin: 8px 0; }
          button { padding: 8px 14px; cursor: pointer; }
          pre {
            background: #0f172a;
            color: #f8fafc;
            padding: 12px;
            border-radius: 6px;
            white-space: pre-wrap;
            word-break: break-word;
          }
        </style>
      </head>
      <body>
        <h1>Human-in-the-Loop Validation</h1>
        <p>Send text to <code>/classify</code> and see the response.</p>
        <label for="text">Text</label>
        <textarea id="text" placeholder="Type text to classify..."></textarea>
        <button id="submit">Classify</button>
        <h3>Response</h3>
        <pre id="output">{}</pre>
        <script>
          const submitBtn = document.getElementById("submit");
          const output = document.getElementById("output");
          submitBtn.addEventListener("click", async () => {
            const text = document.getElementById("text").value.trim();
            if (!text) {
              output.textContent = "Please enter some text.";
              return;
            }
            output.textContent = "Loading...";
            try {
              const response = await fetch("/classify", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text })
              });
              const data = await response.json();
              output.textContent = JSON.stringify(data, null, 2);
            } catch (error) {
              output.textContent = "Error: " + error;
            }
          });
        </script>
      </body>
    </html>
    """


@app.post("/classify", response_model=ClassifyResponse)
def classify(request: ClassifyRequest) -> ClassifyResponse:
    return service.classify(request.text)


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: str) -> TaskResponse:
    return service.get_task(task_id)


@app.post("/tasks/{task_id}/label", response_model=TaskResponse)
def submit_label(task_id: str, request: HumanLabelRequest) -> TaskResponse:
    return service.submit_label(task_id, request.label, request.worker_id)
